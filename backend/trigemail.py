# trigemail/email_trigger_node.py
import threading
from typing import Dict, Any
from imapclient import IMAPClient
from base import BaseNode
import email
from config import get_session as SessionLocal
from models import Email

class EmailReceivedTrigger(BaseNode):
    """Nœud déclencheur LCNC qui surveille les emails via IMAP et les sauvegarde en DB."""

    def execute(self, configuration: Dict[str, Any], context: Dict[str, Any], test_mode: bool = False) -> Any:
        if test_mode:
            return {
                "status": "test_mode",
                "email_data": {
                    "from": "test@example.com",
                    "subject": "Email de test",
                    "body": "Ceci est un email simulé",
                    "attachments": []
                }
            }

        email_address = configuration.get("email_address")
        password_or_token = configuration.get("password")
        imap_server = configuration.get("imap_server", "imap.gmail.com")
        filter_sender = configuration.get("filter_sender")
        filter_subject = configuration.get("filter_subject")

        if not email_address or not password_or_token:
            raise ValueError("Adresse email et token requis")

        thread = threading.Thread(
            target=self._imap_listener,
            args=(email_address, password_or_token, imap_server, filter_sender, filter_subject),
            daemon=True
        )
        thread.start()
        return {"status": "listener_started"}

    def _imap_listener(self, email_address, password_or_token, imap_server, filter_sender, filter_subject):
        with IMAPClient(imap_server) as server:
            server.oauth2_login(email_address, password_or_token)
            server.select_folder("INBOX")
            print(f"✅ IMAP listener démarré pour {email_address}")

            while True:
                server.idle()
                responses = server.idle_check(timeout=60)
                server.idle_done()
                if responses:
                    for msgid in server.search(['UNSEEN']):
                        raw_message = server.fetch([msgid], ['RFC822'])[msgid][b'RFC822']
                        msg = email.message_from_bytes(raw_message)
                        self._process_email(msg, filter_sender, filter_subject)

    def _process_email(self, msg, filter_sender, filter_subject):
        # Décodage sujet et expéditeur
        subject = email.header.decode_header(msg['Subject'])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
        sender = msg['From']

        # Filtrage
        if filter_sender and filter_sender.lower() not in sender.lower():
            return
        if filter_subject and filter_subject.lower() not in subject.lower():
            return

        # Corps et pièces jointes
        body = ""
        attachments = []
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_payload(decode=True).decode()
                elif "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            "filename": filename,
                            "content_type": content_type,
                            "data": part.get_payload(decode=True)
                        })
        else:
            body = msg.get_payload(decode=True).decode()

        print(f"📩 Email reçu de {sender} | Sujet: {subject}")
        print(f"📄 Corps: {body[:50]}... | Attachments: {len(attachments)}")

        # Sauvegarde en DB
        db = SessionLocal()
        try:
            email_obj = Email(
                sender=sender,
                subject=subject,
                body=body,
                attachments=[att["filename"] for att in attachments]
            )
            db.add(email_obj)
            db.commit()
            db.refresh(email_obj)
            print(f"✅ Email sauvegardé en DB: {email_obj.id}")
        except Exception as e:
            db.rollback()
            print(f"❌ Erreur lors de la sauvegarde: {e}")
        finally:
            db.close()
