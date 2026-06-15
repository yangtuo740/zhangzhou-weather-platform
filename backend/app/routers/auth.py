from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from ..database import get_session
from ..schemas import Token, LoginRequest, RegisterRequest, UserOut, UserCreate, UserUpdate
from ..auth import verify_password, create_access_token, get_current_user, require_admin, hash_password
from ..models import User
from ..services.user_service import get_user_by_username, get_user_by_id, get_all_users, create_user, update_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login(req: LoginRequest, session: Session = Depends(get_session)):
    user = get_user_by_username(session, req.username)
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用")
    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token)

@router.post("/register", response_model=UserOut)
def register(req: RegisterRequest, session: Session = Depends(get_session)):
    existing = get_user_by_username(session, req.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    user = User(username=req.username, password_hash=hash_password(req.password), real_name=req.real_name, role="operator")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# ---- Admin: User Management ----
@router.get("/users", response_model=dict)
def list_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session),
               _: User = Depends(require_admin)):
    users, total = get_all_users(session, skip, limit)
    return {"items": users, "total": total, "page": skip // limit + 1, "page_size": limit}

@router.post("/users", response_model=UserOut)
def add_user(req: UserCreate, session: Session = Depends(get_session),
             current_user: User = Depends(require_admin)):
    existing = get_user_by_username(session, req.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    return create_user(session, req, current_user)

@router.put("/users/{user_id}", response_model=UserOut)
def edit_user(user_id: int, req: UserUpdate, session: Session = Depends(get_session),
              current_user: User = Depends(require_admin)):
    user = update_user(session, user_id, req, current_user)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return user
