#獲取audit的endpoint，讓admin可以看到audit log的內容

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime

from iris.database import get_db
from app.core.deps import require_role
from app.models.audit import AuditLog
from app.models.user import User

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("")
def list_audit(
    user_id: int | None = Query(None),
    action: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    q = db.query(AuditLog)
    if user_id:
        q = q.filter(AuditLog.actor_user_id == user_id)
    if action:
        q = q.filter(AuditLog.action == action)
    if date_from:
        q = q.filter(AuditLog.occurred_at >= date_from)
    if date_to:
        q = q.filter(AuditLog.occurred_at <= date_to)
    total = q.count()
    items = q.order_by(AuditLog.occurred_at.desc()).offset(offset).limit(limit).all()
    return {"total": total, "items": [
        {
            "id": i.id,
            "occurred_at": i.occurred_at,
            "actor_user_id": i.actor_user_id,
            "action": i.action,
            "resource_type": i.resource_type,
            "resource_id": i.resource_id,
            "ip_address": i.ip_address,
            "result": i.result,
            "extra": i.extra,
        }
        for i in items
    ]}