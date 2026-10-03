import pytest
from datetime import datetime, timezone
from core.entities import LeakEvent, LeakType, Rail, RawCodes, Context, Layer
from core.diagnose.normalize import normalize_event
from core.diagnose.resolver_l1 import resolve_l1

def _make_event(
    leak_type=LeakType.MANDATE_FAIL,
    npci_code=None,
    mac=None,
    network_category=None,
    issuer_code=None,
    gateway_code=None,
):
    now = datetime.now(timezone.utc)
    rc = RawCodes(
        npci_code=npci_code,
        mac=mac,
        network_category=network_category,
        issuer_code=issuer_code,
        gateway_code=gateway_code
    )
    return LeakEvent(
        id="evt_test",
        tenant_id="t1",
        leak_type=leak_type,
        subject_ref="sub_1",
        amount=100.0,
        currency="INR",
        due_at=now,
        occurred_at=now,
        rail=Rail.UPI_AUTOPAY,
        raw_codes=rc,
        context=Context(),
        idempotency_key="idemp_1"
    )

# 1-13: Test specific mappings present in code_map.yaml
MAPPINGS = [
    (LeakType.MANDATE_FAIL, {"mac": "05"}, "INSUFFICIENT_FUNDS", Layer.L1_DETERMINISTIC),
    (LeakType.MANDATE_FAIL, {"mac": "91"}, "TECHNICAL_DECLINE", Layer.L1_DETERMINISTIC),
    (LeakType.MANDATE_FAIL, {"mac": "14"}, "MANDATE_NOT_FOUND", Layer.L1_DETERMINISTIC),
    (LeakType.MANDATE_FAIL, {"mac": "54"}, "EXPIRED_CARD", Layer.L1_DETERMINISTIC),
    (LeakType.MANDATE_FAIL, {"mac": "AFA"}, "AFA_REQUIRED", Layer.L1_DETERMINISTIC),
    (LeakType.MANDATE_FAIL, {"mac": "59"}, "SUSPECTED_FRAUD", Layer.L1_DETERMINISTIC),
    (LeakType.MANDATE_FAIL, {"mac": "21"}, "VELOCITY_LIMIT_EXCEEDED", Layer.L1_DETERMINISTIC),
    (LeakType.MANDATE_FAIL, {"npci_code": "REVOKED"}, "MANDATE_REVOKED", Layer.L1_DETERMINISTIC),
    (LeakType.CHECKOUT_ABANDON, {"network_category": "TIMEOUT"}, "CHECKOUT_TIMEOUT", Layer.L1_DETERMINISTIC),
    (LeakType.MANDATE_DEBIT_DUE, {}, "UPCOMING_DEBIT", Layer.L1_DETERMINISTIC),
    (LeakType.INVOICE_OVERDUE, {}, "INVOICE_OVERDUE", Layer.L1_DETERMINISTIC),
    (LeakType.CHECKOUT_ABANDON, {}, "ABANDONMENT", Layer.L1_DETERMINISTIC),
    (LeakType.MANDATE_FAIL, {}, "UNKNOWN_DECLINE", Layer.L1_DETERMINISTIC),
]

@pytest.mark.parametrize("leak_type, rc_kwargs, expected_cause, expected_layer", MAPPINGS)
def test_resolver_mappings(leak_type, rc_kwargs, expected_cause, expected_layer):
    ev = _make_event(leak_type=leak_type, **rc_kwargs)
    diag = resolve_l1(ev)
    assert diag.root_cause == expected_cause
    assert diag.layer == expected_layer

# 14-23: Test Unresolved / Fallbacks (10 cases)
UNRESOLVED_CASES = [
    (LeakType.PAYMENT_FAIL, {"mac": "UNKNOWN_99"}),
    (LeakType.PAYMENT_FAIL, {"npci_code": "UNKNOWN_99"}),
    (LeakType.PAYMENT_FAIL, {"network_category": "UNKNOWN_99"}),
    (LeakType.PAYMENT_FAIL, {"issuer_code": "UNKNOWN_99"}),
    (LeakType.PAYMENT_FAIL, {"gateway_code": "UNKNOWN_99"}),
    (LeakType.MANDATE_FAIL, {"mac": "OTHER"}),
    (LeakType.CHECKOUT_ABANDON, {"mac": "05"}), # MAC:05 is mapped, so it resolves despite being CHECKOUT_ABANDON
    (LeakType.PAYMENT_FAIL, {}), # LEAK:PAYMENT_FAIL is not mapped -> UNRESOLVED
    (LeakType.INVOICE_OVERDUE, {"mac": "UNMAPPED"}), 
    (LeakType.MANDATE_DEBIT_DUE, {"issuer_code": "404"}),
]

@pytest.mark.parametrize("leak_type, rc_kwargs", UNRESOLVED_CASES)
def test_resolver_unresolved(leak_type, rc_kwargs):
    ev = _make_event(leak_type=leak_type, **rc_kwargs)
    diag = resolve_l1(ev)
    
    # If the normalized code actually exists in mapping, it should resolve.
    # Otherwise it should be UNRESOLVED.
    norm = normalize_event(ev)
    from core.diagnose.resolver_l1 import get_code_map
    cmap = get_code_map()
    
    if norm in cmap:
        assert diag.layer == Layer.L1_DETERMINISTIC
    else:
        assert diag.layer == Layer.UNRESOLVED
        assert diag.root_cause == "UNKNOWN"

# 24-40: Normalization Precedence Tests (17 cases)
PRECEDENCE_CASES = [
    # NPCI beats everything
    ({"npci_code": "A", "mac": "B", "network_category": "C", "issuer_code": "D", "gateway_code": "E"}, "NPCI:A"),
    ({"npci_code": "A", "mac": "B"}, "NPCI:A"),
    ({"npci_code": "A", "network_category": "C"}, "NPCI:A"),
    ({"npci_code": "A", "issuer_code": "D"}, "NPCI:A"),
    ({"npci_code": "A", "gateway_code": "E"}, "NPCI:A"),
    
    # MAC beats Network, Issuer, Gateway
    ({"mac": "B", "network_category": "C", "issuer_code": "D", "gateway_code": "E"}, "MAC:B"),
    ({"mac": "B", "network_category": "C"}, "MAC:B"),
    ({"mac": "B", "issuer_code": "D"}, "MAC:B"),
    ({"mac": "B", "gateway_code": "E"}, "MAC:B"),
    
    # Network beats Issuer, Gateway
    ({"network_category": "C", "issuer_code": "D", "gateway_code": "E"}, "NETWORK:C"),
    ({"network_category": "C", "issuer_code": "D"}, "NETWORK:C"),
    ({"network_category": "C", "gateway_code": "E"}, "NETWORK:C"),
    
    # Issuer beats Gateway
    ({"issuer_code": "D", "gateway_code": "E"}, "ISSUER:D"),
    
    # Gateway beats Leak fallback
    ({"gateway_code": "E", "mac": None}, "GATEWAY:E"),
    ({"gateway_code": "E"}, "GATEWAY:E"),
    
    # Leak fallback
    ({"npci_code": None, "mac": None}, "LEAK:MANDATE_FAIL"),
    ({}, "LEAK:MANDATE_FAIL")
]

@pytest.mark.parametrize("rc_kwargs, expected_norm", PRECEDENCE_CASES)
def test_normalization_precedence(rc_kwargs, expected_norm):
    ev = _make_event(leak_type=LeakType.MANDATE_FAIL, **rc_kwargs)
    norm = normalize_event(ev)
    assert norm == expected_norm

# 41-50: Edge Cases (10 cases)
EDGE_CASES = [
    # Whitespaces / cases (assuming exact match is currently implemented, if it fails, it's UNRESOLVED)
    ({"mac": " 05"}, "MAC: 05"),
    ({"npci_code": ""}, "LEAK:MANDATE_FAIL"), # Empty string should fall through if falsy
    ({"mac": None}, "LEAK:MANDATE_FAIL"),
    ({"mac": "05", "npci_code": ""}, "MAC:05"),
    ({"network_category": "TIMEOUT "}, "NETWORK:TIMEOUT "),
    # Different leak types fallback correctly
    ({}, "LEAK:PAYMENT_FAIL", LeakType.PAYMENT_FAIL),
    ({}, "LEAK:CHECKOUT_ABANDON", LeakType.CHECKOUT_ABANDON),
    ({}, "LEAK:INVOICE_OVERDUE", LeakType.INVOICE_OVERDUE),
    ({}, "LEAK:MANDATE_DEBIT_DUE", LeakType.MANDATE_DEBIT_DUE),
    ({"gateway_code": "XYZ"}, "GATEWAY:XYZ", LeakType.PAYMENT_FAIL),
]

@pytest.mark.parametrize("case", EDGE_CASES)
def test_normalization_edge_cases(case):
    if len(case) == 2:
        rc_kwargs, expected_norm = case
        leak_type = LeakType.MANDATE_FAIL
    else:
        rc_kwargs, expected_norm, leak_type = case
        
    ev = _make_event(leak_type=leak_type, **rc_kwargs)
    norm = normalize_event(ev)
    assert norm == expected_norm
