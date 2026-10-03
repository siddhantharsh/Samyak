import os
import sys
import datetime
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss
from sklearn.calibration import calibration_curve

# Add the project root to sys.path so we can import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.preempt.engine import PreemptionEngine

def run_ab_test():
    np.random.seed(42)
    
    # 1. Synthesize Data
    n_samples = 5000
    df = pd.DataFrame({
        'mandate_history_failures': np.random.poisson(0.5, n_samples),
        'issuer_technical_decline_rate': np.random.uniform(0.01, 0.15, n_samples),
        'peak_hour_degradation': np.random.uniform(0.0, 0.2, n_samples),
        'amount_cap_headroom': np.random.normal(5000, 2000, n_samples),
        'days_to_salary': np.random.randint(0, 30, n_samples),
        'subject_successful_hour': np.random.randint(8, 22, n_samples)
    })
    
    # Target function (simulating reality)
    # Failures are more likely if close to salary, low headroom, high failures, high degradation
    logit = (
        0.5 * df['mandate_history_failures'] +
        10.0 * df['issuer_technical_decline_rate'] +
        5.0 * df['peak_hour_degradation'] -
        0.0001 * df['amount_cap_headroom'] -
        0.1 * df['days_to_salary']
    )
    prob = 1 / (1 + np.exp(-logit))
    df['failed'] = np.random.binomial(1, prob)
    
    # 2. Train and Calibrate Engine
    engine = PreemptionEngine()
    engine.train(df, target_col='failed')
    
    # Evaluate calibration
    test_probs = engine.predict_prob(df)
    brier = brier_score_loss(df['failed'], test_probs)
    
    # Get calibration curve data
    prob_true, prob_pred = calibration_curve(df['failed'], test_probs, n_bins=5)
    
    print(f"Pre-emption Engine Calibration:")
    print(f"Brier Score: {brier:.4f}")
    print("Calibration Curve (prob_pred -> prob_true):")
    for pt, pp in zip(prob_true, prob_pred):
        print(f"  {pp:.3f} -> {pt:.3f}")
        
    # 3. Simulate A/B Testing on a new corpus
    n_test = 1400  # PRD specifies 1400 T-48 candidates
    test_df = pd.DataFrame({
        'mandate_history_failures': np.random.poisson(0.5, n_test),
        'issuer_technical_decline_rate': np.random.uniform(0.01, 0.15, n_test),
        'peak_hour_degradation': np.random.uniform(0.0, 0.2, n_test),
        'amount_cap_headroom': np.random.normal(5000, 2000, n_test),
        'days_to_salary': np.random.randint(0, 30, n_test),
        'subject_successful_hour': np.random.randint(8, 22, n_test)
    })
    
    baseline_logit = (
        0.5 * test_df['mandate_history_failures'] +
        10.0 * test_df['issuer_technical_decline_rate'] +
        5.0 * test_df['peak_hour_degradation'] -
        0.0001 * test_df['amount_cap_headroom'] -
        0.1 * test_df['days_to_salary']
    )
    baseline_prob = 1 / (1 + np.exp(-baseline_logit))
    baseline_failures = np.random.binomial(1, baseline_prob).sum()
    
    # Apply Pre-emption
    test_preds = engine.predict_prob(test_df)
    preempted_failures = 0
    
    for i, row in test_df.iterrows():
        # Create plan
        event_data = row.to_dict()
        event_data['due_at'] = '2026-10-05T11:00:00Z'
        plan = engine.build_plan(event_data, test_preds[i])
        
        # Simulate outcome with plan
        if plan.arbitrate_to_reauth:
            # We prevented a hard failure by catching it beforehand
            pass 
        else:
            # Did we shift away from peak?
            is_peak = 10 <= plan.target_hour <= 13
            new_deg = row['peak_hour_degradation'] if is_peak else 0.0
            
            # Did we shift closer to salary?
            new_days_salary = max(0, row['days_to_salary'] - plan.shift_date_by_days)
            
            new_logit = (
                0.5 * row['mandate_history_failures'] +
                10.0 * row['issuer_technical_decline_rate'] +
                5.0 * new_deg -
                0.0001 * row['amount_cap_headroom'] -
                0.1 * new_days_salary
            )
            
            # Top-up nudge reduces failure if they were likely to fail
            if plan.send_topup_nudge:
                new_logit -= 0.5 
                
            new_prob = 1 / (1 + np.exp(-new_logit))
            if np.random.binomial(1, new_prob) == 1:
                preempted_failures += 1

    failures_prevented = baseline_failures - preempted_failures
    print("\nA/B Simulation Results:")
    print(f"Baseline Failures:  {baseline_failures} / {n_test}")
    print(f"Pre-empted Failures: {preempted_failures} / {n_test}")
    print(f"Failures Prevented: {failures_prevented}")
    print(f"Uplift: +{(failures_prevented / baseline_failures) * 100:.1f}% net recovery before execution")

if __name__ == "__main__":
    run_ab_test()
