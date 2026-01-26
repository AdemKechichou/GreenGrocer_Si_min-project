from fastapi import APIRouter ,Depends , HTTPException 
from models.user_model import Item ,ItemCreate , ItemEdit , FarmerProfile
from auth import require_farmer
from database import get_farmer_pid , add_to_stock , item_edit , validate_item_ownership , item_delete , get_item_by_farmer
from database import edit_farmer

router = APIRouter()


@router.post('/add_item')

def add_item(item : ItemCreate , current_user = Depends(require_farmer)):
    farmer_id = get_farmer_pid(current_user['user_id'])
    item.profile_id = farmer_id
    add_to_stock(item)
    return {"message": "Items added successfully", "status": "ok"}

@router.patch('/edit_item')

def edit_item(item : ItemEdit , current_user = Depends(require_farmer)):
    farmer_id = get_farmer_pid(current_user['user_id'])
    if not validate_item_ownership(item.id ,farmer_id):
        raise HTTPException(status_code=409, detail="This profile doesn't have the authority to modify this item.")
    response = item_edit(item)
    if response is None:
        return {"message": "failed to edit the item", "status": "error"}
    else:
        return response

@router.delete('/delete_item')

def delete_item(item_id: int ,  current_user = Depends(require_farmer)):
    farmer_id = get_farmer_pid(current_user['user_id'])
    if not validate_item_ownership(item_id ,farmer_id):
        raise HTTPException(status_code=409, detail="This profile doesn't have the authority to modify this item.")
    response = item_delete(item_id)
    if response is None:
        return {"message": "failed to edit the item", "status": "error"}
    else:
        return response
    
@router.get('/items')

def items(current_user = Depends(require_farmer))-> list[Item]:
    items_list = get_item_by_farmer(get_farmer_pid(current_user['user_id']))
    return items_list

@router.patch('/edit_profile')

def edit_profile(profile : FarmerProfile,current_user = Depends(require_farmer)):
    profile.user_id = current_user['user_id']
    response = edit_farmer(profile)
    return response
