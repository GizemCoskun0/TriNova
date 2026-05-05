try:
    from ultralytics import YOLO  # type: ignore[import]
except ImportError as e:
    raise ImportError("ultralytics package not found. Install with 'pip install ultralytics'.") from e

import os
import cv2  
import numpy as np 


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'weights.pt')

_model = None

def get_model():
    """Modeli sadece ilk çağrıldığında yükler, sonra hafızada tutar."""
    global _model
    if _model is None:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model bulunamadi: {model_path}")
        _model = YOLO(model_path)
    return _model

def analyze_image_from_bytes(image_bytes):
    """
    FastAPI'den gelen (kullanıcının arayüzden yüklediği) fotograf bytelarını okur, 
    YOLO modeline sokar ve bulunan malzemelerin listesini döndürür.
    """
    
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