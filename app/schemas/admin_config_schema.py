from pydantic import BaseModel
from typing import Optional


class UpdateAISettingsRequest(BaseModel):
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    temperature: Optional[float] = None
    system_prompt: Optional[str] = None


class UpdateVoiceSettingsRequest(BaseModel):
    voice_mode: Optional[str] = None
    stt_provider: Optional[str] = None
    stt_model: Optional[str] = None
    tts_provider: Optional[str] = None
    tts_model: Optional[str] = None
    voice_id: Optional[str] = None
    language: Optional[str] = None


class UpdatePhoneSettingsRequest(BaseModel):
    phone_provider: Optional[str] = None
    twilio_processing_mode: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    webhook_url: Optional[str] = None


class UpdateFeatureFlagsRequest(BaseModel):
    enable_text_chat: Optional[bool] = None
    enable_voice_chat: Optional[bool] = None
    enable_phone_calling: Optional[bool] = None
    enable_realtime_streaming: Optional[bool] = None
    enable_human_handoff: Optional[bool] = None
    enable_call_recording: Optional[bool] = None
