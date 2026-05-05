from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas import InventoryItem

router = APIRouter(
    prefix="/api",
    tags=["Inventory"]
)

@router.get("/inventory/{username}")
def get_inventory(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return {"status": "error", "message": "User not found. Please create a profile first."}
    
    items = db.query(models.Inventory).filter(models.Inventory.user_id == user.id).all()
    
    return {
        "status": "success", 
        "data": [{"id": i.id, "name": i.name, "amount": i.amount, "unit": i.unit} for i in items]
    }
@router.post("/inventory")
def add_inventory(item: InventoryItem, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == item.username).first()
    if not user:
        return {"status": "error", "message": "User not found."}
        
    existing_item = db.query(models.Inventory).filter(
        models.Inventory.user_id == user.id, 
        models.Inventory.name == item.item_name
    ).first()
    
    if existing_item:
        existing_item.amount += item.amount
        db.commit()
        return {"status": "success", "message": f"'{item.item_name}' amount updated (+{item.amount})!"}

    new_item = models.Inventory(user_id=user.id, name=item.item_name, amount=item.amount, unit=item.unit)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return {"status": "success", "message": f"'{item.item_name}' added to the inventory!"}
@router.delete("/inventory/{item_id}")
def delete_inventory(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Inventory).filter(models.Inventory.id == item_id).first()
    if not item:
        return {"status": "error", "message": "Item not found."}
        
    db.delete(item)
    db.commit()
    return {"status": "success", "message": "Item deleted successfully!"}
