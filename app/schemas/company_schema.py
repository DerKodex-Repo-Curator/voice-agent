from pydantic import BaseModel, Field
from typing import Optional


class AISettingsRequest(BaseModel):
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    temperature: float = 0.7
    system_prompt: str = "You are a helpful voice assistant."


class VoiceSettingsRequest(BaseModel):
    voice_mode: str = "batch"
    stt_provider: str = "openai"
    stt_model: str = "whisper-1"
    tts_provider: str = "openai"
    tts_model: str = "tts-1"
    voice_id: str = "alloy"
    language: str = "en"


class PhoneSettingsRequest(BaseModel):
    phone_provider: str = "none"
    twilio_processing_mode: str = "batch"
    twilio_phone_number: Optional[str] = None
    webhook_url: Optional[str] = None


class FeatureFlagsRequest(BaseModel):
    enable_text_chat: bool = True
    enable_voice_chat: bool = True
    enable_phone_calling: bool = False
    enable_realtime_streaming: bool = False
    enable_human_handoff: bool = False
    enable_call_recording: bool = False


class CompanySetupRequest(BaseModel):
    name: str = Field(..., examples=["ABC Insurance"])
    industry: Optional[str] = Field(default=None, examples=["Insurance"])
    use_case: Optional[str] = Field(default=None, examples=["claims_support"])
    status: str = "active"

    default_persona_name: str = "General Assistant"

    ai_settings: AISettingsRequest = AISettingsRequest()
    voice_settings: VoiceSettingsRequest = VoiceSettingsRequest()
    phone_settings: PhoneSettingsRequest = PhoneSettingsRequest()
    feature_flags: FeatureFlagsRequest = FeatureFlagsRequest()
