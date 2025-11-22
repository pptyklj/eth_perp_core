import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from typing import List


def send_email(
    host: str,
    port: int,
    sender: str,
    receivers: List[str],
    subject_prefix: str,
    auth_env: str,
    content: str,
    use_ssl: bool = True,
):
    password = os.getenv(auth_env)
    if password is None:
        raise RuntimeError(f"Missing SMTP auth env: {auth_env}")

    msg = MIMEText(content, "markdown", "utf-8")
    msg["From"] = sender
    msg["To"] = ",".join(receivers)
    msg["Subject"] = Header(f"{subject_prefix} Signal Update", "utf-8")

    if use_ssl:
        with smtplib.SMTP_SSL(host, port) as smtp:  # pragma: no cover - network
            smtp.login(sender, password)
            smtp.sendmail(sender, receivers, msg.as_string())
    else:  # pragma: no cover - network
        with smtplib.SMTP(host, port) as smtp:
            smtp.starttls()
            smtp.login(sender, password)
            smtp.sendmail(sender, receivers, msg.as_string())
