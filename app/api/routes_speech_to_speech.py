import json

import httpx
from fastapi import APIRouter, Header, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, PlainTextResponse

from app.core.config import settings

router = APIRouter()


def _load_company_api_keys():
    raw = getattr(settings, "company_api_keys", None)

    if isinstance(raw, dict):
        return raw

    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return {}

    return {}


def require_company_key(company_id: str, x_company_api_key: str | None):
    company_keys = _load_company_api_keys()
    expected = company_keys.get(company_id)

    if not expected:
        raise HTTPException(
            status_code=403,
            detail="Company API key is not configured for this company_id",
        )

    if x_company_api_key != expected:
        raise HTTPException(
            status_code=403,
            detail="Invalid company API key",
        )

    return True


@router.get("/providers")
async def speech_to_speech_providers():
    return {
        "status": "ok",
        "native_speech_to_speech": {
            "openai_realtime": {
                "status": "configured" if bool(settings.openai_api_key) else "not_configured",
                "type": "native_realtime_speech_to_speech",
                "connection": "webrtc",
                "models": [
                    "gpt-realtime",
                    "gpt-realtime-2 if enabled on your account",
                    "gpt-realtime-translate if enabled on your account",
                ],
            },
            "gemini_live": {
                "status": "planned",
                "type": "native_realtime_speech_to_speech",
            },
            "kyutai_moshi": {
                "status": "planned_local_experiment",
                "type": "open_source_native_speech_to_speech",
            },
            "nvidia_nemotron_voicechat": {
                "status": "planned_enterprise_gpu_or_early_access",
                "type": "native_full_duplex_speech_to_speech",
            },
        },
        "pipeline_speech_to_speech": {
            "deepgram_nova_to_llm_to_azure_speech": "configured",
            "deepgram_nova_to_llm_to_aws_polly": "configured",
            "deepgram_nova_to_llm_to_elevenlabs": "configured",
            "deepgram_nova_to_llm_to_cartesia": "planned",
        },
        "note": "Deepgram Nova is STT. It is used in pipeline speech-to-speech, not native speech-to-speech.",
    }


@router.post("/openai/session", response_class=PlainTextResponse)
async def create_openai_realtime_session(
    request: Request,
    company_id: str = Query(...),
    model: str = Query(default="gpt-realtime"),
    voice: str = Query(default="marin"),
    x_company_api_key: str | None = Header(default=None, alias="X-Company-API-Key"),
):
    require_company_key(company_id, x_company_api_key)

    if not settings.openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not configured",
        )

    sdp = (await request.body()).decode("utf-8")

    if not sdp.strip():
        raise HTTPException(
            status_code=400,
            detail="SDP body is required",
        )

    session_config = {
        "type": "realtime",
        "model": model,
        "instructions": (
            "You are a helpful realtime voice assistant. "
            "LANGUAGE RULE: Always respond only in English. "
            "Do not respond in Spanish, Hindi, Telugu, Kannada, or any other language. "
            "Even if the user speaks another language, politely answer in English. "
            "Speak naturally, keep responses short, and ask clarifying questions only when needed."
        ),
        "audio": {
            "output": {
                "voice": voice
            }
        },
    }

    files = {
        "sdp": (None, sdp),
        "session": (None, json.dumps(session_config)),
    }

    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "OpenAI-Safety-Identifier": company_id,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/realtime/calls",
            headers=headers,
            files=files,
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"OpenAI Realtime session failed: {response.text}",
        )

    return PlainTextResponse(
        content=response.text,
        media_type="application/sdp",
    )


@router.get("/openai-demo", response_class=HTMLResponse)
async def openai_speech_to_speech_demo():
    return HTMLResponse(
        content="""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>OpenAI Native Speech-to-Speech Demo</title>
  <style>
    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #020617;
      color: #e5e7eb;
      min-height: 100vh;
      display: grid;
      place-items: center;
    }
    .card {
      width: min(860px, 92vw);
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 22px;
      padding: 24px;
      box-shadow: 0 25px 80px rgba(0,0,0,.4);
    }
    h1 { margin: 0 0 8px; }
    p { color: #94a3b8; }
    label {
      display: block;
      color: #94a3b8;
      font-size: 13px;
      margin-top: 14px;
      margin-bottom: 6px;
    }
    input, select {
      width: 100%;
      background: #020617;
      color: #e5e7eb;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 11px 12px;
      font-size: 14px;
      box-sizing: border-box;
    }
    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }
    button {
      border: 0;
      border-radius: 12px;
      padding: 11px 16px;
      font-weight: 700;
      cursor: pointer;
      color: white;
      background: linear-gradient(135deg, #0ea5e9, #2563eb);
      margin-right: 10px;
      margin-top: 18px;
    }
    button.danger {
      background: linear-gradient(135deg, #ef4444, #b91c1c);
    }
    button:disabled {
      opacity: .5;
      cursor: not-allowed;
    }
    .log {
      background: #020617;
      border: 1px solid #334155;
      border-radius: 14px;
      padding: 12px;
      white-space: pre-wrap;
      max-height: 240px;
      overflow: auto;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 12px;
      margin-top: 16px;
    }
    audio {
      width: 100%;
      margin-top: 14px;
    }
    .badge {
      display: inline-block;
      padding: 5px 9px;
      background: rgba(34,197,94,.12);
      color: #86efac;
      border: 1px solid rgba(34,197,94,.25);
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      margin-bottom: 14px;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">Native Speech-to-Speech / WebRTC</div>
    <h1>OpenAI Realtime Speech-to-Speech</h1>
    <p>
      This is different from uploaded-audio batch voice. Here your microphone streams live to the realtime model and the assistant speaks back live.
    </p>

    <label>Base URL</label>
    <input id="baseUrl" value="http://localhost:4002" />

    <label>Company API Key</label>
    <input id="companyKey" type="password" placeholder="Paste X-Company-API-Key" />

    <label>Company ID</label>
    <input id="companyId" value="2f2d77c9-9a60-422a-b6bb-ba475112255e" />

    <div class="grid">
      <div>
        <label>Realtime Model</label>
        <select id="model">
          <option value="gpt-realtime">gpt-realtime</option>
          <option value="gpt-realtime-2">gpt-realtime-2</option>
          <option value="gpt-realtime-translate">gpt-realtime-translate</option>
        </select>
      </div>
      <div>
        <label>Voice</label>
        <select id="voice">
          <option value="marin">marin</option>
          <option value="alloy">alloy</option>
          <option value="verse">verse</option>
          <option value="sage">sage</option>
        </select>
      </div>
    </div>

    <button id="startBtn" onclick="startSession()">Start Live Speech-to-Speech</button>
    <button id="stopBtn" class="danger" onclick="stopSession()" disabled>Stop</button>

    <audio id="remoteAudio" autoplay controls></audio>

    <div id="log" class="log">Status: idle</div>
  </div>

<script>
let pc = null;
let localStream = null;
let dc = null;

function log(message) {
  const box = document.getElementById("log");
  box.textContent += "\\n" + message;
  box.scrollTop = box.scrollHeight;
}

function baseUrl() {
  return document.getElementById("baseUrl").value.replace(/\\/$/, "");
}

async function startSession() {
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");

  startBtn.disabled = true;
  stopBtn.disabled = false;
  document.getElementById("log").textContent = "Status: starting...";

  try {
    const companyId = document.getElementById("companyId").value.trim();
    const companyKey = document.getElementById("companyKey").value.trim();
    const model = document.getElementById("model").value;
    const voice = document.getElementById("voice").value;

    pc = new RTCPeerConnection();

    const remoteAudio = document.getElementById("remoteAudio");
    pc.ontrack = (event) => {
      remoteAudio.srcObject = event.streams[0];
      log("Remote assistant audio connected.");
    };

    localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    localStream.getTracks().forEach(track => pc.addTrack(track, localStream));
    log("Microphone connected.");

    dc = pc.createDataChannel("oai-events");

    dc.onopen = () => {
      log("Data channel open.");

      dc.send(JSON.stringify({
        type: "conversation.item.create",
        item: {
          type: "message",
          role: "user",
          content: [
            {
              type: "input_text",
              text: "Greet the user briefly in English and ask how you can help. Reply only in English."
            }
          ]
        }
      }));

      dc.send(JSON.stringify({
        type: "response.create"
      }));
    };

    dc.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (
          data.type &&
          (
            data.type.includes("response.output_text") ||
            data.type.includes("response.output_audio_transcript") ||
            data.type.includes("error")
          )
        ) {
          log(JSON.stringify(data));
        }
      } catch {
        log(event.data);
      }
    };

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    log("Sending SDP offer to backend...");

    const sessionUrl =
      `${baseUrl()}/speech-to-speech/openai/session?company_id=${encodeURIComponent(companyId)}&model=${encodeURIComponent(model)}&voice=${encodeURIComponent(voice)}`;

    const response = await fetch(sessionUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/sdp",
        "X-Company-API-Key": companyKey
      },
      body: offer.sdp
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText);
    }

    const answerSdp = await response.text();

    await pc.setRemoteDescription({
      type: "answer",
      sdp: answerSdp
    });

    log("Live speech-to-speech session connected. Speak now.");

  } catch (error) {
    log("ERROR: " + error.message);
    stopSession();
  }
}

function stopSession() {
  if (dc) {
    try { dc.close(); } catch {}
    dc = null;
  }

  if (pc) {
    try { pc.close(); } catch {}
    pc = null;
  }

  if (localStream) {
    localStream.getTracks().forEach(track => track.stop());
    localStream = null;
  }

  document.getElementById("startBtn").disabled = false;
  document.getElementById("stopBtn").disabled = true;

  log("Session stopped.");
}
</script>
</body>
</html>
        """
    )
