from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

import models
from database import get_db
from schemas import ProfileCreate


class PasswordChangeRequest(BaseModel):
    username: str
    current_password: str
    new_password: str


router = APIRouter(prefix="/api", tags=["Profile"])


@router.post("/profile")
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
        db_allergy = (
            db.query(models.Allergy).filter(models.Allergy.name == allergy_name).first()
        )

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
        "data": {"saved_diet": profile.diet, "saved_allergies": profile.allergies},
    }


@router.get("/profile/{username}")
def get_profile(username: str, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == username).first()

    if not db_user:
        return {"status": "error", "message": "User not found"}

    email = db_user.email
    diet = db_user.diets[0].name if db_user.diets else "None"
    allergies = [allergy.name for allergy in db_user.allergies]

    return {"status": "success", "email": email, "diet": diet, "allergies": allergies}


@router.put("/profile/change-password")
def change_password(request: PasswordChangeRequest, db: Session = Depends(get_db)):
    db_user = (
        db.query(models.User).filter(models.User.username == request.username).first()
    )

    if not db_user:
        return {"status": "error", "message": "User not found"}
    if getattr(db_user, "password", None) != request.current_password:
        return {"status": "error", "message": "Incorrect current password."}

    db_user.password = request.new_password
    db.commit()

    return {"status": "success", "message": "Password changed successfully"}
