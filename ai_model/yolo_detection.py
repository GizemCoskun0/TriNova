from ultralytics import YOLO
import os
import cv2  

def test_single_image_visual():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    model_path = os.path.join(BASE_DIR, 'weights.pt')
    image_path = os.path.join(BASE_DIR, 'test6.jpg') 
    
    if not os.path.exists(model_path):
        print(f"❌ Error: '{model_path}' not found.")
        return
        
    if not os.path.exists(image_path):
        print(f"❌ Error: '{image_path}' not found. Please add the photo.")
        return

    print("✅ Loading model...")
    model = YOLO(model_path)

    print(f"🔍 Analyzing '{image_path}'...")
    
    
    results = model.predict(source=image_path, conf=0.5, imgsz=800)

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