from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.models.user import User
from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth import (
    CurrentUserResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    VerifyEmailResponse,
)
from app.services.auth_service import (
    EmailAlreadyRegisteredError,
    EmailNotVerifiedError,
    EmailVerificationError,
    InactiveUserError,
    InvalidCredentialsError,
    PasswordResetError,
    SuspendedUserError,
    login_user,
    register_user,
    request_password_reset,
    reset_password,
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
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    status_code=status.HTTP_200_OK,
)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> ForgotPasswordResponse:
    reset_request = request_password_reset(
        db,
        email=request.email,
    )

    if reset_request is not None:
        reset_token = quote(
            reset_request.reset_token,
            safe="",
        )

        reset_url = (
            f"{settings.frontend_url.rstrip('/')}"
            f"/reset-password?token={reset_token}"
        )

        try:
            email_service.send_password_reset_email(
                recipient=reset_request.user.email,
                reset_url=reset_url,
            )
        except EmailServiceError:
            pass

    return ForgotPasswordResponse(
        message=(
            "If an account exists for this email address, "
            "a password reset link has been sent."
        ),
    )

@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse,
    status_code=status.HTTP_200_OK,
)
def reset_password_endpoint(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> ResetPasswordResponse:
    try:
        reset_password(
            db,
            raw_token=request.token,
            new_password=request.password,
        )
    except PasswordResetError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ResetPasswordResponse(
        message="Password reset successfully.",
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
    "/me",
    response_model=CurrentUserResponse,
)
def get_current_user_details(
    current_user: User = Depends(get_current_user),
) -> CurrentUserResponse:
    return CurrentUserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_email_verified=current_user.is_email_verified,
        status=current_user.status.value,
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

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    response: Response,
) -> Response:
    response.delete_cookie(
        key=settings.auth_cookie_name,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
    )

    return response