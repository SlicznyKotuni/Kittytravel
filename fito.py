import requests
import json
import os
from urllib.parse import quote

# Konfiguracja
API_KEY = "9a86938907be9835b9546b0475a4b9ace2815a494f7d8430b63c60ada660144d"
BASE_DIR = "foto"
MAX_IMAGES = 5

def search_images(query, api_key):
    """Wyszukuje obrazy używając SerpAPI"""
    url = f"https://serpapi.com/search.json?q={quote(query)}&tbm=isch&ijn=0&api_key={api_key}"
    print(f"Zapytanie do SerpAPI: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            results = response.json()
            images = results.get("images_results", [])
            if not images:
                print("⚠️ Brak wyników w 'images_results'")
            return [img["original"] for img in images[:MAX_IMAGES] if "original" in img]
        else:
            print(f"❌ Błąd odpowiedzi SerpAPI: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Błąd wyszukiwania: {e}")
    return []

def download_image(url, path):
    """Pobiera i zapisuje pojedyncze zdjęcie"""
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
        else:
            print(f"⚠️ Nieudane pobieranie ({response.status_code}): {url}")
    except Exception as e:
        print(f"❌ Błąd pobierania {url}: {e}")
    return False

def process_section(item, is_subsection=False):
    """Przetwarza sekcję lub podsekcję"""
    item_id = item.get("id", "brak_id")
    query = item.get("tytul", "brak_tytulu")
    print(f"\n🔹 Przetwarzanie {'podsekcji' if is_subsection else 'sekcji'}: {item_id} - {query}")

    # Utwórz folder
    folder = os.path.join(BASE_DIR, item_id)
    os.makedirs(folder, exist_ok=True)

    # Pobierz i zapisz obrazy
    image_urls = search_images(query, API_KEY)
    if not image_urls:
        print("⚠️ Brak obrazów do pobrania.")
        return

    for idx, img_url in enumerate(image_urls):
        filename = os.path.join(folder, f"{idx+1}.jpg")
        if not os.path.exists(filename):
            success = download_image(img_url, filename)
            if success:
                print(f"✅ Zapisano: {filename}")
            else:
                print(f"❌ Nie udało się pobrać: {img_url}")

def main():
    # Wczytaj dane z pliku JSON
    try:
        with open("trip.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            print("✅ Plik JSON został wczytany poprawnie.")
    except Exception as e:
        print(f"❌ Błąd wczytywania pliku JSON: {e}")
        return

    # Przetwórz sekcje i podsekcje
    for section in data.get("sekcje", []):
        process_section(section)
        for subsection in section.get("podsekcje", []):
            process_section(subsection, is_subsection=True)

if __name__ == "__main__":
    main()
