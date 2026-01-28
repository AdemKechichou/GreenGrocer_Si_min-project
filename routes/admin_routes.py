from fastapi import APIRouter ,Depends , HTTPException ,Response ,Query
from models.user_model import Item , ItemOrder ,farmerRegistration , workerRegistration
from auth import  require_admin
from database import  create_farmer,get_user_by_email, create_worker,admin_revenue


router = APIRouter()

@router.post('/create_farmer')

def create_farmer_account(info : farmerRegistration,current_user = Depends(require_admin)):
    user = get_user_by_email(info.email)
    if user is not None:
        raise HTTPException(status_code=409, detail="the email you're using is already linked to an account")
    
    return create_farmer(info)
    
@router.post('/create_worker')

def create_worker_account(info : workerRegistration,current_user = Depends(require_admin)):
    user = get_user_by_email(info.email)
    if user is not None:
        raise HTTPException(status_code=409, detail="the email you're using is already linked to an account")
    
    return create_worker(info)

@router.get('/revenue')

def revenue(): #current_user = Depends(require_admin))
    return admin_revenue()

    
