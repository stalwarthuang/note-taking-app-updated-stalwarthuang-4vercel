from flask import Blueprint, request, Response, stream_with_context
import requests
import json

# Import config (handle both cases: with/without config.py)
try:
    from config import AI_API_KEY, AI_API_ENDPOINT, AI_MODEL
except ImportError:
    # Fallback to environment variables if config.py doesn't exist
    import os

    AI_API_KEY = os.getenv("AI_API_KEY", "")
    AI_API_ENDPOINT = os.getenv("AI_API_ENDPOINT", "")
    AI_MODEL = os.getenv("AI_MODEL", "Qwen/Qwen2-7B-Instruct")

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/ai/chat", methods=["POST"])
def ai_chat():
    """
    Proxy endpoint for AI chat requests
    This keeps the API key secure on the server side
    """
    try:
        data = request.json
        messages = data.get("messages", [])

        if not messages:
            return {"error": "No messages provided"}, 400

        if not AI_API_KEY:
            return {"error": "AI API key not configured"}, 500

        # Prepare the request to AI API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AI_API_KEY}",
        }

        payload = {"model": AI_MODEL, "messages": messages, "stream": True}

        # Make streaming request to AI API
        def generate():
            with requests.post(
                AI_API_ENDPOINT, headers=headers, json=payload, stream=True
            ) as response:
                if response.status_code != 200:
                    yield f"data: {json.dumps({'error': 'AI API error'})}\n\n"
                    return

                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        # Forward the streaming response to client
                        yield f"{decoded_line}\n"

        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    except Exception as e:
        return {"error": str(e)}, 500


@ai_bp.route("/ai/config", methods=["GET"])
def get_ai_config():
    """
    Get AI configuration (without exposing the API key)
    """
    return {
        "endpoint": "/api/ai/chat",  # Our proxy endpoint
        "model": AI_MODEL,
        "configured": bool(AI_API_KEY),
    }
