from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_organization_membership
from app.db.session import get_db
from app.models.organization import Organization
from app.models.organization_membership import (
    OrganizationMembership,
    OrganizationMembershipRole,
)
from app.schemas.organization import OrganizationResponse, OrganizationUpdateRequest


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def get_organization(
    current_membership: OrganizationMembership = Depends(
        get_current_organization_membership
    ),
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    organization = db.get(Organization, current_membership.organization_id)

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    return OrganizationResponse(
        id=str(organization.id),
        name=organization.name,
        slug=organization.slug,
        description=organization.description,
        logo_url=organization.logo_url,
        status=organization.status.value,
        created_at=organization.created_at,
        updated_at=organization.updated_at,
    )


@router.patch(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def update_organization(
    update_request: OrganizationUpdateRequest,
    current_membership: OrganizationMembership = Depends(
        get_current_organization_membership
    ),
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    if current_membership.role not in (
        OrganizationMembershipRole.OWNER,
        OrganizationMembershipRole.ADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this organization.",
        )

    if not update_request.model_fields_set:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="At least one field must be provided for update.",
        )

    if "name" in update_request.model_fields_set and update_request.name is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Organization name cannot be null.",
        )

    organization = db.get(Organization, current_membership.organization_id)

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    if "name" in update_request.model_fields_set:
        organization.name = update_request.name
    if "description" in update_request.model_fields_set:
        organization.description = update_request.description
    if "logo_url" in update_request.model_fields_set:
        organization.logo_url = update_request.logo_url

    db.commit()
    db.refresh(organization)

    return OrganizationResponse(
        id=str(organization.id),
        name=organization.name,
        slug=organization.slug,
        description=organization.description,
        logo_url=organization.logo_url,
        status=organization.status.value,
        created_at=organization.created_at,
        updated_at=organization.updated_at,
    )
