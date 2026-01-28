from fastapi import APIRouter ,HTTPException ,Depends
from models.user_model import login , ClientCreation , ClientRegistration ,Password , UserEdit
from database import get_user_by_email , create_client ,account_info, get_user_by_id ,edit_password ,edit_user
from auth import verify_password , create_token ,require_farmer ,require_client ,require_client_or_farmer 



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

@router.get('/account')

def get_account_information(current_user = Depends(require_client_or_farmer) ):
    farmer_id = current_user['user_id']
    info = account_info(farmer_id, current_user['user_type'])
    return info
    
@router.patch('/update_password')

def update_password(password :Password ,current_user = Depends(require_client_or_farmer)):
    user = get_user_by_id(current_user['user_id'])
    if not verify_password(password.current, user['password']):
         raise HTTPException(status_code=401, detail="wrong password.")
    return edit_password(password.new, current_user['user_id'])
    
@router.put('/update_profile')

def edit_profile(user :UserEdit,current_user = Depends(require_client_or_farmer)):
    return edit_user(user , current_user['user_id'], current_user['user_type'])
    

