# Script-Controlled ACL – Restrict Record Access Based on Field Value

This project is a **local educational simulator** of the ServiceNow lab described in the supplied documentation. The source lab creates an `Institution Details` table and uses four custom roles:

- `bb1` → READ
- `bb2` → CREATE
- `bb3` → WRITE
- `bb4` → DELETE
- `admin` → full access

The READ rule includes the data condition **Branch = EEE**. The supplied lab therefore demonstrates record-level access using both role checks and a field-value condition.

## Important scope note

The supplied document is a ServiceNow administration lab, not a conventional standalone Python web application. This repository does not replace a ServiceNow instance or its native ACL engine. It provides a runnable VS Code/FastAPI simulator so learners can practice and test the same access-control logic locally.

The source document does not specify an AI/LLM component. An optional Gemini explanation endpoint has therefore been added only as an extension; it is not required for ACL functionality.

## Folder structure

```text
ACL-Micro-Project/
├── app/
│   ├── main.py
│   ├── acl.py
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── schemas.py
│   ├── ai_service.py
│   ├── templates/index.html
│   └── static/
│       ├── style.css
│       └── app.js
├── tests/test_app.py
├── data/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## VS Code setup

### 1. Install Python

Use Python 3.10 or newer.

Verify:

```bash
python --version
```

### 2. Open the project

Extract the ZIP and open the `ACL-Micro-Project` folder in VS Code.

### 3. Create a virtual environment

Windows PowerShell:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
py -3 -m venv .venv
.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure environment

Copy `.env.example` to `.env`.

Gemini is optional:

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
```

If no key is supplied, the ACL simulator still works and the explanation endpoint uses a deterministic explanation.

## Run

```bash
uvicorn app.main:app --reload
```

Open:

- Application: http://127.0.0.1:8000/
- API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## Test the lab scenarios

### Scenario 1 – Admin

Select `admin`.

Expected:

- READ → granted
- CREATE → granted
- WRITE → granted
- DELETE → granted
- All ECE, EEE and CSE records are visible.

### Scenario 2 – EEE User

Select `EEEUser`.

Expected:

- READ → granted
- Only EEE records are displayed.
- CREATE/WRITE/DELETE → denied.

### Scenario 3 – No Role User

Select `NoRoleUser`.

Expected:

- READ → denied
- No records displayed.
- CREATE/WRITE/DELETE → denied.

### Scenario 4 – All roles

Select `ACLUser`.

Expected:

- READ → only EEE records are displayed.
- CREATE → granted.
- WRITE → granted.
- DELETE → granted.

## API examples

### Read

```bash
curl http://127.0.0.1:8000/api/records
```

Use a cookie to impersonate a user:

```bash
curl -H "Cookie: acl_user=EEEUser" http://127.0.0.1:8000/api/records
```

### Create

```bash
curl -X POST http://127.0.0.1:8000/api/records   -H "Content-Type: application/json"   -H "Cookie: acl_user=ACLUser"   -d "{"student_name":"New Student","faculty_name":"Faculty","branch":"EEE","email":"new@example.com","phone_number":"9999999999","description":"Demo"}"
```

### Run automated tests

```bash
pytest -q
```

The included test suite covers health, admin visibility, EEE-only read access, no-role denial, create, write and delete permissions.

## ServiceNow mapping

The local simulator maps the supplied lab to:

| Supplied lab item | Local implementation |
|---|---|
| Institution Details | `institution_details` SQLite table |
| Student Roll Number | `student_roll_number` |
| Student Name | `student_name` |
| Faculty Name | `faculty_name` |
| Branch | `branch` |
| Email | `email` |
| Phone Number | `phone_number` |
| Description | `description` |
| bb1 | `can_read()` |
| bb2 | `can_create()` |
| bb3 | `can_write()` |
| bb4 | `can_delete()` |
| Admin | full access |
| Branch = EEE condition | read filtering |

## Optional Gemini explanation

Install nothing extra because `google-genai` is already included in `requirements.txt`.

Add:

```env
GEMINI_API_KEY=your-key
```

Then use **ACL Explanation → Explain Decision** in the UI. The Gemini call explains the already-computed ACL decision; the LLM does not decide permissions. This is intentional: authorization must remain deterministic and must never depend on an LLM response.

## Security note

This is a teaching project. The user-switching mechanism intentionally simulates ServiceNow impersonation and is not suitable as production authentication. For production, replace it with real authentication, authorization middleware, CSRF protection, secure sessions, HTTPS and a proper user/role provider.

## Direct ServiceNow implementation

For the actual ServiceNow lab, follow the supplied documentation inside a ServiceNow instance:

1. Create the EEE user.
2. Create `bb1`, `bb2`, `bb3`, `bb4`.
3. Create `u_institution_details`.
4. Add the documented fields.
5. Create the READ ACL with `Branch = EEE`.
6. Add the documented script.
7. Create CREATE/WRITE/DELETE ACLs with the corresponding roles.
8. Impersonate users and verify the access matrix.

The screenshots in the source document show the corresponding ServiceNow forms, ACL list, data condition, script field, impersonation and verification screens.
