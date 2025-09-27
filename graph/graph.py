import time
import json
import os
import logging
from pathlib import Path
from typing import Literal, Tuple, override, List, Dict, Any, Optional, cast

from langchain_core.runnables.config import RunnableConfig
from langgraph.config import get_stream_writer
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langchain_core.documents import Document as LCDocument
from langchain_core.retrievers import BaseRetriever
from langgraph.graph import StateGraph, END, START
from langgraph.types import Command
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from tools import search_hotels, search_flights

from langchain_core.tools import BaseTool

from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from langchain_core.runnables.config import RunnableConfig

from openai import AsyncOpenAI
import openai
from openai.helpers import LocalAudioPlayer


import numpy as np
import sounddevice as sd
import tempfile
import wave
import io
import asyncio

from .state import State
import yaml


BASE_DIR = Path(__file__).resolve().parent.parent

logger = logging.getLogger(__name__)

class GraphBuilder():

    def __init__(self):
        self.builder = None
        self.prompts_path = BASE_DIR / "prompts.yaml"
        self.tools = [search_hotels, search_flights]
        self.prompts = yaml.safe_load(self.prompts_path.read_text())
        # Single shared async OpenAI client for all LLM (voice) calls
        self._openai_client: AsyncOpenAI = AsyncOpenAI()
        self.FULL_INFO_SET = """- Clear Destination(either city or a region)
                                - Number of People Traveling
                                - User's Interests (interests like art, history, food, sports)
                                - Preferred Travel Dates
                                - User's Budget (ask for a maximum estimated total cost per person)
                                - User's Preferred Activities (specific activities such as going to a fine restaurant, or visiting a specific museum)
                                """

    # --- Improved microphone capture with RMS level + enhanced silence detection ---
    async def _capture_microphone(
        self,
        max_duration: float = 12.0,
        samplerate: int = 16000,
        channels: int = 1,
        silence_threshold: float = 0.012,  # lowered threshold
        min_active_seconds: float = 0.6,
        max_silence_seconds: float = 1.2,
    ) -> np.ndarray:
        """Record audio until trailing silence or max_duration. Returns float32 ndarray (-1..1)."""
        loop = asyncio.get_running_loop()
        recorded: List[np.ndarray] = []
        block_size = 1024
        silence_blocks = 0
        min_active_blocks = int(min_active_seconds * samplerate / block_size)
        max_silence_blocks = int(max_silence_seconds * samplerate / block_size)
        total_blocks_limit = int(max_duration * samplerate / block_size)
        q: List[np.ndarray] = []

        def callback(indata, frames, time_info, status):
            if status:
                logger.debug("Input status: %s", status)
            q.append(indata.copy())

        stream = sd.InputStream(
            callback=callback,
            channels=channels,
            samplerate=samplerate,
            blocksize=block_size,
            dtype="float32",
        )
        stream.start()
        start_time = loop.time()
        try:
            while True:
                await asyncio.sleep(block_size / samplerate)
                while q:
                    chunk = q.pop(0)
                    recorded.append(chunk)
                    rms = float(np.sqrt((chunk ** 2).mean()))  # RMS level
                    logger.debug("Audio block=%d rms=%.5f", len(recorded), rms)
                    if rms < silence_threshold and len(recorded) > min_active_blocks:
                        silence_blocks += 1
                    else:
                        silence_blocks = 0
                if recorded and silence_blocks >= max_silence_blocks:
                    logger.debug("Trailing silence detected (blocks=%d)", silence_blocks)
                    break
                if len(recorded) >= total_blocks_limit:
                    logger.debug("Max duration reached")
                    break
                if loop.time() - start_time > max_duration + 2:
                    logger.debug("Safety timeout triggered")
                    break
        finally:
            stream.stop(); stream.close()

        if not recorded:
            logger.warning("No audio captured.")
            return np.zeros((1, channels), dtype=np.float32)

        audio = np.concatenate(recorded, axis=0).astype(np.float32)
        logger.info("Captured frames=%d duration=%.2fs", audio.shape[0], audio.shape[0] / samplerate)
        return audio

    # --- Helper: save ndarray PCM to temp WAV file ---
    def _save_temp_wav(self, audio: np.ndarray, samplerate: int = 16000) -> str:
        fd, path = tempfile.mkstemp(suffix=".wav", prefix="user_input_")
        os.close(fd)
        with wave.open(path, 'wb') as wf:
            wf.setnchannels(1 if audio.ndim == 1 else audio.shape[1])
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(samplerate)
            # Convert float32 (-1..1) to int16
            int16_audio = np.clip(audio, -1, 1)
            int16_audio = (int16_audio * 32767).astype(np.int16)
            wf.writeframes(int16_audio.tobytes())
        logger.debug("Saved temp wav %s size=%.1fKB", path, os.path.getsize(path)/1024)
        return path

    # Simplified non-streaming transcription for reliability
    async def _transcribe_audio(self, wav_path: str) -> str:
        model = os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe")
        try:
            with open(wav_path, "rb") as f:
                resp = await self._openai_client.audio.transcriptions.create(  # type: ignore
                    model=model,
                    file=f,
                    response_format="text",
                )

            if not resp:
                logger.warning("Empty transcription response: %s", resp)
            else:
                return resp
        except Exception:
            logger.exception("Transcription failed")
            return ""
        finally:
            try:
                os.remove(wav_path)
            except OSError:
                pass

    async def greeting_node(self, state: State):
        """Greeting node: TTS greeting -> record mic -> transcribe -> update state."""
        
        voice_model = os.getenv("OPENAI_VOICE_MODEL", "gpt-4o-mini-tts")

        logger.debug("Starting greeting TTS model=%s", voice_model)
        # try:
        #     async with self._openai_client.audio.speech.with_streaming_response.create(
        #         model=voice_model,
        #         voice="coral",
        #         input="Follow the instruction",
        #         instructions=prompt + "\nBe synthetic and direct, use a welcoming tone.",
        #         response_format="pcm",
        #     ) as response:
        #         await LocalAudioPlayer().play(response)
        # except Exception:
        #     logger.exception("Greeting TTS failed")

        try:
            async with self._openai_client.audio.speech.with_streaming_response.create(
                model=voice_model,
                voice="coral",
                input="Hi! how can I help you plan your next trip? Tell me more about what you're looking for.",
                instructions="\nBe synthetic and direct using a welcoming tone.",
                response_format="pcm",
            ) as response:
                await LocalAudioPlayer().play(response)
        except Exception:
            logger.exception("Greeting TTS failed")

        logger.info("Listening for user input...")
        audio = await self._capture_microphone()
        if audio.size <= 1:
            logger.warning("Audio empty or silent; skipping transcription")
            user_input = ""
        else:
            wav_path = self._save_temp_wav(audio)
            user_input = await self._transcribe_audio(wav_path)
        logger.info("User transcription: %r", user_input)

        try:
            messages = state.get("messages", [])
            if user_input:
                messages.append(HumanMessage(content=user_input))
            state["messages"] = messages
        except Exception:
            logger.exception("Failed updating state")

        return Command(goto="ask_more_info", update=state)


    async def ask_more_info(self, state:State):

        prompt = self.prompts.get("ask_more_info")
        voice_model = os.getenv("OPENAI_VOICE_MODEL", "gpt-4o-mini-tts")

        logger.debug("Starting ask more info TTS model=%s", voice_model)

    
        current_info = self._inject_current_information(state)
        prompt = prompt.replace("{full_info_set}", self.FULL_INFO_SET)
        prompt = prompt.replace("{current_info}", current_info)

        try:

            chat_messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": state["messages"][-1].content},
            ]

            completion = await self._openai_client.chat.completions.create(  # type: ignore
                model="gpt-4.1-nano",
                messages=chat_messages,
                temperature=0.2
            )
            raw_content = ""
            
            if completion and getattr(completion, "choices", None):
                try:
                    raw_content = completion.choices[0].message.content
                except Exception as e:
                    logger.exception("Failed to extract content from completion: %s", e)

            async with self._openai_client.audio.speech.with_streaming_response.create(
                model=voice_model,
                voice="coral",
                input=raw_content,
                instructions="\nBe synthetic and direct, use a welcoming tone. Acknowledge the fact that you received the information previously mentioned by the user",
                response_format="pcm",
            ) as response:
                # Store the textual content (raw_content) instead of attempting to read audio bytes as text
                state["messages"].append(AIMessage(content=raw_content))
                await LocalAudioPlayer().play(response)


        except Exception as e:
            logger.exception("Greeting TTS failed: %s", e)

        audio = await self._capture_microphone()
        if audio.size <= 1:
            logger.warning("Audio empty or silent; skipping transcription")
            user_input = ""
        else:
            wav_path = self._save_temp_wav(audio)
            user_input = await self._transcribe_audio(wav_path)
        logger.info("User transcription: %r", user_input)

        try:
            messages = state.get("messages", [])
            if user_input:
                messages.append(HumanMessage(content=user_input))
            state["messages"] = messages
        except Exception:
            logger.exception("Failed updating state")


        return Command(goto="append_info_to_state", update=state)


    async def append_info_to_state(self, state: State):
        """Append user input context to the state using an OpenAI chat completion with structured JSON output.

        The model is instructed (and constrained when supported) to emit a JSON object
        representing the partial or complete State fields. Parsed fields are merged
        into state and also stored raw under 'append_info_raw'.
        """
        prompt = self.prompts.get("append_info_to_state")
        prompt = prompt.replace("{current_info}", self._inject_current_information(state))
        prompt = prompt.replace("{full_info_set}", self.FULL_INFO_SET)

        messages = state.get("messages")
        formatted_messages:list = self._format_messages(messages)

        # System instruction emphasizing JSON schema compliance
        system_instruction = (
            "You are an information extraction assistant. Extract ONLY the travel planning fields "
            "you can confidently fill from the conversation. Return STRICT JSON matching the schema. "
            "If a field is unknown, omit it. Do not invent data."
        )

        # JSON schema for structured output corresponding to State keys
        json_schema = {
            "name": "StateInfo",
            "schema": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string", "description": "City or region"},
                    "people_number": {"type": "integer", "minimum": 1},
                    "interests": {"type": "string", "description": "Comma-separated interests"},
                    "travel_dates": {"type": "string", "description": "Date range or specific dates"},
                    "budget": {"type": "string", "description": "Budget level per person"},
                    "activities": {"type": "string", "description": "Comma-separated activity categories"}
                },
                "required": [],
                "additionalProperties": False
            }
        }

        chat_messages = [
            {"role": "system", "content": system_instruction + "\n" + prompt}
        ]

        chat_messages.extend(formatted_messages)    

        try:
            completion = await self._openai_client.chat.completions.create(  # type: ignore
                model="gpt-4.1-nano",
                messages=chat_messages,
                temperature=0.2,
                response_format={
                    "type": "json_schema",
                    "json_schema": json_schema,
                },
            )
            raw_content = ""
            parsed: Dict[str, Any] = {}
            if completion and getattr(completion, "choices", None):
                try:
                    raw_content = completion.choices[0].message.content  # type: ignore
                    logger.debug("Raw structured output: %s", raw_content)
                    parsed = json.loads(raw_content)
                except Exception:
                    logger.exception("Failed parsing JSON structured output; attempting fallback cleanup")
                    try:
                        cleaned = raw_content.replace("```json", "").replace("```", "").strip()
                        parsed = json.loads(cleaned)
                    except Exception:
                        parsed = {}
            state["append_info_raw"] = parsed or raw_content

            # Merge parsed fields into state only if present
            for key in ["destination", "people_number", "interests", "travel_dates", "budget", "activities"]:
                if key in parsed and parsed[key] not in (None, ""):
                    state[key] = parsed[key]

            if not self._all_info_provided(state):
                return Command(goto="ask_more_info", update=state)
            return Command(goto="__end__", update=state)
        except Exception as e:
            logger.exception("Failed to append data to the state (structured): %s", e)
            return Command(goto="final_message", update=state)
        

    async def final_message(self, state:State):
        voice_model = os.getenv("OPENAI_VOICE_MODEL", "gpt-4o-mini-tts")
        try:
            async with self._openai_client.audio.speech.with_streaming_response.create(
                model=voice_model,
                voice="coral",
                input="Great! It's all set! I have all the information I need to generate an immersive and personalized travel experience!",
                instructions="Be synthetic and direct using a welcoming tone.",
                response_format="pcm",
            ) as response:
                await LocalAudioPlayer().play(response)
        except Exception:
            logger.exception("Greeting TTS failed")

        logger.info("Listening for user input...")
        audio = await self._capture_microphone()
        if audio.size <= 1:
            logger.warning("Audio empty or silent; skipping transcription")
            user_input = ""
        else:
            wav_path = self._save_temp_wav(audio)
            user_input = await self._transcribe_audio(wav_path)
        
        return Command(goto="__end__", update=state)

    async def data_gatherer(self, state:State):
        model = openai.OpenAI(model="gpt-4.1-nano", temperature=0)
        prompt = self.prompts.get("data_gatherer", "")

        prompt = prompt.replace

        agent = create_react_agent(
            llm=model,
            tools=self.tools,
            prompt=prompt
        )



    def _format_messages(self, messages):

        output = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                output.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                output.append({"role": "assistant", "content": msg.content})
        return output

    def _all_info_provided(self, state:State):
        required_keys = ["destination", "people_number", "interests", "travel_dates", "budget", "activities"]
        return all(key in state for key in required_keys)
        # return True

    def _inject_current_information(self, state: State) -> str:
        """Inject current information from the state into the prompt."""
        current_info = ""
        # Appends all key features inside State as a string to be provided to the LLM

        if state.get("destination"):
            current_info += f"Travel destination: {state['destination']}\n"
        if state.get("people_number"):
            current_info += f"Number of people traveling: {state['people_number']}\n"
        if state.get("interests"):
            current_info += f"User's interests: {state['interests']}\n"
        if state.get("travel_dates"):
            current_info += f"Preferred travel dates: {state['travel_dates']}\n"
        if state.get("budget"):
            current_info += f"User's budget: {state['budget']}\n"
        if state.get("activities"):
            current_info += f"User's preferred activities: {state['activities']}\n"
        return current_info

    # --- New public method for constructing a streaming voice chain ---
    def build_chain(
        self,
        name: str,
        tools: Optional[List[BaseTool]] = None,  # kept for API symmetry, unused here
        max_messages_history: int = 15,
        voice: str = "coral",
        response_format: str = "pcm",
        instructions: Optional[str] = None,
    ):
        """Create an async streaming generator factory for a given prompt name.

        Returns a function that, when passed a list of messages, produces an async
        generator yielding raw audio byte chunks (PCM by default).

        Usage:
          gen_factory = build_chain("greeting_prompt")
          async for chunk in gen_factory(messages):
              ...  # stream chunk to client
        """
        prompt_prefix = self.prompts.get(name, "") or ""
        model_name = os.getenv("OPENAI_VOICE_MODEL", "gpt-4o-mini-tts")
        system_instructions = instructions or "Respond as a concise, helpful travel voice assistant."

        def generator_factory(messages: List[Any]):
            limited_messages = self._limit_messages(messages, max_messages_history)
            user_content = ""
            if limited_messages:
                last_msg = limited_messages[-1]
                try:
                    user_content = getattr(last_msg, "content", str(last_msg)) or ""
                except Exception:
                    user_content = str(last_msg)
            input_text = (f"{prompt_prefix}\n{user_content}" if prompt_prefix else user_content).strip()

            async def async_generator():
                logger.debug("Starting streaming TTS call: model=%s voice=%s", model_name, voice)
                async with self._openai_client.audio.speech.with_streaming_response.create(
                    model=model_name,
                    voice=voice,
                    input=input_text or "Hello!",
                    instructions=system_instructions,
                    response_format=response_format,
                ) as response:
                    async for chunk in response.iter_bytes():
                        yield chunk
                logger.debug("Completed streaming TTS call")
            return async_generator()

        return generator_factory

    def _limit_messages(self, messages: list, max_messages: int) -> list:
        """Limit the number of messages stored in the state."""
        if len(messages) > max_messages:
            messages = messages[-max_messages:]
        return messages

    def build(self):
        """Build the LangGraph workflow."""
        workflow = self.builder

        workflow.add_node("greeting", self.greeting_node)
        workflow.add_node("ask_more_info", self.ask_more_info)
        workflow.add_node("append_info_to_state", self.append_info_to_state)
        workflow.add_node("final_message", self.final_message)

        # Set entry point
        workflow.set_entry_point("greeting")

        # Compile the graph
        logger.info("Graph built successfully with nodes and edges.")
        return workflow