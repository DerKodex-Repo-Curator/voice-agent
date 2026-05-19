import json
import os
import urllib.request
import urllib.error


BASE_URL = os.getenv("BASE_URL", "http://localhost:4002")


def load_env(path=".env"):
    data = {}

    if not os.path.exists(path):
        return data

    with open(path, "r") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()

    return data


ENV = load_env()

ADMIN_API_KEY = ENV.get("ADMIN_API_KEY", "")
COMPANY_API_KEYS_RAW = ENV.get("COMPANY_API_KEYS", "{}")

try:
    COMPANY_API_KEYS = json.loads(COMPANY_API_KEYS_RAW)
except Exception:
    COMPANY_API_KEYS = {}

COMPANY_ID = next(iter(COMPANY_API_KEYS.keys()), "")
COMPANY_API_KEY = COMPANY_API_KEYS.get(COMPANY_ID, "")


def request(method, path, headers=None, body=None):
    url = BASE_URL.rstrip("/") + path

    data = None

    if body is not None:
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers=headers or {},
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            text = response.read().decode("utf-8")
            return response.status, text
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")
    except Exception as exc:
        return 0, str(exc)


def print_result(name, status, body):
    ok = 200 <= status < 300
    print(f"{'✅' if ok else '❌'} {name}: {status}")
    preview = body[:350].replace("\n", " ")
    print(f"   {preview}")


def main():
    print(f"Running smoke test against {BASE_URL}")
    print("-" * 80)

    tests = [
        (
            "System readiness",
            "GET",
            "/system/readiness",
            {"X-Admin-API-Key": ADMIN_API_KEY},
            None,
        ),
        (
            "Provider status",
            "GET",
            "/providers/status",
            {},
            None,
        ),
        (
            "Company summary",
            "GET",
            f"/analytics/company-summary?company_id={COMPANY_ID}&days=7",
            {"X-Admin-API-Key": ADMIN_API_KEY},
            None,
        ),
        (
            "Recent sessions",
            "GET",
            "/debug/sessions/recent?limit=3",
            {"X-Admin-API-Key": ADMIN_API_KEY},
            None,
        ),
    ]

    for name, method, path, headers, body in tests:
        status, response_body = request(method, path, headers, body)
        print_result(name, status, response_body)

    if COMPANY_ID and COMPANY_API_KEY:
        body = {
            "company_id": COMPANY_ID,
            "session_id": None,
            "message": "Smoke test: say hello in one short sentence.",
            "channel": "smoke_test",
        }

        status, response_body = request(
            "POST",
            "/chat/message",
            {
                "Content-Type": "application/json",
                "X-Company-API-Key": COMPANY_API_KEY,
            },
            body,
        )

        print_result("Chat message", status, response_body)
    else:
        print("⚠️ Skipped chat test because COMPANY_API_KEYS could not be parsed.")


if __name__ == "__main__":
    main()
