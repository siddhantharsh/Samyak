from core.execute.dlt_scrub import dlt_scrub

def test_dlt_scrub_success():
    # template: "Dear {#var1#}, your scheduled payment of INR {#var2#} for {#var3#} is due on {#var4#}. Please ensure sufficient balance. - Razorpay"
    vars = ["Siddhanth", "1500", "Netflix", "Oct 15"]
    body = "Dear Siddhanth, your scheduled payment of INR 1500 for Netflix is due on Oct 15. Please ensure sufficient balance. - Razorpay"
    
    verdict = dlt_scrub(body, "NUDGE_01", vars)
    assert verdict.passed is True

def test_dlt_scrub_plausible_rewrite():
    # LLM hallucinates a more polite, "improved" message
    vars = ["Siddhanth", "1500", "Netflix", "Oct 15"]
    body = "Hi Siddhanth, just a quick reminder that your INR 1500 payment for Netflix is due on Oct 15. Please keep sufficient balance!"
    
    verdict = dlt_scrub(body, "NUDGE_01", vars)
    assert verdict.passed is False
    assert "Message body does not exactly match" in verdict.reason

def test_dlt_url_whitelist_fail():
    vars = ["Netflix", "https://scam.com/pay"]
    body = "Your mandate for Netflix failed. Tap here to pay via alternate method: https://scam.com/pay"
    
    verdict = dlt_scrub(body, "LINK_01", vars)
    assert verdict.passed is False
    assert "not in whitelist" in verdict.reason

def test_dlt_url_whitelist_success():
    vars = ["Netflix", "https://rzp.io/i/1234"]
    body = "Your mandate for Netflix failed. Tap here to pay via alternate method: https://rzp.io/i/1234"
    
    verdict = dlt_scrub(body, "LINK_01", vars)
    assert verdict.passed is True
