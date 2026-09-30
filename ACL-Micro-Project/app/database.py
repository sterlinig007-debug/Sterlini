import sqlite3
from pathlib import Path
from .config import settings

def db_path() -> Path:
    path = Path(settings.database_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent.parent / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def get_connection():
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL,
        is_admin INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS user_roles (
        user_id INTEGER NOT NULL,
        role_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, role_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS institution_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_roll_number TEXT UNIQUE NOT NULL,
        student_name TEXT NOT NULL,
        faculty_name TEXT NOT NULL,
        branch TEXT NOT NULL CHECK(branch IN ('ECE','EEE','CSE')),
        email TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT ''
    );
    """)
    seed(conn)
    conn.commit()
    conn.close()

def seed(conn):
    roles = [
        ("bb1", "Read access to EEE records"),
        ("bb2", "Create access"),
        ("bb3", "Write/edit access"),
        ("bb4", "Delete access"),
    ]
    for name, desc in roles:
        conn.execute("INSERT OR IGNORE INTO roles(name, description) VALUES (?,?)", (name, desc))

    users = [
        ("admin", "System", "Administrator", "admin@example.com", 1),
        ("EEEUser", "EEE", "User", "eeeuser@gmail.com", 0),
        ("NoRoleUser", "No", "Role", "norole@example.com", 0),
        ("ACLUser", "ACL", "User", "acluser@example.com", 0),
    ]
    for u in users:
        conn.execute(
            "INSERT OR IGNORE INTO users(user_id,first_name,last_name,email,is_admin) VALUES (?,?,?,?,?)",
            u
        )
    conn.execute("""
        INSERT OR IGNORE INTO user_roles(user_id, role_id)
        SELECT u.id, r.id FROM users u, roles r
        WHERE u.user_id='EEEUser' AND r.name='bb1'
    """)
    for role in ("bb1","bb2","bb3","bb4"):
        conn.execute("""
            INSERT OR IGNORE INTO user_roles(user_id, role_id)
            SELECT u.id, r.id FROM users u, roles r
            WHERE u.user_id='ACLUser' AND r.name=?
        """, (role,))

    count = conn.execute("SELECT COUNT(*) FROM institution_details").fetchone()[0]
    if count == 0:
        rows = [
            ("INS000001","Guna Sai","Abel Tuer","EEE","guna.sai@example.com","9090909765","EEE sample record"),
            ("INS000002","Pashanth Reddy","Abel Tuer","EEE","pashanth.reddy@example.com","9090909090","EEE sample record"),
            ("INS000003","Praneeth","ITI User","ECE","praneeth@example.com","9090901906","ECE sample record"),
            ("INS000004","Abraham Lincoln","Mala Sreen Kumar","CSE","abraham@example.com","8978089699","CSE sample record"),
            ("INS000005","Siva Nandini","ITI User","ECE","siva@example.com","9080909090","ECE sample record"),
            ("INS000006","Guna Sri","Abel Tuer","CSE","guna.sri@example.com","9090900765","CSE sample record"),
        ]
        conn.executemany("""
            INSERT INTO institution_details
            (student_roll_number,student_name,faculty_name,branch,email,phone_number,description)
            VALUES (?,?,?,?,?,?,?)
        """, rows)
