import difflib

# ÖZEL KISALTMALAR VE TÜRKÇE DESTEĞİ (Fast-Track)
# Sadece algoritmanın çok zorlanacağı veya bizim özel olarak dönüştürmek 
# istediğimiz istisnalar burada
CUSTOM_MAPPINGS = {
    "mlk": "milk",
    "grlc": "garlic",
    "ches": "cheese",
    "chckn": "chicken",
    "eg": "egg",
    "domates": "tomato",
    "soğan": "onion",
    "sogan": "onion",
    "patates": "potato"
}

# DOĞRU İNGİLİZCE KELİMELER HAVUZU (Master English List)
# Hatalı yazımların yerine SADECE doğrularını burada
# Kullanıcının hatalı girdisi bu havuza çarpıp doğru kelimeyi bulacak
VALID_ENGLISH_INGREDIENTS = [
    # Sebzeler & Meyveler
    "tomato", "potato", "onion", "garlic", "carrot", "broccoli", "spinach", 
    "mushroom", "cucumber", "pepper", "bell pepper", "lettuce", "cabbage",
    "lemon", "apple", "banana", "strawberry", "orange",
    
    # Süt Ürünleri & Yumurta
    "milk", "cheese", "butter", "yogurt", "cream", "egg",
    
    # Et Ürünleri
    "chicken", "beef", "pork", "fish", "salmon", "shrimp", "sausage", "bacon",
    
    # Temel Gıdalar & Baharatlar
    "flour", "sugar", "salt", "olive oil", "vegetable oil", "rice", "pasta", 
    "water", "bread", "honey", "vinegar", "soy sauce", "mayonnaise", "mustard"
]

def correct_ingredient_name(user_input: str) -> tuple[str, bool]:
   
    normalized_input = user_input.strip().lower()

    # Hızlı eşleşme (Özel kısaltmalar veya Türkçe karşılıklar)
    if normalized_input in CUSTOM_MAPPINGS:
        corrected_word = CUSTOM_MAPPINGS[normalized_input]
        return corrected_word.capitalize(), True

    # Kelime zaten birebir doğru yazılmış mı?
    if normalized_input in VALID_ENGLISH_INGREDIENTS:
        return normalized_input.capitalize(), False

    # İNGİLİZCE YAZIM YANLIŞI ARAMASI (Fuzzy Matching)
    # Kullanıcı "tomtos", "tometo" veya "carrt" yazsa bile bu aşamada tespit edilecek
    # Kısa kelimelerde (<=4 harf) tolerans yüksek (0.5), uzunlarda normal (0.65)
    cutoff_val = 0.5 if len(normalized_input) <= 4 else 0.65

    possible_matches = difflib.get_close_matches(
        normalized_input,
        VALID_ENGLISH_INGREDIENTS,  # Hatalı kelime Master List ile kıyaslanıyor
        n=1,
        cutoff=cutoff_val
    )

    if possible_matches:
        best_match = possible_matches[0]
        return best_match.capitalize(), True

    # Hiçbir eşleşme bulunamazsa mecburen orijinalini döndür
    return user_input.strip().capitalize(), False