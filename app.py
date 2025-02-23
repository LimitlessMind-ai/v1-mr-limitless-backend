import asyncio
import uvicorn
import os
from livekit.agents import (
    WorkerOptions,
    Worker
)
from livekit.agents.cli.log import setup_logging
from app.routes.routes_AI_Agent_Interaction.agent import entrypoint, prewarm
from app import app

async def run_servers():
    # Setup logging for LiveKit worker
    setup_logging("DEBUG", devmode=True)
    
    # Get port from Heroku environment, default to 8000 if not available
    port = int(os.getenv('PORT', 8000))
    
    # Create config for uvicorn with Heroku's PORT
    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    
    # Create worker directly instead of using cli.run_app
    worker_options = WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm,
        ws_url=os.getenv('LIVEKIT_URL'),
        api_key=os.getenv('LIVEKIT_API_KEY'),
        api_secret=os.getenv('LIVEKIT_API_SECRET')
    )
    
    # Validate the worker configuration
    worker_options.validate_config(devmode=True)
    
    # Create worker with debug settings
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    worker = Worker(worker_options, devmode=True, loop=loop)
    
    # Run both servers concurrently
    await asyncio.gather(
        server.serve(),
        worker.run()
    )

if __name__ == "__main__":
    # Force the use of SelectorEventLoop on Windows
    if os.name == 'nt':  # Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(run_servers())
