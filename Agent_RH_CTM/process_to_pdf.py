import os
import shutil
import subprocess
import tempfile
import time

# Extensions ciblées
doc_exts = {'.doc', '.docx'}
ppt_exts = {'.ppt', '.pptx'}

# Dossiers
source_dir = './to_pdf'
to_txt_dir = './to_txt'
archive_dir = './static/cvs'
error_dir = './static/errors'  # Nouveau dossier pour les fichiers problématiques

# Créer les dossiers s'ils n'existent pas
os.makedirs(source_dir, exist_ok=True)
os.makedirs(to_txt_dir, exist_ok=True)
os.makedirs(archive_dir, exist_ok=True)
os.makedirs(error_dir, exist_ok=True)

# Génère un nom de fichier sans écrasement
def get_unique_filename(directory, filename):
    name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{name}_{counter}{ext}"
        counter += 1
    return new_filename
# Fonction de conversion avec LibreOffice améliorée
def convert_to_pdf(input_path, output_dir):
    abs_input_path = os.path.abspath(input_path)
    abs_output_dir = os.path.abspath(output_dir)
    
    print(f"Conversion de {abs_input_path} vers PDF dans {abs_output_dir}")
    
    try:
        # Essayer d'abord avec soffice
        result = subprocess.run([
            'soffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', abs_output_dir,
            abs_input_path
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"   Erreur LibreOffice (code {result.returncode}): {result.stderr}")
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        print(f"   Timeout lors de la conversion")
        return False
    except FileNotFoundError:
        print(f"   LibreOffice non trouvé. Essayez d'installer LibreOffice ou vérifiez le PATH")
        return False
    except Exception as e:
        print(f"   Erreur inattendue: {str(e)}")
        return False

# Fonction pour vérifier si un fichier est corrompu
def is_file_corrupted(file_path):
    try:
        # Tentative de lecture basique du fichier
        with open(file_path, 'rb') as f:
            f.read(1024)  # Lire les premiers 1024 octets
        return False
    except Exception:
        return True

# Parcourir les fichiers
total_files = 0
success_count = 0
error_count = 0

for root, dirs, files in os.walk(source_dir):
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext in doc_exts or ext in ppt_exts:
            total_files += 1
            source_path = os.path.join(root, file)
            abs_source_path = os.path.abspath(source_path)
            
            print(f"\n📄 Traitement de: {file}")
            
            # Vérifier si le fichier est corrompu
            if is_file_corrupted(abs_source_path):
                print(f"   ⚠️  Fichier potentiellement corrompu détecté")
                unique_error_name = get_unique_filename(error_dir, file)
                shutil.move(abs_source_path, os.path.join(error_dir, unique_error_name))
                print(f"   📁 Déplacé vers le dossier d'erreurs: {unique_error_name}")
                error_count += 1
                continue
            
            try:
                # 1. Générer un nom de fichier PDF unique
                pdf_name = os.path.splitext(file)[0] + '.pdf'
                unique_pdf_name = get_unique_filename(to_txt_dir, pdf_name)
                
                # 2. Conversion en PDF
                abs_to_txt_dir = os.path.abspath(to_txt_dir)
                conversion_success = convert_to_pdf(abs_source_path, abs_to_txt_dir)
                
                if not conversion_success:
                    raise Exception("Échec de la conversion")
                
                # 3. Vérifier que le PDF a bien été généré
                final_pdf_path = os.path.join(abs_to_txt_dir, pdf_name)
                
                # Attendre un peu pour que le fichier soit bien écrit
                time.sleep(0.5)
                
                if not os.path.exists(final_pdf_path):
                    raise FileNotFoundError(f"Le PDF n'a pas été généré à {final_pdf_path}")
                
                # Renommer le PDF si nécessaire pour avoir un nom unique
                if pdf_name != unique_pdf_name:
                    unique_pdf_path = os.path.join(abs_to_txt_dir, unique_pdf_name)
                    os.rename(final_pdf_path, unique_pdf_path)
                    final_pdf_path = unique_pdf_path
                
                # 4. Déplacer l'original dans archive avec nom unique
                abs_archive_dir = os.path.abspath(archive_dir)
                unique_original_name = get_unique_filename(abs_archive_dir, file)
                shutil.move(abs_source_path, os.path.join(abs_archive_dir, unique_original_name))
                
                print(f"   ✅ Converti: {os.path.basename(final_pdf_path)}")
                print(f"   📁 Archivé: {unique_original_name}")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Erreur: {str(e)}")
                # Déplacer le fichier problématique vers le dossier d'erreurs
                try:
                    unique_error_name = get_unique_filename(error_dir, file)
                    shutil.move(abs_source_path, os.path.join(error_dir, unique_error_name))
                    print(f"   📁 Déplacé vers le dossier d'erreurs: {unique_error_name}")
                except Exception as move_error:
                    print(f"   ⚠️  Impossible de déplacer le fichier: {move_error}")
                error_count += 1

# Résumé final
print(f"\n{'='*50}")
print(f" RÉSUMÉ DU TRAITEMENT")
print(f"{'='*50}")
print(f"Total de fichiers traités: {total_files}")
print(f" Conversions réussies: {success_count}")
print(f" Fichiers en erreur: {error_count}")
print(f" Dossier d'archives: {archive_dir}")
print(f"Dossier d'erreurs: {error_dir}")

if error_count > 0:
    print(f"\n⚠️ {error_count} fichier(s) ont été déplacés vers le dossier d'erreurs.")
    print("Vérifiez ces fichiers manuellement.")