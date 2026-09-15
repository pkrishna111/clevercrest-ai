from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_organization_membership
from app.db.session import get_db
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.schemas.organization import OrganizationResponse


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
