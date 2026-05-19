import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    JSON,
    Float,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    industry = Column(String(100), nullable=True)
    use_case = Column(String(100), nullable=True)
    status = Column(String(50), default="active")
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CompanyAISettings(Base):
    __tablename__ = "company_ai_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    llm_provider = Column(String(50), default="openai")
    llm_model = Column(String(100), default="gpt-4o")
    temperature = Column(Float, default=0.7)
    system_prompt = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CompanyVoiceSettings(Base):
    __tablename__ = "company_voice_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    voice_mode = Column(String(50), default="batch")  # batch or realtime

    stt_provider = Column(String(50), default="openai")
    stt_model = Column(String(100), default="whisper-1")

    tts_provider = Column(String(50), default="openai")
    tts_model = Column(String(100), default="tts-1")
    voice_id = Column(String(100), default="alloy")

    language = Column(String(20), default="en")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CompanyPhoneSettings(Base):
    __tablename__ = "company_phone_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    phone_provider = Column(String(50), default="none")  # none, twilio
    twilio_processing_mode = Column(String(50), default="batch")  # batch or stream
    twilio_phone_number = Column(String(50), nullable=True)
    webhook_url = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CompanyFeatureFlags(Base):
    __tablename__ = "company_feature_flags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    enable_text_chat = Column(Boolean, default=True)
    enable_voice_chat = Column(Boolean, default=True)
    enable_phone_calling = Column(Boolean, default=False)
    enable_realtime_streaming = Column(Boolean, default=False)
    enable_human_handoff = Column(Boolean, default=False)
    enable_call_recording = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Persona(Base):
    __tablename__ = "personas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    name = Column(String(100), nullable=False)
    system_prompt = Column(Text, nullable=False)

    voice = Column(String(50), default="alloy")
    model = Column(String(100), default="gpt-4o")
    temperature = Column(String(20), default="0.7")

    config = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    persona_id = Column(UUID(as_uuid=True), ForeignKey("personas.id"), nullable=False)

    channel = Column(String(50), nullable=False)
    status = Column(String(50), default="active")
    metadata_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("conversation_sessions.id"), nullable=False)

    role = Column(String(30), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(30), default="text")
    metadata_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
