from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None


class AnalyticsItem(BaseModel):
    species: str = Field(examples=["Iris-setosa"])
    count: int = Field(description="Number of records for this species")
    avg_sepal_length: float = Field(description="Mean SepalLengthCm")
    avg_sepal_width: float = Field(description="Mean SepalWidthCm")
    avg_petal_length: float = Field(description="Mean PetalLengthCm")
    avg_petal_width: float = Field(description="Mean PetalWidthCm")