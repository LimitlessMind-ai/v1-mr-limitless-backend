from typing import Annotated
import logging
from livekit.agents import llm
import os
from dotenv import load_dotenv
import aiohttp
import asyncio
import json

logger = logging.getLogger("functions")
logger.setLevel(logging.INFO)

# Initialize Gemini API key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

class AssistantFnc(llm.FunctionContext):
    def __init__(self, room=None, participant=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_user_transcript = None
        self.room = room  # Store the room object
        self.participant = participant  # Store the participant
        # Initialize environment variables
        load_dotenv(dotenv_path=".env.local")


    @llm.ai_callable()
    async def get_weather(
            self,
            location: Annotated[
                str, llm.TypeInfo(description="The location to get the weather for")
            ],
    ):
        """Called when the user asks about the weather. This function will return the weather for the given location."""
        logger.info(f"getting weather for {location}")
        url = f"https://wttr.in/{location}?format=%C+%t"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    weather_data = await response.text()
                    return f"The weather in {location} is {weather_data}."
                else:
                    raise f"Failed to get weather data, status code: {response.status}"


    @llm.ai_callable()
    async def generate_prompt(self):
        """
        Collects the conversation history and participant email from the current AgentCallContext 
        and sends it to the Make webhook endpoint.
        """
        from livekit.agents.pipeline.pipeline_agent import AgentCallContext
        import aiohttp
        import asyncio
        import json

        logger.info("Scheduling prompt generation")

        try:
            call_ctx = AgentCallContext.get_current()
        except LookupError:
            return "No active call context found."

        if not call_ctx:
            return "Call context is empty."

        # Extract the conversation messages
        chat_messages = call_ctx.agent.chat_ctx.messages

        # Get participant metadata and extract email
        metadata = json.loads(self.participant.metadata or '{"language": "en", "email": ""}')
        email = metadata.get("email", "")

        # Prepare the conversation history as a string
        conversation_text = ""
        for msg in chat_messages:
            conversation_text += f"{msg.role}: {msg.content}\n"

        # Prepare the payload
        payload = {
            "email": email,
            "text": conversation_text
        }

        url = "https://hook.eu2.make.com/6vn9wwsfrfb4jddstvwn4anek27dykqo"

        # Create a delayed coroutine for sending the conversation text to the webhook
        async def send_delayed_prompt():
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(url, json=payload) as response:
                        status = response.status
                        body = await response.text()
                        logger.info(f"Webhook response - Status: {status}, Body: {body}")
                        if status == 200:
                            return "Your prompt is being generated."
                        if status == 100:
                            logger.error(f"Quick prompt generation is completed.")
                        if status == 101:
                            logger.error(f"High quality prompt generation is completed.")
                        else:
                            logger.error(f"Webhook failed with status: {status}")
                except Exception as e:
                    logger.error(f"Failed to send prompt to webhook: {e}")

        # Schedule the delayed prompt sending without awaiting it
        asyncio.create_task(send_delayed_prompt())

        return "Your prompt is being generated (with a delay before sending)."