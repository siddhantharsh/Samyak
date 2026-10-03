from core.execute.base import BaseExecutor, ExecutorResponse
from core.execute.dlt_scrub import dlt_scrub

class MandateRepresentExecutor(BaseExecutor):
    name = "mandate.represent"
    
    def _do_execute(self, params):
        attempts = params.get("attempts_remaining", 1)
        if attempts <= 0:
            return ExecutorResponse(success=False, details={"error": "attempts_remaining <= 0"})
        return ExecutorResponse(success=True, details={"status": "represented_sandbox"})
        
class MessageSendExecutor(BaseExecutor):
    name = "message.send"
    
    def _do_execute(self, params):
        template_id = params.get("template_id")
        body = params.get("body")
        variables = params.get("variables", [])
        
        verdict = dlt_scrub(body, template_id, variables)
        if not verdict.passed:
            return ExecutorResponse(success=False, details={"error": f"DLT Scrub Failed: {verdict.reason}"})
            
        return ExecutorResponse(success=True, details={"status": "message_sent_sandbox"})

class LinkIssueExecutor(BaseExecutor):
    name = "link.issue"
    def _do_execute(self, params):
        return ExecutorResponse(success=True, details={"status": "link_issued_sandbox", "url": "https://rzp.io/mock"})

class AREscalateExecutor(BaseExecutor):
    name = "ar.escalate"
    def _do_execute(self, params):
        return ExecutorResponse(success=True, details={"status": "escalated_sandbox"})

class HumanHandoffExecutor(BaseExecutor):
    name = "human.handoff"
    def _do_execute(self, params):
        return ExecutorResponse(success=True, details={"status": "handed_off_sandbox"})
        
class VoiceScriptExecutor(BaseExecutor):
    name = "voice.script"
    def _do_execute(self, params):
        return ExecutorResponse(success=True, details={"status": "script_generated_sandbox", "script": "Hello, I am an AI..."})

# Registry to fetch executor instances
_EXECUTORS = {
    e.name: e() for e in [
        MandateRepresentExecutor,
        MessageSendExecutor,
        LinkIssueExecutor,
        AREscalateExecutor,
        HumanHandoffExecutor,
        VoiceScriptExecutor
    ]
}

def get_executor(name: str) -> BaseExecutor:
    return _EXECUTORS.get(name)
