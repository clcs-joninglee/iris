from sqlalchemy import Column, Float, Integer, String

from iris.database import Base


class Iris(Base):
    __tablename__ = "Iris"

    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    SepalLengthCm = Column(Float, nullable=False)
    SepalWidthCm = Column(Float, nullable=False)
    PetalLengthCm = Column(Float, nullable=False)
    PetalWidthCm = Column(Float, nullable=False)
    Species = Column(String(50), nullable=False, index=True)