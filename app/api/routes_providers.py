from fastapi import APIRouter

router = APIRouter()


@router.get("/llm")
async def get_llm_provider_options():
    return {
        "providers": [
            {
                "provider": "openrouter",
                "label": "OpenRouter",
                "models": [
                    "openrouter/free",
                    "meta-llama/llama-3.2-3b-instruct:free"
                ],
                "notes": "Useful for free or low-cost model routing."
            },
            {
                "provider": "openai",
                "label": "OpenAI",
                "models": [
                    "gpt-4o",
                    "gpt-4o-mini"
                ],
                "notes": "Use when OpenAI API billing is enabled."
            }
        ]
    }


@router.get("/voice")
async def get_voice_provider_options():
    return {
        "stt_providers": [
            {
                "provider": "browser",
                "label": "Browser Speech Recognition",
                "notes": "Free browser-based speech-to-text for demo use."
            },
            {
                "provider": "openai",
                "label": "OpenAI Whisper / Transcribe",
                "models": [
                    "whisper-1",
                    "gpt-4o-transcribe",
                    "gpt-4o-mini-transcribe"
                ]
            }
        ],
        "tts_providers": [
            {
                "provider": "browser",
                "label": "Browser Speech Synthesis",
                "notes": "Free browser-based text-to-speech for demo use."
            },
            {
                "provider": "openai",
                "label": "OpenAI TTS",
                "models": [
                    "tts-1",
                    "tts-1-hd",
                    "gpt-4o-mini-tts"
                ]
            },
            {
                "provider": "elevenlabs",
                "label": "ElevenLabs",
                "models": [
                    "eleven_multilingual_v2"
                ]
            }
        ]
    }
