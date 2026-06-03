import logging
from collections.abc import AsyncIterable
from typing import Any, Coroutine, Union

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentSession,
    ConversationItemAddedEvent,
    JobContext,
    ModelSettings,
    RoomInputOptions,
    RoomOutputOptions,
    RunContext,
    WorkerOptions,
    cli,
)
from livekit.agents.beta.tools.end_call import EndCallTool
from livekit.agents.llm import ChatMessage, function_tool
from livekit.plugins import cartesia, openai

# uncomment to enable Krisp background voice/noise cancellation
# from livekit.plugins import noise_cancellation

logger = logging.getLogger("basic-agent")

load_dotenv()


class CartesiaAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="your name is Katie."
            " you would interact with users via voice."
            " with that in mind, keep your responses concise and to the point."
            " do not use emojis, asterisks, markdown, or other special characters in your responses."
            " you are curious and friendly, and have a sense of humor."
            " you will speak english to the user.",
            # you can pass tools to the LLM in the list here
            # or by decorating CartesiaAgent methods with @function_tool
            tools=[EndCallTool()],
        )

    async def on_enter(self) -> None:
        # when the agent is added to the session, it'll generate a reply
        # according to its instructions
        self.session.generate_reply()

    def tts_node(
        self, text: AsyncIterable[str], model_settings: ModelSettings
    ) -> Union[
        AsyncIterable[rtc.AudioFrame],
        Coroutine[Any, Any, AsyncIterable[rtc.AudioFrame]],
        Coroutine[Any, Any, None],
    ]:
        # Markdown and emoji filters are enabled in `Agent.tts_node`, markdown symbols
        # and emojis will be removed from the text sent to the TTS model

        # To disable these filters, customize the `tts_node` method and
        # use `return Agent.default.tts_node(self, text, model_settings)` instead

        return super().tts_node(text, model_settings)

    # all functions decorated with @function_tool will be passed to the LLM
    @function_tool
    async def lookup_weather(
        self,
        context: RunContext,
        location: str,
    ) -> str:
        """Lookup weather at a location.

        Args:
            location (str): The location to lookup weather for (city or region).
        """

        logger.info(f"Function called: lookup_weather({location=})")

        # mock implementation
        return "sunny with a temperature of 70 degrees."


async def entrypoint(ctx: JobContext) -> None:
    # each log entry will include these fields
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }
    # For more information, check out the Cartesia Plugin for LiveKit:
    # https://docs.livekit.io/agents/integrations/tts/cartesia/
    session: AgentSession = AgentSession(
        # any combination of STT, LLM, TTS can be used
        stt=cartesia.STT(
            language="en"
            # model="..."
        ),
        llm=openai.LLM(
            # model="..."
        ),
        tts=cartesia.TTS(
            language="en"
            # model="..."
            # voice="..."
        ),
        turn_handling={
            # turn_detection is how your agent decides when the user is done speaking
            # "stt" is supported with cartesia.STT(model="ink-2") and later
            "turn_detection": "stt",
            # preemptive_generation allows the LLM to generate a response
            # while waiting for the end of turn
            # supported with cartesia.STT(model="ink-2") and later
            "preemptive_generation": {
                "enabled": True,
            },
            "interruption": {
                "enabled": True,
                # sometimes background noise can interrupt the agent session
                # these are considered false positive interruptions
                # when it's detected, you may resume the agent's speech
                "resume_false_interruption": True,
                "false_interruption_timeout": 1.0,
                # lower min_duration makes your agent more sensitive to interruptions
                "min_duration": 0.2,
            },
        },
    )

    # log per-turn latency metrics as conversation items are added
    @session.on("conversation_item_added")
    def _on_conversation_item_added(ev: ConversationItemAddedEvent):
        if isinstance(ev.item, ChatMessage) and ev.item.metrics:
            logger.info(f"Metrics: {ev.item.metrics}")

    # log total usage after the session is over
    async def log_usage():
        logger.info(f"Usage: {session.usage}")

    # shutdown callbacks are triggered when the session is over
    ctx.add_shutdown_callback(log_usage)

    await session.start(
        agent=CartesiaAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # uncomment to enable Krisp BVC noise cancellation
            # noise_cancellation=noise_cancellation.BVC(),
        ),
        room_output_options=RoomOutputOptions(transcription_enabled=True),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
