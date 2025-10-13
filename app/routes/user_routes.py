from fastapi import APIRouter, Depends, BackgroundTasks, Query
from app.api import user as user_api
from ..validators.user_validator import UserRead, UserCreate
from sqlmodel import Session
from app.db.database import get_session
from ..validators import user_validator
from app.api.user import get_current_user
from app.utils.email_util import send_email


router = APIRouter(prefix='/users', tags=['users'])

@router.post('/',response_model = UserRead)
def create_user(user_in : user_validator.UserCreate , session : Session = Depends(get_session)):
    return user_api.create_user(session, user_in)

@router.get('/{user_id}', response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)):
    return user_api.get_user(session, user_id)

@router.post('/login', response_model=UserRead)
def login_user(user_in: user_validator.UserLogin, session: Session = Depends(get_session)):
    return user_api.login_user(session, user_in)

@router.post('/logout')
def logout_user(session: Session = Depends(get_session),
                current_user = Depends(get_current_user)):
    return user_api.logout_user(session, current_user)

@router.post('/send-email')
async def send_test(background_tasks: BackgroundTasks, recipients: list[str] = Query(...)):
    await send_email(
        subject="Welcome to FastAPI-Mail 🚀",
        recipients=recipients,
        body="<h1>Hello from FastAPI!</h1><p>This is a test email.</p>",
        background_tasks=background_tasks,
        html=True
    )
    return {"message": "Email sent"}