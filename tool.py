def send_whatsapp_text(to: str, message: str) -> dict:
    """
    Plain Python function (callable from FastAPI webhook).
    Raises RuntimeError if API fails.
    """
    token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    if not token or not phone_id:
        raise ValueError("Missing WHATSAPP_ACCESS_TOKEN or WHATSAPP_PHONE_NUMBER_ID.")

    if not to:
        raise ValueError("Recipient `to` is required.")

    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": (message or "")[:3500]},
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)

    try:
        data = resp.json()
    except Exception:
        resp.raise_for_status()
        return {"ok": True, "result": "sent (no json)"}

    if resp.status_code >= 400 or "error" in data:
        raise RuntimeError(f"WhatsApp API error: {data}")

    return {"ok": True, "result": data}


@tool("send_whatsapp_message")
def send_whatsapp_message(to: str, message: str) -> dict:
    """
    CrewAI Tool wrapper. Use inside Agents.
    For webhook (main.py), call send_whatsapp_text() instead.
    """
    return send_whatsapp_text(to=to, message=message)