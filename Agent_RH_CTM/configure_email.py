#!/usr/bin/env python3
"""
Script de configuration email pour Assistant RH CTM
Permet de configurer facilement l'envoi d'emails
"""

import os
import re

def update_env_file(email, password, test_mode="false"):
    """Met à jour le fichier .env avec les nouvelles configurations"""
    env_file = ".env"
    
    # Lire le fichier .env existant
    with open(env_file, "r") as f:
        content = f.read()
    
    # Mettre à jour EMAIL_SENDER
    content = re.sub(r'EMAIL_SENDER=.*', f'EMAIL_SENDER="{email}"', content)
    
    # Mettre à jour EMAIL_PASSWORD
    content = re.sub(r'EMAIL_PASSWORD=.*', f'EMAIL_PASSWORD="{password}"', content)
    
    # Ajouter ou mettre à jour TEST_MODE
    if "TEST_MODE=" in content:
        content = re.sub(r'TEST_MODE=.*', f'TEST_MODE="{test_mode}"', content)
    else:
        content += f'\nTEST_MODE="{test_mode}"\n'
    
    # Sauvegarder
    with open(env_file, "w") as f:
        f.write(content)
    
    print(f"✅ Configuration sauvegardée dans {env_file}")

def configure_gmail():
    """Configuration pour Gmail"""
    print("📧 === Configuration Gmail ===\n")
    
    email = input("📧 Votre email Gmail: ").strip()
    
    if not email.endswith("@gmail.com"):
        print("❌ Veuillez utiliser une adresse Gmail (@gmail.com)")
        return False
    
    print("\n💡 Pour le mot de passe, vous devez:")
    print("   1. Activer l'authentification à 2 facteurs sur votre compte Gmail")
    print("   2. Générer un 'mot de passe d'application'")
    print("   3. Utiliser ce mot de passe d'application (pas votre mot de passe normal)")
    print("   📖 Guide: https://support.google.com/accounts/answer/185833")
    
    password = input("\n🔐 Mot de passe d'application Gmail: ").strip()
    
    if not password:
        print("❌ Mot de passe requis")
        return False
    
    # Test de la configuration
    confirm = input(f"\n❓ Configurer avec {email} ? (o/n): ").strip().lower()
    
    if confirm in ['o', 'oui', 'y', 'yes']:
        update_env_file(email, password, "false")
        
        # Test d'envoi
        test_email = input(f"\n📨 Email de test (laissez vide pour utiliser {email}): ").strip()
        if not test_email:
            test_email = email
            
        return test_sending(test_email)
    
    return False

def configure_test_mode():
    """Active le mode test (affichage console)"""
    print("🧪 === Mode Test ===\n")
    print("En mode test, les codes d'activation s'affichent dans la console")
    print("Aucun email n'est envoyé.")
    
    confirm = input("\n❓ Activer le mode test ? (o/n): ").strip().lower()
    
    if confirm in ['o', 'oui', 'y', 'yes']:
        # Garder la configuration email existante mais activer TEST_MODE
        env_file = ".env"
        with open(env_file, "r") as f:
            content = f.read()
        
        if "TEST_MODE=" in content:
            content = re.sub(r'TEST_MODE=.*', 'TEST_MODE="true"', content)
        else:
            content += '\nTEST_MODE="true"\n'
        
        with open(env_file, "w") as f:
            f.write(content)
        
        print("✅ Mode test activé")
        return True
    
    return False

def test_sending(test_email):
    """Test d'envoi d'email"""
    print(f"\n📨 === Test d'envoi vers {test_email} ===")
    
    try:
        # Recharger la configuration
        from importlib import reload
        import sys
        if 'auth.user_auth' in sys.modules:
            reload(sys.modules['auth.user_auth'])
        if 'utils.env_config' in sys.modules:
            reload(sys.modules['utils.env_config'])
        
        from auth.user_auth import send_activation_email, generate_code
        
        code = generate_code()
        print(f"🔑 Code de test: {code}")
        
        success = send_activation_email(test_email, code)
        
        if success:
            print(f"\n🎉 Email envoyé avec succès à {test_email} !")
            print(f"📬 Vérifiez votre boîte mail pour le code: {code}")
            return True
        else:
            print(f"\n❌ Échec de l'envoi")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Menu principal"""
    print("🔧 === Configuration Email Assistant RH CTM ===\n")
    
    print("📋 Options disponibles:")
    print("1. Configurer avec Gmail")
    print("2. Activer le mode test (console)")
    print("3. Tester la configuration actuelle")
    print("4. Quitter")
    
    choice = input("\n🔢 Votre choix (1-4): ").strip()
    
    if choice == "1":
        configure_gmail()
    elif choice == "2":
        configure_test_mode()
    elif choice == "3":
        test_email = input("📧 Email pour le test: ").strip()
        if test_email:
            test_sending(test_email)
    elif choice == "4":
        print("👋 Au revoir!")
    else:
        print("❌ Choix invalide")

if __name__ == "__main__":
    main()
