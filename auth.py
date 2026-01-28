import jwt
import os
from fastapi import Depends , HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from dotenv import load_dotenv
from datetime import datetime , timedelta ,timezone
from passlib.hash import pbkdf2_sha256
from typing import Any

load_dotenv()

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security))-> dict[str] | Any:
    token = credentials.credentials
    result = verify_token(token)
    if not result['valid']:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return result['payload'] 



def require_admin(current_user = Depends(get_current_user)):
    if current_user['user_type'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def require_farmer(current_user = Depends(get_current_user)):
    if current_user['user_type'] != 'farmer':
        raise HTTPException(status_code=403, detail="farmer access required")
    return current_user

def require_client(current_user = Depends(get_current_user)):
    if current_user['user_type'] != 'client':
        raise HTTPException(status_code=403, detail="client access required")
    return current_user
def require_client_or_farmer(current_user = Depends(get_current_user)):
    allowed_user = ['client' ,'farmer' ]
    if  current_user['user_type'] not in allowed_user:
        raise HTTPException(status_code=403, detail="client or farmer access required")
    return current_user

def require_worker(current_user = Depends(get_current_user)):
    if current_user['user_type'] != 'worker':
        raise HTTPException(status_code=403, detail="client access required")
    return current_user


def get_jwt_info()-> dict[str, Any]:
    key = os.getenv('JWT_SECRET_KEY')
    algo= os.getenv('JWT_ALGORITHM')
    exp = int(os.getenv('JWT_EXPIRATION_HOURS'))
    return{'key': key, 'algo':algo,'exp':exp}


def create_token(user_id, user_type):
    jwt_info = get_jwt_info()
    current_time = datetime.now(tz= timezone.utc)
    exp_time = current_time + timedelta(hours=jwt_info['exp'])
    encoded = jwt.encode({'exp': exp_time , 'user_id': user_id , 'user_type': user_type }, jwt_info['key'] ,algorithm=jwt_info['algo'])
    return encoded


def verify_token(token)->dict[str]:
    jwt_info = get_jwt_info()
    valid = False
    try:
        decoded_payload = jwt.decode(
        token,
        jwt_info['key'],
        algorithms=jwt_info['algo'],
        )
        valid = True
        return {'valid':valid ,'payload':decoded_payload}
    except Exception as e:
        return {'valid':valid ,'payload':"Invalid or expired token"}


def hash_password(password):
    hash = pbkdf2_sha256.hash(password)
    return hash

def verify_password(plain, hashed)-> bool:
    return pbkdf2_sha256.verify(plain, hashed)

print(hash_password('ademadem'))