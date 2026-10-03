import yaml
import hashlib
from typing import List, Tuple
from core.constraints.schema import Rule
from core.entities import ConstraintSnapshot, PlannedAction
from core.constraints.predicates import evaluate_predicate

class RuleResult:
    def __init__(self, rule_id: str, passed: bool, reason: str, severity: str, penalty: float = None):
        self.rule_id = rule_id
        self.passed = passed
        self.reason = reason
        self.severity = severity
        self.penalty = penalty

class Register:
    def __init__(self, yaml_path: str):
        with open(yaml_path, "r") as f:
            content = f.read()
        self._hash = hashlib.sha256(content.encode()).hexdigest()
        
        data = yaml.safe_load(content)
        self.rules = [Rule(**r) for r in data["rules"]]
        
        self._index = {}
        for r in self.rules:
            for applies in r.applies_to:
                self._index.setdefault(applies, []).append(r)

    def evaluate(self, action: PlannedAction, snapshot: ConstraintSnapshot) -> List[RuleResult]:
        applicable_rules = []
        for r in self.rules:
            if "ALL" in r.applies_to or "ALL_CONTACT" in r.applies_to or action.kind in r.applies_to:
                applicable_rules.append(r)

        results = []
        for r in applicable_rules:
            passed, reason = evaluate_predicate(r.predicate, snapshot, action)
            results.append(RuleResult(r.id, passed, reason, r.severity, r.penalty_cost))
        return results

    def version_hash(self) -> str:
        return self._hash
