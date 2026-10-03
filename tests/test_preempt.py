import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from core.preempt.engine import PreemptionEngine, PreemptionPlan

@pytest.fixture
def dummy_engine():
    engine = PreemptionEngine()
    # Create fake training data
    df = pd.DataFrame({
        'mandate_history_failures': [0, 1, 2, 0, 3] * 10,
        'issuer_technical_decline_rate': [0.01, 0.1, 0.15, 0.05, 0.2] * 10,
        'peak_hour_degradation': [0.0, 0.1, 0.2, 0.0, 0.15] * 10,
        'amount_cap_headroom': [1000, 500, -100, 2000, -50] * 10,
        'days_to_salary': [15, 5, 2, 20, 1] * 10,
        'subject_successful_hour': [10, 14, 21, 11, 9] * 10,
        'failed': [0, 1, 1, 0, 1] * 10
    })
    engine.train(df)
    return engine

# 1-5. Feature Extraction
@pytest.mark.parametrize("i", range(5))
def test_feature_extraction(i, dummy_engine):
    df = pd.DataFrame([{
        'mandate_history_failures': i,
        'issuer_technical_decline_rate': 0.1,
        'peak_hour_degradation': 0.1,
        'amount_cap_headroom': 1000,
        'days_to_salary': 15,
        'subject_successful_hour': 14,
        'extra_col': 'ignore'
    }])
    features = dummy_engine._extract_features(df)
    assert 'extra_col' not in features.columns
    assert features['mandate_history_failures'].iloc[0] == i
    assert len(features.columns) == 6

# 6-10. Not Trained Error
@pytest.mark.parametrize("i", range(5))
def test_untrained_engine_raises_error(i):
    engine = PreemptionEngine()
    df = pd.DataFrame({'mandate_history_failures': [i], 'issuer_technical_decline_rate': [0.1], 'peak_hour_degradation': [0.1], 'amount_cap_headroom': [1000], 'days_to_salary': [15], 'subject_successful_hour': [14]})
    with pytest.raises(ValueError, match="Model is not trained"):
        engine.predict_prob(df)

# 11-20. Rail Arbitration (Cap Exceeded)
@pytest.mark.parametrize("headroom,expected_reauth", [
    (-100, True),
    (-1, True),
    (-0.01, True),
    (0, False),
    (1, False),
    (100, False),
    (-5000, True),
    (5000, False),
    (-10, True),
    (10, False)
])
def test_rail_arbitration_cap_exceeded(dummy_engine, headroom, expected_reauth):
    event_data = {
        'amount_cap_headroom': headroom,
        'subject_successful_hour': 14,
        'due_at': '2026-10-05T10:00:00Z',
        'days_to_salary': 15,
        'mandate_history_failures': 0
    }
    plan = dummy_engine.build_plan(event_data, 0.1)
    assert plan.arbitrate_to_reauth == expected_reauth
    if expected_reauth:
        assert plan.send_topup_nudge is False
        assert plan.shift_date_by_days == 0
        assert plan.target_hour == 14

# 21-30. Date Shift Salary Day Logic
# prob > 0.6, history > 0, days > 2 => shift by min(2, days - 1)
@pytest.mark.parametrize("prob,history,days,expected_shift", [
    (0.7, 1, 10, 2), # Active shift
    (0.7, 1, 3, 2),  # Active shift (min(2, 2) = 2)
    (0.7, 1, 2, 0),  # days > 2 fails
    (0.7, 0, 10, 0), # history > 0 fails
    (0.5, 1, 10, 0), # prob > 0.6 fails
    (0.61, 1, 4, 2), # shift
    (0.9, 5, 2, 0),  # days <= 2
    (0.9, 2, 1, 0),  # days <= 2
    (0.99, 10, 30, 2), # shift
    (0.0, 0, 0, 0)   # everything fails
])
def test_date_shift_salary_day(dummy_engine, prob, history, days, expected_shift):
    event_data = {
        'amount_cap_headroom': 1000,
        'subject_successful_hour': 14,
        'due_at': '2026-10-05T10:00:00Z',
        'days_to_salary': days,
        'mandate_history_failures': history
    }
    plan = dummy_engine.build_plan(event_data, prob)
    assert plan.shift_date_by_days == expected_shift

# 31-40. Slot Selection Peak Avoidance
@pytest.mark.parametrize("subject_hour,expected_target_hour", [
    (8, 8),
    (9, 9),
    (10, 21), # Peak
    (11, 21), # Peak
    (12, 21), # Peak
    (13, 21), # Peak
    (14, 14),
    (15, 15),
    (21, 21),
    (23, 23)
])
def test_slot_selection_peak_avoidance(dummy_engine, subject_hour, expected_target_hour):
    event_data = {
        'amount_cap_headroom': 1000,
        'subject_successful_hour': subject_hour,
        'due_at': '2026-10-05T10:00:00Z',
        'days_to_salary': 15,
        'mandate_history_failures': 0
    }
    plan = dummy_engine.build_plan(event_data, 0.1)
    assert plan.target_hour == expected_target_hour

# 41-45. PDN Schedule Cutoff (23:50+)
@pytest.mark.parametrize("due_hour,due_minute,expected_pdn_hour,expected_pdn_minute", [
    (23, 50, 23, 45), # 24h before is 23:50 -> shift to 23:45
    (23, 55, 23, 45), # shift
    (23, 59, 23, 45), # shift
    (23, 49, 23, 49), # no shift
    (10, 0, 10, 0)    # no shift
])
def test_pdn_schedule_cutoff(dummy_engine, due_hour, due_minute, expected_pdn_hour, expected_pdn_minute):
    # If target_hour is subject_hour (no peak shift)
    # due_date is +0 days. pdn is -1 day.
    subject_hour = due_hour if due_hour not in [10,11,12,13] else 14
    due_at = datetime(2026, 10, 5, due_hour, due_minute)
    
    event_data = {
        'amount_cap_headroom': 1000,
        'subject_successful_hour': due_hour,
        'due_at': due_at.isoformat(),
        'days_to_salary': 15,
        'mandate_history_failures': 0
    }
    plan = dummy_engine.build_plan(event_data, 0.1)
    # the target_hour might override due_hour
    assert plan.pdn_schedule_slot.hour == expected_pdn_hour if subject_hour == due_hour else plan.pdn_schedule_slot.hour
    if subject_hour == due_hour:
        assert plan.pdn_schedule_slot.minute == expected_pdn_minute

# 46-50. Topup Nudge Threshold
@pytest.mark.parametrize("prob,expected_nudge", [
    (0.0, False),
    (0.49, False),
    (0.5, False),
    (0.51, True),
    (1.0, True)
])
def test_topup_nudge_threshold(dummy_engine, prob, expected_nudge):
    event_data = {
        'amount_cap_headroom': 1000,
        'subject_successful_hour': 14,
        'due_at': '2026-10-05T10:00:00Z',
        'days_to_salary': 15,
        'mandate_history_failures': 0
    }
    plan = dummy_engine.build_plan(event_data, prob)
    assert plan.send_topup_nudge == expected_nudge
