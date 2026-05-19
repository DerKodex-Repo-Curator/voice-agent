from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str
    redis_url: str | None = None

    # MongoDB
    use_mongodb: bool = False
    mongodb_url: str | None = None
    mongodb_database: str | None = None
    mongodb_conversations_collection: str | None = None
    mongodb_events_collection: str = "events"

    # AI Providers
    openai_api_key: str | None = None
    elevenlabs_voice_id: str = "JBFqnCBsd6RMkjVDRZzb"
    elevenlabs_model_id: str = "eleven_multilingual_v2"
    elevenlabs_stt_model_id: str = "scribe_v2"
    elevenlabs_output_format: str = "mp3_44100_128"
    deepgram_api_key: str | None = None
    deepgram_stt_model: str = "nova-3"
    deepgram_tts_model: str = "aura-2-thalia-en"
    deepgram_language: str = "en"

    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openrouter/free"
    huggingface_provider: str = "auto"
    huggingface_model_id: str = "meta-llama/Llama-3.1-8B-Instruct"
    huggingface_max_tokens: int = 300
    anthropic_api_key: str | None = None
    anthropic_model_id: str = "claude-sonnet-4-6"
    anthropic_max_tokens: int = 500
    google_api_key: str | None = None
    gemini_api_key: str | None = None
    gemini_model_id: str = "gemini-2.5-flash"
    gemini_max_tokens: int = 500
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_default_region: str = "us-east-2"
    aws_bedrock_model_id: str | None = None
    aws_bedrock_max_tokens: int = 500
    aws_polly_voice_id: str = "Joanna"
    aws_polly_engine: str = "neural"
    aws_polly_output_format: str = "mp3"
    azure_speech_key: str | None = None
    azure_speech_region: str = "eastus2"
    azure_speech_language: str = "en-US"
    azure_speech_voice_name: str = "en-US-JennyNeural"
    cartesia_api_key: str | None = None
    cartesia_model_id: str = "sonic-3"
    cartesia_voice_id: str | None = None
    cartesia_language: str = "en"
    cartesia_output_format: str = "mp3"
    cartesia_version: str = "2026-03-01"
    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_api_version: str = "2024-12-01-preview"
    azure_openai_deployment_name: str | None = None
    azure_openai_max_tokens: int = 500
    ollama_base_url: str = "http://localhost:11434"
    ollama_model_id: str = "llama3.2:1b"
    ollama_max_tokens: int = 300

    elevenlabs_api_key: str | None = None
    huggingface_api_key: str | None = None
    hf_token: str | None = None

    # Cloud Voice Defaults
    voice_mode: str = "batch"
    voice_model: str = "whisper-1"
    tts_model: str = "tts-1"
    inference_model: str = "gpt-4o"

    realtime_model: str = "gpt-realtime"
    realtime_voice: str = "marin"
    tts_provider: str = "openai"

    # OpenAI Batch Voice
    openai_stt_model: str = "whisper-1"
    openai_tts_model: str = "tts-1"
    openai_tts_voice: str = "alloy"
    openai_tts_format: str = "mp3"

    # Local Voice
    local_stt_provider: str = "whisper_cpp"
    whisper_cpp_bin: str = "/opt/homebrew/bin/whisper-cli"
    whisper_model_path: str | None = None

    local_tts_provider: str = "mac_say"
    local_tts_voice: str = "Samantha"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 4002
    debug: bool = True
    reload: bool = True

    # Twilio
    twilio_webhook_base_url: str | None = None
    twilio_auth_token: str | None = None
    twilio_validate_signatures: bool = False
    twilio_processing_mode: str = "batch"
    store_twilio_credentials_in_db: bool = True

    # Security
    secret_key: str
    admin_api_key: str | None = None
    company_api_keys: str | None = None
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Defaults
    default_company_id: str = "default"
    default_persona_id: str = "general-assistant"
    default_language: str = "en"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
