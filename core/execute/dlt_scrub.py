import re
import yaml
from core.execute.base import ScrubVerdict

_TEMPLATES = None

def get_templates():
    global _TEMPLATES
    if _TEMPLATES is None:
        try:
            with open("data/templates.yaml", "r") as f:
                data = yaml.safe_load(f)
                _TEMPLATES = {t["id"]: t for t in data.get("templates", [])}
        except FileNotFoundError:
            _TEMPLATES = {}
    return _TEMPLATES

def dlt_scrub(message_body: str, template_id: str, variables: list[str]) -> ScrubVerdict:
    templates = get_templates()
    if template_id not in templates:
        return ScrubVerdict(passed=False, reason=f"Template {template_id} not found in registry")
        
    template = templates[template_id]
    expected_body = template["body"]
    
    substituted_body = expected_body
    for i, var_val in enumerate(variables, start=1):
        placeholder = f"{{#var{i}#}}"
        substituted_body = substituted_body.replace(placeholder, str(var_val))
        
    # Strict matching - Indian TRAI DLT rule
    if message_body.strip() != substituted_body.strip():
        return ScrubVerdict(passed=False, reason="Message body does not exactly match registered template after substitution")
        
    urls = re.findall(r'(https?://[^\s]+)', message_body)
    whitelisted = template.get("whitelisted_urls", [])
    
    for url in urls:
        domain_match = False
        for w in whitelisted:
            if w in url:
                domain_match = True
                break
        if not domain_match:
            return ScrubVerdict(passed=False, reason=f"URL {url} not in whitelist")
            
    return ScrubVerdict(passed=True)
