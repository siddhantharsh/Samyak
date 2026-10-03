import yaml
import os
from core.entities import LeakEvent, Diagnosis, Layer
from core.diagnose.normalize import normalize_event

_CODE_MAP = None

def get_code_map():
    global _CODE_MAP
    if _CODE_MAP is None:
        path = "data/code_map.yaml"
        if not os.path.exists(path):
            _CODE_MAP = {}
        else:
            with open(path, "r") as f:
                data = yaml.safe_load(f) or []
                _CODE_MAP = {item["unified_code"]: item for item in data}
    return _CODE_MAP

def resolve_l1(event: LeakEvent) -> Diagnosis:
    """
    Deterministic lookup from normalised code to (root_cause, permitted_action_classes).
    Returns Diagnosis(layer=L1_DETERMINISTIC) on success.
    Returns Diagnosis(layer=UNRESOLVED) on failure.
    """
    unified_code = normalize_event(event)
    cmap = get_code_map()
    mapping = cmap.get(unified_code)
    
    if mapping:
        return Diagnosis(
            root_cause=mapping["root_cause"],
            layer=Layer.L1_DETERMINISTIC,
            confidence=1.0,
            permitted_action_classes=set(mapping["permitted_action_classes"]),
            evidence=[f"Mapped from {unified_code}"]
        )
        
    # Unresolved cases fallback to conservative defaults and get routed to L2
    return Diagnosis(
        root_cause="UNKNOWN",
        layer=Layer.UNRESOLVED,
        confidence=0.0,
        permitted_action_classes={"MANUAL_REVIEW"},
        evidence=[f"No L1 mapping found for {unified_code}"]
    )
