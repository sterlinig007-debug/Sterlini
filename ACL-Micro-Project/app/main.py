from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import settings
from .database import get_connection, init_db
from .auth import get_current_user, list_users
from .acl import can_read, can_create, can_write, can_delete
from .schemas import RecordIn, AccessExplanationRequest
from .ai_service import explain_with_gemini

BASE_DIR = Path(__file__).resolve().parent.parent
@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")

def fetch_records(user):
    conn = get_connection()
    if user.is_admin:
        rows = conn.execute("SELECT * FROM institution_details ORDER BY id DESC").fetchall()
    elif "bb1" in user.roles:
        rows = conn.execute(
            "SELECT * FROM institution_details WHERE branch='EEE' ORDER BY id DESC"
        ).fetchall()
    else:
        rows = []
    conn.close()
    return [dict(r) for r in rows]

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    user = get_current_user(request)
    records = fetch_records(user)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "users": list_users(),
        "records": records,
        "can_create": can_create(user).allowed,
        "can_write": can_write(user).allowed,
        "can_delete": can_delete(user).allowed,
        "read_decision": can_read(user),
        "message": request.query_params.get("message"),
    })

@app.post("/switch-user")
def switch_user(user_id: str = Form(...)):
    response = RedirectResponse("/", status_code=303)
    response.set_cookie("acl_user", user_id, httponly=True, samesite="lax")
    return response

@app.get("/api/records")
def api_records(request: Request):
    user = get_current_user(request)
    if not can_read(user).allowed and not user.is_admin:
        return JSONResponse({"records": [], "access": "denied", "reason": can_read(user).reason})
    return {"records": fetch_records(user), "access": "granted"}

@app.post("/api/records")
def api_create(request: Request, record: RecordIn):
    user = get_current_user(request)
    decision = can_create(user)
    if not decision.allowed:
        raise HTTPException(status_code=403, detail=decision.reason)
    conn = get_connection()
    roll = "INS" + str(100000 + (conn.execute("SELECT COUNT(*) FROM institution_details").fetchone()[0] + 1))
    try:
        cur = conn.execute("""
            INSERT INTO institution_details
            (student_roll_number,student_name,faculty_name,branch,email,phone_number,description)
            VALUES (?,?,?,?,?,?,?)
        """, (roll, record.student_name, record.faculty_name, record.branch,
              record.email, record.phone_number, record.description))
        conn.commit()
        return {"id": cur.lastrowid, "student_roll_number": roll, "message": "Record created"}
    finally:
        conn.close()

@app.put("/api/records/{record_id}")
def api_update(request: Request, record_id: int, record: RecordIn):
    user = get_current_user(request)
    decision = can_write(user)
    if not decision.allowed:
        raise HTTPException(status_code=403, detail=decision.reason)
    conn = get_connection()
    cur = conn.execute("""
        UPDATE institution_details SET student_name=?, faculty_name=?, branch=?,
        email=?, phone_number=?, description=? WHERE id=?
    """, (record.student_name, record.faculty_name, record.branch, record.email,
          record.phone_number, record.description, record_id))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Record updated"}

@app.delete("/api/records/{record_id}")
def api_delete(request: Request, record_id: int):
    user = get_current_user(request)
    decision = can_delete(user)
    if not decision.allowed:
        raise HTTPException(status_code=403, detail=decision.reason)
    conn = get_connection()
    cur = conn.execute("DELETE FROM institution_details WHERE id=?", (record_id,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Record deleted"}

@app.post("/api/access/explain")
async def access_explain(request: Request, payload: AccessExplanationRequest):
    user = get_current_user(request)
    operation = payload.operation.lower()
    checks = {
        "read": can_read(user, payload.branch),
        "create": can_create(user),
        "write": can_write(user),
        "update": can_write(user),
        "delete": can_delete(user),
    }
    if operation not in checks:
        raise HTTPException(status_code=400, detail="Operation must be read, create, write/update or delete.")
    decision = checks[operation]
    deterministic = f"User {user.user_id}: {decision.reason} Access {'GRANTED' if decision.allowed else 'DENIED'}."
    ai = await explain_with_gemini(
        f"Explain this educational ServiceNow-style ACL decision simply. "
        f"User={user.user_id}, roles={sorted(user.roles)}, admin={user.is_admin}, "
        f"operation={operation}, branch={payload.branch}, result={deterministic}"
    )
    return {"decision": decision.allowed, "deterministic_reason": decision.reason, "ai_explanation": ai}

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}

@app.get("/docs-info")
def docs_info():
    return {
        "project": "Script-Controlled ACL - Restrict Record Access Based on Field Value",
        "roles": {
            "bb1": "read",
            "bb2": "create",
            "bb3": "write",
            "bb4": "delete",
        },
        "read_condition": "Branch = EEE",
        "admin": "full access",
    }
