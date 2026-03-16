import csv
import json
import ijson

# Chemin vers le fichier CSV source
input_csv_file = 'adresses-13.csv'

# Chemin vers le fichier JSON de sortie
output_json_file = 'adresses.json'

# Ouvrir le fichier CSV pour lecture
with open(input_csv_file, mode='r', encoding='utf-8') as csv_file:
    # Créer un objet DictReader pour lire le fichier CSV
    csv_reader = csv.DictReader(csv_file, delimiter=';')
    
    # Créer une liste pour stocker les données filtrées
    filtered_data = []
    
    # Parcourir chaque ligne du fichier CSV
    for row in csv_reader:
        # Filtrer les données et les ajouter à la liste
        filtered_row = {
            'nom_voie': row['nom_voie'],
            'nom_commune': row['nom_commune'],
            'code_postal': row['code_postal']
        }
        filtered_data.append(filtered_row)

# Ouvrir le fichier JSON pour écriture
with open(output_json_file, mode='w', encoding='utf-8') as json_file:
    # Écrire les données filtrées dans le fichier JSON
    json.dump(filtered_data, json_file, indent=4)

print("Le fichier JSON a été créé avec succès.")

def remove_duplicates(input_filename, output_filename):
    unique_items = set()
    with open(input_filename, 'rb') as input_file:
        items = ijson.items(input_file, 'item')
        cleaned_data = []
        for item in items:
            # Convertit l'objet en chaîne JSON pour l'unicité
            item_str = json.dumps(item, sort_keys=True)
            if item_str not in unique_items:
                unique_items.add(item_str)
                cleaned_data.append(item)
    
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        json.dump(cleaned_data, output_file, ensure_ascii=False, indent=4)

# Appeler la fonction avec le chemin du fichier
remove_duplicates('adresses.json', 'adresses.json')
