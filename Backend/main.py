from fastapi import FastAPI
import models
from database import engine
from api_process import AsyncRecipeAPI
from pydantic import BaseModel
from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
import models

models.Base.metadata.create_all(bind=engine)


app = FastAPI(title="SmartKitchen API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to the SmartKitchen Backend API.! 🚀"}

@app.get("/api/recipes")
async def get_recipes(ingredients: str):

    ingredients_list = [i.strip() for i in ingredients.split(",")]
    
    recipes = await AsyncRecipeAPI.search_by_ingredients(ingredients_list)
    
    if recipes:
        return {"status": "success", "data": recipes}
    
    return {"status": "error", "message": "Recipe not found or API error."}


class ProfileCreate(BaseModel):
    username: str
    email: str
    diet: str
    allergies: List[str]

@app.post("/api/profile")
def save_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    
    db_user = db.query(models.User).filter(models.User.email == profile.email).first()
    
    if not db_user:
        db_user = models.User(username=profile.username, email=profile.email)
        db.add(db_user)
        message = f"New user '{db_user.username}' created successfully!"
    else:
        message = f"User '{db_user.username}' profile updated successfully!"

    db_user.allergies = []
    db_user.diets = []

    for allergy_name in profile.allergies:
        db_allergy = db.query(models.Allergy).filter(models.Allergy.name == allergy_name).first()
        
        if not db_allergy:
            db_allergy = models.Allergy(name=allergy_name)
            db.add(db_allergy)
            
        db_user.allergies.append(db_allergy)

    if profile.diet and profile.diet != "None":
        db_diet = db.query(models.Diet).filter(models.Diet.name == profile.diet).first()
        
        if not db_diet:
            db_diet = models.Diet(name=profile.diet)
            db.add(db_diet)
            
        db_user.diets.append(db_diet)

    db.commit()

    return {
        "status": "success", 
        "message": message,
        "data": {
            "saved_diet": profile.diet, 
            "saved_allergies": profile.allergies
        }
    }


class InventoryItem(BaseModel):
    username: str
    item_name: str
    amount: float = 1.0
    unit: str = "unit"

@app.get("/api/inventory/{username}")
def get_inventory(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return {"status": "error", "message": "User not found. Please create a profile first."}
    
    items = db.query(models.Inventory).filter(models.Inventory.user_id == user.id).all()
    
    return {
        "status": "success", 
        "data": [{"id": i.id, "name": i.name, "amount": i.amount, "unit": i.unit} for i in items]
    }

@app.post("/api/inventory")
def add_inventory(item: InventoryItem, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == item.username).first()
    if not user:
        return {"status": "error", "message": "User not found."}
        
    existing_item = db.query(models.Inventory).filter(
        models.Inventory.user_id == user.id, 
        models.Inventory.name == item.item_name
    ).first()
    
    if existing_item:
        return {"status": "error", "message": f"'{item.item_name}' already exists in the inventory!"}

    new_item = models.Inventory(user_id=user.id, name=item.item_name, amount=item.amount, unit=item.unit)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return {"status": "success", "message": f"'{item.item_name}' added to the inventory!"}

@app.delete("/api/inventory/{item_id}")
def delete_inventory(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Inventory).filter(models.Inventory.id == item_id).first()
    if not item:
        return {"status": "error", "message": "Item not found."}
        
    db.delete(item)
    db.commit()
    return {"status": "success", "message": "Item deleted successfully!"}