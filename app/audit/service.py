#定義auditlog的資料怎麼加

from sqlalchemy.orm import Session
from app.models.audit import AuditLog


def write_audit(
    db: Session,
    action: str,
    result: str,
    actor_user_id: int | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    extra: dict | None = None,
) -> None:
    try:
        log = AuditLog(
            action=action,
            result=result,
            actor_user_id=actor_user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            extra=extra,
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()