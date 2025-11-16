from fastapi import APIRouter
import os

# Try to import LiveKit server SDK; if missing, return a safe placeholder
try:
    from livekit import api
    HAVE_LIVEKIT = True
except Exception:
    HAVE_LIVEKIT = False

router = APIRouter()

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "XXXXX")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "YYYYY")
# Replace the host below with your actual project host (e.g. "wss://<project>.livekit.cloud")
LIVEKIT_URL = os.getenv(
    "LIVEKIT_URL", "wss://livekit-project-id.livekit.cloud")


@router.get("/livekit/token")
def get_token(identity: str = "user", room: str = "voice-room"):
    """Return a short-lived LiveKit access token and the LiveKit websocket URL.

    If the LiveKit server SDK is not installed, the route returns a placeholder
    token and instructive note so the developer can wire their own credentials.
    """
    if HAVE_LIVEKIT:
        token = api.AccessToken(
            LIVEKIT_API_KEY, LIVEKIT_API_SECRET, identity=identity)
        token.add_grant(api.VideoGrant(room=room))
        return {"token": token.to_jwt(), "url": LIVEKIT_URL}

    return {
        "token": "PLACEHOLDER_TOKEN",
        "url": LIVEKIT_URL,
        "note": "LiveKit server SDK not installed on this host. Install `livekit-server-sdk` and set LIVEKIT_API_KEY / LIVEKIT_API_SECRET environment variables to return real tokens."
    }
