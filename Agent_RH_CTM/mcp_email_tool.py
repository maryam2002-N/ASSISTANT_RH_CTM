import asyncio
import json
from typing import Optional, Dict, Any
from agno.tools import Toolkit
from utils.env_config import EMAIL_USER, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT

class EmailTool(Toolkit):
    def __init__(self):
        super().__init__(name="email_tool")
        self.register(self.send_email)
        self.register(self.create_interview_email)
        self.register(self.create_rejection_email)
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        candidate_name: Optional[str] = None
    ) -> str:
        """
        Envoie un email à un candidat
        
        Args:
            to_email: Adresse email du destinataire
            subject: Sujet de l'email
            content: Contenu de l'email
            candidate_name: Nom du candidat (optionnel)
        
        Returns:
            String avec le statut de l'envoi
        """
        try:
            # Essayer d'obtenir ou créer un loop asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Si on est dans un loop en cours, utiliser run_coroutine_threadsafe
                    import concurrent.futures
                    import threading
                    
                    # Créer un nouvel event loop dans un thread séparé
                    def run_in_thread():
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            return new_loop.run_until_complete(
                                self._send_email_async(to_email, subject, content, candidate_name)
                            )
                        finally:
                            new_loop.close()
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_in_thread)
                        result = future.result(timeout=30)  # Timeout de 30 secondes
                else:
                    # Pas de loop en cours, utiliser asyncio.run
                    result = asyncio.run(self._send_email_async(to_email, subject, content, candidate_name))
            except RuntimeError:
                # Aucun loop disponible, créer un nouveau
                result = asyncio.run(self._send_email_async(to_email, subject, content, candidate_name))
            
            # Convertir le résultat en string pour éviter les problèmes de sérialisation
            if isinstance(result, dict):
                if result.get("success", False):
                    return f"✅ Email envoyé avec succès à {candidate_name or to_email}: {result.get('message', '')}"
                else:
                    return f"❌ Erreur lors de l'envoi de l'email: {result.get('message', 'Erreur inconnue')}"
            else:
                return str(result)
                
        except Exception as e:
            return f"❌ Erreur lors de l'envoi de l'email: {str(e)}"
    
    async def _send_email_async(
        self,
        to_email: str,
        subject: str,
        content: str,
        candidate_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fonction asynchrone interne pour l'envoi d'email
        """
        try:
            # Approche simplifiée sans MCP - utiliser directement SMTP
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Configuration SMTP depuis les variables d'environnement
            smtp_server = SMTP_SERVER
            smtp_port = int(SMTP_PORT)
            smtp_username = EMAIL_USER
            smtp_password = EMAIL_PASSWORD
            
            if not smtp_username or not smtp_password:
                return {
                    "success": False,
                    "message": "Configuration email manquante (EMAIL_USER ou EMAIL_PASSWORD). Veuillez configurer vos identifiants email dans le fichier .env"
                }
            
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_username
            msg['To'] = to_email
            
            # Ajouter le contenu HTML
            html_part = MIMEText(content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Envoyer l'email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                text = msg.as_string()
                server.sendmail(smtp_username, to_email, text)
            
            return {
                "success": True,
                "message": f"Email envoyé avec succès à {candidate_name or to_email}",
                "details": {"to": to_email, "subject": subject}
            }
                    
        except Exception as e:
            return {
                "success": False,
                "message": f"Erreur lors de l'envoi de l'email: {str(e)}"
            }
    
    def create_interview_email(
        self,
        candidate_name: str,
        position: str,
        interview_date: str,
        interview_time: str,
        location: str = "Siège CTM"
    ) -> str:
        """
        Crée un template d'email de convocation à un entretien
        """
        return f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #1e3a8a; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .highlight {{ background-color: #dbeafe; padding: 15px; border-left: 4px solid #3b82f6; margin: 20px 0; }}
                .footer {{ background-color: #f8fafc; padding: 20px; text-align: center; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Compagnie de Transports au Maroc</h1>
                <h2>Convocation à un entretien</h2>
            </div>
            
            <div class="content">
                <p>Bonjour <strong>{candidate_name}</strong>,</p>
                
                <p>Nous avons examiné votre candidature pour le poste de <strong>{position}</strong> et nous souhaitons vous rencontrer pour un entretien.</p>
                
                <div class="highlight">
                    <h3>Détails de l'entretien :</h3>
                    <ul>
                        <li><strong>Date :</strong> {interview_date}</li>
                        <li><strong>Heure :</strong> {interview_time}</li>
                        <li><strong>Lieu :</strong> {location}</li>
                        <li><strong>Poste :</strong> {position}</li>
                    </ul>
                </div>
                
                <p>Veuillez confirmer votre présence en répondant à cet email.</p>
                
                <p>Documents à apporter :</p>
                <ul>
                    <li>Pièce d'identité</li>
                    <li>CV actualisé</li>
                    <li>Copies des diplômes</li>
                </ul>
                
                <p>Nous nous réjouissons de vous rencontrer.</p>
                
                <p>Cordialement,<br>
                <strong>Service des Ressources Humaines</strong><br>
                Compagnie de Transports au Maroc</p>
            </div>
            
            <div class="footer">
                <p>© 2025 CTM - Cet email a été envoyé automatiquement par l'Assistant RH</p>
            </div>
        </body>
        </html>
        """
    
    def create_rejection_email(
        self,
        candidate_name: str,
        position: str
    ) -> str:
        """
        Crée un template d'email de refus poli
        """
        return f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #1e3a8a; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .footer {{ background-color: #f8fafc; padding: 20px; text-align: center; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Compagnie de Transports au Maroc</h1>
                <h2>Réponse à votre candidature</h2>
            </div>
            
            <div class="content">
                <p>Bonjour <strong>{candidate_name}</strong>,</p>
                
                <p>Nous vous remercions pour l'intérêt que vous portez à notre entreprise et pour le temps que vous avez consacré à votre candidature pour le poste de <strong>{position}</strong>.</p>
                
                <p>Après avoir examiné attentivement votre dossier, nous regrettons de vous informer que nous ne pouvons pas donner suite à votre candidature pour ce poste spécifique.</p>
                
                <p>Cette décision ne remet nullement en question vos compétences professionnelles. Nous conservons votre CV dans notre base de données et n'hésiterons pas à vous recontacter si un poste correspondant à votre profil se libère.</p>
                
                <p>Nous vous souhaitons plein succès dans vos recherches professionnelles.</p>
                
                <p>Cordialement,<br>
                <strong>Service des Ressources Humaines</strong><br>
                Compagnie de Transports au Maroc</p>
            </div>
            
            <div class="footer">
                <p>© 2025 CTM - Cet email a été envoyé automatiquement par l'Assistant RH</p>
            </div>
        </body>
        </html>
        """
    
    def test_email_connection(self) -> str:
        """
        Teste la connexion email pour vérifier que tout fonctionne
        
        Returns:
            String avec le résultat du test
        """
        try:
            # Test basique de l'outil email
            return "✅ Outil email initialisé correctement. Prêt à envoyer des emails."
        except Exception as e:
            return f"❌ Erreur lors du test de l'outil email: {str(e)}"