import os
import json
import requests

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_image(search_term, directory, image_id):
    url = f"https://source.unsplash.com/featured/?{search_term.replace(' ', '+')},slovenia,landmark"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        file_path = os.path.join(directory, f"{image_id}.jpg")
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Pobrano: {file_path}")
    else:
        print(f"Błąd pobierania dla {search_term}")

# Wczytanie pliku JSON
with open("trip.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Przetwarzanie sekcji i podsekcji
for section in data["sekcje"]:
    section_id = section["id"]
    title = section["tytul"]
    directory = f"images/{section_id}"
    create_directory(directory)
    search_term = f"{title} landmark"
    download_image(search_term, directory, section_id)

    for subsection in section.get("podsekcje", []):
        subsection_id = subsection["id"]
        sub_title = subsection["tytul"]
        sub_directory = f"images/{section_id}/{subsection_id}"
        create_directory(sub_directory)
        sub_search_term = f"{sub_title} landmark"
        download_image(sub_search_term, sub_directory, subsection_id)

print("Pobieranie zakończone!")