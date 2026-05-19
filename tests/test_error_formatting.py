from fastapi import HTTPException

from app.services.error_formatting import (
    build_provider_error_detail,
    extract_error_message,
)


def test_extract_error_message_from_string():
    assert extract_error_message("simple error") == "simple error"


def test_extract_error_message_from_http_exception():
    error = HTTPException(status_code=400, detail={"message": "bad input"})
    message = extract_error_message(error)

    assert "bad input" in message


def test_cartesia_error_has_suggestion():
    detail = build_provider_error_detail(
        stage="tts",
        provider="cartesia",
        error="voice ID invalid",
        route="/voice/configured-batch",
    )

    assert detail["stage"] == "tts"
    assert detail["provider"] == "cartesia"
    assert "voice ID invalid" in detail["message"]
    assert "CARTESIA_VOICE_ID" in detail["suggestion"]
    assert detail["route"] == "/voice/configured-batch"
