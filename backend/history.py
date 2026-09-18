"""
history.py – CRUD operations for decision history.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from models import DecisionHistory
from schemas import HistoryItem, HistoryDetail, DecisionResult


def create_history_entry(
    db: Session,
    category: str,
    user_query: Optional[str],
    input_data: dict,
    result: DecisionResult,
) -> DecisionHistory:
    """Create and persist a new decision history entry."""
    entry = DecisionHistory(
        category=category,
        user_query=user_query,
        recommendation=result.recommendation[:490] if result.recommendation else None,
        confidence=result.confidence,
        confidence_band=result.confidence_band,
    )
    entry.set_input_data(input_data)
    entry.set_factors([f.model_dump() for f in result.factors])
    entry.set_result(result.model_dump())

    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_all_history(db: Session, limit: int = 50) -> List[HistoryItem]:
    """Get all history items, newest first."""
    rows = (
        db.query(DecisionHistory)
        .order_by(DecisionHistory.timestamp.desc())
        .limit(limit)
        .all()
    )
    items = []
    for row in rows:
        items.append(HistoryItem(
            id=row.id,
            timestamp=row.timestamp or datetime.utcnow(),
            category=row.category,
            user_query=row.user_query,
            recommendation=row.recommendation,
            confidence=row.confidence,
            confidence_band=row.confidence_band,
        ))
    return items


def get_history_by_id(db: Session, history_id: int) -> Optional[HistoryDetail]:
    """Get full detail for a single history entry."""
    row = db.query(DecisionHistory).filter(DecisionHistory.id == history_id).first()
    if not row:
        return None
    return HistoryDetail(
        id=row.id,
        timestamp=row.timestamp or datetime.utcnow(),
        category=row.category,
        user_query=row.user_query,
        input_data=row.get_input_data(),
        recommendation=row.recommendation,
        confidence=row.confidence,
        confidence_band=row.confidence_band,
        factors=row.get_factors(),
        result=row.get_result(),
    )


def delete_history_by_id(db: Session, history_id: int) -> bool:
    """Delete a single history entry. Returns True if deleted."""
    row = db.query(DecisionHistory).filter(DecisionHistory.id == history_id).first()
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


def delete_all_history(db: Session) -> int:
    """Delete all history. Returns count deleted."""
    count = db.query(DecisionHistory).count()
    db.query(DecisionHistory).delete()
    db.commit()
    return count
