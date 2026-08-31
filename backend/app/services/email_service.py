import html
import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import settings


class EmailServiceError(Exception):
    """Raised when an email cannot be sent."""


class EmailService:
    def __init__(self) -> None:
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.username = settings.smtp_username
        self.password = settings.smtp_password
        self.use_tls = settings.smtp_use_tls
        self.email_from = settings.email_from

    def send_email(
        self,
        *,
        recipient: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None:
        message = EmailMessage()

        message["From"] = self.email_from
        message["To"] = recipient
        message["Subject"] = subject

        message.set_content(text_body)

        if html_body is not None:
            message.add_alternative(html_body, subtype="html")

        try:
            with smtplib.SMTP(
                self.host,
                self.port,
                timeout=10,
            ) as smtp:
                smtp.ehlo()

                if self.use_tls:
                    tls_context = ssl.create_default_context()
                    smtp.starttls(context=tls_context)
                    smtp.ehlo()

                smtp.login(
                    self.username,
                    self.password,
                )

                smtp.send_message(message)

        except (smtplib.SMTPException, OSError) as exc:
            raise EmailServiceError(
                "Unable to send email through the configured SMTP server."
            ) from exc

    def send_verification_email(
        self,
        *,
        recipient: str,
        verification_url: str,
    ) -> None:
        subject = "Verify your CleverCrest AI email address"

        text_body = (
            "Welcome to CleverCrest AI.\n\n"
            "Please verify your email address by opening the link below:\n\n"
            f"{verification_url}\n\n"
            "This verification link expires in "
            f"{settings.email_verification_token_expire_hours} hours.\n\n"
            "If you did not create this account, you can safely ignore "
            "this email."
        )

        safe_url = html.escape(verification_url, quote=True)

        html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Verify your CleverCrest AI email</title>
</head>
<body>
    <h2>Welcome to CleverCrest AI</h2>

    <p>
        Please verify your email address by clicking the button below.
    </p>

    <p>
        <a href="{safe_url}">
            Verify Email Address
        </a>
    </p>

    <p>
        This verification link expires in
        {settings.email_verification_token_expire_hours} hours.
    </p>

    <p>
        If you did not create this account, you can safely ignore
        this email.
    </p>
</body>
</html>
"""

        self.send_email(
            recipient=recipient,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
        )

    def send_password_reset_email(
        self,
        *,
        recipient: str,
        reset_url: str,
    ) -> None:
        subject = "Reset your CleverCrest AI password"

        text_body = (
            "A password reset was requested for your CleverCrest AI account.\n\n"
            "Open the link below to reset your password:\n\n"
            f"{reset_url}\n\n"
            "This password reset link expires in "
            f"{settings.password_reset_token_expire_minutes} minutes.\n\n"
            "If you did not request a password reset, you can safely ignore "
            "this email."
        )

        safe_url = html.escape(reset_url, quote=True)

        html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Reset your CleverCrest AI password</title>
</head>
<body>
    <h2>Password Reset</h2>

    <p>
        A password reset was requested for your CleverCrest AI account.
    </p>

    <p>
        <a href="{safe_url}">
            Reset Password
        </a>
    </p>

    <p>
        This password reset link expires in
        {settings.password_reset_token_expire_minutes} minutes.
    </p>

    <p>
        If you did not request a password reset, you can safely ignore
        this email.
    </p>
</body>
</html>
"""

        self.send_email(
            recipient=recipient,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
        )

    def send_invitation_email(
        self,
        *,
        recipient: str,
        organization_name: str,
        invitation_url: str,
    ) -> None:
        subject = f"Invitation to join {organization_name} on CleverCrest AI"

        text_body = (
            f"You have been invited to join {organization_name} "
            "on CleverCrest AI.\n\n"
            "Open the link below to review and accept the invitation:\n\n"
            f"{invitation_url}\n\n"
            "This invitation expires in "
            f"{settings.invitation_token_expire_days} days.\n\n"
            "If you were not expecting this invitation, you can safely "
            "ignore this email."
        )

        safe_url = html.escape(invitation_url, quote=True)
        safe_organization_name = html.escape(organization_name)

        html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CleverCrest AI Invitation</title>
</head>
<body>
    <h2>You're invited to CleverCrest AI</h2>

    <p>
        You have been invited to join
        <strong>{safe_organization_name}</strong>
        on CleverCrest AI.
    </p>

    <p>
        <a href="{safe_url}">
            Review Invitation
        </a>
    </p>

    <p>
        This invitation expires in
        {settings.invitation_token_expire_days} days.
    </p>

    <p>
        If you were not expecting this invitation, you can safely
        ignore this email.
    </p>
</body>
</html>
"""

        self.send_email(
            recipient=recipient,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
        )


email_service = EmailService()