import logging

logger = logging.getLogger(__name__)

_KILLSWITCH_ENGAGED = False
_KILLSWITCH_REASON = None

def engage_killswitch(reason: str):
    global _KILLSWITCH_ENGAGED, _KILLSWITCH_REASON
    logger.critical(f"KILLSWITCH ENGAGED: {reason}")
    _KILLSWITCH_ENGAGED = True
    _KILLSWITCH_REASON = reason

def is_killswitch_engaged() -> bool:
    return _KILLSWITCH_ENGAGED

def get_killswitch_reason() -> str:
    return _KILLSWITCH_REASON or ""

def reset_killswitch():
    """For testing purposes."""
    global _KILLSWITCH_ENGAGED, _KILLSWITCH_REASON
    _KILLSWITCH_ENGAGED = False
    _KILLSWITCH_REASON = None
