from fastapi import APIRouter ,Depends , HTTPException ,Response ,Query
from models.user_model import Item , ItemOrder
from auth import  require_worker
from database import  get_today_orders , edit_order_status , get_orders


router = APIRouter()

@router.get('/today_orders')

def orders(current_user = Depends(require_worker)):
    return get_today_orders()
@router.get('/all_orders')

def all_orders(current_user = Depends(require_worker)):
    return get_orders()

@router.patch('/update_status')

def update_status(order_id: int , status: str = Query(...,description="Options: Processing ,Out for Delivery , Delivered, Canceled , Refunded"),current_user = Depends(require_worker)):
    return edit_order_status(order_id, status)
    pass