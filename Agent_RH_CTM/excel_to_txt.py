import os
import pandas as pd
import re
from datetime import datetime

def convert_excel_to_txt_files(excel_file, sheet_name='GLOBAL', output_dir='fichiers_txt'):
    """
    Convertit chaque ligne d'une feuille Excel en fichier texte distinct.
   
    Args:
        excel_file (str): Chemin vers le fichier Excel
        sheet_name (str): Nom de la feuille à traiter
        output_dir (str): Dossier de sortie pour les fichiers texte
    """
    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Dossier '{output_dir}' créé.")
   
    # Lire la feuille Excel
    print(f"Lecture du fichier '{excel_file}', feuille '{sheet_name}'...")
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
   
    # Nettoyer les en-têtes (supprimer les espaces en fin de chaîne et renommer les colonnes vides)
    df.columns = [str(col).strip() if pd.notna(col) and str(col).strip() != "" else f"Colonne_{i}"
                  for i, col in enumerate(df.columns)]    # Supprimer les lignes qui sont des duplications d'en-têtes (seulement si c'est vraiment un doublon d'en-tête)
    # On garde les lignes avec des données réelles, même si elles contiennent "Date" ou "Nom et Prénom"
    header_mask = ((df.iloc[:, 0].astype(str).str.contains('Date', case=False)) & 
                   (df.iloc[:, 1].astype(str).str.contains('Nom et Prénom', case=False)) &
                   (df.iloc[:, 0].astype(str).str.strip() == 'Date') &
                   (df.iloc[:, 1].astype(str).str.strip() == 'Nom et Prénom'))
    df = df[~header_mask]
   
    # Supprimer les lignes vides (où toutes les colonnes sont NaN ou vides)
    df = df.dropna(how='all')
    df = df[~(df.astype(str).apply(lambda x: x.str.strip() == "").all(axis=1))]
     # Remplacer les NaN par des chaînes vides
    df = df.fillna("")
    
    # PROPAGATION DES DATES : chaque date s'applique aux lignes suivantes jusqu'à la prochaine date
    print("Application de la propagation des dates...")
    derniere_date = None
    for i in range(len(df)):
        date_actuelle = df.iloc[i]['Date']
        # Si on trouve une nouvelle date valide, on la sauvegarde
        if pd.notna(date_actuelle) and str(date_actuelle) != 'Date' and str(date_actuelle).strip() != '':
            derniere_date = date_actuelle
            print(f"Nouvelle date trouvée ligne {i}: {date_actuelle}")
        # Si la ligne n'a pas de date mais qu'on a une dernière date valide, on l'applique
        elif derniere_date is not None and (pd.isna(date_actuelle) or str(date_actuelle).strip() == ''):
            df.iloc[i, df.columns.get_loc('Date')] = derniere_date
            print(f"Date propagée ligne {i}: {derniere_date} pour {df.iloc[i]['Nom et Prénom']}")
   
    # Récupérer les noms des colonnes (pour conserver l'ordre des colonnes du fichier Excel)
    colonnes = df.columns.tolist()# Compteur pour les fichiers sans nom
    no_name_counter = 1
    # Compteur global unique pour éviter tous les doublons
    fichier_counter = 1
    
    # Pour chaque ligne, créer un fichier texte
    for index, row in df.iterrows():
        # Utiliser le nom et prénom comme base pour le nom de fichier, ou un compteur si vide
        nom_prenom = str(row.get('Nom et Prénom', '')).strip()
        if nom_prenom and nom_prenom != "":
            # Nettoyer le nom pour qu'il soit valide comme nom de fichier
            nom_fichier = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in nom_prenom)
            nom_fichier = nom_fichier.replace(' ', '_')
        else:
            nom_fichier = f"ligne_{no_name_counter}"
            no_name_counter += 1
       
        # Ajouter un horodatage et un compteur unique pour éviter les doublons
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_final = f"{nom_fichier}_{timestamp}_{fichier_counter:03d}"
        fichier_counter += 1
            
        chemin_fichier = os.path.join(output_dir, f"{nom_final}.txt")
         # Traiter les valeurs pour enlever les métadonnées pandas et formater correctement
        values_dict = {}
        statut_integration = None
       
        for colonne in colonnes:
            valeur = str(row.get(colonne, '')).strip()
            
            # Traitement spécial pour la colonne Date - toujours inclure même si vide
            if colonne == "Date":
                if pd.notna(row.get(colonne)) and str(row.get(colonne)).strip():
                    # Si c'est un objet datetime pandas, le convertir en string
                    date_value = row.get(colonne)
                    if hasattr(date_value, 'strftime'):
                        # C'est un objet datetime
                        values_dict[colonne] = date_value.strftime("%d/%m/%Y")
                    else:
                        # C'est déjà une string
                        values_dict[colonne] = str(date_value).strip()
                else:
                    # Date vide - inclure quand même avec une valeur par défaut
                    values_dict[colonne] = "Non renseignée"
                continue
            
            # Pour les autres colonnes, ignorer si vide
            if not valeur:
                continue            # Extraire proprement les valeurs du statut qui peuvent contenir des métadonnées pandas
            if colonne == "Statut":
                # Nettoyer la valeur du statut
                if "Name:" in valeur:
                    # Extraction des informations
                    match_present = re.search(r'Statut\s+Présent', valeur)
                    match_integration = re.search(r'Intégration le \d+/\d+/\d+', valeur)
                   
                    if match_present:
                        values_dict["Statut"] = "Présent"
                   
                    if match_integration:
                        statut_integration = match_integration.group(0)
                else:
                    values_dict[colonne] = valeur
            else:
                values_dict[colonne] = valeur
       
        # Créer le contenu du fichier texte dans l'ordre des colonnes du fichier Excel
        with open(chemin_fichier, 'w', encoding='utf-8') as f:
            for colonne in colonnes:
                if colonne in values_dict:
                    f.write(f"{colonne}: {values_dict[colonne]}\n")
           
            # Ajouter la ligne d'intégration à la fin si elle existe
            if statut_integration:
                f.write(f"{statut_integration}\n")
       
        print(f"Fichier créé: {chemin_fichier}")
   
    print(f"\nConversion terminée. {len(df)} fichiers ont été créés dans le dossier '{output_dir}'.")

if __name__ == "__main__":
    # Chemin vers votre fichier Excel
    fichier_excel = "Etat conducteurs 2024-2025 (2).xlsx"
   
    # Nom de la feuille à traiter
    nom_feuille = "GLOBAL"    # Dossier de sortie
    dossier_sortie = "fichiers_txt_conducteurs_final"
   
    # Exécuter la conversion
    convert_excel_to_txt_files(fichier_excel, nom_feuille, dossier_sortie)
