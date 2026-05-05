from fastapi import FastAPI, File, UploadFile  # File ve UploadFile EKLENDİ
import models
from database import engine
from api_process import AsyncRecipeAPI
from pydantic import BaseModel
from typing import List, Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from pydantic import BaseModel

from schemas import ProfileCreate, InventoryItem, MealPlanGenerateRequest, MealPlanItemRequest
from routers import recipes,inventory,profile,shopping_list,meal_plan

import models
import json
import sys  # EKLENDİ
import os   # EKLENDİ

# --- YENİ EKLENEN KISIM: AI MODELİNİ İÇERİ AKTARMA ---
# Backend klasöründen bir üst dizine çıkıp ai_model klasörünü görebilmek için
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from ai_model.yolo_detection import analyze_image_from_bytes
# -----------------------------------------------------

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartKitchen API", version="1.0.0")
app.include_router(recipes.router)
app.include_router(inventory.router)
app.include_router(profile.router)
app.include_router(shopping_list.router)
app.include_router(meal_plan.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the SmartKitchen Backend API.! 🚀"}

# --- YENİ EKLENEN KISIM: ARAYÜZDEN GELEN FOTOĞRAFI YAKALAYIP AI'A GÖNDEREN KÖPRÜ ---
@app.post("/api/analyze-image")
def analyze_image(file: UploadFile = File(...)):
    try:
        # await file.read() yerine senkron (normal) okuma yapıyoruz
        image_bytes = file.file.read()
        detected_items = analyze_image_from_bytes(image_bytes)
        return {"status": "success", "detected_items": detected_items}
    except Exception as e:
        return {"status": "error", "message": f"AI Analiz Hatası: {str(e)}"}