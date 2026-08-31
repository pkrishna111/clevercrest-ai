from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    VerifyEmailResponse,
)
from app.services.auth_service import (
    EmailAlreadyRegisteredError,
    EmailNotVerifiedError,
    EmailVerificationError,
    InactiveUserError,
    InvalidCredentialsError,
    SuspendedUserError,
    login_user,
    register_user,
    verify_email,
)
from app.services.email_service import EmailServiceError, email_service


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
) -> RegisterResponse:
    try:
        registration = register_user(
            db,
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            organization_name=request.organization_name,
        )

    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    verification_token = quote(
        registration.verification_token,
        safe="",
    )

    verification_url = (
        f"{settings.frontend_url.rstrip('/')}"
        f"/verify-email?token={verification_token}"
    )

    try:
        email_service.send_verification_email(
            recipient=registration.user.email,
            verification_url=verification_url,
        )
    except EmailServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Your account was created, but the verification email "
                "could not be sent. Please try again later."
            ),
        ) from exc

    return RegisterResponse(
        message=(
            "Registration successful. "
            "Please check your email to verify your account."
        ),
    )

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> LoginResponse:
    try:
        login_result = login_user(
            db,
            email=request.email,
            password=request.password,
        )

    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    except EmailNotVerifiedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except InactiveUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except SuspendedUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    response.set_cookie(
        key=settings.auth_cookie_name,
        value=login_result.access_token,
        max_age=settings.jwt_access_token_expire_minutes * 60,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
    )

    return LoginResponse(
        message="Login successful.",
    )

@router.get(
    "/verify-email",
    response_model=VerifyEmailResponse,
)
def verify_email_address(
    token: str,
    db: Session = Depends(get_db),
) -> VerifyEmailResponse:
    try:
        verify_email(
            db,
            raw_token=token,
        )
    except EmailVerificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return VerifyEmailResponse(
        message="Email address verified successfully.",
    )