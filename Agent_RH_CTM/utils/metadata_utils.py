import os
import re
import datetime
from datetime import datetime

def extract_date_from_filename(filename):
    """Extrait la date du nom de fichier au format YYYYMMDDhhmmssSSS__ ou YYYYMMDD-hhmmss__"""
    # Motif pour capturer les dates au format 20250416092736555__ (année-mois-jour-heure-minute-seconde-ms)
    pattern1 = r'^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(\d{3})__'
    
    # Motif pour capturer les dates au format 20250506-103026__ (année-mois-jour-heure-minute-seconde)
    pattern2 = r'^(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})__'
    
    # Motif pour capturer les dates au format 2025-05-05T07_33_19+00_00- (ISO)
    pattern3 = r'^(\d{4})-(\d{2})-(\d{2})T(\d{2})_(\d{2})_(\d{2})\+\d{2}_\d{2}-'
    
    # Essayer le premier format
    match = re.match(pattern1, filename)
    if match:
        year, month, day, hour, minute, second, _ = match.groups()
        return datetime(int(year), int(month), int(day), 
                        int(hour), int(minute), int(second))
    
    # Essayer le deuxième format
    match = re.match(pattern2, filename)
    if match:
        year, month, day, hour, minute, second = match.groups()
        return datetime(int(year), int(month), int(day), 
                        int(hour), int(minute), int(second))
    
    # Essayer le troisième format
    match = re.match(pattern3, filename)
    if match:
        year, month, day, hour, minute, second = match.groups()
        return datetime(int(year), int(month), int(day), 
                        int(hour), int(minute), int(second))
    
    # Si aucun format ne correspond, retourner l'heure de dernière modification du fichier
    return None

def get_document_date(file_path):
    """
    Récupère la date d'un document en suivant cette priorité:
    1. Date extraite du nom de fichier
    2. Date de dernière modification du fichier
    3. Date actuelle
    
    Retourne un objet datetime
    """
    filename = os.path.basename(file_path)
    
    # 1. Essayer d'extraire la date du nom de fichier
    date_from_name = extract_date_from_filename(filename)
    if date_from_name:
        return date_from_name
    
    # 2. Récupérer la date de dernière modification
    try:
        mod_timestamp = os.path.getmtime(file_path)
        return datetime.fromtimestamp(mod_timestamp)
    except:
        # 3. Utiliser la date actuelle en dernier recours
        return datetime.now()

def format_date(date_obj):
    """Formate une date en format lisible"""
    if not date_obj:
        return "Date inconnue"
    return date_obj.strftime("%d/%m/%Y %H:%M:%S")

def get_document_metadata(file_path):
    """
    Récupère les métadonnées d'un document
    Retourne un dictionnaire avec les métadonnées
    """
    date = get_document_date(file_path)
    return {
        "date_ajout": date,
        "date_ajout_str": format_date(date),
        "nom_fichier": os.path.basename(file_path),
        "chemin_complet": file_path
    }