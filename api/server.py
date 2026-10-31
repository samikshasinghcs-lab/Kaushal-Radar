"""Kaushal Radar prototype HTTP API."""

import json
import os
import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer

from ai.final_service import (
    generate_district_report,
    query_district,
    create_decision_summary
)


HOST = os.getenv("KAUSHAL_HOST", "127.0.0.1")
PORT = int(os.getenv("KAUSHAL_PORT", "8000"))
API_TOKEN = os.getenv("KAUSHAL_API_TOKEN", "")


class KaushalHandler(BaseHTTPRequestHandler):

    def send_json(self, status, payload):

        body = json.dumps(payload, indent=2).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def authorised(self):

        if not API_TOKEN:
            self.send_json(503, {
                "error": "API authentication is not configured."
            })
            return False

        supplied = self.headers.get("Authorization", "")
        expected = "Bearer " + API_TOKEN

        if not hmac.compare_digest(supplied, expected):
            self.send_json(401, {
                "error": "Unauthorised request."
            })
            return False

        return True

    def do_GET(self):

        if self.path == "/health":
            self.send_json(200, {
                "system": "KAUSHAL_RADAR",
                "status": "OPERATIONAL",
                "deployment": "PROTOTYPE"
            })
            return

        self.send_json(404, {"error": "Route not found."})

    def do_POST(self):

        if not self.authorised():
            return

        if self.path not in (
            "/api/district/report",
            "/api/district/query"
        ):
            self.send_json(404, {"error": "Route not found."})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))

            if length <= 0 or length > 1_000_000:
                self.send_json(413, {
                    "error": "Invalid request size."
                })
                return

            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))

            if not isinstance(data, dict):
                raise ValueError("Request must be a JSON object.")

            district = data.get("district")
            evidence = data.get("evidence")

            if not isinstance(district, str) or not district.strip():
                raise ValueError("A district is required.")

            if not isinstance(evidence, list):
                raise ValueError("Evidence must be a list.")

            report = generate_district_report(
                district=district,
                evidence=evidence,
                expected_indicators=data.get(
                    "expected_indicators", []
                )
            )

            if self.path == "/api/district/report":

                self.send_json(200, {
                    "report": report,
                    "summary": create_decision_summary(report)
                })
                return

            question = data.get("question")

            answer = query_district(question, report)

            self.send_json(200, {
                "district": district,
                "answer": answer,
                "report_status": report["status"]
            })

        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self.send_json(400, {"error": str(error)})

        except Exception:
            self.send_json(500, {
                "error": "Internal processing error."
            })

    def log_message(self, format, *args):
        # Avoid logging request bodies or authentication headers.
        return


def main():

    server = HTTPServer((HOST, PORT), KaushalHandler)

    print(f"Kaushal Radar API listening on {HOST}:{PORT}")
    print("Prototype mode. Human review remains mandatory.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
