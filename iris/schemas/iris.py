from pydantic import BaseModel, ConfigDict, Field


class IrisBase(BaseModel):
    sepal_length: float = Field(alias="SepalLengthCm", gt=0, examples=[5.1])
    sepal_width: float = Field(alias="SepalWidthCm", gt=0, examples=[3.5])
    petal_length: float = Field(alias="PetalLengthCm", gt=0, examples=[1.4])
    petal_width: float = Field(alias="PetalWidthCm", gt=0, examples=[0.2])
    species: str = Field(alias="Species", min_length=1, examples=["Iris-setosa"])

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class IrisCreate(IrisBase): #POST 新增時客戶端傳進來的格式
    pass


class IrisUpdate(IrisBase): #PUT 更新時客戶端傳進來的格式，因為是更新，所以欄位都不是必填的
    pass


class IrisResponse(IrisBase): #回傳給客戶端的格式（多了 Id）
    id: int = Field(alias="Id", examples=[1])


class IrisListResponse(BaseModel): #列表回傳格式（含分頁資訊）
    data: list[IrisResponse]
    total: int
    limit: int
    offset: int