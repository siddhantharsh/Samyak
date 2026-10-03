import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.isotonic import IsotonicRegression
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class PreemptionPlan(BaseModel):
    shift_date_by_days: int
    target_hour: int
    send_topup_nudge: bool
    arbitrate_to_reauth: bool
    pdn_schedule_slot: datetime
    predicted_failure_prob: float

class PreemptionEngine:
    def __init__(self):
        self.model = lgb.LGBMClassifier(random_state=42, n_estimators=50)
        self.calibrator = IsotonicRegression(out_of_bounds='clip')
        self.is_trained = False
        
    def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Features expected:
        - mandate_history_failures (int)
        - issuer_technical_decline_rate (float)
        - peak_hour_degradation (float)
        - amount_cap_headroom (float)
        - days_to_salary (int)
        - subject_successful_hour (int)
        """
        features = df[['mandate_history_failures', 'issuer_technical_decline_rate', 
                       'peak_hour_degradation', 'amount_cap_headroom', 
                       'days_to_salary', 'subject_successful_hour']].copy()
        return features

    def train(self, df: pd.DataFrame, target_col: str = 'failed'):
        X = self._extract_features(df)
        y = df[target_col]
        
        split_idx = int(len(X) * 0.8)
        X_train, y_train = X.iloc[:split_idx], y.iloc[:split_idx]
        X_cal, y_cal = X.iloc[split_idx:], y.iloc[split_idx:]
        
        self.model.fit(X_train, y_train)
        
        if len(X_cal) > 0:
            probs = self.model.predict_proba(X_cal)[:, 1]
            self.calibrator.fit(probs, y_cal)
        else:
            probs = self.model.predict_proba(X_train)[:, 1]
            self.calibrator.fit(probs, y_train)
            
        self.is_trained = True
        
    def predict_prob(self, df: pd.DataFrame) -> np.ndarray:
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")
        X = self._extract_features(df)
        uncalibrated_probs = self.model.predict_proba(X)[:, 1]
        calibrated_probs = self.calibrator.predict(uncalibrated_probs)
        return calibrated_probs
        
    def build_plan(self, event_data: dict, prob: float) -> PreemptionPlan:
        cap_exceeded = event_data.get('amount_cap_headroom', 0) < 0
        
        due_at = event_data.get('due_at')
        if isinstance(due_at, str):
            due_at = datetime.fromisoformat(due_at)
            
        if cap_exceeded:
            return PreemptionPlan(
                shift_date_by_days=0,
                target_hour=event_data.get('subject_successful_hour', 10),
                send_topup_nudge=False,
                arbitrate_to_reauth=True,
                pdn_schedule_slot=due_at - timedelta(days=1),
                predicted_failure_prob=prob
            )
            
        days_to_salary = event_data.get('days_to_salary', 15)
        history_failures = event_data.get('mandate_history_failures', 0)
        
        shift_days = 0
        if prob > 0.6 and history_failures > 0 and days_to_salary > 2:
            shift_days = min(2, days_to_salary - 1)
            
        subject_hour = event_data.get('subject_successful_hour', 14)
        if 10 <= subject_hour <= 13: # Peak window
            target_hour = 21 # Shift to night
        else:
            target_hour = subject_hour
            
        due_date = due_at + timedelta(days=int(shift_days))
        new_due_time = due_date.replace(hour=int(target_hour), minute=due_at.minute, second=0, microsecond=0)
        
        pdn_time = new_due_time - timedelta(days=1)
        if pdn_time.hour == 23 and pdn_time.minute >= 50:
            pdn_time = pdn_time.replace(minute=45)
            
        send_nudge = prob > 0.5
        
        return PreemptionPlan(
            shift_date_by_days=shift_days,
            target_hour=target_hour,
            send_topup_nudge=send_nudge,
            arbitrate_to_reauth=False,
            pdn_schedule_slot=pdn_time,
            predicted_failure_prob=prob
        )
