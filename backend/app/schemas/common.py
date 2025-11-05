from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """
    通用API响应模型
    """
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    分页响应模型
    """
    items: List[T] = Field(..., description="数据列表")
    total: int = Field(..., description="总数据量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")


class ErrorResponse(BaseModel):
    """
    错误响应模型
    """
    success: bool = Field(False, description="操作是否成功")
    message: str = Field(..., description="错误消息")
    error: Optional[dict] = Field(None, description="详细错误信息")