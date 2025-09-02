import re
from datetime import datetime, timedelta
from typing import Dict, Any
from base import BaseNode

class CalendarAddEventAction(BaseNode):
    """Nœud d'action qui ajoute un événement au calendrier."""
    
    def execute(self, configuration: Dict[str, Any], context: Dict[str, Any], test_mode: bool = False) -> Any:
        """
        Ajoute un rendez-vous au calendrier si l'email est classifié comme RDV.
        
        Configuration attendue:
        - calendar_service: Service de calendrier (google, outlook)
        - api_key: Clé API du service
        
        Context attendu:
        - Classification de l'email comme "rdv"
        - Données de l'email avec informations de date/heure
        """
        if test_mode:
            return {
                "status": "test_mode",
                "message": "Simulation d'ajout d'événement au calendrier",
                "event": {
                    "title": "Rendez-vous extrait de l'email",
                    "date": "2024-01-25",
                    "time": "14:30",
                    "duration": 60,
                    "calendar_id": "test_calendar"
                }
            }
        
        calendar_service = configuration.get("calendar_service")
        api_key = configuration.get("api_key")
        
        if not calendar_service or not api_key:
            return {
                "status": "error",
                "message": "Configuration du calendrier manquante (service et clé API requis)"
            }
        
        # Vérifier si l'email a été classifié comme RDV
        classification_result = None
        for key, value in context.items():
            if isinstance(value, dict) and "category" in value:
                classification_result = value
                break
        
        if not classification_result or classification_result.get("category") != "rdv":
            return {
                "status": "skipped",
                "message": "Email non classifié comme rendez-vous, aucun événement créé"
            }
        
        # Récupérer les données de l'email
        email_data = None
        for key, value in context.items():
            if isinstance(value, dict) and "email_data" in value:
                email_data = value["email_data"]
                break
        
        if not email_data:
            email_data = context.get("trigger_data", {}).get("email_data")
        
        if not email_data:
            return {
                "status": "error",
                "message": "Aucune donnée d'email trouvée"
            }
        
        # Extraire les informations de date et heure
        subject = email_data.get("subject", "")
        body = email_data.get("body", "")
        full_text = f"{subject} {body}"
        
        # Récupérer aussi le texte OCR si disponible
        for key, value in context.items():
            if isinstance(value, dict) and "combined_text" in value:
                full_text += f" {value['combined_text']}"
        
        event_info = self._extract_event_info(full_text)
        
        if not event_info["date_found"]:
            return {
                "status": "error",
                "message": "Aucune date/heure trouvée dans l'email pour créer l'événement"
            }
        
        # Créer l'événement selon le service de calendrier
        if calendar_service.lower() == "google":
            result = self._create_google_calendar_event(event_info, api_key)
        elif calendar_service.lower() == "outlook":
            result = self._create_outlook_calendar_event(event_info, api_key)
        else:
            return {
                "status": "error",
                "message": f"Service de calendrier non supporté: {calendar_service}"
            }
        
        return result
    
    def _extract_event_info(self, text: str) -> Dict[str, Any]:
        """Extrait les informations de date, heure et titre du texte."""
        event_info = {
            "title": "",
            "date": None,
            "time": None,
            "duration": 60,  # Durée par défaut en minutes
            "date_found": False
        }
        
        text_lower = text.lower()
        
        # Patterns pour les dates
        date_patterns = [
            r'(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})',  # DD/MM/YYYY ou DD-MM-YYYY
            r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{2,4})',
            r'(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+(\d{1,2})[\/\-\.](\d{1,2})',
            r'le\s+(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})',
            r'(\d{2,4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})'  # YYYY/MM/DD
        ]
        
        # Patterns pour les heures
        time_patterns = [
            r'(\d{1,2})[h:](\d{2})',  # 14h30 ou 14:30
            r'(\d{1,2})h(\d{2})?',    # 14h ou 14h30
            r'à\s+(\d{1,2})[h:](\d{2})',
            r'(\d{1,2}):(\d{2})',     # 14:30
        ]
        
        # Chercher les dates
        for pattern in date_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                event_info["date_found"] = True
                # Prendre la première date trouvée
                match = matches[0]
                if len(match) >= 2:
                    try:
                        if pattern.index('janvier') >= 0:  # Pattern avec nom de mois
                            day, month_name, year = match
                            months = {
                                'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
                                'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
                                'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
                            }
                            month = months.get(month_name, 1)
                            event_info["date"] = f"{year}-{month:02d}-{int(day):02d}"
                        else:
                            # Format numérique
                            if len(match) == 3:
                                day, month, year = match
                                if len(year) == 2:
                                    year = f"20{year}"
                                event_info["date"] = f"{year}-{int(month):02d}-{int(day):02d}"
                    except (ValueError, KeyError):
                        continue
                break
        
        # Chercher les heures
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            if matches:
                match = matches[0]
                if len(match) >= 1:
                    try:
                        if len(match) == 2 and match[1]:
                            hour, minute = match
                            event_info["time"] = f"{int(hour):02d}:{int(minute):02d}"
                        else:
                            hour = match[0]
                            event_info["time"] = f"{int(hour):02d}:00"
                    except ValueError:
                        continue
                break
        
        # Extraire le titre (utiliser l'objet de l'email ou une partie du corps)
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) < 100:  # Titre raisonnable
                event_info["title"] = line
                break
        
        if not event_info["title"]:
            event_info["title"] = "Rendez-vous (extrait automatiquement)"
        
        # Chercher la durée
        duration_patterns = [
            r'(\d+)\s*h(?:eure)?s?',
            r'(\d+)\s*minutes?',
            r'durée[:\s]+(\d+)',
        ]
        
        for pattern in duration_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    duration = int(matches[0])
                    if 'minute' in pattern:
                        event_info["duration"] = duration
                    else:  # heures
                        event_info["duration"] = duration * 60
                    break
                except ValueError:
                    continue
        
        return event_info
    
    def _create_google_calendar_event(self, event_info: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Crée un événement dans Google Calendar (simulation)."""
        # En production, utiliser l'API Google Calendar
        return {
            "status": "created",
            "message": "Événement créé dans Google Calendar",
            "event": {
                "title": event_info["title"],
                "date": event_info["date"],
                "time": event_info["time"],
                "duration": event_info["duration"],
                "calendar_service": "google",
                "event_id": f"google_event_{datetime.now().timestamp()}"
            }
        }
    
    def _create_outlook_calendar_event(self, event_info: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Crée un événement dans Outlook Calendar (simulation)."""
        # En production, utiliser l'API Microsoft Graph
        return {
            "status": "created",
            "message": "Événement créé dans Outlook Calendar",
            "event": {
                "title": event_info["title"],
                "date": event_info["date"],
                "time": event_info["time"],
                "duration": event_info["duration"],
                "calendar_service": "outlook",
                "event_id": f"outlook_event_{datetime.now().timestamp()}"
            }
        }