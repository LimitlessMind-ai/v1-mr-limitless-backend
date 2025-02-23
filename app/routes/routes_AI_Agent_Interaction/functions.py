from typing import Annotated
import logging
from livekit.agents import llm
import os
from dotenv import load_dotenv
import aiohttp

logger = logging.getLogger("functions")
logger.setLevel(logging.INFO)

# Initialize Gemini API key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

class AssistantFnc(llm.FunctionContext):
    def __init__(self, room=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_user_transcript = None
        self.room = room  # Store the room object
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
        Collects the conversation history from the current AgentCallContext and sends it
        to the specified Make (Integromat) webhook endpoint.

        Returns a string indicating success or failure.
        """
        from livekit.agents.pipeline.pipeline_agent import AgentCallContext
        import aiohttp

        # Retrieve the current AgentCallContext (which tracks the conversation history via chat_ctx)
        try:
            call_ctx = AgentCallContext.get_current()
        except LookupError:
            return "No active call context found."

        if not call_ctx:
            return "Call context is empty."

        # Extract the conversation messages
        chat_messages = call_ctx.agent.chat_ctx.messages

        # Prepare the conversation history as a string
        conversation_text = ""
        for msg in chat_messages:
            conversation_text += f"{msg.role}: {msg.content}\n"

        # Send the string directly without JSON wrapping
        url = "https://hook.eu2.make.com/6vn9wwsfrfb4jddstvwn4anek27dykqo"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=conversation_text) as resp:
                if resp.status == 200:
                    return "Your prompt is being generated."
                else:
                    return "Your prompt is being generated."