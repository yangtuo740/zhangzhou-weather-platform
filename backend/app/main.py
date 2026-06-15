from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlmodel import Session
from .database import init_db, get_session
from .config import settings
from .routers import auth, devices, ocr
from .models import User, Device, AuditLog
from .auth import hash_password
import os

app = FastAPI(title="漳州市气象局装备保障管理平台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.include_router(auth.router)
app.include_router(devices.router)
app.include_router(ocr.router)

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

@app.on_event("startup")
def on_startup():
    init_db()
    with next(get_session()) as session:
        from sqlmodel import select
        admin = session.exec(select(User).where(User.username == "admin")).first()
        if not admin:
            admin_user = User(
                username="admin",
                password_hash=hash_password("admin123"),
                real_name="系统管理员",
                role="admin",
            )
            session.add(admin_user)
            session.commit()

@app.get("/api/dashboard")
def dashboard(session: Session = Depends(get_session)):
    from .services.device_service import get_expiring_devices, get_audit_logs
    devices_all = session.exec(Device.__table__.select().where(Device.deleted == False)).all()
    total = len(devices_all)
    active = sum(1 for d in devices_all if d.status == "active")
    expiring = sum(1 for d in devices_all if d.status == "expiring")
    expired = sum(1 for d in devices_all if d.status == "expired")
    logs, _ = get_audit_logs(session, limit=10)
    return {
        "total_devices": total,
        "active_devices": active,
        "expiring_devices": expiring,
        "expired_devices": expired,
        "recent_logs": [
            {"id": l.id, "username": l.username, "action": l.action, "target": l.target,
             "detail": l.detail, "created_at": l.created_at.isoformat()}
            for l in logs
        ]
    }

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if full_path.startswith("api/") or full_path.startswith("uploads/"):
        raise HTTPException(status_code=404)
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "漳州市气象局装备保障管理平台 API", "version": "1.0.0"}
