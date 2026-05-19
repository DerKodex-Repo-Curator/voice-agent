from app.services.cost_estimator import estimate_tokens, estimate_voice_request_cost


def test_estimate_tokens_empty_text():
    assert estimate_tokens("") == 0
    assert estimate_tokens(None) == 0


def test_estimate_tokens_basic_text():
    assert estimate_tokens("hello world") >= 1


def test_estimate_voice_request_cost_has_required_fields():
    result = estimate_voice_request_cost(
        stt_provider="deepgram",
        llm_provider="bedrock",
        llm_model="us.anthropic.claude-sonnet-4-6",
        tts_provider="cartesia",
        transcript="hello there",
        assistant_text="hello, how can I help you?",
        audio_upload_info={"size_bytes": 32000},
    )

    assert result["currency"] == "USD"
    assert result["stt_provider"] == "deepgram"
    assert result["llm_provider"] == "bedrock"
    assert result["tts_provider"] == "cartesia"
    assert result["estimated_audio_seconds"] > 0
    assert result["estimated_total_cost_usd"] >= 0
