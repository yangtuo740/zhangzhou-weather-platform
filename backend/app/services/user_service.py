from sqlmodel import Session, select
from ..models import User, AuditLog
from ..schemas import UserCreate, UserUpdate
from ..auth import hash_password
from datetime import datetime

def get_user_by_username(session: Session, username: str) -> User | None:
    return session.exec(select(User).where(User.username == username)).first()

def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)

def get_all_users(session: Session, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
    total = session.exec(select(User)).all()
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users, len(total)

def create_user(session: Session, data: UserCreate, creator: User) -> User:
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        real_name=data.real_name,
        role=data.role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    add_log(session, creator.id, creator.username, "create_user", f"创建用户 {user.username}")
    return user

def update_user(session: Session, user_id: int, data: UserUpdate, current_user: User) -> User | None:
    user = session.get(User, user_id)
    if not user:
        return None
    if data.real_name is not None:
        user.real_name = data.real_name
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.password:
        user.password_hash = hash_password(data.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    add_log(session, current_user.id, current_user.username, "update_user", f"更新用户 {user.username}")
    return user

def add_log(session: Session, user_id: int, username: str, action: str, target: str, detail: str = ""):
    log = AuditLog(user_id=user_id, username=username, action=action, target=target, detail=detail)
    session.add(log)
    session.commit()
