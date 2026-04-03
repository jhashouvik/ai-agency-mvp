"""
ghl/formatter.py
─────────────────
Formats agent outputs into the GHL API payload structure.
Currently produces MOCK output — swap the push() function
below for real GHL REST calls when you have a live API key.

GHL API docs: https://highlevel.stoplight.io/docs/integrations
"""

import json


def format_ghl_payload(client_data: dict, outputs: dict) -> dict:
    """
    Build the full mock GHL payload from client data + agent outputs.
    Structure mirrors the real GHL REST API request bodies.
    """
    business = client_data.get("business_name", "Unknown Client")

    return {
        "_meta": {
            "note": "MOCK OUTPUT — replace push() in ghl/formatter.py with live GHL API calls",
            "ghl_docs": "https://highlevel.stoplight.io/docs/integrations",
        },

        # ── Contact record ─────────────────────────────────────────
        "contact": {
            "firstName": business,
            "email": "placeholder@client.com",
            "phone": "+440000000000",
            "source": "AI Agency System",
            "tags": ["AI-Generated", "Awaiting-Review", "New-Client"],
            "customFields": [
                {"key": "offer",         "field_value": client_data.get("offer", "")},
                {"key": "audience",      "field_value": client_data.get("audience", "")},
                {"key": "goals",         "field_value": client_data.get("goals", "")},
                {"key": "budget",        "field_value": client_data.get("budget", "")},
                {"key": "positioning",   "field_value": client_data.get("positioning", "")},
            ],
        },

        # ── Pipeline / opportunity ──────────────────────────────────
        "opportunity": {
            "pipelineName": f"{business} — Fulfilment",
            "pipelineStages": [
                "1. Strategy Approved",
                "2. Copy in Review",
                "3. Funnel Being Built",
                "4. Automations Live",
                "5. Campaign Launched",
            ],
            "currentStage": "1. Strategy Approved",
            "monetaryValue": 0,
            "status": "open",
        },

        # ── Automation triggers ─────────────────────────────────────
        "automation": {
            "workflowName": f"{business} — Onboarding Sequence",
            "triggerEvent": "Contact Created",
            "actions": [
                {"step": 1, "type": "Send Email",    "detail": "Welcome email (Email 1 from copy output)"},
                {"step": 2, "type": "Wait",           "detail": "2 days"},
                {"step": 3, "type": "Send Email",    "detail": "Value email (Email 2 from copy output)"},
                {"step": 4, "type": "Wait",           "detail": "2 days"},
                {"step": 5, "type": "Send SMS",      "detail": "Check-in message"},
                {"step": 6, "type": "Add Tag",       "detail": "Nurture-Active"},
                {"step": 7, "type": "Move Pipeline", "detail": "2. Copy in Review"},
            ],
            "note": "Full workflow logic is in the Automations tab above.",
        },

        # ── Funnel pages (structure only) ──────────────────────────
        "funnel": {
            "funnelName": f"{business} — Main Funnel",
            "pages": [
                {"name": "Opt-in Page",       "path": "/optin",    "status": "draft"},
                {"name": "Thank You Page",     "path": "/thankyou", "status": "draft"},
                {"name": "Sales Page",         "path": "/sales",    "status": "draft"},
                {"name": "Application Page",   "path": "/apply",    "status": "draft"},
            ],
            "note": "Full page-by-page spec is in the Funnel tab above.",
        },
    }


def render_ghl_json(client_data: dict, outputs: dict) -> str:
    """Return the GHL payload as a formatted JSON string for display."""
    payload = format_ghl_payload(client_data, outputs)
    return json.dumps(payload, indent=2)


# ── Production stub ────────────────────────────────────────────────
def push_to_ghl(client_data: dict, outputs: dict, api_key: str, location_id: str) -> dict:
    """
    Replace this function body with live GHL API calls.

    Example endpoints:
        POST https://rest.gohighlevel.com/v1/contacts/
        POST https://rest.gohighlevel.com/v1/opportunities/
        POST https://rest.gohighlevel.com/v1/contacts/{id}/workflow/{workflowId}

    Returns a dict of {endpoint: response_status}.
    """
    raise NotImplementedError(
        "push_to_ghl() is a production stub. "
        "Add your GHL API key to .env and implement the REST calls here."
    )
