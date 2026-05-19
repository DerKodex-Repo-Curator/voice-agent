def estimate_tokens(text: str | None) -> int:
    if not text:
        return 0

    # Simple estimate: roughly 4 characters per token.
    return max(1, round(len(text) / 4))


def estimate_audio_seconds_from_upload_info(audio_upload_info: dict | None) -> float:
    if not audio_upload_info:
        return 0.0

    size_bytes = audio_upload_info.get("size_bytes") or 0

    # Rough local estimate only. Real duration should later come from ffprobe/pydub.
    # For compressed speech audio, this gives demo-friendly approximate duration.
    estimated_seconds = size_bytes / 16000

    return round(max(1.0, estimated_seconds), 2)


def estimate_voice_request_cost(
    *,
    stt_provider: str,
    llm_provider: str,
    tts_provider: str,
    llm_model: str | None,
    transcript: str,
    assistant_text: str,
    audio_upload_info: dict | None = None,
):
    input_tokens = estimate_tokens(transcript)
    output_tokens = estimate_tokens(assistant_text)
    tts_characters = len(assistant_text or "")
    audio_seconds = estimate_audio_seconds_from_upload_info(audio_upload_info)

    # Demo-friendly configurable-style baseline rates.
    # These are approximate placeholders, not exact vendor billing.
    stt_cost = 0.0001 * audio_seconds
    llm_cost = 0.0000015 * input_tokens + 0.000004 * output_tokens
    tts_cost = 0.00003 * (tts_characters / 100)

    total = stt_cost + llm_cost + tts_cost

    return {
        "currency": "USD",
        "note": "Approximate demo estimate only. Not exact vendor billing.",
        "stt_provider": stt_provider,
        "llm_provider": llm_provider,
        "llm_model": llm_model,
        "tts_provider": tts_provider,
        "estimated_audio_seconds": audio_seconds,
        "estimated_input_tokens": input_tokens,
        "estimated_output_tokens": output_tokens,
        "estimated_tts_characters": tts_characters,
        "estimated_stt_cost_usd": round(stt_cost, 6),
        "estimated_llm_cost_usd": round(llm_cost, 6),
        "estimated_tts_cost_usd": round(tts_cost, 6),
        "estimated_total_cost_usd": round(total, 6),
    }
