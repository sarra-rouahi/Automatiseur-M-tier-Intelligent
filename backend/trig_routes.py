# trigemail/trigroutes.py
from fastapi import APIRouter
from trigemail import EmailReceivedTrigger

router = APIRouter()

@router.post("/start")
async def start_email_listener(config: dict):
    """
    Démarre le listener IMAP pour l'adresse email donnée.
    JSON attendu :
    {
        "email_address": "...",
        "password": "...",  # token OAuth2
        "imap_server": "imap.gmail.com",
        "filter_sender": "example@domain.com",
        "filter_subject": "Sujet à filtrer"
    }
    """
    trigger = EmailReceivedTrigger()
    result = trigger.execute(configuration=config, context={}, test_mode=False)
    return result
