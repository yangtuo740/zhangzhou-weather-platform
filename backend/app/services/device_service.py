from sqlmodel import Session, select
from ..models import Device, AuditLog
from ..schemas import DeviceCreate, DeviceUpdate, OcrResult
from datetime import datetime, timedelta

def get_devices(session: Session, skip: int = 0, limit: int = 20,
                keyword: str = "", status: str = "", export_all: bool = False):
    query = select(Device).where(Device.deleted == False)
    if keyword:
        kw = f"%{keyword}%"
        query = query.where(
            (Device.device_name.like(kw)) | (Device.equip_code.like(kw)) |
            (Device.send_unit.like(kw)) | (Device.cert_no.like(kw))
        )
    if status:
        query = query.where(Device.status == status)
    query = query.order_by(Device.updated_at.desc())
    total = len(session.exec(query).all())
    if not export_all:
        query = query.offset(skip).limit(limit)
    items = session.exec(query).all()
    return items, total

def get_device_by_id(session: Session, device_id: int) -> Device | None:
    device = session.get(Device, device_id)
    if device and device.deleted:
        return None
    return device

def create_device(session: Session, data: DeviceCreate, user_id: int, username: str) -> Device:
    device = Device(**data.model_dump(), created_by=user_id)
    _update_status(device)
    session.add(device)
    session.commit()
    session.refresh(device)
    _add_log(session, user_id, username, "create", f"新增设备 {device.device_name}")
    return device

def update_device(session: Session, device_id: int, data: DeviceUpdate, user_id: int, username: str) -> Device | None:
    device = session.get(Device, device_id)
    if not device or device.deleted:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(device, key, value)
    device.updated_at = datetime.utcnow()
    _update_status(device)
    session.add(device)
    session.commit()
    session.refresh(device)
    _add_log(session, user_id, username, "update", f"更新设备 {device.device_name}")
    return device

def delete_device(session: Session, device_id: int, user_id: int, username: str) -> bool:
    device = session.get(Device, device_id)
    if not device:
        return False
    device.deleted = True
    device.updated_at = datetime.utcnow()
    session.add(device)
    session.commit()
    _add_log(session, user_id, username, "delete", f"删除设备 {device.device_name}")
    return True

def save_ocr_result(session: Session, ocr: OcrResult, image_path: str, user_id: int, username: str) -> Device:
    device = Device(**ocr.model_dump(), cert_image_path=image_path, created_by=user_id)
    _update_status(device)
    session.add(device)
    session.commit()
    session.refresh(device)
    _add_log(session, user_id, username, "ocr_create", f"OCR录入设备 {device.device_name}")
    return device

def get_expiring_devices(session: Session) -> list[Device]:
    """获取30天内到期的设备"""
    now = datetime.utcnow()
    deadline = now + timedelta(days=30)
    devices = session.exec(select(Device).where(Device.deleted == False)).all()
    result = []
    for d in devices:
        if d.calib_date:
            try:
                cd = datetime.strptime(d.calib_date, "%Y-%m-%d")
                if cd <= deadline:
                    result.append(d)
            except ValueError:
                pass
    return result

def _update_status(device: Device):
    if not device.calib_date:
        device.status = "active"
        return
    try:
        cd = datetime.strptime(device.calib_date, "%Y-%m-%d")
        now = datetime.utcnow()
        if cd < now:
            device.status = "expired"
        elif cd <= now + timedelta(days=30):
            device.status = "expiring"
        else:
            device.status = "active"
    except ValueError:
        device.status = "active"

def _add_log(session: Session, user_id: int, username: str, action: str, target: str, detail: str = ""):
    log = AuditLog(user_id=user_id, username=username, action=action, target=target, detail=detail)
    session.add(log)
    session.commit()

def get_audit_logs(session: Session, skip: int = 0, limit: int = 20,
                   keyword: str = "") -> tuple[list[AuditLog], int]:
    query = select(AuditLog)
    if keyword:
        query = query.where(
            (AuditLog.username.like(f"%{keyword}%")) | (AuditLog.action.like(f"%{keyword}%"))
        )
    query = query.order_by(AuditLog.created_at.desc())
    total = len(session.exec(query).all())
    items = session.exec(query.offset(skip).limit(limit)).all()
    return items, total
