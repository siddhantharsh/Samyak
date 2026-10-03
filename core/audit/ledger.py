import json
import hashlib
import os
from typing import Dict, Any, List, Optional
from core.entities import DecisionRecord, Diagnosis, ActionPlan, Layer, Arm

def canonical_json(obj: Any) -> str:
    """
    Serializes a dictionary to a canonical JSON string.
    Ensures keys are sorted and whitespace is removed.
    Float formatting is standardized by rounding to 6 decimal places.
    """
    def _normalize_floats(data):
        if isinstance(data, float):
            return round(data, 6)
        elif isinstance(data, dict):
            return {k: _normalize_floats(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [_normalize_floats(item) for item in data]
        return data
        
    normalized = _normalize_floats(obj)
    return json.dumps(normalized, sort_keys=True, separators=(',', ':'))


class AuditLedger:
    def __init__(self, filepath: str = "data/audit_log.jsonl"):
        self.filepath = filepath
        self._ensure_file()
        
    def _ensure_file(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.filepath)), exist_ok=True)
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) == 0:
            with open(self.filepath, 'w') as f:
                # Genesis block
                gen = {"hash": "0" * 64, "is_genesis": True}
                f.write(json.dumps(gen) + "\n")
                
    def get_all(self):
        records = []
        with open(self.filepath, 'r') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        return records
        
    def append(self, record: DecisionRecord) -> str:
        all_recs = self.get_all()
        prev_hash = all_recs[-1]["hash"]
        
        record.seq = len(all_recs)
        record.prev_hash = prev_hash
        record.hash = ""
        
        record_dict = record.model_dump(mode='json')
        del record_dict["hash"]
        
        canonical_str = canonical_json(record_dict)
        
        hasher = hashlib.sha256()
        hasher.update(prev_hash.encode('utf-8'))
        hasher.update(canonical_str.encode('utf-8'))
        
        new_hash = hasher.hexdigest()
        record.hash = new_hash
        
        final_dict = record.model_dump(mode='json')
        
        with open(self.filepath, 'a') as f:
            f.write(json.dumps(final_dict) + "\n")
            
        return new_hash
        
    def verify_chain(self) -> bool:
        records = self.get_all()
        if not records:
            return True
            
        prev_hash = "0" * 64
        # Skip genesis block at index 0
        for i in range(1, len(records)):
            entry = records[i]
            stored_hash = entry["hash"]
            
            verify_dict = entry.copy()
            del verify_dict["hash"]
            
            canonical_str = canonical_json(verify_dict)
            hasher = hashlib.sha256()
            hasher.update(prev_hash.encode('utf-8'))
            hasher.update(canonical_str.encode('utf-8'))
            calculated_hash = hasher.hexdigest()
            
            if calculated_hash != stored_hash:
                return False
                
            prev_hash = stored_hash
            
        return True
