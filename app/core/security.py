import json
import secrets
from uuid import UUID

from fastapi import Header, HTTPException, Request

from twilio.request_validator import RequestValidator

from app.core.config import settings


async def require_admin_api_key(
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key"),
):
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=500,
            detail="ADMIN_API_KEY is not configured on the server",
        )

    if not x_admin_api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing X-Admin-API-Key header",
        )

    if not secrets.compare_digest(x_admin_api_key, settings.admin_api_key):
        raise HTTPException(
            status_code=403,
            detail="Invalid admin API key",
        )

    return True


def get_company_api_key_map() -> dict:
    if not settings.company_api_keys:
        raise HTTPException(
            status_code=500,
            detail="COMPANY_API_KEYS is not configured on the server",
        )

    try:
        return json.loads(settings.company_api_keys)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="COMPANY_API_KEYS is not valid JSON",
        )


def require_company_api_key(
    company_id: UUID | str,
    x_company_api_key: str | None,
):
    if not x_company_api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing X-Company-API-Key header",
        )

    company_key_map = get_company_api_key_map()
    company_id_str = str(company_id)

    expected_key = company_key_map.get(company_id_str)

    if not expected_key:
        raise HTTPException(
            status_code=403,
            detail="No API key configured for this company",
        )

    if not secrets.compare_digest(x_company_api_key, expected_key):
        raise HTTPException(
            status_code=403,
            detail="Invalid company API key",
        )

    return True



async def require_twilio_signature(
    request: Request,
    x_twilio_signature: str | None = Header(default=None, alias="X-Twilio-Signature"),
):
    if not settings.twilio_validate_signatures:
        return True

    if not settings.twilio_auth_token:
        raise HTTPException(
            status_code=500,
            detail="TWILIO_AUTH_TOKEN is not configured on the server",
        )

    if not x_twilio_signature:
        raise HTTPException(
            status_code=401,
            detail="Missing X-Twilio-Signature header",
        )

    base_url = (
        settings.twilio_webhook_base_url.rstrip("/")
        if settings.twilio_webhook_base_url
        else str(request.base_url).rstrip("/")
    )

    validation_url = f"{base_url}{request.url.path}"

    if request.url.query:
        validation_url = f"{validation_url}?{request.url.query}"

    form = await request.form()
    params = dict(form)

    validator = RequestValidator(settings.twilio_auth_token)

    is_valid = validator.validate(
        validation_url,
        params,
        x_twilio_signature,
    )

    if not is_valid:
        raise HTTPException(
            status_code=403,
            detail="Invalid Twilio signature",
        )

    return True
