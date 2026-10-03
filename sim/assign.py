import hashlib
from enum import Enum

class Arm(str, Enum):
    TREATMENT = "TREATMENT"
    HOLDOUT = "HOLDOUT"

def assign_arm(subject_id: str) -> Arm:
    """
    Deterministic treatment/holdout assignment hashed on subject ID.
    Holdout receives statutory communications (post-debit confirmations under RBI-EM-03)
    but no pre-emption or recovery optimization.
    """
    digest = hashlib.sha256(subject_id.encode('utf-8')).hexdigest()
    # Use the first 8 characters to form an integer. 50/50 split.
    val = int(digest[:8], 16)
    if val % 2 == 0:
        return Arm.TREATMENT
    return Arm.HOLDOUT
