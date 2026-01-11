import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger("wealthwise.audit")

def log_audit_event(
    *,
    request_id: str,
    profile: Dict[str, Any],
    itr: str,
    regime: str,
    old_tax: float,
    new_tax: float,
    income_breakup: Dict[str, Any],
) -> None:
    audit_record = {
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "decision": {
            "itr": itr,
            "regime": regime,
            "old_tax": old_tax,
            "new_tax": new_tax,
        },
        "income_breakup": income_breakup,
        "profile_snapshot": {
            "assessment_year": profile.get("assessment_year"),
            "income_keys": list((profile.get("income") or {}).keys()),
            "flags": profile.get("flags"),
        },
    }

    logger.info("AUDIT_EVENT " + json.dumps(audit_record))