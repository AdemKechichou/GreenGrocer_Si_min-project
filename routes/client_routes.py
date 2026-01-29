from fastapi import APIRouter ,Depends , HTTPException ,Response ,Query
from models.user_model import Item , ItemOrder
from auth import  require_client
from database import  check_qty , get_farmer_pid_by_item ,place_order ,get_client_pid , subtract_from_stock ,items_in_stock , order_by_client, order_items , validate_order_ownership, order_cancel , edit_order_status


router = APIRouter()

@router.post('/place_order')

def place_an_order( items : list[ItemOrder] ,current_user = Depends(require_client) , day: str = Query(...,description="Options: monday, tuesday, wednesday, thursday, friday, saturday and sunday"), repeat: bool | None = None):
    for item in items:
        check = check_qty(item.item_id, item.qty)
        if check is None:
            raise HTTPException(status_code=404,detail=f"there is no item with the id: {item.item_id} ")
        if not check:
            raise HTTPException(status_code=409,detail=f"request cannot be completed because the current stock level for the item with the id: {item.item_id} is too low to satisfy the request")
        item.farmer_id = get_farmer_pid_by_item(item.item_id)
        
    client_pid = get_client_pid(current_user['user_id'])
    
    place_order(client_pid , items , day, repeat)
    for item in items:
        subtract_from_stock(item.item_id,item.qty)
    
    return {"message": "order placed successfully", "status": "ok"}

@router.get('/items')

def items()-> list[Item]:
    items_list = items_in_stock()
    return items_list

@router.get('/orders')

def orders(current_user = Depends(require_client)):
    client_pid = get_client_pid(current_user['user_id'])
    orders = order_by_client(client_pid)
    orders_item = list()
    for order in orders:
        orders_item.append({"order": order , "items": order_items(order['order_id'])})
    return orders_item

@router.patch('/cancel_order')

def cancel_order(order_id: int ,current_user = Depends(require_client)):
    client_pid = get_client_pid(current_user['user_id'])
    if not validate_order_ownership(order_id,client_pid):
        raise HTTPException(status_code=409, detail="This profile doesn't have the authority to modify this order.")
    response = edit_order_status(order_id , 'Canceled')
    if response is None:
        return {"message": "failed to edit the order", "status": "error"}
    else:
        return response
    
    