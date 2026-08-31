import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.core.tokens import generate_token, hash_token
from app.models.email_verification_token import EmailVerificationToken
from app.models.organization import Organization
from app.models.organization_membership import (
    OrganizationMembership,
    OrganizationMembershipRole,
    OrganizationMembershipStatus,
)
from app.models.user import User, UserStatus



class RegistrationError(Exception):
    """Base exception for registration failures."""


class EmailAlreadyRegisteredError(RegistrationError):
    """Raised when an email address is already registered."""

class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""


class EmailNotVerifiedError(Exception):
    """Raised when a user tries to log in before verifying their email."""


class InactiveUserError(Exception):
    """Raised when an inactive user tries to log in."""


class SuspendedUserError(Exception):
    """Raised when a suspended user tries to log in."""

class EmailVerificationError(Exception):
    """Raised when an email verification token is invalid or expired."""


@dataclass(frozen=True)
class RegistrationResult:
    user: User
    organization: Organization
    verification_token: str

@dataclass(frozen=True)
class LoginResult:
    user: User
    access_token: str


def normalize_email(email: str) -> str:
    return email.strip().lower()


def create_base_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_value = ascii_value.lower()

    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value)
    slug = slug.strip("-")

    return slug or "organization"


def generate_unique_organization_slug(
    db: Session,
    organization_name: str,
) -> str:
    base_slug = create_base_slug(organization_name)

    candidate = base_slug
    suffix = 2

    while True:
        existing = db.scalar(
            select(Organization.id).where(
                Organization.slug == candidate,
            )
        )

        if existing is None:
            return candidate

        candidate = f"{base_slug}-{suffix}"
        suffix += 1


def register_user(
    db: Session,
    *,
    email: str,
    password: str,
    first_name: str,
    last_name: str | None,
    organization_name: str,
) -> RegistrationResult:
    normalized_email = normalize_email(email)

    existing_user = db.scalar(
        select(User).where(
            User.email == normalized_email,
        )
    )

    if existing_user is not None:
        raise EmailAlreadyRegisteredError(
            "An account with this email already exists."
        )

    organization_slug = generate_unique_organization_slug(
        db,
        organization_name,
    )

    organization = Organization(
        name=organization_name,
        slug=organization_slug,
        settings={},
    )

    user = User(
        email=normalized_email,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        is_email_verified=False,
    )

    db.add(organization)
    db.add(user)

    db.flush()

    membership = OrganizationMembership(
        user_id=user.id,
        organization_id=organization.id,
        role=OrganizationMembershipRole.OWNER,
        status=OrganizationMembershipStatus.ACTIVE,
    )

    raw_verification_token = generate_token()

    verification_token = EmailVerificationToken(
        user_id=user.id,
        token_hash=hash_token(raw_verification_token),
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(
                hours=settings.email_verification_token_expire_hours,
            )
        ),
    )

    db.add(membership)
    db.add(verification_token)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()

        raise RegistrationError(
            "Registration could not be completed."
        ) from exc
    except Exception:
        db.rollback()
        raise

    db.refresh(user)
    db.refresh(organization)

    return RegistrationResult(
        user=user,
        organization=organization,
        verification_token=raw_verification_token,
    )

def login_user(
    db: Session,
    *,
    email: str,
    password: str,
) -> LoginResult:
    normalized_email = normalize_email(email)

    user = db.scalar(
        select(User).where(
            User.email == normalized_email,
        )
    )

    if user is None or user.password_hash is None:
        raise InvalidCredentialsError(
            "Invalid email or password."
        )

    if not verify_password(
        password,
        user.password_hash,
    ):
        raise InvalidCredentialsError(
            "Invalid email or password."
        )

    if not user.is_email_verified:
        raise EmailNotVerifiedError(
            "Please verify your email before signing in."
        )

    if user.status == UserStatus.INACTIVE:
        raise InactiveUserError(
            "This account is inactive."
        )

    if user.status == UserStatus.SUSPENDED:
        raise SuspendedUserError(
            "This account is suspended."
        )

    user.last_login_at = datetime.now(timezone.utc)

    access_token = create_access_token(user.id)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(user)

    return LoginResult(
        user=user,
        access_token=access_token,
    )

def verify_email(
    db: Session,
    *,
    raw_token: str,
) -> None:
    token_hash = hash_token(raw_token)
    now = datetime.now(timezone.utc)

    verification_token = db.scalar(
        select(EmailVerificationToken)
        .where(
            EmailVerificationToken.token_hash == token_hash,
        )
        .with_for_update()
    )

    if verification_token is None:
        raise EmailVerificationError(
            "Invalid or expired email verification link."
        )

    if verification_token.used_at is not None:
        raise EmailVerificationError(
            "Invalid or expired email verification link."
        )

    if verification_token.expires_at <= now:
        raise EmailVerificationError(
            "Invalid or expired email verification link."
        )

    user = db.get(User, verification_token.user_id)

    if user is None:
        raise EmailVerificationError(
            "Invalid or expired email verification link."
        )

    user.is_email_verified = True
    verification_token.used_at = now

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise