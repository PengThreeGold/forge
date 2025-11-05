from typing import List, Optional
from pydantic import BaseModel, Field


class WebhookConfig(BaseModel):
    webhook_url: Optional[str] = Field(None, description="Webhook URL")
    webhook_secret: Optional[str] = Field(None, description="Webhook密钥")
    webhook_events: Optional[List[str]] = Field(None, description="启用的事件类型")


class WebhookConfigUpdate(BaseModel):
    webhook_url: Optional[str] = Field(None, description="Webhook URL")
    webhook_secret: Optional[str] = Field(None, description="Webhook密钥")
    webhook_events: Optional[List[str]] = Field(None, description="启用的事件类型")


class WebhookSecretResponse(BaseModel):
    webhook_secret: str = Field(..., description="新的Webhook密钥")


class WebhookPayload(BaseModel):
    event: str = Field(..., description="事件类型")
    data: dict = Field(..., description="事件数据")
    timestamp: str = Field(..., description="时间戳")
    signature: Optional[str] = Field(None, description="签名")