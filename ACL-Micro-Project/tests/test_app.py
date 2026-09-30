import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

@pytest.fixture()
def client():
    init_db()
    with TestClient(app) as c:
        yield c

def switch(client, user):
    r = client.post("/switch-user", data={"user_id": user}, follow_redirects=False)
    return r.cookies.get("acl_user")

def test_health(client):
    assert client.get("/health").json()["status"] == "ok"

def test_admin_sees_all_records(client):
    cookie = switch(client, "admin")
    r = client.get("/api/records", cookies={"acl_user": cookie})
    data = r.json()
    assert data["access"] == "granted"
    assert len(data["records"]) >= 6

def test_eee_user_sees_only_eee(client):
    cookie = switch(client, "EEEUser")
    r = client.get("/api/records", cookies={"acl_user": cookie})
    assert r.json()["access"] == "granted"
    assert all(x["branch"] == "EEE" for x in r.json()["records"])

def test_no_role_user_sees_no_records(client):
    cookie = switch(client, "NoRoleUser")
    r = client.get("/api/records", cookies={"acl_user": cookie})
    assert r.json()["access"] == "denied"
    assert r.json()["records"] == []

def test_acl_user_can_create(client):
    cookie = switch(client, "ACLUser")
    payload = {
        "student_name":"Test Student","faculty_name":"Test Faculty",
        "branch":"EEE","email":"test@example.com","phone_number":"9999999999",
        "description":"automated test"
    }
    r = client.post("/api/records", json=payload, cookies={"acl_user":cookie})
    assert r.status_code == 200

def test_acl_user_can_write_and_delete(client):
    cookie = switch(client, "ACLUser")
    records = client.get("/api/records", cookies={"acl_user": cookie}).json()["records"]
    record = records[0]
    payload = {
        "student_name":record["student_name"],"faculty_name":record["faculty_name"],
        "branch":record["branch"],"email":record["email"],
        "phone_number":record["phone_number"],"description":"updated"
    }
    r = client.put(f"/api/records/{record['id']}", json=payload, cookies={"acl_user":cookie})
    assert r.status_code == 200
    r = client.delete(f"/api/records/{record['id']}", cookies={"acl_user":cookie})
    assert r.status_code == 200
