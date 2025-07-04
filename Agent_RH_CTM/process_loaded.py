import os
import shutil
import pandas as pd
from datetime import datetime

# Types de fichiers
image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
pdf_exts = {'.pdf'}
doc_exts = {'.doc', '.docx'}
ppt_exts = {'.ppt', '.pptx'}

# Dossier source à parcourir
#source_dir = r'C:\Users\PC\AppData\Local\Temp\test_loaded_icky698z'
#source_dir = r'C:\Users\PC\OneDrive - CTM (COMPAGNIE DE TRANSPORT AU MAROC S.A)\loaded'
# Dossiers cibles
to_txt_dir = './to_txt'
to_pdf_dir = './to_pdf'

# Créer les dossiers cibles s'ils n'existent pas
os.makedirs(to_txt_dir, exist_ok=True)
os.makedirs(to_pdf_dir, exist_ok=True)

# Liste pour enregistrer les logs
logs = []

# Parcours récursif du dossier source
for root, dirs, files in os.walk(source_dir):
    for file in files:        # Vérifier si le fichier a déjà été traité (se termine par "_done" avant l'extension)
        name_without_ext = os.path.splitext(file)[0]
        if name_without_ext.endswith("_done"):
            print(f"Fichier déjà traité ignoré : {file}")
            continue
            
        ext = os.path.splitext(file)[1].lower()
        source_path = os.path.join(root, file)        # Nouveau nom sans espaces et limité en longueur
        cleaned_name = file.replace(" ","")
        
        # Limiter la longueur du nom de fichier (Windows limite à ~260 caractères pour le chemin complet)
        name_without_ext = os.path.splitext(cleaned_name)[0]
        file_ext = os.path.splitext(cleaned_name)[1]
        
        # Limiter à 150 caractères pour le nom sans extension pour éviter les problèmes de chemin
        if len(name_without_ext) > 150:
            name_without_ext = name_without_ext[:150]
            cleaned_name = f"{name_without_ext}{file_ext}"
            print(f"Nom tronqué pour éviter la limite Windows : {cleaned_name}")
        
        cleaned_path = os.path.join(root, cleaned_name)

        # Si le nom a été modifié, renommer le fichier avec gestion d'erreurs
        if file != cleaned_name:
            try:
                os.rename(source_path, cleaned_path)
                print(f"Renommé : {file} → {cleaned_name}")
                source_path = cleaned_path  # mettre à jour le chemin
            except (FileNotFoundError, OSError) as e:
                print(f"ERREUR de renommage pour {file}: {e}")
                # Utiliser le chemin original si le renommage échoue
                cleaned_name = file
                cleaned_path = source_path# Variable pour suivre si le fichier a été traité
        traite = False
        destination = ""
        error_message = ""

        # Rediriger selon l'extension
        try:
            if ext in image_exts or ext in pdf_exts:
                shutil.copy2(source_path, os.path.join(to_txt_dir, cleaned_name))
                destination = to_txt_dir
                traite = True
                print(f"Copié vers to_txt: {cleaned_name}")
            elif ext in doc_exts or ext in ppt_exts:
                shutil.copy2(source_path, os.path.join(to_pdf_dir, cleaned_name))
                destination = to_pdf_dir
                traite = True
                print(f"Copié vers to_pdf: {cleaned_name}")
        except OSError as e:
            if e.winerror == 380:
                print(f"ERREUR OneDrive - Fichier non synchronisé: {cleaned_name}")
                error_message = "Fichier OneDrive non synchronisé localement"
            else:
                print(f"ERREUR de copie pour {cleaned_name}: {e}")
                error_message = f"Erreur de copie: {str(e)}"
        except Exception as e:
            print(f"ERREUR inattendue pour {cleaned_name}: {e}")
            error_message = f"Erreur inattendue: {str(e)}"        # Si le fichier a été traité, le renommer avec le suffixe "_done"
        if traite:
            name_without_ext = os.path.splitext(cleaned_name)[0]
            file_ext = os.path.splitext(cleaned_name)[1]
            done_name = f"{name_without_ext}_done{file_ext}"
            done_path = os.path.join(root, done_name)
            
            # Vérifier si le fichier de destination existe déjà
            counter = 1
            original_done_name = done_name
            while os.path.exists(done_path):
                done_name = f"{name_without_ext}_done_{counter}{file_ext}"
                done_path = os.path.join(root, done_name)
                counter += 1
            
            try:
                os.rename(source_path, done_path)
                print(f"Fichier traité et renommé : {cleaned_name} → {done_name}")
            except (FileExistsError, OSError) as e:
                print(f"ERREUR de renommage final pour {cleaned_name}: {e}")
                # Si le renommage échoue, on garde quand même le log mais sans renommer
                done_name = f"ECHEC_RENOMMAGE_{cleaned_name}"
            
            # Ajouter aux logs
            logs.append({
                'Date_Traitement': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Nom_Original': file,
                'Nom_Nettoye': cleaned_name,
                'Nom_Final': done_name,
                'Extension': ext,
                'Dossier_Source': root,
                'Dossier_Destination': destination,
                'Statut': 'Traité avec succès'
            })
        elif error_message:
            # Ajouter aux logs même en cas d'erreur
            logs.append({
                'Date_Traitement': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Nom_Original': file,
                'Nom_Nettoye': cleaned_name,
                'Nom_Final': 'NON TRAITÉ',
                'Extension': ext,
                'Dossier_Source': root,
                'Dossier_Destination': 'AUCUNE',
                'Statut': f'Erreur: {error_message}'
            })

# Enregistrer les logs dans un fichier Excel
if logs:
    df_logs = pd.DataFrame(logs)
    log_filename = f"logs_traitement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df_logs.to_excel(log_filename, index=False)
    print(f"Logs enregistrés dans : {log_filename}")
    print(f"Nombre de fichiers traités : {len(logs)}")
else:
    print("Aucun fichier traité.")
