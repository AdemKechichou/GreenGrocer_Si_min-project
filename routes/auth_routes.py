from fastapi import APIRouter ,HTTPException
from models.user_model import login , ClientCreation , ClientRegistration
from database import get_user_by_email , create_client
from auth import verify_password , create_token



router = APIRouter()


@router.post('/login')

def login(info : login):
    user = get_user_by_email(info.email)
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    valid = verify_password(info.password , user['password'])
    if not valid:
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = create_token(user['user_id'],user['type'])
    return {'token':token}

@router.post('/register')

def register(info : ClientRegistration):
    user = get_user_by_email(info.email)
    if user is not None:
        raise HTTPException(status_code=409, detail="the email you're using is already linked to an account")
    private_info = ClientCreation(**info.model_dump())
    return create_client(private_info)
    
    