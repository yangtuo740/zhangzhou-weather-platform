from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# ---- Auth ----
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    real_name: str = ""

class UserOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    username: str
    real_name: str
    role: str
    is_active: bool
    created_at: datetime

class UserCreate(BaseModel):
    username: str
    password: str
    real_name: str = ""
    role: str = "operator"

class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

# ---- Device ----
class DeviceBase(BaseModel):
    cert_no: str = ""
    send_unit: str = ""
    device_name: str = ""
    model_spec: str = ""
    equip_code: str = ""
    manufacturer: str = ""
    approver: str = ""
    reviewer: str = ""
    calibrator: str = ""
    calib_date: Optional[str] = None
    seal: str = ""
    remarks: str = ""

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    cert_no: Optional[str] = None
    send_unit: Optional[str] = None
    device_name: Optional[str] = None
    model_spec: Optional[str] = None
    equip_code: Optional[str] = None
    manufacturer: Optional[str] = None
    approver: Optional[str] = None
    reviewer: Optional[str] = None
    calibrator: Optional[str] = None
    calib_date: Optional[str] = None
    seal: Optional[str] = None
    status: Optional[str] = None
    remarks: Optional[str] = None

class DeviceOut(DeviceBase):
    model_config = {"from_attributes": True}
    id: int
    status: str
    remarks: str
    cert_image_path: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    deleted: bool

class DeviceListResponse(BaseModel):
    items: list[DeviceOut]
    total: int
    page: int
    page_size: int

# ---- OCR ----
class OcrResult(BaseModel):
    cert_no: str = ""
    send_unit: str = ""
    device_name: str = ""
    model_spec: str = ""
    equip_code: str = ""
    manufacturer: str = ""
    approver: str = ""
    reviewer: str = ""
    calibrator: str = ""
    calib_date: str = ""
    seal: str = ""

# ---- Export ----
class ExportRequest(BaseModel):
    device_ids: Optional[list[int]] = None
    fields: Optional[list[str]] = None
    file_format: str = "xlsx"

# ---- Audit ----
class AuditLogOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    user_id: Optional[int]
    username: str
    action: str
    target: str
    detail: str
    created_at: datetime

class AuditLogListResponse(BaseModel):
    items: list[AuditLogOut]
    total: int
    page: int
    page_size: int

# ---- Dashboard ----
class DashboardStats(BaseModel):
    total_devices: int
    active_devices: int
    expiring_devices: int
    expired_devices: int
    recent_logs: list[AuditLogOut]
