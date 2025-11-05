from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class WebhookLog(BaseModel):
    id: int = Field(..., description="日志ID")
    space_name: str = Field(..., description="软件空间名称")
    event_type: str = Field(..., description="事件类型")
    payload: Optional[str] = Field(None, description="请求数据")
    response_status: Optional[int] = Field(None, description="响应状态码")
    response_body: Optional[str] = Field(None, description="响应体")
    attempt_time: datetime = Field(..., description="尝试时间")

    class Config:
        from_attributes = True