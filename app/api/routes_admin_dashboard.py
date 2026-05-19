from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard():
    return HTMLResponse(
        content="""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Voice Agent Admin Dashboard</title>
  <style>
    :root {
      --bg: #0f172a;
      --panel: #111827;
      --panel-2: #1f2937;
      --card: #020617;
      --border: #334155;
      --text: #e5e7eb;
      --muted: #94a3b8;
      --accent: #38bdf8;
      --accent-2: #22c55e;
      --warning: #f59e0b;
      --danger: #ef4444;
      --purple: #a78bfa;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top left, #1e293b 0, #020617 42%, #000 100%);
      color: var(--text);
      min-height: 100vh;
    }

    .layout {
      display: grid;
      grid-template-columns: 280px 1fr;
      min-height: 100vh;
    }

    aside {
      background: rgba(15, 23, 42, 0.9);
      border-right: 1px solid var(--border);
      padding: 24px;
      position: sticky;
      top: 0;
      height: 100vh;
      overflow-y: auto;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 28px;
    }

    .logo {
      width: 44px;
      height: 44px;
      border-radius: 14px;
      background: linear-gradient(135deg, var(--accent), var(--purple));
      display: grid;
      place-items: center;
      font-weight: 800;
      color: white;
      box-shadow: 0 10px 30px rgba(56, 189, 248, 0.3);
    }

    .brand h1 {
      margin: 0;
      font-size: 18px;
      line-height: 1.2;
    }

    .brand p {
      margin: 3px 0 0;
      font-size: 12px;
      color: var(--muted);
    }

    label {
      display: block;
      font-size: 12px;
      color: var(--muted);
      margin: 14px 0 6px;
    }

    input, select, textarea {
      width: 100%;
      background: #020617;
      border: 1px solid var(--border);
      color: var(--text);
      border-radius: 10px;
      padding: 10px 12px;
      outline: none;
      font-size: 13px;
    }

    textarea {
      min-height: 84px;
      resize: vertical;
    }

    input:focus, select:focus, textarea:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.16);
    }

    button {
      border: 0;
      background: linear-gradient(135deg, #0ea5e9, #2563eb);
      color: white;
      border-radius: 12px;
      padding: 10px 14px;
      cursor: pointer;
      font-weight: 700;
      font-size: 13px;
      box-shadow: 0 12px 24px rgba(37, 99, 235, 0.28);
    }

    button.secondary {
      background: #1f2937;
      border: 1px solid var(--border);
      box-shadow: none;
    }

    button.danger {
      background: linear-gradient(135deg, #ef4444, #b91c1c);
    }

    button.success {
      background: linear-gradient(135deg, #22c55e, #15803d);
    }

    button:hover {
      filter: brightness(1.08);
    }

    main {
      padding: 28px;
      overflow-x: hidden;
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 20px;
      margin-bottom: 24px;
    }

    .topbar h2 {
      margin: 0;
      font-size: 30px;
      letter-spacing: -0.04em;
    }

    .topbar p {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 14px;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 7px 10px;
      border-radius: 999px;
      background: rgba(34, 197, 94, 0.12);
      color: #86efac;
      border: 1px solid rgba(34, 197, 94, 0.25);
      font-size: 12px;
      font-weight: 700;
    }

    .grid {
      display: grid;
      gap: 18px;
    }

    .grid.stats {
      grid-template-columns: repeat(5, minmax(0, 1fr));
      margin-bottom: 18px;
    }

    .grid.two {
      grid-template-columns: 1.1fr 0.9fr;
    }

    .grid.three {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .card {
      background: linear-gradient(180deg, rgba(15, 23, 42, 0.92), rgba(2, 6, 23, 0.92));
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 18px;
      box-shadow: 0 18px 60px rgba(0, 0, 0, 0.28);
      min-width: 0;
    }

    .card h3 {
      margin: 0 0 14px;
      font-size: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .stat {
      padding: 16px;
      border-radius: 18px;
      background: rgba(15, 23, 42, 0.76);
      border: 1px solid rgba(148, 163, 184, 0.16);
    }

    .stat .value {
      font-size: 28px;
      font-weight: 800;
      letter-spacing: -0.04em;
    }

    .stat .label {
      color: var(--muted);
      font-size: 12px;
      margin-top: 5px;
    }

    .status-pill {
      display: inline-flex;
      align-items: center;
      padding: 5px 9px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 800;
      border: 1px solid transparent;
      white-space: nowrap;
    }

    .configured, .local_configured {
      background: rgba(34, 197, 94, 0.12);
      color: #86efac;
      border-color: rgba(34, 197, 94, 0.25);
    }

    .pending_quota_or_deployment, .pending {
      background: rgba(245, 158, 11, 0.12);
      color: #fcd34d;
      border-color: rgba(245, 158, 11, 0.28);
    }

    .not_configured, .failed {
      background: rgba(239, 68, 68, 0.12);
      color: #fca5a5;
      border-color: rgba(239, 68, 68, 0.28);
    }

    .table-wrap {
      overflow-x: auto;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }

    th, td {
      text-align: left;
      border-bottom: 1px solid rgba(148, 163, 184, 0.16);
      padding: 10px 8px;
      vertical-align: top;
    }

    th {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }

    td {
      color: var(--text);
    }

    .muted {
      color: var(--muted);
    }

    .mono {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 12px;
      word-break: break-all;
    }

    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 14px;
    }

    .links {
      display: grid;
      gap: 10px;
    }

    a {
      color: #7dd3fc;
      text-decoration: none;
    }

    a:hover {
      text-decoration: underline;
    }

    .logbox {
      background: #020617;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 12px;
      max-height: 260px;
      overflow: auto;
      font-size: 12px;
      color: #cbd5e1;
      white-space: pre-wrap;
    }

    .toast {
      position: fixed;
      right: 24px;
      bottom: 24px;
      background: #020617;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px 16px;
      color: var(--text);
      display: none;
      max-width: 460px;
      box-shadow: 0 18px 70px rgba(0,0,0,0.35);
      z-index: 99;
    }

    .section-title {
      margin: 28px 0 14px;
      font-size: 20px;
      letter-spacing: -0.03em;
    }



    .chart-box {
      background: #020617;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px;
      font-size: 13px;
      color: #cbd5e1;
      white-space: normal;
      min-height: 160px;
    }

    .chart-box .bar-row {
      display: grid;
      grid-template-columns: 170px minmax(180px, 1fr) 70px;
      align-items: center;
      gap: 12px;
      margin: 14px 0;
      min-height: 28px;
    }

    .chart-box .bar-track {
      height: 14px;
      background: rgba(148, 163, 184, 0.14);
      border-radius: 999px;
      overflow: hidden;
      border: 1px solid rgba(148, 163, 184, 0.18);
    }

    .chart-box .bar-fill {
      height: 100%;
      background: linear-gradient(90deg, #38bdf8, #22c55e);
      border-radius: 999px;
      min-width: 6px;
      box-shadow: 0 0 14px rgba(56, 189, 248, 0.35);
    }

    .chart-box .bar-label {
      color: #cbd5e1;
      overflow-wrap: anywhere;
      font-weight: 600;
    }

    .chart-box .bar-value {
      text-align: right;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      color: #f8fafc;
      font-weight: 700;
    }

    .chart-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }

    .bar-row {
      display: grid;
      grid-template-columns: 150px 1fr 70px;
      align-items: center;
      gap: 10px;
      margin: 10px 0;
      font-size: 13px;
    }

    .bar-track {
      height: 12px;
      background: rgba(148, 163, 184, 0.16);
      border-radius: 999px;
      overflow: hidden;
      border: 1px solid rgba(148, 163, 184, 0.12);
    }

    .bar-fill {
      height: 100%;
      background: linear-gradient(90deg, #0ea5e9, #22c55e);
      border-radius: 999px;
      min-width: 3px;
    }

    .bar-label {
      color: var(--muted);
      word-break: break-word;
    }

    .bar-value {
      text-align: right;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      color: #e5e7eb;
    }

    @media (max-width: 1100px) {
      .chart-grid {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 1100px) {
      .layout {
        grid-template-columns: 1fr;
      }

      aside {
        position: static;
        height: auto;
      }

      .grid.stats {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .grid.two, .grid.three {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="layout">
    <aside>
      <div class="brand">
        <div class="logo">VA</div>
        <div>
          <h1>Voice Agent Admin</h1>
          <p>Provider routing, logs, analytics</p>
        </div>
      </div>

      <label>Base URL</label>
      <input id="baseUrl" value="http://localhost:4002" />

      <label>Admin API Key</label>
      <input id="adminKey" type="password" placeholder="Paste ADMIN_API_KEY" />

      <label>Company API Key</label>
      <input id="companyKey" type="password" placeholder="Paste COMPANY_API_KEYS value" />

      <label>Company ID</label>
      <input id="companyId" value="2f2d77c9-9a60-422a-b6bb-ba475112255e" />

      <div class="actions">
        <button onclick="saveSettings()">Save</button>
        <button class="secondary" onclick="loadAll()">Refresh</button>
        <button class="danger" onclick="clearSavedKeys()">Clear Saved Keys</button>
      </div>

      <p class="muted" style="font-size:11px;line-height:1.4;">
        Local development only. Keys are stored in this browser's localStorage.
        Do not use production keys here.
      </p>

      <div class="section-title">Quick Links</div>
      <div class="links">
        <a href="/docs" target="_blank">Swagger Docs</a>
        <a href="/providers/status" target="_blank">Provider Status API</a>
        <a href="/analytics/provider-usage?days=7" target="_blank">Provider Usage API</a>
        <a href="/debug/errors/recent?limit=10" target="_blank">Recent Errors API</a>
        <a href="/demo/local_voice.html" target="_blank">Local Voice Demo</a>
        <a href="/demo/openai_voice.html" target="_blank">OpenAI Voice Demo</a>
      </div>
    </aside>

    <main>
      <div class="topbar">
        <div>
          <h2>Admin Dashboard</h2>
          <p>Monitor provider health, company config, fallbacks, sessions, and voice/chat usage.</p>
        </div>
        <div class="badge">● Local Dev Mode</div>
      </div>

      <div class="grid stats">
        <div class="stat">
          <div id="totalEvents" class="value">—</div>
          <div class="label">Total Events</div>
        </div>
        <div class="stat">
          <div id="totalErrors" class="value">—</div>
          <div class="label">Provider Errors</div>
        </div>
        <div class="stat">
          <div id="totalFallbacks" class="value">—</div>
          <div class="label">Fallbacks</div>
        </div>
        <div class="stat">
          <div id="voiceEvents" class="value">—</div>
          <div class="label">Voice Events</div>
        </div>
        <div class="stat">
          <div id="chatEvents" class="value">—</div>
          <div class="label">Chat Events</div>
        </div>
      </div>

      <div class="grid two">
        <div class="card">
          <h3>Provider Status <button class="secondary" onclick="loadProviderStatus()">Refresh</button></h3>
          <div id="providerStatus"></div>
        </div>

        <div class="card">
          <h3>Current Company Config <button class="secondary" onclick="loadCompanyConfig()">Refresh</button></h3>
          <div id="companyConfig" class="logbox">No config loaded yet.</div>
        </div>
      </div>

      <div class="section-title">Provider Switch Center</div>
      <div class="grid two">
        <div class="card">
          <h3>Update Provider Config</h3>

          <label>LLM Provider</label>
          <select id="llmProvider">
            <option value="bedrock">bedrock</option>
            <option value="openrouter">openrouter</option>
            <option value="ollama">ollama</option>
            <option value="gemini">gemini</option>
            <option value="anthropic">anthropic</option>
            <option value="huggingface">huggingface</option>
            <option value="openai">openai</option>
            <option value="azure_openai">azure_openai</option>
          </select>

          <label>LLM Model</label>
          <input id="llmModel" value="us.anthropic.claude-sonnet-4-6" />

          <label>STT Provider</label>
          <select id="sttProvider">
            <option value="deepgram">deepgram</option>
            <option value="azure_speech">azure_speech</option>
            <option value="openai">openai</option>
            <option value="elevenlabs">elevenlabs</option>
            <option value="whisper_cpp">whisper_cpp</option>
          </select>

          <label>TTS Provider</label>
          <select id="ttsProvider">
            <option value="azure_speech">azure_speech</option>
            <option value="cartesia">cartesia</option>
            <option value="aws_polly">aws_polly</option>
            <option value="deepgram">deepgram</option>
            <option value="elevenlabs">elevenlabs</option>
            <option value="openai">openai</option>
            <option value="mac_say">mac_say</option>
          </select>

          <label>Voice ID</label>
          <input id="voiceId" value="en-US-JennyNeural" />

          <label>System Prompt</label>
          <textarea id="systemPrompt">You are a helpful assistant. Keep answers short and clear.</textarea>

          <div class="actions">
            <button class="success" onclick="updateProviderConfig()">Apply Config</button>
            <button class="secondary" onclick="setPreset('enterpriseAws')">Enterprise AWS Mode</button>
            <button class="secondary" onclick="setPreset('bedrockAzure')">Azure Voice Mode</button>
            <button class="secondary" onclick="setPreset('cartesiaSonic')">Cartesia Sonic Mode</button>
            <button class="secondary" onclick="setPreset('ollamaAzure')">Local Demo Mode</button>
            <button class="secondary" onclick="setPreset('fallbackTest')">Fallback Test Mode</button>
          </div>
        </div>

        <div class="card">
          <h3>Chat Test</h3>
          <label>Message</label>
          <textarea id="chatMessage">Are you responding through the configured provider?</textarea>
          <div class="actions">
            <button onclick="sendChat()">Send Chat</button>
          </div>
          <label>Response</label>
          <div id="chatResponse" class="logbox">No chat response yet.</div>
        </div>
      </div>


      <div class="section-title">Voice Test</div>
      <div class="card">
        <h3>Configured Voice Test</h3>
        <p class="muted">Upload a short audio file and test the full configured STT → LLM → TTS pipeline.</p>

        <label>Upload Audio File</label>
        <input id="voiceFile" type="file" accept="audio/*" />

        <div class="actions">
          <button onclick="sendVoice()">Run Uploaded Audio Test</button>
        </div>

        <hr style="border:0;border-top:1px solid rgba(148,163,184,0.18); margin:18px 0;" />

        <label>Live Microphone Recording</label>
        <div class="actions">
          <button id="startRecordBtn" onclick="startRecording()">Start Recording</button>
          <button id="stopRecordBtn" class="danger" onclick="stopRecording()" disabled>Stop Recording</button>
          <button id="sendRecordedBtn" class="success" onclick="sendRecordedVoice()" disabled>Send Recorded Voice</button>
        </div>

        <p id="recordingStatus" class="muted">Recording status: idle</p>

        <label>Recorded Audio Preview</label>
        <audio id="recordedAudio" controls style="width:100%; margin-top:6px; display:none;"></audio>

        <label>Generated Assistant Audio</label>
        <audio id="voiceAudio" controls style="width:100%; margin-top:6px; display:none;"></audio>

        <label>Voice Response</label>
        <div id="voiceResponse" class="logbox">No voice response yet.</div>
      </div>

      <div class="section-title">Analytics</div>
      <div class="grid two">
        <div class="card">
          <h3>Provider Usage</h3>
          <div id="providerUsage"></div>
        </div>

        <div class="card">
          <h3>Recent Errors</h3>
          <div id="recentErrors"></div>
        </div>
      </div>




      <div class="section-title">Cost Monitoring</div>
      <div class="grid stats">
        <div class="stat">
          <div id="lastCostTotal" class="value">—</div>
          <div class="label">Last Voice Cost USD</div>
        </div>
        <div class="stat">
          <div id="lastCostStt" class="value">—</div>
          <div class="label">STT Cost</div>
        </div>
        <div class="stat">
          <div id="lastCostLlm" class="value">—</div>
          <div class="label">LLM Cost</div>
        </div>
        <div class="stat">
          <div id="lastCostTts" class="value">—</div>
          <div class="label">TTS Cost</div>
        </div>
        <div class="stat">
          <div id="lastAudioSeconds" class="value">—</div>
          <div class="label">Audio Seconds</div>
        </div>
      </div>

      <div class="section-title">Dashboard Charts</div>
      <div class="chart-grid">
        <div class="card">
          <h3>Provider Usage Chart <button class="secondary" onclick="loadDashboardCharts()">Refresh</button></h3>
          <div id="providerUsageChart" class="chart-box">No provider usage chart loaded yet.</div>
        </div>

        <div class="card">
          <h3>Event Summary Chart</h3>
          <div id="eventSummaryChart" class="chart-box">No event summary chart loaded yet.</div>
        </div>
      </div>


      <div class="section-title">Maintenance</div>
      <div class="card">
        <h3>Generated Audio Cleanup</h3>
        <p class="muted">
          Preview or delete generated audio files from app/static/generated.
          Use dry run first before deleting.
        </p>

        <label>Max Age Hours</label>
        <input id="cleanupMaxAgeHours" type="number" value="24" min="0" />

        <div class="actions">
          <button class="secondary" onclick="cleanupGeneratedAudio(true)">Preview Cleanup</button>
          <button class="danger" onclick="cleanupGeneratedAudio(false)">Delete Matching Files</button>
        </div>

        <label>Cleanup Result</label>
        <div id="cleanupResult" class="logbox">No cleanup action yet.</div>
      </div>

      <div class="section-title">Provider Benchmark</div>
      <div class="card">
        <h3>TTS Provider Benchmark</h3>
        <p class="muted">Compare TTS provider latency and generated audio output.</p>

        <label>Benchmark Text</label>
        <textarea id="benchmarkText">Hello, compare Azure Speech and Cartesia Sonic in English.</textarea>

        <label>TTS Providers</label>
        <input id="benchmarkProviders" value="azure_speech,cartesia" />

        <div class="actions">
          <button onclick="runTtsBenchmark()">Run TTS Benchmark</button>
          <button class="secondary" onclick="loadRecentBenchmarks()">Load Recent Benchmarks</button>
        </div>

        <label>Benchmark Result</label>
        <div id="benchmarkResult" class="logbox">No benchmark run yet.</div>

        <div id="benchmarkTable" style="margin-top:14px;"></div>
      </div>

      <div class="section-title">Recent Sessions</div>
      <div class="card">
        <h3>Sessions <button class="secondary" onclick="loadSessions()">Refresh</button></h3>
        <div id="recentSessions"></div>
      </div>

      <div class="section-title">Session Detail</div>
      <div class="card">
        <h3>Selected Session</h3>
        <div id="sessionDetail" class="logbox">Click a session to inspect details.</div>
      </div>
    </main>
  </div>

  <div id="toast" class="toast"></div>

<script>
  function $(id) {
    return document.getElementById(id);
  }

  function getBaseUrl() {
    return $("baseUrl").value.replace(/\\/$/, "");
  }

  function adminHeaders() {
    return {
      "X-Admin-API-Key": $("adminKey").value,
      "Content-Type": "application/json"
    };
  }

  function companyHeaders() {
    return {
      "X-Company-API-Key": $("companyKey").value,
      "Content-Type": "application/json"
    };
  }

  function toast(message) {
    const t = $("toast");
    t.textContent = message;
    t.style.display = "block";
    setTimeout(() => t.style.display = "none", 4200);
  }


  function clearSavedKeys() {
    localStorage.removeItem("va_admin_key");
    localStorage.removeItem("va_company_key");
    $("adminKey").value = "";
    $("companyKey").value = "";
    toast("Saved dashboard keys cleared from this browser.");
  }

  function saveSettings() {
    localStorage.setItem("va_base_url", $("baseUrl").value);
    localStorage.setItem("va_admin_key", $("adminKey").value);
    localStorage.setItem("va_company_key", $("companyKey").value);
    localStorage.setItem("va_company_id", $("companyId").value);
    toast("Settings saved locally in this browser.");
  }

  function loadSettings() {
    $("baseUrl").value = localStorage.getItem("va_base_url") || "http://localhost:4002";
    $("adminKey").value = localStorage.getItem("va_admin_key") || "";
    $("companyKey").value = localStorage.getItem("va_company_key") || "";
    $("companyId").value = localStorage.getItem("va_company_id") || "2f2d77c9-9a60-422a-b6bb-ba475112255e";
  }

  async function apiGet(path) {
    const res = await fetch(getBaseUrl() + path, { headers: adminHeaders() });
    if (!res.ok) throw new Error(await res.text());
    return await res.json();
  }


  async function apiPostAdmin(path, body) {
    const res = await fetch(getBaseUrl() + path, {
      method: "POST",
      headers: adminHeaders(),
      body: JSON.stringify(body || {})
    });
    if (!res.ok) throw new Error(await res.text());
    return await res.json();
  }

  async function apiPatch(path, body) {
    const res = await fetch(getBaseUrl() + path, {
      method: "PATCH",
      headers: adminHeaders(),
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(await res.text());
    return await res.json();
  }

  function statusPill(value) {
    const cls = String(value || "not_configured").replaceAll(" ", "_");
    return `<span class="status-pill ${cls}">${value}</span>`;
  }

  function renderProviderGroup(title, data) {
    let rows = Object.entries(data || {}).map(([provider, status]) => `
      <tr>
        <td class="mono">${provider}</td>
        <td>${statusPill(status)}</td>
      </tr>
    `).join("");

    return `
      <div style="margin-bottom:16px;">
        <h4 style="margin:10px 0;color:#cbd5e1;">${title}</h4>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Provider</th><th>Status</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      </div>
    `;
  }

  async function loadProviderStatus() {
    try {
      const data = await apiGet("/providers/status");
      $("providerStatus").innerHTML =
        renderProviderGroup("LLM Providers", data.llm_providers) +
        renderProviderGroup("STT Providers", data.stt_providers) +
        renderProviderGroup("TTS Providers", data.tts_providers) +
        renderProviderGroup("Realtime Providers", data.realtime_providers);
    } catch (err) {
      $("providerStatus").innerHTML = `<div class="logbox">${err.message}</div>`;
    }
  }

  async function loadCompanyConfig() {
    const companyId = $("companyId").value;
    try {
      const data = await apiGet(`/admin/companies/${companyId}/full-config`);
      $("companyConfig").textContent = JSON.stringify(data, null, 2);

      const ai = data.ai_settings || data.ai || {};
      const voice = data.voice_settings || data.voice || {};

      if (ai.llm_provider) $("llmProvider").value = ai.llm_provider;
      if (ai.llm_model) $("llmModel").value = ai.llm_model;
      if (ai.system_prompt) $("systemPrompt").value = ai.system_prompt;

      if (voice.stt_provider) $("sttProvider").value = voice.stt_provider;
      if (voice.tts_provider) $("ttsProvider").value = voice.tts_provider;
      if (voice.voice_id) $("voiceId").value = voice.voice_id;

    } catch (err) {
      $("companyConfig").textContent = err.message;
    }
  }

  async function loadAnalytics() {
    const companyId = $("companyId").value;
    try {
      const summary = await apiGet(`/analytics/company-summary?company_id=${companyId}&days=7`);
      const s = summary.summary || {};
      $("totalEvents").textContent = s.total_events ?? "0";
      $("totalErrors").textContent = s.total_errors ?? "0";
      $("totalFallbacks").textContent = s.total_fallbacks ?? "0";
      $("voiceEvents").textContent = s.total_voice_events ?? "0";
      $("chatEvents").textContent = s.total_chat_events ?? "0";
    } catch (err) {
      toast("Analytics summary failed: " + err.message);
    }

    try {
      const usage = await apiGet("/analytics/provider-usage?days=7");
      const rows = (usage.provider_usage || []).map(row => `
        <tr>
          <td class="mono">${row.provider || "unknown"}</td>
          <td>${row.event_type || "unknown"}</td>
          <td>${row.count}</td>
        </tr>
      `).join("");

      $("providerUsage").innerHTML = `
        <div class="table-wrap">
          <table>
            <thead><tr><th>Provider</th><th>Event Type</th><th>Count</th></tr></thead>
            <tbody>${rows || "<tr><td colspan='3'>No usage found.</td></tr>"}</tbody>
          </table>
        </div>
      `;
    } catch (err) {
      $("providerUsage").innerHTML = `<div class="logbox">${err.message}</div>`;
    }
  }


  function renderBarChart(rows, labelKey, valueKey) {
    const maxValue = Math.max(...(rows || []).map(row => Number(row[valueKey] || 0)), 1);

    return (rows || []).map(row => {
      const value = Number(row[valueKey] || 0);
      const width = Math.max((value / maxValue) * 100, value > 0 ? 3 : 0);

      return `
        <div class="bar-row">
          <div class="bar-label">${row[labelKey] || "unknown"}</div>
          <div class="bar-track">
            <div class="bar-fill" style="width:${width}%"></div>
          </div>
          <div class="bar-value">${value}</div>
        </div>
      `;
    }).join("") || "<p class='muted'>No chart data available.</p>";
  }

  async function loadDashboardCharts() {
    const companyId = $("companyId").value;

    try {
      const usage = await apiGet("/analytics/provider-usage?days=7");

      const providerTotals = {};

      for (const row of usage.provider_usage || []) {
        const rawProvider = row.provider || "unknown";
        const count = Number(row.count || 0);

        const providers = String(rawProvider)
          .split(",")
          .map(item => item.trim())
          .filter(Boolean);

        for (const provider of providers) {
          providerTotals[provider] = (providerTotals[provider] || 0) + count;
        }
      }

      const providerRows = Object.entries(providerTotals)
        .map(([provider, count]) => ({ provider, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10);

      $("providerUsageChart").innerHTML = renderBarChart(providerRows, "provider", "count");
    } catch (err) {
      $("providerUsageChart").textContent = err.message;
    }

    try {
      const summary = await apiGet(`/analytics/company-summary?company_id=${companyId}&days=7`);
      const s = summary.summary || {};

      const eventRows = [
        { label: "Total Events", count: s.total_events || 0 },
        { label: "Voice Events", count: s.total_voice_events || 0 },
        { label: "Chat Events", count: s.total_chat_events || 0 },
        { label: "Fallbacks", count: s.total_fallbacks || 0 },
        { label: "Errors", count: s.total_errors || 0 },
      ];

      $("eventSummaryChart").innerHTML = renderBarChart(eventRows, "label", "count");
    } catch (err) {
      $("eventSummaryChart").textContent = err.message;
    }
  }

  async function loadErrors() {
    try {
      const data = await apiGet("/debug/errors/recent?limit=8");
      const rows = (data.errors || []).map(err => `
        <tr>
          <td class="mono">${err.created_at || ""}</td>
          <td>${err.provider || ""}</td>
          <td>${(err.metadata && err.metadata.stage) || ""}</td>
          <td class="mono">${String(err.error || "").slice(0, 160)}</td>
        </tr>
      `).join("");

      $("recentErrors").innerHTML = `
        <div class="table-wrap">
          <table>
            <thead><tr><th>Created</th><th>Provider</th><th>Stage</th><th>Error</th></tr></thead>
            <tbody>${rows || "<tr><td colspan='4'>No recent errors.</td></tr>"}</tbody>
          </table>
        </div>
      `;
    } catch (err) {
      $("recentErrors").innerHTML = `<div class="logbox">${err.message}</div>`;
    }
  }


  function renderBenchmarkRows(results) {
    const rows = (results || []).map(row => `
      <tr>
        <td class="mono">${row.provider || ""}</td>
        <td>${row.status || ""}</td>
        <td>${row.latency_ms || ""}</td>
        <td>${row.audio_url ? `<a href="${getBaseUrl() + row.audio_url}" target="_blank">Play Audio</a>` : ""}</td>
        <td class="mono">${row.error ? String(row.error).slice(0, 180) : ""}</td>
      </tr>
    `).join("");

    return `
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Provider</th>
              <th>Status</th>
              <th>Latency ms</th>
              <th>Audio</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>${rows || "<tr><td colspan='5'>No benchmark results.</td></tr>"}</tbody>
        </table>
      </div>
    `;
  }


  async function cleanupGeneratedAudio(dryRun) {
    const maxAgeHours = $("cleanupMaxAgeHours").value || 24;

    if (!dryRun) {
      const confirmed = confirm(
        `Delete generated audio files older than ${maxAgeHours} hour(s)?`
      );

      if (!confirmed) {
        return;
      }
    }

    $("cleanupResult").textContent = dryRun
      ? "Previewing generated audio cleanup..."
      : "Deleting generated audio files...";

    try {
      const res = await fetch(
        `${getBaseUrl()}/system/generated-audio?dry_run=${dryRun}&max_age_hours=${encodeURIComponent(maxAgeHours)}`,
        {
          method: "DELETE",
          headers: adminHeaders()
        }
      );

      const text = await res.text();

      try {
        const data = JSON.parse(text);
        $("cleanupResult").textContent = JSON.stringify(data, null, 2);

        if (dryRun) {
          toast(`Preview complete: ${data.matched_count || 0} file(s) matched.`);
        } else {
          toast(`Cleanup complete: ${data.deleted_count || 0} file(s) deleted.`);
        }
      } catch {
        $("cleanupResult").textContent = text;
      }

    } catch (err) {
      $("cleanupResult").textContent = err.message;
      toast("Generated audio cleanup failed.");
    }
  }

  async function runTtsBenchmark() {
    const text = encodeURIComponent($("benchmarkText").value);
    const providers = encodeURIComponent($("benchmarkProviders").value);

    $("benchmarkResult").textContent = "Running TTS benchmark...";

    try {
      const data = await apiPostAdmin(`/benchmark/tts?text=${text}&providers=${providers}`, {});
      $("benchmarkResult").textContent = JSON.stringify(data, null, 2);
      $("benchmarkTable").innerHTML = renderBenchmarkRows(data.results || []);
      toast("Benchmark completed.");
    } catch (err) {
      $("benchmarkResult").textContent = err.message;
      toast("Benchmark failed.");
    }
  }

  async function loadRecentBenchmarks() {
    try {
      const data = await apiGet("/benchmark/recent?limit=5");
      $("benchmarkResult").textContent = JSON.stringify(data, null, 2);

      const latest = data.benchmarks && data.benchmarks.length > 0
        ? data.benchmarks[0].metadata
        : null;

      if (latest && latest.results) {
        $("benchmarkTable").innerHTML = renderBenchmarkRows(latest.results);
      }

      toast("Recent benchmarks loaded.");
    } catch (err) {
      $("benchmarkResult").textContent = err.message;
      toast("Could not load recent benchmarks.");
    }
  }

  async function loadSessions() {
    try {
      const data = await apiGet("/debug/sessions/recent?limit=10");
      const rows = (data.sessions || []).map(s => `
        <tr>
          <td class="mono"><a href="#" onclick="loadSessionDetail('${s.session_id}'); return false;">${s.session_id}</a></td>
          <td>${s.channel || ""}</td>
          <td>${s.status || ""}</td>
          <td class="mono">${s.created_at || ""}</td>
        </tr>
      `).join("");

      $("recentSessions").innerHTML = `
        <div class="table-wrap">
          <table>
            <thead><tr><th>Session ID</th><th>Channel</th><th>Status</th><th>Created</th></tr></thead>
            <tbody>${rows || "<tr><td colspan='4'>No recent sessions.</td></tr>"}</tbody>
          </table>
        </div>
      `;
    } catch (err) {
      $("recentSessions").innerHTML = `<div class="logbox">${err.message}</div>`;
    }
  }

  async function loadSessionDetail(sessionId) {
    try {
      const data = await apiGet(`/debug/sessions/${sessionId}?mongo_event_limit=50`);
      $("sessionDetail").textContent = JSON.stringify(data, null, 2);
    } catch (err) {
      $("sessionDetail").textContent = err.message;
    }
  }

  function setPreset(name) {

    if (name === "enterpriseAws") {
      $("llmProvider").value = "bedrock";
      $("llmModel").value = "us.anthropic.claude-sonnet-4-6";
      $("sttProvider").value = "deepgram";
      $("ttsProvider").value = "aws_polly";
      $("voiceId").value = "Joanna";
    }

    if (name === "bedrockAzure") {
      $("llmProvider").value = "bedrock";
      $("llmModel").value = "us.anthropic.claude-sonnet-4-6";
      $("sttProvider").value = "deepgram";
      $("ttsProvider").value = "azure_speech";
      $("voiceId").value = "en-US-JennyNeural";
    }


    if (name === "cartesiaSonic") {
      $("llmProvider").value = "bedrock";
      $("llmModel").value = "us.anthropic.claude-sonnet-4-6";
      $("sttProvider").value = "deepgram";
      $("ttsProvider").value = "cartesia";
      $("voiceId").value = "Gemma - Decisive Agent";
    }

    if (name === "ollamaAzure") {
      $("llmProvider").value = "ollama";
      $("llmModel").value = "llama3.2:1b";
      $("sttProvider").value = "deepgram";
      $("ttsProvider").value = "azure_speech";
      $("voiceId").value = "en-US-JennyNeural";
    }

    if (name === "fallbackTest") {
      $("llmProvider").value = "azure_openai";
      $("llmModel").value = "gpt-4o-mini-dev";
      $("sttProvider").value = "deepgram";
      $("ttsProvider").value = "azure_speech";
      $("voiceId").value = "en-US-JennyNeural";
    }
  }

  async function updateProviderConfig() {
    const companyId = $("companyId").value;

    const body = {
      llm_provider: $("llmProvider").value,
      llm_model: $("llmModel").value,
      temperature: 0.5,
      system_prompt: $("systemPrompt").value,
      voice_mode: "configured_batch",
      stt_provider: $("sttProvider").value,
      stt_model: $("sttProvider").value === "deepgram" ? "nova-3" : $("sttProvider").value,
      tts_provider: $("ttsProvider").value,
      tts_model: $("ttsProvider").value === "cartesia" ? "sonic-3" : $("ttsProvider").value,
      voice_id: $("voiceId").value,
      language: $("ttsProvider").value === "azure_speech" ? "en-US" : "en"
    };

    try {
      const data = await apiPatch(`/admin/companies/${companyId}/provider-config`, body);
      toast("Provider config updated.");
      $("companyConfig").textContent = JSON.stringify(data, null, 2);
      await loadAll();
    } catch (err) {
      toast("Provider config failed: " + err.message);
    }
  }

  async function sendChat() {
    const companyId = $("companyId").value;
    const body = {
      company_id: companyId,
      session_id: null,
      message: $("chatMessage").value,
      channel: "dashboard"
    };

    try {
      const res = await fetch(getBaseUrl() + "/chat/message", {
        method: "POST",
        headers: companyHeaders(),
        body: JSON.stringify(body)
      });

      const text = await res.text();

      try {
        $("chatResponse").textContent = JSON.stringify(JSON.parse(text), null, 2);
      } catch {
        $("chatResponse").textContent = text;
      }

      await loadAnalytics();
      await loadSessions();

    } catch (err) {
      $("chatResponse").textContent = err.message;
    }
  }



  let mediaRecorder = null;
  let recordedChunks = [];
  let recordedBlob = null;

  async function startRecording() {
    try {
      recordedChunks = [];
      recordedBlob = null;

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      let options = {};
      if (MediaRecorder.isTypeSupported("audio/webm")) {
        options = { mimeType: "audio/webm" };
      } else if (MediaRecorder.isTypeSupported("audio/mp4")) {
        options = { mimeType: "audio/mp4" };
      }

      mediaRecorder = new MediaRecorder(stream, options);

      mediaRecorder.ondataavailable = function(event) {
        if (event.data && event.data.size > 0) {
          recordedChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = function() {
        recordedBlob = new Blob(recordedChunks, { type: mediaRecorder.mimeType || "audio/webm" });

        const recordedAudio = $("recordedAudio");
        recordedAudio.src = URL.createObjectURL(recordedBlob);
        recordedAudio.style.display = "block";
        recordedAudio.load();

        $("sendRecordedBtn").disabled = false;
        $("recordingStatus").textContent = "Recording status: recorded and ready to send";

        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();

      $("startRecordBtn").disabled = true;
      $("stopRecordBtn").disabled = false;
      $("sendRecordedBtn").disabled = true;
      $("recordingStatus").textContent = "Recording status: recording... speak now";

      toast("Recording started.");

    } catch (err) {
      $("recordingStatus").textContent = "Recording status: microphone access failed";
      toast("Microphone error: " + err.message);
    }
  }

  function stopRecording() {
    if (!mediaRecorder || mediaRecorder.state === "inactive") {
      toast("No active recording.");
      return;
    }

    mediaRecorder.stop();

    $("startRecordBtn").disabled = false;
    $("stopRecordBtn").disabled = true;

    toast("Recording stopped.");
  }

  async function sendRecordedVoice() {
    if (!recordedBlob) {
      toast("No recorded audio available.");
      return;
    }

    const companyId = $("companyId").value;

    const extension = recordedBlob.type.includes("mp4") ? "mp4" : "webm";
    const file = new File([recordedBlob], `dashboard-recording.${extension}`, {
      type: recordedBlob.type || "audio/webm"
    });

    const formData = new FormData();
    formData.append("company_id", companyId);
    formData.append("channel", "dashboard_live_recording");
    formData.append("audio_file", file);

    $("voiceResponse").textContent = "Sending recorded voice to configured voice pipeline...";

    try {
      const res = await fetch(getBaseUrl() + "/voice/configured-batch", {
        method: "POST",
        headers: {
          "X-Company-API-Key": $("companyKey").value
        },
        body: formData
      });

      const text = await res.text();

      let data;
      try {
        data = JSON.parse(text);
        $("voiceResponse").textContent = JSON.stringify(data, null, 2);
        updateCostCards(data.cost_estimate);
      } catch {
        $("voiceResponse").textContent = text;
        return;
      }

      if (!res.ok) {
        toast("Recorded voice test failed.");
        await loadErrors();
        return;
      }

      if (data.audio_url) {
        const audio = $("voiceAudio");
        audio.src = getBaseUrl() + data.audio_url;
        audio.style.display = "block";
        audio.load();
      }

      updateCostCards(data.cost_estimate);

      updateCostCards(data.cost_estimate);

      toast("Recorded voice test completed.");
      await loadAnalytics();
      await loadSessions();

    } catch (err) {
      $("voiceResponse").textContent = err.message;
      toast("Recorded voice test failed: " + err.message);
    }
  }


  function updateCostCards(costEstimate) {
    if (!costEstimate) {
      return;
    }

    $("lastCostTotal").textContent = costEstimate.estimated_total_cost_usd ?? "—";
    $("lastCostStt").textContent = costEstimate.estimated_stt_cost_usd ?? "—";
    $("lastCostLlm").textContent = costEstimate.estimated_llm_cost_usd ?? "—";
    $("lastCostTts").textContent = costEstimate.estimated_tts_cost_usd ?? "—";
    $("lastAudioSeconds").textContent = costEstimate.estimated_audio_seconds ?? "—";
  }

  async function sendVoice() {
    const companyId = $("companyId").value;
    const fileInput = $("voiceFile");

    if (!fileInput.files || fileInput.files.length === 0) {
      toast("Please select an audio file first.");
      return;
    }

    const formData = new FormData();
    formData.append("company_id", companyId);
    formData.append("channel", "dashboard_configured_voice");
    formData.append("audio_file", fileInput.files[0]);

    $("voiceResponse").textContent = "Running voice pipeline...";

    try {
      const res = await fetch(getBaseUrl() + "/voice/configured-batch", {
        method: "POST",
        headers: {
          "X-Company-API-Key": $("companyKey").value
        },
        body: formData
      });

      const text = await res.text();

      let data;
      try {
        data = JSON.parse(text);
        $("voiceResponse").textContent = JSON.stringify(data, null, 2);
        updateCostCards(data.cost_estimate);
      } catch {
        $("voiceResponse").textContent = text;
        return;
      }

      if (!res.ok) {
        toast("Voice test failed.");
        await loadErrors();
        return;
      }

      if (data.audio_url) {
        const audio = $("voiceAudio");
        audio.src = getBaseUrl() + data.audio_url;
        audio.style.display = "block";
        audio.load();
      }

      toast("Voice test completed.");
      await loadAnalytics();
      await loadSessions();

    } catch (err) {
      $("voiceResponse").textContent = err.message;
      toast("Voice test failed: " + err.message);
    }
  }

  async function loadAll() {
    saveSettings();
    await Promise.allSettled([
      loadProviderStatus(),
      loadCompanyConfig(),
      loadAnalytics(),
      loadDashboardCharts(),
      loadErrors(),
      loadSessions()
    ]);
  }

  loadSettings();
  loadAll();
</script>
</body>
</html>
        """
    )
