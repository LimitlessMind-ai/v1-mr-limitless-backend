import logging
import json

from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
    metrics,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import openai, deepgram, silero, elevenlabs
from app.routes.routes_AI_Agent_Interaction.functions import AssistantFnc
from .prompt import SYSTEM_PROMPT


load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=SYSTEM_PROMPT,
    )

    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()

    # Parse metadata JSON string
    metadata = json.loads(participant.metadata or '{"language": "en", "email": ""}')
    language = metadata.get("language", "en")  # Default to English if not specified
    email = metadata.get("email", "")  # Get email from metadata
    
    logger.info(f"starting voice assistant for participant {participant.identity} with email {email}")

    # Map the language codes to Deepgram language codes
    deepgram_language = {
        "en": "en-US",
        "pl": "pl",
        "ko": "ko"
    }.get(language.lower(), "en-US")  # Default to English if language not supported

    fnc_ctx = AssistantFnc(ctx.room)
    
    agent = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(model="nova-3", language=deepgram_language),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=elevenlabs.TTS(
            voice=elevenlabs.Voice(
                id="tsq894MzvrjtuIYu6WS5",
                name="Jin",
                category="premade",
                settings=elevenlabs.VoiceSettings(
                    stability=0.71,
                    similarity_boost=0.5,
                    style=0.0,
                    use_speaker_boost=True
                )
            )
        ),
        min_endpointing_delay=0.5,
        max_endpointing_delay=5.0,
        chat_ctx=initial_ctx,
        fnc_ctx=fnc_ctx
    )
    

    # usage_collector = metrics.UsageCollector()

    # @agent.on("metrics_collected")
    # def on_metrics_collected(agent_metrics: metrics.AgentMetrics):
    #     metrics.log_metrics(agent_metrics)
    #     usage_collector.collect(agent_metrics)

    agent.start(ctx.room, participant)

    # Select greeting based on language
    greeting = {
        "en": "I'm MindPrompt, a Prompt Engineering expert from LimitlessMind.ai. I'll help you craft highly effective prompts. Let's begin with your primary objective - what is the single, main goal of the prompt you want to create?",
        "pl": "Jestem MindPrompt, ekspertem od Prompt Engineering z LimitlessMind.ai. Pomogę Ci stworzyć wysoce efektywne prompty. Zacznijmy od Twojego głównego celu - jaki jest pojedynczy, główny cel promptu, który chcesz stworzyć?",
        "ko": "저는 LimitlessMind.ai의 프롬프트 엔지니어링 전문가 MindPrompt입니다. 효과적인 프롬프트를 만드는 것을 도와드리겠습니다. 먼저 주요 목표부터 시작하겠습니다 - 만들고자 하는 프롬프트의 단일 주요 목적이 무엇인가요?"
    }.get(language.lower(), "I'm MindPrompt, a Prompt Engineering expert from LimitlessMind.ai. I'll help you craft highly effective prompts. Let's begin with your primary objective - what is the single, main goal of the prompt you want to create?")  # Default to English if language not supported
    
    # The agent should greet the user in their preferred language
    await agent.say(greeting, allow_interruptions=True)