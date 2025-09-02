import imaplib
import json
import base64

def generate_oauth2_string(email, access_token):
    auth_string = f"user={email}\1auth=Bearer {access_token}\1\1"
    return base64.b64encode(auth_string.encode())

imap_server = "imap.gmail.com"

with open("user_info.json", "r") as f:
    data = json.load(f)

email_add = data["email"]
access_token = data["access_token"]

imap = imaplib.IMAP4_SSL(imap_server)

auth_string = generate_oauth2_string(email_add, access_token)

imap.authenticate('XOAUTH2', lambda x: auth_string)

imap.select("INBOX")

status, msgnums = imap.search(None, "ALL")

for num in msgnums[0].split():
    status, data = imap.fetch(num, "(RFC822)")
    message = email_add.message_from_bytes(data[0][1])
    # Traite ton message ici

imap.close()
imap.logout()
