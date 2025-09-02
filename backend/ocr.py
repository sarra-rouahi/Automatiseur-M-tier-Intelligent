
import base64
import io
from typing import Dict, Any
from PIL import Image
import pytesseract
from base import BaseNode
from fastapi import APIRouter
router = APIRouter()

class OCRImageAction(BaseNode):
    """Nœud d'action qui extrait le texte des images attachées."""
    
    def execute(self, configuration: Dict[str, Any], context: Dict[str, Any], test_mode: bool = False) -> Any:
        """
        Extrait le texte des images attachées à un email.
        
        Configuration attendue:
        - language: Langue du texte (fr, en, etc.) - optionnel
        
        Context attendu:
        - email_data avec attachments contenant des images
        """
        if test_mode:
            return {
                "status": "test_mode",
                "message": "Simulation d'extraction OCR",
                "extracted_texts": [
                    {
                        "filename": "test_image.jpg",
                        "text": "Ceci est un texte extrait d'une image de test. Rendez-vous prévu le 25 janvier à 14h30."
                    }
                ]
            }
        
        language = configuration.get("language", "fra")  # français par défaut
        
        # Récupérer les données de l'email depuis le contexte
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
                "message": "Aucune donnée d'email trouvée dans le contexte"
            }
        
        attachments = email_data.get("attachments", [])
        
        if not attachments:
            return {
                "status": "no_images",
                "message": "Aucune pièce jointe trouvée",
                "extracted_texts": []
            }
        
        extracted_texts = []
        
        for attachment in attachments:
            filename = attachment.get("filename", "")
            content_type = attachment.get("content_type", "")
            data = attachment.get("data")
            
            # Vérifier si c'est une image
            if not content_type.startswith("image/"):
                continue
            
            try:
                # Convertir les données en image PIL
                if isinstance(data, str):
                    # Si les données sont en base64
                    image_data = base64.b64decode(data)
                else:
                    # Si les données sont déjà en bytes
                    image_data = data
                
                image = Image.open(io.BytesIO(image_data))
                
                # Extraire le texte avec Tesseract
                extracted_text = pytesseract.image_to_string(image, lang=language)
                
                if extracted_text.strip():
                    extracted_texts.append({
                        "filename": filename,
                        "text": extracted_text.strip(),
                        "content_type": content_type
                    })
                
            except Exception as e:
                extracted_texts.append({
                    "filename": filename,
                    "error": f"Erreur lors de l'extraction OCR: {str(e)}",
                    "content_type": content_type
                })
        
        if not extracted_texts:
            return {
                "status": "no_text_found",
                "message": "Aucun texte extrait des images",
                "extracted_texts": []
            }
        
        # Combiner tous les textes extraits
        combined_text = "\n\n".join([
            f"=== {item['filename']} ===\n{item.get('text', item.get('error', ''))}"
            for item in extracted_texts
        ])
        
        return {
            "status": "text_extracted",
            "extracted_texts": extracted_texts,
            "combined_text": combined_text,
            "total_images_processed": len([item for item in extracted_texts if "text" in item])
        }
