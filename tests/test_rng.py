from datetime import datetime
from core.rng import seeded_rng, FrozenClock, SystemClock

def test_seeded_rng_determinism():
    rng1 = seeded_rng(42)
    rng2 = seeded_rng(42)
    
    assert rng1.random() == rng2.random()
    assert rng1.randint(1, 100) == rng2.randint(1, 100)
    
    rng3 = seeded_rng(24)
    assert rng1.random() != rng3.random()

def test_frozen_clock():
    fixed_time = datetime(2026, 1, 1, 12, 0, 0)
    clock = FrozenClock(fixed_time)
    
    assert clock.now() == fixed_time
    assert clock.now() == clock.now()

def test_system_clock():
    clock = SystemClock()
    time1 = clock.now()
    
    assert isinstance(time1, datetime)
