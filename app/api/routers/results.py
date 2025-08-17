#app/api/routers/results.py

from __future__ import annotations
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_api_key
from app.db.session import get_session
from app.models.result import Result
from app.schemas.result import ResultRead

router = APIRouter(prefix="/results", tags=["results"], dependencies=[Depends(require_api_key)])


@router.get("/{run_id}", response_model=list[ResultRead])
def get_results(
    run_id: UUID,
    db: Session = Depends(get_session),
    limit: int = Query(1, ge=1, le=50, description="Son kaç sonucu döneceği (varsayılan 1)"),
):
    stmt = select(Result).where(Result.run_id == run_id).order_by(Result.created_at.desc()).limit(limit)
    rows = db.execute(stmt).scalars().all()
    if not rows:
        # run var ama sonucu yoksa boş liste dönebiliriz; fakat run yoksa 404 daha doğru
        # burada sadece sonuç kontrolü yapıyoruz. İstersen JobRun varlığını ayrıca kontrol edebilirsin.
        return []
    return [ResultRead.model_validate(r) for r in rows]
