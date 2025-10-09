from sqlmodel import Session, select
from fastapi import HTTPException, Header

from app.models.user_model import User
from app.validators.user_validator import UserCreate, UserLogin
from jose import jwt, JWTError
from app.core.security import hash_password
from app.core.security import SECRET_KEY, ALGORITHM
from app.core.security import create_access_token, create_refresh_token, verify_password
from datetime import timedelta
from app.core.config import ACCESS_TOKEN_EXPIRES_MINUTES,REFRESH_TOKEN_EXPIRES_MINUTES



# def get_current_user(x_auth_token: str = Header(...)):
#     try:
#         # validate token here
#         payload = jwt.decode(x_auth_token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id = payload.get("sub")
#         if not user_id:
#             raise HTTPException(status_code=401, detail="Invalid token")
#         return user_id
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(
    x_auth_token: str = Header(...),  # FastAPI passes the header string here
) -> User:
    try:
        # If token comes as "Bearer <token>", remove "Bearer "
        if x_auth_token.startswith("Bearer "):
            token = x_auth_token.split(" ")[1]
        else:
            token = x_auth_token

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        return user_id

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_user(session: Session, user_in: UserCreate) -> User:
    try:
        # Check if user already exists
        existing_user = session.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        existing_username = session.query(User).filter(User.username == user_in.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already exists")
        new_user = User(
            email=user_in.email,
            username=user_in.username,
            password=hash_password(user_in.password),  # hash this before storing
            is_active=user_in.is_active,
            user_role=user_in.user_role,
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # Generate tokens
        access_token = create_access_token(data={"sub": str(new_user.id)}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES))
        refresh_token = create_refresh_token(data={"sub": str(new_user.id)}, expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRES_MINUTES))

        new_user.access_token = access_token
        new_user.refresh_token = refresh_token
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def get_user(session: Session, user_id: int) -> User:
    try:
        user =  session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

def update_user(session: Session, user_id: int, **kwargs) -> User:
    try:   
        user = session.get(User, user_id)
    
        for key, value in kwargs.items():
            if value is not None:
                setattr(user, key, value)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def login_user(session: Session, user_in: UserLogin) -> User:
    try:
        data = user_in.model_dump()  # convert to dict
        email = data.get("email")
        username = data.get("username")

        # Query the user
        if username:
            statement = select(User).where(User.username == username)
        else:
            statement = select(User).where(User.email == email)

        user = session.exec(statement).first()

        if not user:
            raise HTTPException(status_code=401, detail="Incorrect username/email or password")

        if not verify_password(user_in.password, user.password):
            raise HTTPException(status_code=401, detail="Incorrect username/email or password")

        # Create tokens
        access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES))
        refresh_token = create_refresh_token(data={"sub": str(user.id)}, expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRES_MINUTES))

        # Save tokens in user
        user.access_token = access_token
        user.refresh_token = refresh_token
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))

def logout_user(session: Session, user_id: int):
    try:
        # Fetch the user from DB
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Clear tokens
        user.access_token = None
        user.refresh_token = None

        session.add(user)
        session.commit()
        session.refresh(user)

        return {"detail": "Logged out successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
