import os
import builtins
from unittest import mock

from notifier.email_sender_qq import send_email


def test_send_email_uses_env_and_smtp_ssl():
    with mock.patch.dict(os.environ, {"QQ_SMTP_AUTH": "token"}):
        with mock.patch("smtplib.SMTP_SSL") as smtp_cls:
            smtp_instance = smtp_cls.return_value.__enter__.return_value
            send_email(
                host="smtp.qq.com",
                port=465,
                sender="a@qq.com",
                receivers=["b@qq.com"],
                subject_prefix="[TEST]",
                auth_env="QQ_SMTP_AUTH",
                content="hello",
            )
            smtp_instance.login.assert_called_once_with("a@qq.com", "token")
            smtp_instance.sendmail.assert_called_once()
