from typing import Annotated
import json
import logging
from livekit.agents import llm
import os
from dotenv import load_dotenv
import aiohttp
import asyncio

logger = logging.getLogger("functions")
logger.setLevel(logging.INFO)

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
                    # Send weather data to frontend via RPC
                    if self.room and self.room.local_participant:
                        try:
                            await self.room.local_participant.perform_rpc(
                                destination_identity="frontend",  # Broadcast to all participants
                                method="displayWeather",
                                payload=json.dumps({
                                    "location": location,
                                    "weather": weather_data
                                })
                            )
                        except Exception as e:
                            logger.error(f"Failed to send weather data to frontend: {e}")
                    
                    return f"The weather in {location} is {weather_data}."
                else:
                    raise f"Failed to get weather data, status code: {response.status}"

    @llm.ai_callable()
    async def get_quick_start_report_link(self):
        """Called when the user asks for a quick start report."""
        logger.info("getting quick start report link")
        quick_start_report_link = "https://vrtsandbox.limitlessmind.ai/quick-start-report"
        
        # Create a delayed coroutine for sending the link
        async def send_delayed_link():
            await asyncio.sleep(3)
            if self.room and self.room.local_participant:
                try:
                    await self.room.local_participant.perform_rpc(
                        destination_identity="frontend",
                        method="displayLink",
                        payload=json.dumps({
                            "link": quick_start_report_link
                        })
                    )
                except Exception as e:
                    logger.error(f"Failed to send quick start report link to frontend: {e}")

        # Schedule the delayed link sending without awaiting it
        asyncio.create_task(send_delayed_link())
        
        return "Initializing enterprise solution synthesis. Activating optimal scenario matrix and deploying specialized AI agents for your workflow requirements. Establishing secure integration pathways and configuring advanced task orchestration protocols... Let me present you with the proposed solution - MIKE."

    @llm.ai_callable()
    async def get_mike_link(self):
        """Called when the user wants to further discuss a potential AI project."""
        logger.info("getting Mike link")
        mike_link = "https://vrtsandbox.limitlessmind.ai/mike"
        
        # Create a delayed coroutine for sending the link
        async def send_delayed_link():
            await asyncio.sleep(3)
            if self.room and self.room.local_participant:
                try:
                    await self.room.local_participant.perform_rpc(
                        destination_identity="frontend",
                        method="displayLink",
                        payload=json.dumps({
                            "link": mike_link
                        })
                    )
                except Exception as e:
                    logger.error(f"Failed to send Mike link to frontend: {e}")

        # Schedule the delayed link sending without awaiting it
        asyncio.create_task(send_delayed_link())
        
        return "I will redirect you to a page where you can speak with our AI meta agent."
  
