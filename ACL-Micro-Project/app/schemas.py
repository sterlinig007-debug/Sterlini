from pydantic import BaseModel, Field, field_validator

BRANCHES = {"ECE", "EEE", "CSE"}

class RecordIn(BaseModel):
    student_name: str = Field(min_length=1, max_length=100)
    faculty_name: str = Field(min_length=1, max_length=100)
    branch: str
    email: str = Field(min_length=3, max_length=150)
    phone_number: str = Field(min_length=5, max_length=30)
    description: str = Field(default="", max_length=1000)

    @field_validator("branch")
    @classmethod
    def valid_branch(cls, value):
        value = value.upper()
        if value not in BRANCHES:
            raise ValueError("Branch must be ECE, EEE or CSE")
        return value

class RecordOut(RecordIn):
    id: int
    student_roll_number: str

class AccessExplanationRequest(BaseModel):
    operation: str
    branch: str | None = None
