import re
from typing import Dict, Any, List
from backend.base import BaseNode

class EmailClassifierAction(BaseNode):
    """Nœud d'action qui classifie le contenu des emails."""
    
    def execute(self, configuration: Dict[str, Any], context: Dict[str, Any], test_mode: bool = False) -> Any:
        """
        Classifie un email selon les catégories configurées.
        
        Configuration attendue:
        - categories: Liste des catégories possibles (ex: ["rdv", "feedback", "spam", "info"])
        
        Context attendu:
        - email_data: Données de l'email (from, subject, body)
        """
        categories = configuration.get("categories", ["rdv", "feedback", "spam", "info"])
        
        # Récupérer les données de l'email depuis le contexte
        email_data = None
        for key, value in context.items():
            if isinstance(value, dict) and "email_data" in value:
                email_data = value["email_data"]
                break
        
        if not email_data:
            # Chercher dans trigger_data
            email_data = context.get("trigger_data", {}).get("email_data")
        
        if not email_data:
            return {
                "status": "error",
                "message": "Aucune donnée d'email trouvée dans le contexte"
            }
        
        subject = email_data.get("subject", "").lower()
        body = email_data.get("body", "").lower()
        sender = email_data.get("from", "").lower()
        
        # Règles de classification basées sur des mots-clés
        classification_rules = {
            "rdv": [
                "rendez-vous", "rdv", "meeting", "réunion", "appointment",
                "rencontre", "entretien", "disponibilité", "créneau",
                "calendrier", "planning", "horaire", "date", "heure"
            ],
            "feedback": [
                "feedback", "retour", "avis", "commentaire", "opinion",
                "satisfaction", "évaluation", "critique", "suggestion",
                "amélioration", "problème", "bug", "erreur"
            ],
            "spam": [
                "promotion", "offre spéciale", "gratuit", "gagner", "urgent",
                "cliquez ici", "limited time", "act now", "viagra",
                "casino", "lottery", "winner", "congratulations"
            ],
            "info": [
                "information", "newsletter", "actualité", "news",
                "mise à jour", "update", "notification", "rappel"
            ]
        }
        
        # Calculer les scores pour chaque catégorie
        scores = {}
        text_to_analyze = f"{subject} {body}"
        
        for category in categories:
            if category in classification_rules:
                keywords = classification_rules[category]
                score = sum(1 for keyword in keywords if keyword in text_to_analyze)
                scores[category] = score
            else:
                scores[category] = 0
        
        # Déterminer la catégorie avec le score le plus élevé
        if max(scores.values()) == 0:
            predicted_category = "info"  # Catégorie par défaut
            confidence = 0.1
        else:
            predicted_category = max(scores, key=scores.get)
            confidence = scores[predicted_category] / sum(scores.values()) if sum(scores.values()) > 0 else 0
        
        # Règles spéciales pour améliorer la précision
        if any(word in text_to_analyze for word in ["urgent", "asap", "immédiat"]):
            if predicted_category == "rdv":
                confidence += 0.2
        
        if "@" in sender and any(domain in sender for domain in ["noreply", "no-reply", "newsletter"]):
            predicted_category = "info"
            confidence = 0.8
        
        return {
            "status": "classified",
            "category": predicted_category,
            "confidence": min(confidence, 1.0),
            "scores": scores,
            "email_summary": {
                "subject": email_data.get("subject"),
                "sender": email_data.get("from"),
                "classification": predicted_category
            }
        }
