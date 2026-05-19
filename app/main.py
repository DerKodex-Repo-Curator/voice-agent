from time import perf_counter
from app.services.rate_limiter import rate_limiter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes_health import router as health_router
from app.api.routes_db import router as db_router
from app.api.routes_mongo import router as mongo_router
from app.api.routes_companies import router as companies_router
from app.api.routes_chat import router as chat_router
from app.api.routes_providers import router as providers_router
from app.api.routes_provider_status import router as provider_status_router
from app.api.routes_huggingface import router as huggingface_router
from app.api.routes_anthropic import router as anthropic_router
from app.api.routes_gemini import router as gemini_router
from app.api.routes_ollama import router as ollama_router
from app.api.routes_voice_local import router as voice_local_router
from app.api.routes_voice_openai import router as voice_openai_router
from app.api.routes_voice_elevenlabs import router as voice_elevenlabs_router
from app.api.routes_voice_configured import router as voice_configured_router
from app.api.routes_voice_stream import router as voice_stream_router
from app.api.routes_realtime_openai import router as realtime_openai_router
from app.api.routes_admin_config import router as admin_config_router
from app.api.routes_twilio import router as twilio_router
from app.api.routes_twilio_realtime import router as twilio_realtime_router
from app.api.routes_admin_provider_config import router as admin_provider_config_router
from app.api.routes_provider_fallback import router as provider_fallback_router
from app.api.routes_debug_errors import router as debug_errors_router
from app.api.routes_debug_sessions import router as debug_sessions_router
from app.api.routes_analytics import router as analytics_router
from app.api.routes_admin_dashboard import router as admin_dashboard_router
from app.api.routes_system_readiness import router as system_readiness_router
from app.api.routes_system_maintenance import router as system_maintenance_router
from app.api.routes_speech_to_speech import router as speech_to_speech_router
from app.api.routes_benchmark import router as benchmark_router
from app.core.config import settings


app = FastAPI(


    title="General Voice Agent Backend",
    description="A configurable multi-company voice agent backend using FastAPI, OpenRouter/OpenAI, local Whisper.cpp, OpenAI STT/TTS, OpenAI Realtime, PostgreSQL, Twilio, and provider routing.",
    version="0.1.0",
    debug=settings.debug,
)



@app.middleware("http")
async def rate_limit_requests(request, call_next):
    path = request.url.path

    skip_prefixes = (
        "/docs",
        "/openapi.json",
        "/redoc",
        "/admin/dashboard",
        "/demo/",
        "/favicon.ico",
    )

    if path.startswith(skip_prefixes):
        return await call_next(request)

    if path.startswith("/voice"):
        limit = 20
        scope = "voice"
    elif path.startswith("/chat"):
        limit = 60
        scope = "chat"
    elif path.startswith("/benchmark"):
        limit = 60
        scope = "benchmark"
    elif path.startswith(("/admin", "/debug", "/analytics", "/system", "/providers")):
        limit = 120
        scope = "admin"
    else:
        limit = 100
        scope = "general"

    admin_key = request.headers.get("X-Admin-API-Key")
    company_key = request.headers.get("X-Company-API-Key")
    client_host = request.client.host if request.client else "unknown"

    identity = admin_key or company_key or client_host
    limiter_key = f"{scope}:{identity}"

    result = rate_limiter.check(
        key=limiter_key,
        limit=limit,
        window_seconds=60,
    )

    if not result["allowed"]:
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=429,
            content={
                "detail": {
                    "message": "Rate limit exceeded",
                    "scope": scope,
                    "limit_per_minute": result["limit"],
                    "retry_after_seconds": result["retry_after"],
                }
            },
            headers={
                "Retry-After": str(result["retry_after"]),
                "X-RateLimit-Limit": str(result["limit"]),
                "X-RateLimit-Remaining": "0",
            },
        )

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(result["limit"])
    response.headers["X-RateLimit-Remaining"] = str(result["remaining"])
    return response


@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = perf_counter()
    response = await call_next(request)
    process_time_ms = round((perf_counter() - start_time) * 1000, 2)
    response.headers["X-Process-Time-MS"] = str(process_time_ms)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(db_router, prefix="/db", tags=["Database"])
app.include_router(mongo_router, prefix="/mongo", tags=["MongoDB"])
app.include_router(companies_router, prefix="/companies", tags=["Companies"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(providers_router, prefix="/providers", tags=["Providers"])
app.include_router(provider_status_router, prefix="/providers", tags=["Provider Status"])
app.include_router(provider_fallback_router, prefix="/providers", tags=["Provider Fallback"])
app.include_router(huggingface_router, prefix="/huggingface", tags=["Hugging Face"])
app.include_router(anthropic_router, prefix="/anthropic", tags=["Anthropic / Claude"])
app.include_router(gemini_router, prefix="/gemini", tags=["Google Gemini"])
app.include_router(ollama_router, prefix="/ollama", tags=["Ollama Local"])
app.include_router(voice_local_router, prefix="/voice", tags=["Local Voice"])
app.include_router(voice_openai_router, prefix="/voice", tags=["OpenAI Batch Voice"])
app.include_router(voice_elevenlabs_router, prefix="/voice", tags=["ElevenLabs Voice"])
app.include_router(voice_configured_router, prefix="/voice", tags=["Configured Voice"])
app.include_router(voice_stream_router, prefix="/ws", tags=["WebSocket Voice"])
app.include_router(realtime_openai_router, prefix="/realtime", tags=["OpenAI Realtime"])
app.include_router(twilio_router, prefix="/twilio", tags=["Twilio Phone"])
app.include_router(twilio_realtime_router, prefix="/twilio-realtime", tags=["Twilio Realtime"])
app.include_router(admin_config_router, prefix="/admin", tags=["Admin Config"])
app.include_router(admin_provider_config_router, prefix="/admin", tags=["Admin Provider Config"])
app.include_router(debug_errors_router, prefix="/debug", tags=["Debug Errors"])
app.include_router(debug_sessions_router, prefix="/debug", tags=["Debug Sessions"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
app.include_router(admin_dashboard_router, prefix="/admin", tags=["Admin Dashboard"])
app.include_router(system_readiness_router, prefix="/system", tags=["System Readiness"])
app.include_router(system_maintenance_router, prefix="/system", tags=["System Maintenance"])
app.include_router(speech_to_speech_router, prefix="/speech-to-speech", tags=["Speech-to-Speech"])
app.include_router(benchmark_router, prefix="/benchmark", tags=["Benchmark"])

app.mount("/demo", StaticFiles(directory="app/static", html=True), name="demo")


@app.get("/")
async def root():
    return {
        "message": "General Voice Agent Backend is running",
        "docs": "/docs",
        "health": "/health",
        "db_health": "/db/health",
        "companies": "/companies",
        "chat": "/chat/message",
        "providers": "/providers/llm",
        "browser_voice_demo": "/demo",
        "local_voice_demo": "/demo/local_voice.html",
        "openai_batch_voice_demo": "/demo/openai_voice.html",
        "websocket_voice_demo": "/demo/realtime_voice.html",
        "openai_realtime_demo": "/demo/openai_realtime.html",
        "admin_config": "/admin/companies/{company_id}/full-config",
    }
