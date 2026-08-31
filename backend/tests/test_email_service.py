import unittest
from unittest.mock import MagicMock, patch

from app.services.email_service import EmailService


class EmailServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = EmailService()

    @patch("app.services.email_service.smtplib.SMTP")
    def test_send_email_uses_configured_smtp(self, mock_smtp_class) -> None:
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp

        self.service.send_email(
            recipient="recipient@example.com",
            subject="Test Email",
            text_body="This is a test email.",
        )

        mock_smtp_class.assert_called_once_with(
            self.service.host,
            self.service.port,
            timeout=10,
        )

        mock_smtp.ehlo.assert_called()

        mock_smtp.starttls.assert_called_once()

        mock_smtp.login.assert_called_once_with(
            self.service.username,
            self.service.password,
        )

        mock_smtp.send_message.assert_called_once()

    @patch("app.services.email_service.EmailService.send_email")
    def test_verification_email_uses_expected_content(
        self,
        mock_send_email,
    ) -> None:
        verification_url = (
            "http://localhost:5173/verify-email?token=test-token"
        )

        self.service.send_verification_email(
            recipient="recipient@example.com",
            verification_url=verification_url,
        )

        mock_send_email.assert_called_once()

        call_kwargs = mock_send_email.call_args.kwargs

        self.assertEqual(
            call_kwargs["recipient"],
            "recipient@example.com",
        )

        self.assertIn(
            "Verify your CleverCrest AI email address",
            call_kwargs["subject"],
        )

        self.assertIn(
            verification_url,
            call_kwargs["text_body"],
        )

        self.assertIn(
            verification_url,
            call_kwargs["html_body"],
        )

    @patch("app.services.email_service.EmailService.send_email")
    def test_password_reset_email_uses_expected_content(
        self,
        mock_send_email,
    ) -> None:
        reset_url = (
            "http://localhost:5173/reset-password?token=test-token"
        )

        self.service.send_password_reset_email(
            recipient="recipient@example.com",
            reset_url=reset_url,
        )

        call_kwargs = mock_send_email.call_args.kwargs

        self.assertEqual(
            call_kwargs["recipient"],
            "recipient@example.com",
        )

        self.assertIn(
            reset_url,
            call_kwargs["text_body"],
        )

    @patch("app.services.email_service.EmailService.send_email")
    def test_invitation_email_uses_expected_content(
        self,
        mock_send_email,
    ) -> None:
        invitation_url = (
            "http://localhost:5173/invitations/accept?token=test-token"
        )

        self.service.send_invitation_email(
            recipient="recipient@example.com",
            organization_name="CleverCrest Demo",
            invitation_url=invitation_url,
        )

        call_kwargs = mock_send_email.call_args.kwargs

        self.assertEqual(
            call_kwargs["recipient"],
            "recipient@example.com",
        )

        self.assertIn(
            "CleverCrest Demo",
            call_kwargs["text_body"],
        )

        self.assertIn(
            invitation_url,
            call_kwargs["text_body"],
        )


if __name__ == "__main__":
    unittest.main()