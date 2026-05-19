# Multi-Provider AI Voice Agent Backend

A production-style **FastAPI backend** for building configurable AI voice agents.

This project supports text chat, uploaded audio voice conversations, live browser microphone recording, native speech-to-speech with OpenAI Realtime, STT → LLM → TTS voice pipelines, multi-provider routing, provider fallback, admin dashboard, MongoDB event logging, PostgreSQL conversation persistence, analytics, debugging tools, provider benchmarking, latency tracking, cost estimation, rate limiting, generated audio cleanup, smoke tests, pytest tests, and Docker Compose setup.

---

# Table of Contents

1. [Project Overview](#project-overview)
2. [Why This Project Is Useful](#why-this-project-is-useful)
3. [Core Concept](#core-concept)
4. [Voice Agent Architecture](#voice-agent-architecture)
5. [Speech-to-Speech Modes](#speech-to-speech-modes)
6. [Supported Providers](#supported-providers)
7. [Main Features](#main-features)
8. [Admin Dashboard](#admin-dashboard)
9. [Important API Routes](#important-api-routes)
10. [Local Setup](#local-setup)
11. [Environment Variables](#environment-variables)
12. [Running the Project](#running-the-project)
13. [Testing the Project](#testing-the-project)
14. [Provider Routing and Fallback](#provider-routing-and-fallback)
15. [Latency Tracking](#latency-tracking)
16. [Cost Estimate Logging](#cost-estimate-logging)
17. [Provider Benchmarking](#provider-benchmarking)
18. [Debugging and Observability](#debugging-and-observability)
19. [Generated Audio Cleanup](#generated-audio-cleanup)
20. [Security Notes](#security-notes)
21. [Recommended Demo Flow](#recommended-demo-flow)
22. [Troubleshooting Guide](#troubleshooting-guide)
23. [Final Verification Checklist](#final-verification-checklist)

---

# Project Overview

This project is a backend system for creating **AI-powered voice agents**.

The system allows a company or client to configure how their AI assistant works:

- User speaks.
- Speech-to-Text provider converts audio to text.
- LLM generates a response.
- Text-to-Speech provider converts response to audio.
- User hears the assistant reply.

Example production-style pipeline:

- Deepgram Nova-3 STT
- AWS Bedrock Claude
- Cartesia Sonic TTS
- Generated assistant audio

The project also supports **native realtime speech-to-speech** using OpenAI Realtime:

- Browser microphone
- OpenAI Realtime WebRTC
- Assistant speaks back live

---

# Why This Project Is Useful

Real-world voice agent systems need more than one API call.

A proper voice AI backend should support:

- Multiple companies or tenants
- Configurable AI providers
- Provider fallback when one service fails
- Audio upload and recording support
- Real-time and batch voice flows
- Observability and logs
- Cost tracking
- Latency tracking
- Admin dashboard
- Debug endpoints
- Production-style security controls

This project combines those into one backend.

---

# Core Concept

The project is built around three main AI stages.

## 1. STT — Speech-to-Text

STT means **Speech-to-Text**.

It converts user audio into text.

Example:

User audio:

"Can you help me schedule an appointment?"

Text output:

"Can you help me schedule an appointment?"

Current main STT provider:

Deepgram Nova-3

---

## 2. LLM — Large Language Model

The LLM receives the user’s text and generates an intelligent response.

Example input:

"Can you help me schedule an appointment?"

Example output:

"Sure, I can help with that. What date works best for you?"

Supported LLM providers include:

- AWS Bedrock
- OpenAI
- OpenRouter
- Anthropic
- Google Gemini
- Hugging Face
- Ollama local
- Azure OpenAI

---

## 3. TTS — Text-to-Speech

TTS means **Text-to-Speech**.

It converts the assistant’s text response into spoken audio.

Example:

Assistant text:

"Sure, I can help with that."

Output:

Generated MP3 audio

Current major TTS providers:

- Cartesia Sonic
- Azure Speech
- AWS Polly
- ElevenLabs
- OpenAI TTS
- Deepgram TTS
- macOS say


---

# Voice Agent Architecture

## High-Level System Flow

The system has four main layers:

1. Client Layer
2. FastAPI Backend Layer
3. Provider Router Layer
4. Storage Layer

Simple flow:

    Dashboard / Swagger / Twilio / Browser Voice
            |
            v
    FastAPI API Layer
            |
            v
    Provider Router + Fallback Router
            |
            v
    STT / LLM / TTS Providers
            |
            v
    PostgreSQL + MongoDB

---

## Detailed Architecture

Client Layer:

- Admin Dashboard
- Swagger UI
- Browser Microphone
- Uploaded Audio
- Twilio Phone Call

FastAPI Backend:

- API-key authentication
- Company configuration loading
- STT routing
- LLM routing
- TTS routing
- Fallback handling
- Error logging
- Latency tracking
- Cost estimation
- Analytics

Provider Layer:

- Deepgram Nova-3
- AWS Bedrock
- Cartesia Sonic
- Azure Speech
- OpenAI Realtime
- OpenRouter
- Ollama
- ElevenLabs
- AWS Polly

Storage Layer:

- PostgreSQL for structured sessions and messages
- MongoDB for events, errors, analytics, and benchmarks

---

# Speech-to-Speech Modes

This project supports two types of speech-to-speech.

---

## 1. Pipeline Speech-to-Speech

This is the main configured voice flow.

Flow:

    Audio
    → STT
    → LLM
    → TTS
    → Audio response

Example:

    User uploads or records audio
    → Deepgram Nova-3 transcribes it
    → Bedrock / OpenRouter / Ollama generates answer
    → Cartesia Sonic speaks the answer
    → MP3 is returned

Main API:

    POST /voice/configured-batch

This flow is easy to debug because each stage is visible.

Example response fields:

    stt_provider: deepgram
    llm_provider: bedrock
    tts_provider: cartesia
    audio_url: /demo/generated/example.mp3

---

## 2. Native Speech-to-Speech

Native speech-to-speech means the model directly handles live speech input and speech output.

Current native mode:

    OpenAI Realtime WebRTC

Flow:

    Browser microphone
    → WebRTC connection
    → OpenAI Realtime
    → Assistant speaks back live

Demo page:

    /speech-to-speech/openai-demo

This is different from the pipeline flow because it is more real-time and does not require uploading a completed audio file first.

---

# Supported Providers

## LLM Providers

| Provider | Purpose |
|---|---|
| OpenAI | General LLM responses |
| OpenRouter | Routing to multiple external models |
| Anthropic / Claude | Claude model support |
| AWS Bedrock | Enterprise cloud LLM support |
| Google Gemini | Gemini model support |
| Hugging Face | Open-source model support |
| Ollama | Local model support |
| Azure OpenAI | Azure-hosted OpenAI deployment |

---

## STT Providers

| Provider | Purpose |
|---|---|
| Deepgram Nova-3 | Main STT provider |
| OpenAI Whisper | Speech transcription |
| Azure Speech | Microsoft STT |
| ElevenLabs STT | ElevenLabs speech recognition |
| Whisper.cpp | Local transcription option |

---

## TTS Providers

| Provider | Purpose |
|---|---|
| Cartesia Sonic | Low-latency high-quality TTS |
| Azure Speech | Microsoft neural voice |
| AWS Polly | AWS TTS |
| ElevenLabs | High-quality voice generation |
| OpenAI TTS | OpenAI speech generation |
| Deepgram TTS | Deepgram voice output |
| macOS say | Local Mac TTS fallback |

---

# Main Features

## Multi-Tenant Company Configuration

Each company can have its own AI settings.

Example:

    Company A:
    Deepgram → Bedrock → Cartesia

    Company B:
    Deepgram → OpenRouter → Azure Speech

    Company C:
    Whisper.cpp → Ollama → macOS say

Configuration is stored in PostgreSQL.

---

## Provider Fallback

If the selected LLM provider fails, the fallback router can try another provider.

Example:

    Primary LLM: Azure OpenAI
    Fails due to quota/deployment
    ↓
    Fallback: OpenRouter
    ↓
    Response still succeeds

Fallback metadata is returned and logged.

Example response fields:

    primary_llm_provider: azure_openai
    llm_provider: openrouter
    fallback_used: true

Fallback attempts are also logged so the system can show what failed and what succeeded.

---

## MongoDB Event Logging

MongoDB stores event logs such as:

- User transcript
- Assistant message
- Provider used
- Fallback attempts
- TTS audio URL
- Errors
- Benchmarks
- Analytics events

This is useful for debugging and observability.

---

## PostgreSQL Traceability

PostgreSQL stores structured conversation data:

- Companies
- Personas
- AI settings
- Voice settings
- Sessions
- Messages

MongoDB events also store PostgreSQL message IDs for traceability.

Example:

    MongoDB event
    → postgres_message_id
    → PostgreSQL conversation_messages row


---

# Admin Dashboard

Open:

    http://localhost:4002/admin/dashboard

The dashboard acts as a control panel for testing and demonstrating the system.

---

## Dashboard Sections

### 1. Provider Status

Shows which providers are configured.

Examples:

    openai: configured
    bedrock: configured
    deepgram: configured
    cartesia: configured
    azure_speech: configured
    ollama: local_configured

---

### 2. Company Config Viewer

Shows the current company settings:

- LLM provider
- LLM model
- STT provider
- STT model
- TTS provider
- TTS model
- Voice ID
- Language
- System prompt

---

### 3. Provider Switch Center

Lets you switch provider configurations from the UI.

Presets include:

- Enterprise AWS Mode
- Azure Voice Mode
- Cartesia Sonic Mode
- Local Demo Mode
- Fallback Test Mode

Example Cartesia Sonic Mode:

    STT: Deepgram Nova-3
    LLM: Bedrock Claude
    TTS: Cartesia Sonic
    Voice: Gemma - Decisive Agent

---

### 4. Chat Test Panel

Allows direct text chat testing from the dashboard.

Flow:

    Dashboard message
    → /chat/message
    → LLM response
    → response displayed in dashboard

---

### 5. Voice Test Panel

Supports two voice testing methods:

- Upload Audio File
- Live Microphone Recording

Flow:

    Audio
    → STT
    → LLM
    → TTS
    → Generated audio playback

---

### 6. Cost Monitoring

Shows approximate cost for the last voice request:

- Total voice cost
- STT cost
- LLM cost
- TTS cost
- Estimated audio seconds

These are demo estimates, not official billing.

---

### 7. Dashboard Charts

Shows visual charts for:

- Provider usage
- Voice events
- Chat events
- Fallbacks
- Errors

---

### 8. Provider Benchmark

Compares TTS providers.

Example:

    Azure Speech vs Cartesia Sonic

Returns:

- Provider name
- Success or failure
- Latency
- Audio URL
- Fastest provider

---

### 9. Recent Errors

Shows recent provider errors from MongoDB.

Useful for debugging:

- TTS failed
- STT failed
- LLM fallback failed
- Invalid provider
- Invalid API key

---

### 10. Recent Sessions

Shows recent chat and voice sessions.

Clicking a session shows:

- PostgreSQL messages
- MongoDB events
- Provider used
- Audio URL
- Errors
- Fallback metadata

---

### 11. Maintenance

Allows generated audio cleanup.

Options:

- Preview cleanup
- Delete matching files

---

# Important API Routes

## Health and Readiness

    GET /health
    GET /db/health
    GET /mongo/health
    GET /system/readiness
    GET /system/routes

---

## Providers

    GET /providers/status
    GET /speech-to-speech/providers

---

## Chat

    POST /chat/message
    GET /chat/sessions/{session_id}/messages

---

## Voice

    POST /voice/configured-batch
    POST /voice/openai-batch
    POST /voice/elevenlabs-full-batch

---

## Native Speech-to-Speech

    GET  /speech-to-speech/openai-demo
    POST /speech-to-speech/openai/session
    GET  /speech-to-speech/providers

---

## Admin Config

    GET   /admin/companies/{company_id}/full-config
    PATCH /admin/companies/{company_id}/provider-config
    PATCH /admin/companies/{company_id}/ai-settings
    PATCH /admin/companies/{company_id}/voice-settings

---

## Analytics and Debug

    GET /analytics/provider-usage
    GET /analytics/company-summary
    GET /debug/errors/recent
    GET /debug/sessions/recent
    GET /debug/sessions/{session_id}

---

## Benchmark

    POST /benchmark/tts
    GET  /benchmark/recent

---

## Maintenance

    DELETE /system/generated-audio

---

# Local Setup

## 1. Create Virtual Environment

    python3 -m venv venv
    source venv/bin/activate

---

## 2. Install Dependencies

    pip install -r requirements.txt

---

## 3. Create .env

    cp .env.example .env

Then add your API keys.

Important:

- Never commit .env
- Never share API keys in screenshots
- Rotate exposed keys


---

# Environment Variables

The project uses environment variables from `.env`.

## Security

    ADMIN_API_KEY=replace_with_admin_key
    COMPANY_API_KEYS={"company_id_here":"replace_with_company_key"}

`ADMIN_API_KEY` is used for admin routes.

`COMPANY_API_KEYS` is used for company-level API access.

Example:

    COMPANY_API_KEYS={"2f2d77c9-9a60-422a-b6bb-ba475112255e":"your_company_api_key"}

---

## Database

    DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/voiceagent

PostgreSQL stores:

- Company records
- AI settings
- Voice settings
- Conversation sessions
- Conversation messages

---

## MongoDB

    USE_MONGODB=True
    MONGODB_URL=replace_with_mongodb_url
    MONGODB_DATABASE=voiceagent
    MONGODB_EVENTS_COLLECTION=events

MongoDB stores:

- Provider events
- Transcripts
- Assistant responses
- Provider errors
- Benchmark results
- Analytics events

---

## Deepgram

    DEEPGRAM_API_KEY=replace_with_deepgram_key
    DEEPGRAM_STT_MODEL=nova-3

Deepgram Nova-3 is used as the main speech-to-text model.

---

## Cartesia

    CARTESIA_API_KEY=replace_with_cartesia_key
    CARTESIA_MODEL_ID=sonic-3
    CARTESIA_VOICE_ID=replace_with_cartesia_voice_uuid
    CARTESIA_LANGUAGE=en
    CARTESIA_OUTPUT_FORMAT=mp3
    CARTESIA_VERSION=2026-03-01

Important:

`CARTESIA_VOICE_ID` must be the actual UUID, not the display name.

Wrong:

    Gemma - Decisive Agent

Correct:

    xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

The dashboard can display the friendly voice name, but the Cartesia API needs the UUID in `.env`.

---

## Azure Speech

    AZURE_SPEECH_KEY=replace_with_azure_speech_key
    AZURE_SPEECH_REGION=eastus
    AZURE_SPEECH_LANGUAGE=en-US
    AZURE_SPEECH_VOICE_NAME=en-US-JennyNeural

Azure Speech can be used for TTS and STT depending on configuration.

---

## AWS Bedrock and Polly

    AWS_ACCESS_KEY_ID=replace_with_aws_access_key
    AWS_SECRET_ACCESS_KEY=replace_with_aws_secret_key
    AWS_DEFAULT_REGION=us-east-2
    AWS_BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-6
    AWS_POLLY_VOICE_ID=Joanna
    AWS_POLLY_ENGINE=neural
    AWS_POLLY_OUTPUT_FORMAT=mp3

AWS Bedrock is used for LLM responses.

AWS Polly is used for text-to-speech.

---

## OpenAI

    OPENAI_API_KEY=replace_with_openai_key
    OPENAI_MODEL=gpt-4o-mini

OpenAI is used for:

- Chat/LLM support
- TTS support
- Native realtime speech-to-speech with OpenAI Realtime

---

## OpenRouter

    OPENROUTER_API_KEY=replace_with_openrouter_key
    OPENROUTER_MODEL=openrouter/free

OpenRouter is used as an LLM provider and fallback option.

---

## Anthropic

    ANTHROPIC_API_KEY=replace_with_anthropic_key
    ANTHROPIC_MODEL_ID=claude-sonnet-4-6

Anthropic can be used as an LLM provider.

---

## Gemini

    GOOGLE_API_KEY=replace_with_google_api_key
    GEMINI_API_KEY=replace_with_google_api_key
    GEMINI_MODEL_ID=gemini-2.5-flash

Gemini can be used as an LLM provider.

---

## Ollama

    OLLAMA_BASE_URL=http://localhost:11434
    OLLAMA_MODEL_ID=llama3.2:1b

Ollama is used for local LLM testing.

Make sure Ollama is running before using this provider.

---

## Twilio

    TWILIO_WEBHOOK_BASE_URL=https://your-tunnel-url.trycloudflare.com
    TWILIO_PROCESSING_MODE=batch
    TWILIO_AUTH_TOKEN=replace_with_twilio_auth_token
    TWILIO_VALIDATE_SIGNATURES=True

Twilio routes can be used for phone-based voice workflows.

---

# Running the Project

Start FastAPI locally:

    python3 -m uvicorn app.main:app --host 0.0.0.0 --port 4002 --reload

Open Swagger:

    http://localhost:4002/docs

Open dashboard:

    http://localhost:4002/admin/dashboard

---

# Docker Compose

Docker files are included for deployment-style setup.

Validate Docker Compose config:

    docker compose config

Start with Docker:

    docker compose up --build

For local development, using Uvicorn directly is recommended.

---

# Testing the Project

## Unit Tests

Run:

    python3 -m pytest -q

These tests check small internal components like:

- Cost estimator
- Error formatter
- Rate limiter
- Latency tracker

---

## Smoke Test

Run:

    python3 scripts/smoke_test.py

Smoke test checks the main system endpoints:

- `/system/readiness`
- `/providers/status`
- `/analytics/company-summary`
- `/debug/sessions/recent`
- `/chat/message`

Expected:

    ✅ System readiness: 200
    ✅ Provider status: 200
    ✅ Company summary: 200
    ✅ Recent sessions: 200
    ✅ Chat message: 200

If smoke test says connection refused, start FastAPI first on port `4002`.


---

# Provider Routing and Fallback

The project supports dynamic provider routing.

A company can choose which LLM provider should answer requests.

Example:

    Company config:
    LLM provider = azure_openai

If Azure OpenAI fails because of quota, deployment, or key issues, the fallback router can try another provider.

Example fallback flow:

    Primary LLM: Azure OpenAI
    ↓ fails
    Fallback 1: OpenRouter
    ↓ succeeds
    Assistant response is still returned

Example response fields:

    fallback_used: true
    primary_llm_provider: azure_openai
    llm_provider: openrouter

This is useful because one provider failure should not break the full chat or voice pipeline.

---

# Latency Tracking

Voice responses include timing for each major stage.

Example:

    latency_ms:
      stt: 812.4
      llm: 2301.8
      tts: 640.2
      total: 3860.7

Meaning:

- `stt` = speech-to-text time
- `llm` = language model response time
- `tts` = text-to-speech generation time
- `total` = full voice request time

All API responses also include:

    X-Process-Time-MS

This header shows total API processing time.

Rate limit headers are also returned:

    X-RateLimit-Limit
    X-RateLimit-Remaining

---

# Cost Estimate Logging

Voice responses include approximate cost estimates.

Example:

    cost_estimate:
      currency: USD
      note: Approximate demo estimate only. Not exact vendor billing.
      stt_provider: deepgram
      llm_provider: bedrock
      tts_provider: cartesia
      estimated_audio_seconds: 6.2
      estimated_input_tokens: 20
      estimated_output_tokens: 45
      estimated_tts_characters: 180
      estimated_stt_cost_usd: 0.00062
      estimated_llm_cost_usd: 0.00021
      estimated_tts_cost_usd: 0.000054
      estimated_total_cost_usd: 0.000884

Important:

These are approximate demo estimates.

They are not official vendor billing numbers.

The purpose is to show how the backend can track estimated usage and cost per request.

---

# Provider Benchmarking

The project can benchmark TTS providers.

Endpoint:

    POST /benchmark/tts?providers=azure_speech,cartesia

Example result:

    status: ok
    benchmark_type: tts
    fastest:
      provider: cartesia
      status: success
      latency_ms: 530.4
      audio_url: /demo/generated/example.mp3

    results:
      - provider: azure_speech
        status: success
        latency_ms: 940.2
        audio_url: /demo/generated/azure-example.mp3

      - provider: cartesia
        status: success
        latency_ms: 530.4
        audio_url: /demo/generated/cartesia-example.mp3

The dashboard includes a benchmark panel for easy comparison.

This is useful for comparing:

- Azure Speech vs Cartesia Sonic
- AWS Polly vs Azure Speech
- Cartesia Sonic vs other TTS providers

---

# Debugging and Observability

## Recent Errors

Endpoint:

    GET /debug/errors/recent

Shows recent provider errors.

Useful for checking:

- STT failures
- LLM failures
- TTS failures
- Invalid provider names
- Invalid API keys
- Provider timeout issues

---

## Recent Sessions

Endpoint:

    GET /debug/sessions/recent

Shows latest sessions.

This helps quickly inspect recent activity.

---

## Session Details

Endpoint:

    GET /debug/sessions/{session_id}

Shows:

- Session metadata
- PostgreSQL messages
- MongoDB events
- Provider errors
- Audio URLs
- Fallback metadata

This is useful when debugging one complete conversation or voice request.

---

## Provider Usage Analytics

Endpoint:

    GET /analytics/provider-usage

Shows provider usage counts.

Example providers:

- deepgram
- bedrock
- cartesia
- azure_speech
- openrouter
- ollama

---

## Company Summary

Endpoint:

    GET /analytics/company-summary

Shows:

- Total events
- Total errors
- Total fallbacks
- Voice event count
- Chat event count
- Latest events

The dashboard uses this information for charts and summary cards.

---

# Structured Error Messages

Provider failures return structured error details.

Example:

    detail:
      stage: tts
      provider: cartesia
      message: Voice ID invalid
      suggestion: Check CARTESIA_API_KEY, CARTESIA_VOICE_ID UUID, CARTESIA_MODEL_ID, and Cartesia-Version in .env.
      route: /voice/configured-batch

This makes debugging much easier than plain string errors.

Example stages:

- `stt`
- `llm`
- `tts`

Example provider-specific suggestions:

- Cartesia: check API key and voice UUID
- Deepgram: check API key, model, and audio format
- Azure Speech: check key, region, and voice name
- Bedrock: check AWS credentials, region, and model access

---

# Rate Limiting

Basic in-memory rate limiting is enabled.

Example limits:

    /voice/*       -> 20 requests/min
    /chat/*        -> 60 requests/min
    /benchmark/*   -> 60 requests/min
    /admin/*       -> 120 requests/min
    /debug/*       -> 120 requests/min
    /analytics/*   -> 120 requests/min
    /system/*      -> 120 requests/min
    /providers/*   -> 120 requests/min

Response headers include:

    X-RateLimit-Limit
    X-RateLimit-Remaining

For local development and demo, in-memory rate limiting is enough.

For production, use Redis or another shared rate-limit store.


---

# Generated Audio Cleanup

Generated audio files are stored here:

    app/static/generated

These files are produced when the system generates TTS audio responses.

To avoid the folder growing forever, the project includes a cleanup endpoint.

Preview cleanup:

    DELETE /system/generated-audio?dry_run=true&max_age_hours=24

Delete matching files:

    DELETE /system/generated-audio?dry_run=false&max_age_hours=24

Meaning:

- `dry_run=true` only previews what would be deleted.
- `dry_run=false` deletes matching files.
- `max_age_hours=24` means delete files older than 24 hours.
- `max_age_hours=0` matches all generated audio files except `.gitkeep`.

The admin dashboard also has a maintenance panel for this.

Recommended safe usage:

    Preview Cleanup first
    Then Delete Matching Files only if the preview looks correct

---

# Security Notes

This project includes basic local/demo security controls.

## API Key Security

Admin routes use:

    X-Admin-API-Key

Company routes use:

    X-Company-API-Key

Do not expose these keys in:

- Screenshots
- GitHub
- Logs
- Public demos
- README files
- Shared curl commands

If a key is exposed, rotate it.

---

## Dashboard Key Storage

The dashboard stores keys in browser `localStorage` for local development only.

This is convenient for testing, but not recommended for production.

The dashboard includes:

    Clear Saved Keys

Use it after demos.

Production should replace this with:

- Admin login
- Secure session cookie
- Logout
- Role-based access control

---

## Environment File Safety

Never commit:

    .env

The project includes:

    .env.example

Use `.env.example` to show required variables without exposing real secrets.

---

## Generated Audio Safety

Generated audio files are ignored from Git except:

    app/static/generated/.gitkeep

This keeps the folder structure while avoiding committing generated MP3/WAV files.

---

## Rate Limiting

The project includes in-memory rate limiting for local/demo safety.

For production, use:

- Redis
- API gateway rate limiting
- Cloud load balancer rules
- Per-company usage quotas

---

# Recommended Demo Flow

Use this flow for a recruiter, client, or GitHub walkthrough.

## Step 1: Start the Backend

    python3 -m uvicorn app.main:app --host 0.0.0.0 --port 4002 --reload

---

## Step 2: Open Readiness Check

    http://localhost:4002/system/readiness

Show that:

- PostgreSQL is connected
- MongoDB is connected
- Providers are configured
- Ollama runtime status is visible
- Dashboard is available

---

## Step 3: Open Provider Status

    http://localhost:4002/providers/status

Show configured providers:

- Deepgram
- Bedrock
- Cartesia
- Azure Speech
- OpenRouter
- Ollama
- OpenAI
- Anthropic
- Gemini

---

## Step 4: Open Speech-to-Speech Providers

    http://localhost:4002/speech-to-speech/providers

Explain two modes:

    Native speech-to-speech:
    OpenAI Realtime WebRTC

    Pipeline speech-to-speech:
    Deepgram Nova-3 → LLM Router → Cartesia Sonic / Azure Speech / AWS Polly

---

## Step 5: Open Admin Dashboard

    http://localhost:4002/admin/dashboard

Enter:

- Admin API key
- Company API key
- Company ID

Click:

    Save
    Refresh

---

## Step 6: Show Provider Config

Use the dashboard to show:

- Current LLM provider
- Current STT provider
- Current TTS provider
- Voice mode
- System prompt

---

## Step 7: Select Cartesia Sonic Mode

Click:

    Cartesia Sonic Mode

Then click:

    Apply Config

This sets:

    STT: Deepgram Nova-3
    LLM: Bedrock Claude
    TTS: Cartesia Sonic

---

## Step 8: Run Uploaded Audio Voice Test

Upload a short audio file.

Click:

    Run Uploaded Audio Test

Show response fields:

- transcript
- assistant message
- audio_url
- stt_provider
- llm_provider
- tts_provider
- latency_ms
- cost_estimate

---

## Step 9: Run Live Microphone Recording

Click:

    Start Recording
    Stop Recording
    Send Recorded Voice

Show:

- Recorded audio preview
- Generated assistant audio playback
- Cost monitoring cards
- Latency values

---

## Step 10: Run TTS Provider Benchmark

Use:

    Azure Speech vs Cartesia Sonic

Show:

- Provider latency
- Fastest provider
- Play Audio links
- Benchmark result saved in MongoDB

---

## Step 11: Show Dashboard Charts

Show:

- Provider usage
- Event summary
- Voice events
- Chat events
- Errors
- Fallbacks

---

## Step 12: Show Recent Sessions

Click a recent session.

Show:

- PostgreSQL messages
- MongoDB events
- Provider metadata
- Audio URL
- Fallback details
- Error trace if any

---

## Step 13: Show Maintenance Panel

Use:

    Preview Cleanup

Explain that generated audio files can be cleaned safely.

---

# Troubleshooting Guide

## Smoke test says connection refused

Reason:

FastAPI is not running on port `4002`.

Fix:

    python3 -m uvicorn app.main:app --host 0.0.0.0 --port 4002 --reload

Then run:

    python3 scripts/smoke_test.py

---

## Cartesia says voice ID invalid

Reason:

`CARTESIA_VOICE_ID` is not a valid UUID.

Wrong:

    Gemma - Decisive Agent

Correct:

    xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

Fix:

Update `.env`:

    CARTESIA_VOICE_ID=actual_uuid_here

Restart FastAPI.

---

## Cartesia key works but TTS fails

Check:

    CARTESIA_API_KEY
    CARTESIA_MODEL_ID
    CARTESIA_VOICE_ID
    CARTESIA_VERSION

Also confirm:

    CARTESIA_MODEL_ID=sonic-3
    CARTESIA_LANGUAGE=en

---

## Deepgram STT fails

Check:

    DEEPGRAM_API_KEY=...
    DEEPGRAM_STT_MODEL=nova-3

Also check audio file type.

Allowed examples:

    audio/webm
    audio/wav
    audio/mp3
    audio/mp4
    audio/m4a
    audio/x-m4a

---

## Azure Speech gives 401

Reason:

Azure key and region may not match.

Check:

    AZURE_SPEECH_KEY
    AZURE_SPEECH_REGION

The region must match the Azure Speech resource.

Example:

    eastus
    eastus2

---

## Bedrock model fails

Check:

    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_DEFAULT_REGION
    AWS_BEDROCK_MODEL_ID

Also verify:

- AWS credentials are valid
- Bedrock model access is enabled
- Region supports the selected model

---

## Ollama fails

Make sure Ollama is running:

    ollama serve

Check installed models:

    ollama list

Pull model if needed:

    ollama pull llama3.2:1b

---

## Dashboard does not update

Try hard refresh:

    Cmd + Shift + R

Also restart FastAPI:

    lsof -ti :4002 | xargs kill -9
    python3 -m uvicorn app.main:app --host 0.0.0.0 --port 4002 --reload

---

## Dashboard does not show a new button or panel

Reason:

Browser may be showing cached HTML.

Fix:

- Restart FastAPI
- Hard refresh browser
- Open dashboard with query parameter:

    http://localhost:4002/admin/dashboard?fresh=1

---

## POST /voice/configured-batch says Session not found

Reason:

You probably entered `company_id` inside the `session_id` field.

Fix:

Use:

    company_id = your company UUID
    session_id = leave blank
    channel = configured_batch_voice

In Swagger, leave `session_id` empty and uncheck “Send empty value.”

---

## Smoke test skips chat test

Reason:

`COMPANY_API_KEYS` is not valid JSON.

Correct format:

    COMPANY_API_KEYS={"company_id_here":"company_api_key_here"}

Do not wrap the whole JSON in single quotes.

Wrong:

    COMPANY_API_KEYS='{"company_id":"key"}'

Correct:

    COMPANY_API_KEYS={"company_id":"key"}

---

# Current Notes

- Deepgram Nova-3 is used as the main STT provider.
- Cartesia Sonic is used as a low-latency TTS provider.
- Azure Speech is supported as a TTS provider.
- AWS Polly is supported as a TTS provider.
- OpenAI Realtime is supported for native speech-to-speech.
- Azure OpenAI may require quota or deployment approval depending on subscription.
- Ollama requires a local Ollama server running.
- Docker Compose is included, but local Uvicorn is preferred during development.
- Cost estimates are demo estimates, not exact billing numbers.
- In-memory rate limiting is suitable for local/demo use only.

---

# Final Verification Checklist

Before demo or commit, run:

    python3 -m py_compile app/main.py
    find app -name "*.py" -print0 | xargs -0 python3 -m py_compile
    python3 -m pytest -q
    python3 scripts/smoke_test.py
    docker compose config

Also verify Git status:

    git status

Make sure `.env` is not committed.

---

# Suggested Commit Message

    Add multi-provider AI voice agent backend with dashboard, Cartesia Sonic, OpenAI Realtime, analytics, benchmarking, latency, and cost tracking

---

# Summary

This project demonstrates a complete AI voice backend with:

- Configurable STT, LLM, and TTS providers
- Deepgram Nova-3 speech recognition
- Cartesia Sonic voice generation
- OpenAI Realtime native speech-to-speech
- Provider fallback
- MongoDB observability
- PostgreSQL session persistence
- Admin dashboard
- Latency and cost tracking
- Benchmarking
- Rate limiting
- Testing and smoke checks

It is built as a practical, demo-ready foundation for multi-tenant conversational AI voice systems.

