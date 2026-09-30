from dataclasses import dataclass
from fastapi import Request
from .database import get_connection

@dataclass
class CurrentUser:
    id: int
    user_id: str
    first_name: str
    last_name: str
    email: str
    is_admin: bool
    roles: set[str]

def get_current_user(request: Request) -> CurrentUser:
    selected = request.cookies.get("acl_user", "admin")
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE user_id=?", (selected,)).fetchone()
    if not row:
        row = conn.execute("SELECT * FROM users WHERE user_id='admin'").fetchone()
    role_rows = conn.execute("""
        SELECT r.name FROM roles r
        JOIN user_roles ur ON ur.role_id=r.id
        WHERE ur.user_id=?
    """, (row["id"],)).fetchall()
    conn.close()
    return CurrentUser(
        id=row["id"], user_id=row["user_id"], first_name=row["first_name"],
        last_name=row["last_name"], email=row["email"],
        is_admin=bool(row["is_admin"]), roles={r["name"] for r in role_rows}
    )

def list_users():
    conn = get_connection()
    rows = conn.execute("SELECT user_id, first_name, last_name FROM users ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]
