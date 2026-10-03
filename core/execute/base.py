import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ScrubVerdict(BaseModel):
    passed: bool
    reason: Optional[str] = None

class ExecutorResponse(BaseModel):
    success: bool
    details: Dict[str, Any]

class BaseExecutor:
    name = "base_executor"
    
    def __init__(self):
        self._execution_log = set() # Sandbox idempotency tracking
        
    def execute(self, case_id: str, action_id: str, plan_cert: Optional[str], params: Dict[str, Any]) -> ExecutorResponse:
        # Must possess valid plan certificate
        if not plan_cert or plan_cert != "VALID_CERT":
            return ExecutorResponse(success=False, details={"error": "Missing or invalid plan certificate"})
            
        idempotency_key = f"{case_id}_{action_id}"
        if idempotency_key in self._execution_log:
            logger.info(f"[{self.name}] Idempotency hit for {idempotency_key}. Skipping.")
            return ExecutorResponse(success=True, details={"note": "idempotent skip"})
            
        # Sandbox mode (logging intent without side effects)
        logger.info(f"[{self.name}] Executing {action_id} for case {case_id} with params {params}")
        
        response = self._do_execute(params)
        
        if response.success:
            self._execution_log.add(idempotency_key)
            
        return response
        
    def _do_execute(self, params: Dict[str, Any]) -> ExecutorResponse:
        raise NotImplementedError
