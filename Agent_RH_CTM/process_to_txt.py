from pathlib import Path
import os
import shutil
import pandas as pd
from datetime import datetime
import re

from agno.agent import Agent
from agno.media import File
from agno.models.google import Gemini
from utils.env_config import GEMINI_API_KEY
# Configuration
api_key = GEMINI_API_KEY
input_dir = Path(r"./to_txt")
output_dir = Path(r"./txt")
archive_dir = Path(r"./static/cvs")
excel_file = Path(r"C:/Users/PC/OneDrive - CTM (COMPAGNIE DE TRANSPORT AU MAROC S.A)/logs/logs.xlsx")  # Path to the Excel file

# Créer les dossiers s'ils n'existent pas
output_dir.mkdir(exist_ok=True)
archive_dir.mkdir(exist_ok=True)


def load_excel_data():
    """Charge les données depuis le fichier Excel et retourne un dictionnaire avec les noms de fichiers et dates"""
    try:
        # Charger le fichier Excel
        df = pd.read_excel(excel_file)

        # Filtrer seulement les colonnes qui nous intéressent
        if 'output_file' not in df.columns or 'date' not in df.columns:
            print("Les colonnes 'output_file' et 'date' ne sont pas trouvées dans le fichier Excel")
            return {}

        # Créer un dictionnaire pour stocker les dates par nom de fichier (sans extension)
        file_dates = {}

        for _, row in df.iterrows():
            # Vérifier que les valeurs ne sont pas NaN ou None
            output_file = row['output_file']
            date = row['date']
            
            if pd.notna(output_file) and pd.notna(date):
                # Extraire le nom de fichier sans extension
                full_filename = str(output_file)  # Convertir en string au cas où
                # Extraire le nom de base du fichier (sans timestamp ni extension)
                base_name = Path(full_filename).stem
                # Supprimer le timestamp du début si présent
                clean_name = re.sub(r'^[\d]{4}-[\d]{2}-[\d]{2}T[\d]{2}:[\d]{2}:[\d]{2}\+[\d]{2}:[\d]{2}-', '',
                                    base_name)

                # Stocker la date pour ce fichier
                file_dates[clean_name] = date

        print(f"Données Excel chargées : {len(file_dates)} entrées trouvées")
        return file_dates
    except Exception as e:
        print(f"Erreur lors du chargement des données Excel : {str(e)}")
        return {}

def unique_path(directory, filename):
    """Renvoie un chemin unique dans le dossier en évitant les écrasements."""
    path = directory / filename
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    i = 1
    while True:
        new_name = f"{stem}_{i}{suffix}"
        new_path = directory / new_name
        if not new_path.exists():
            return new_path
        i += 1


def find_date_for_file(file_name, file_dates):
    """Trouve la date correspondante pour un fichier donné avec une correspondance plus précise."""
    # Supprimer l'extension pour la comparaison
    base_name = Path(file_name).stem
    
    # Nettoyer le nom de fichier (supprimer le timestamp du début)
    clean_base_name = re.sub(r'^[\d]{4}-[\d]{2}-[\d]{2}T?[\d]{2}:?[\d]{2}:?[\d]{2}[+-]?[\d]{2}:?[\d]{2}[-_]?', '', base_name)
    
    print(f"Recherche de correspondance pour: '{file_name}' -> base: '{base_name}' -> clean: '{clean_base_name}'")
    
    # Essayer de trouver une correspondance exacte d'abord
    for name, date in file_dates.items():
        if clean_base_name == name:
            print(f"  ✓ Correspondance exacte trouvée: '{name}' -> {date}")
            return date
    
    # Essayer de trouver une correspondance partielle (le nom du fichier Excel contient le nom nettoyé)
    best_match = None
    best_score = 0
    
    for name, date in file_dates.items():
        # Calculer un score de similarité
        if clean_base_name in name:
            score = len(clean_base_name) / len(name)  # Plus le nom est proche, plus le score est élevé
            if score > best_score:
                best_score = score
                best_match = (name, date)
                print(f"  ~ Correspondance partielle: '{name}' (score: {score:.2f})")
        elif name in clean_base_name:
            score = len(name) / len(clean_base_name)
            if score > best_score:
                best_score = score
                best_match = (name, date)
                print(f"  ~ Correspondance partielle inverse: '{name}' (score: {score:.2f})")
    
    if best_match and best_score > 0.3:  # Seuil minimum de similarité
        print(f"  ✓ Meilleure correspondance: '{best_match[0]}' -> {best_match[1]}")
        return best_match[1]
    
    print(f"  ✗ Aucune correspondance trouvée pour '{clean_base_name}'")
    return None

def format_date(date_str):
    """Formate la date en format français."""
    if not date_str:
        return "Date inconnue"

    try:
        # Convertir la chaîne de date en objet datetime
        if isinstance(date_str, str):
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            date_obj = date_str

        # Formater en format français
        return date_obj.strftime('%d/%m/%Y à %H:%M')
    except Exception as e:
        print(f"Erreur lors du formatage de la date {date_str}: {str(e)}")
        return str(date_str)


def parse_files():
    """Traite les fichiers et ajoute les dates depuis le fichier Excel."""
    valid_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

    # Charger les données Excel
    file_dates = load_excel_data()

    for file in input_dir.iterdir():
        if file.is_file() and file.suffix.lower() in valid_extensions:
            try:
                output_file = unique_path(output_dir, f"{file.name}.txt")
                print(f"Traitement: {file} -> {output_file}")

                # Extraire le contenu du CV
                extract_cv(input=file, output=output_file)

                # Trouver la date correspondante dans le fichier Excel
                date = find_date_for_file(file.name, file_dates)
                formatted_date = format_date(date)

                # Ajouter la date au fichier texte
                add_date_to_file(output_file, formatted_date)

                print(f"✓ Extraction réussie: {output_file} (Date: {formatted_date})")

                # Déplacement dans archive sans écraser les anciens
                archived_file = unique_path(archive_dir, file.name)
                shutil.move(str(file), str(archived_file))
            except Exception as e:
                print(f"✗ Erreur lors du traitement de {file}: {str(e)}")


def add_date_to_file(file_path, date):
    """Ajoute la date au début du fichier texte avec un format plus détaillé et cohérent."""
    try:
        # Lire le contenu actuel
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Si la date est "Date inconnue", essayer d'extraire la date du nom de fichier
        if date == "Date inconnue":
            from utils.metadata_utils import extract_date_from_filename, format_date
            filename = Path(file_path).name
            date_from_name = extract_date_from_filename(filename)
            if date_from_name:
                date = format_date(date_from_name)

        # Ajouter la date au début avec un format standardisé
        new_content = f"Date de réception : {date}\n\n{content}"

        # Écrire le nouveau contenu
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(new_content)
    except Exception as e:
        print(f"Erreur lors de l'ajout de la date au fichier {file_path}: {str(e)}")


def get_agent():
    return Agent(
        model=Gemini(id="gemini-1.5-flash", api_key=api_key),
        description="Tu es un expert dans l'analyse des CVs.",
        instructions=[
            "Utiliser uniquement le français.",
            "Organiser le CV.",
            "Produire une copie fidèle du contenu.",
            "Ne pas modifier le contenu du CV.",
        ],
        markdown=True,
    )


def extract_cv(input, output):
    msg = "Voici le fichier à traiter. Extrait tout le texte du CV sans ajouter de commentaires:"
    agent = get_agent()

    if not input.exists():
        raise FileNotFoundError(f"Le fichier {input} n'existe pas")

    chunks = agent.run(
        message=msg,
        files=[File(filepath=str(input))],
    )

    content = chunks.content.replace("```markdown", "").replace("```", "").strip()

    with open(output, "w", encoding="utf-8") as file:
        file.write(content)


if __name__ == "__main__":
    print(f"Début de l'extraction des CV depuis: {input_dir}")
    print(f"Les fichiers texte seront enregistrés dans: {output_dir}")
    print(f"Utilisation du fichier Excel: {excel_file}")
    parse_files()
    print("Traitement terminé!")