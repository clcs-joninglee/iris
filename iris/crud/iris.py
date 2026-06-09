from sqlalchemy import func, select
from sqlalchemy.orm import Session

from iris.models.iris import Iris
from iris.schemas.iris import IrisCreate, IrisUpdate


def get_all(db: Session, limit: int = 100, offset: int = 0):
    total = db.scalar(select(func.count(Iris.Id))) or 0
    items = list(
        db.execute(select(Iris).order_by(Iris.Id).limit(limit).offset(offset))
        .scalars()
        .all()
    )
    return items, total


def get_by_id(db: Session, iris_id: int):
    return db.get(Iris, iris_id)


def search(db: Session, species=None, min_petal_length=None, limit: int = 10, offset: int = 0):
    q = select(Iris).order_by(Iris.Id)
    if species is not None:
        q = q.where(Iris.Species == species)
    if min_petal_length is not None:
        q = q.where(Iris.PetalLengthCm >= min_petal_length)
    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    items = list(db.execute(q.limit(limit).offset(offset)).scalars().all())
    return items, total


def analytics_stats(db: Session):
    return db.execute(
        select(
            Iris.Species,
            func.count(Iris.Id).label("count"),
            func.avg(Iris.SepalLengthCm).label("avg_sepal_length"),
            func.avg(Iris.SepalWidthCm).label("avg_sepal_width"),
            func.avg(Iris.PetalLengthCm).label("avg_petal_length"),
            func.avg(Iris.PetalWidthCm).label("avg_petal_width"),
        ).group_by(Iris.Species).order_by(Iris.Species)
    ).all()


def create(db: Session, data: IrisCreate):
    obj = Iris(**data.model_dump(by_alias=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, iris_id: int, data: IrisUpdate):
    obj = db.get(Iris, iris_id)
    if obj is None:
        return None
    for key, value in data.model_dump(by_alias=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, iris_id: int):
    obj = db.get(Iris, iris_id)
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True