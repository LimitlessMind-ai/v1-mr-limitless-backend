from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from livekit import api
import os

router = APIRouter()

class TokenRequest(BaseModel):
    identity: str
    roomName: str
    language: str  # Add language field
    # Removed other fields as they're no longer needed for token generation

@router.get('/health')
def health_check():
    return {"status": "healthy"}

@router.post('/generate-token')
async def generate_token_endpoint(request: TokenRequest):
    # Pass language parameter to generate_token
    return generate_token(request.identity, request.roomName, request.language)

def generate_token(identity: str, room_name: str, language: str):
    try:
        # Create token with default permissions
        token = api.AccessToken(
            api_key=os.getenv('LIVEKIT_API_KEY'),
            api_secret=os.getenv('LIVEKIT_API_SECRET')
        )

        # Set token properties
        token.with_identity(identity)
        token.with_name(room_name)
        token.with_metadata(language)  # Add language as metadata
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True
        ))

        # Generate JWT token
        jwt_token = token.to_jwt()

        return {
            'token': jwt_token
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))