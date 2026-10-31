# Kaushal Radar — Final Integration

## Purpose

Kaushal Radar is an evidence-grounded labour-market
decision-support prototype for Karnataka.

## Architecture

1. Evidence validation
2. Deterministic intelligence analysis
3. Contradiction and anomaly detection
4. Uncertainty reporting
5. Source and numeric validation
6. Security and governance checks
7. API delivery
8. Dashboard presentation
9. Human officer review

## API routes

GET /health

POST /api/district/report

POST /api/district/query

## Authentication

The prototype API requires a bearer token.

Set KAUSHAL_API_TOKEN before starting the server.

This is not a government identity-management integration.

## Run

python -m api.server

## Tests

python -m unittest tests.test_final_integration -v

## Limitations

- No live government data connection is assumed.
- No live LLM provider is connected by this integration.
- Synthetic data is only for demonstration.
- API authentication is prototype-level.
- District access requires integration with an authenticated
  government identity and authorisation system.
- The dashboard is a standalone prototype.
- Human officers retain all policy and funding authority.
