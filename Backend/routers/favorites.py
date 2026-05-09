from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
from database import get_db
from schemas import FavoriteAddRequest

router = APIRouter(prefix="/api/favorites", tags=["Favorites"])

@router.post("/")
def toggle_favorite(req: FavoriteAddRequest, db: Session = Depends(get_db)):

    existing = db.query(models.FavoriteRecipe).filter(
        models.FavoriteRecipe.user_email == req.email,
        models.FavoriteRecipe.recipe_id == req.recipe_id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"status": "success", "message": "Recipe removed from favorites.", "is_favorite": False}
    
    else:
        new_fav = models.FavoriteRecipe(
            user_email=req.email,
            recipe_id=req.recipe_id,
            recipe_title=req.recipe_title,
            recipe_image=req.recipe_image,
            source_url=req.source_url,
            ingredients=req.ingredients_json
        )
        db.add(new_fav)
        db.commit()
        return {"status": "success", "message": "Recipe added to favorites.", "is_favorite": True}

@router.get("/{email}")
def get_favorites(email: str, db: Session = Depends(get_db)):
    favorites = db.query(models.FavoriteRecipe).filter(
        models.FavoriteRecipe.user_email == email
    ).order_by(models.FavoriteRecipe.id.desc()).all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": f.id, "recipe_id": f.recipe_id, "recipe_title": f.recipe_title,
                "recipe_image": f.recipe_image, "source_url": f.source_url, "ingredients": f.ingredients
            } for f in favorites
        ]
    }