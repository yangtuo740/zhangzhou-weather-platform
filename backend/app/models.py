from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=50)
    password_hash: str
    real_name: str = Field(default="", max_length=50)
    role: str = Field(default="operator", max_length=20)  # admin, operator, readonly
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cert_no: str = Field(default="", max_length=100)           # 证书编号
    send_unit: str = Field(default="", max_length=200)         # 送检单位
    device_name: str = Field(default="", max_length=200)       # 计量器具名称
    model_spec: str = Field(default="", max_length=100)        # 型号/规格
    equip_code: str = Field(default="", max_length=200)        # 装备编码
    manufacturer: str = Field(default="", max_length=200)      # 制造单位
    approver: str = Field(default="", max_length=50)           # 批准人
    reviewer: str = Field(default="", max_length=50)           # 核验员
    calibrator: str = Field(default="", max_length=50)         # 校准员
    calib_date: Optional[str] = Field(default=None, max_length=20)  # 校准日期
    seal: str = Field(default="", max_length=200)              # 印章
    status: str = Field(default="active", max_length=20)       # active, expiring, expired
    remarks: str = Field(default="", max_length=500)           # 备注
    cert_image_path: Optional[str] = Field(default=None, max_length=500)  # 证书图片路径
    created_by: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted: bool = Field(default=False)                       # 逻辑删除

class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    username: str = Field(default="", max_length=50)
    action: str = Field(max_length=50)                         # create, update, delete, export, login, ocr
    target: str = Field(default="", max_length=200)            # 操作对象
    detail: str = Field(default="", max_length=500)            # 操作详情
    created_at: datetime = Field(default_factory=datetime.utcnow)
