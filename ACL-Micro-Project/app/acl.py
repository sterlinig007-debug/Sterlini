from dataclasses import dataclass
from .auth import CurrentUser

@dataclass
class Decision:
    allowed: bool
    reason: str

def can_read(user: CurrentUser, branch: str | None = None) -> Decision:
    if user.is_admin:
        return Decision(True, "Administrator has full access.")
    if "bb1" not in user.roles:
        return Decision(False, "Read ACL requires role bb1.")
    if branch is not None and branch != "EEE":
        return Decision(False, "The read ACL data condition allows only Branch = EEE.")
    return Decision(True, "Role bb1 is allowed to read EEE records.")

def can_create(user: CurrentUser) -> Decision:
    if user.is_admin:
        return Decision(True, "Administrator has full access.")
    if "bb2" in user.roles:
        return Decision(True, "Create ACL requires role bb2.")
    return Decision(False, "Create ACL requires role bb2.")

def can_write(user: CurrentUser) -> Decision:
    if user.is_admin:
        return Decision(True, "Administrator has full access.")
    if "bb3" in user.roles:
        return Decision(True, "Write ACL requires role bb3.")
    return Decision(False, "Write ACL requires role bb3.")

def can_delete(user: CurrentUser) -> Decision:
    if user.is_admin:
        return Decision(True, "Administrator has full access.")
    if "bb4" in user.roles:
        return Decision(True, "Delete ACL requires role bb4.")
    return Decision(False, "Delete ACL requires role bb4.")
