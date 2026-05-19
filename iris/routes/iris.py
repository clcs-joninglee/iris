from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from iris import crud, schemas
from iris.database import get_db
from iris.schemas.common import AnalyticsItem, ErrorResponse
from app.core.deps import get_current_user, require_role
from app.models.user import User

router = APIRouter(
    prefix="/iris",
    tags=["Iris"],
    responses={404: {"model": ErrorResponse, "description": "Record not found"}},
)


@router.get(
    "/search",
    response_model=list[schemas.IrisResponse],
    summary="搜尋 Iris 資料",
    description="根據品種或最小花瓣長度篩選資料",
)
def search_iris(
    species: str | None = Query(None, description="品種名稱，例如 Iris-setosa"),
    min_petal_length: float | None = Query(None, ge=0, description="花瓣長度下限（cm）"),
    db: Session = Depends(get_db),
):
    return crud.iris.search(db, species=species, min_petal_length=min_petal_length)


@router.get(
    "/analytics/stats",
    response_model=list[AnalyticsItem],
    summary="各品種統計數據",
)
def analytics_stats(db: Session = Depends(get_db)):
    rows = crud.iris.analytics_stats(db)
    return [
        AnalyticsItem(
            species=row.Species,
            count=row.count,
            avg_sepal_length=round(row.avg_sepal_length, 4),
            avg_sepal_width=round(row.avg_sepal_width, 4),
            avg_petal_length=round(row.avg_petal_length, 4),
            avg_petal_width=round(row.avg_petal_width, 4),
        )
        for row in rows
    ]


@router.get(
    "/",
    response_model=schemas.IrisListResponse,
    summary="列出所有 Iris 資料",
)
def list_iris(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    items, total = crud.iris.get_all(db, limit=limit, offset=offset)
    return schemas.IrisListResponse(data=items, total=total, limit=limit, offset=offset)


@router.get(
    "/{iris_id}",
    response_model=schemas.IrisResponse,
    summary="取得單筆 Iris 資料",
)
def get_iris(iris_id: int, db: Session = Depends(get_db)):
    obj = crud.iris.get_by_id(db, iris_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"Iris id={iris_id} not found")
    return obj


@router.post(
    "/",
    response_model=schemas.IrisResponse,
    status_code=201,
    summary="新增 Iris 資料",
)
def create_iris(data: schemas.IrisCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "scientist"))):
    return crud.iris.create(db, data)


@router.put(
    "/{iris_id}",
    response_model=schemas.IrisResponse,
    summary="更新 Iris 資料",
)
def update_iris(iris_id: int, data: schemas.IrisUpdate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "scientist"))):
    obj = crud.iris.update(db, iris_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"Iris id={iris_id} not found")
    return obj


@router.delete(
    "/{iris_id}",
    status_code=204,
    summary="刪除 Iris 資料",
)
def delete_iris(iris_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "scientist"))):
    if not crud.iris.delete(db, iris_id):
        raise HTTPException(status_code=404, detail=f"Iris id={iris_id} not found")