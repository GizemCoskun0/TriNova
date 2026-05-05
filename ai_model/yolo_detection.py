try:
    from ultralytics import YOLO  # type: ignore[import]
except ImportError as e:
    raise ImportError("ultralytics package not found. Install with 'pip install ultralytics'.") from e

import os
import cv2  
import numpy as np # DISARIDAN GELEN FOTOGRAFI OKUMAK ICIN EKLENDI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'weights.pt')

# --- YENI EKLENEN KISIM: API ICIN DINAMIK FOTOGRAF OKUMA FONKSIYONU ---
# Modeli her seferinde bastan yukleyip sistemi yavaslatmamak icin globalde tutuyoruz
_model = None

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model bulunamadi: {model_path}")
        _model = YOLO(model_path)
    return _model

def analyze_image_from_bytes(image_bytes):
    """
    FastAPI'den gelen fotograf bytelarini okur, 
    YOLO modeline sokar ve bulunan malzemelerin listesini dondurur.
    """
    # Gelen bytelari OpenCV formatina ceviriyoruz
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    model = get_model()
    results = model.predict(source=img, conf=0.2, imgsz=800)
    
    found_ingredients = set()
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            found_ingredients.add(class_name)
            
    return list(found_ingredients)
# -----------------------------------------------------------------------


# SENIN ORİJİNAL TEST FONKSİYONUN (HİÇBİR ŞEY DEĞİŞTİRİLMEDİ)
def test_single_image_visual():
    if not os.path.exists(model_path):
        print(f"❌ Error: '{model_path}' not found.")
        return
        
    image_path = os.path.join(BASE_DIR, 'testt.jpeg') 
    if not os.path.exists(image_path):
        print(f"❌ Error: '{image_path}' not found. Please add the photo.")
        return

    print("✅ Loading model...")
    model = YOLO(model_path)

    print(f"🔍 Analyzing '{image_path}'...")
    
    results = model.predict(source=image_path, conf=0.2, imgsz=800)

    found_ingredients = set() 

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            found_ingredients.add(class_name)
            
        plotted_image = result.plot() 
        cv2.imshow("Smart Kitchen - AI Eye", plotted_image)

    ingredient_list = list(found_ingredients)
    
    print("\n" + "=" * 40)
    if ingredient_list:
        print(f"🍽️  Found Ingredients: {ingredient_list}")
    else:
        print("🤷 No ingredients found.")
    print("=" * 40 + "\n")

    print("📸 IMAGE ON SCREEN! Press ANY KEY on your keyboard while the photo window is selected to exit...")
    
    cv2.waitKey(0) 
    cv2.destroyAllWindows() 

if __name__ == "__main__":
    test_single_image_visual()