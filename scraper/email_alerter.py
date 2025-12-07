import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_alert(receiver_email, subject, body):
    """
    Wysyła powiadomienie email przy użyciu serwera SMTP.

    Args:
        receiver_email (str): Adres email odbiorcy.
        subject (str): Temat wiadomości.
        body (str): Treść wiadomości.
    """
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Błąd: Plik konfiguracyjny 'config.json' nie został znaleziony.")
        return

    smtp_server = config.get("smtp_server")
    port = config.get("smtp_port")
    sender_email = config.get("sender_email")
    password = config.get("email_password")

    if not all([sender_email, password, smtp_server, port]):
        print("Błąd: Brak pełnej konfiguracji email w pliku 'config.json'. Wymagane są: smtp_server, smtp_port, sender_email, email_password.")
        return

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()  # Szyfrowanie połączenia
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"Email został pomyślnie wysłany na adres: {receiver_email}")
    except Exception as e:
        print(f"Nie udało się wysłać emaila: {e}")
