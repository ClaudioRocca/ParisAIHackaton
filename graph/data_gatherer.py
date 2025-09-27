import time
import json
import os
import logging
from pathlib import Path
from typing import Literal, Tuple, override, List, Dict, Any, Optional, cast
from langchain.chat_models import init_chat_model


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
from graph.utils import all_info_provided, inject_current_information
from langchain_core.tools import BaseTool

from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from langchain_core.runnables.config import RunnableConfig
from graph.models import ToolInfo

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

class DataGatherer():

    def __init__(self):
        self.builder = None
        self.prompts_path = BASE_DIR / "prompts.yaml"
        self._executed_steps: List[ToolInfo] = []
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
    
    def data_gatherer(self, state: State):
        from langchain_core.prompts import PromptTemplate

        model = self._get_openai_model()
        prompt_template = self.prompts.get("data_gatherer", "")
        prompt_text = prompt_template.replace("{user_info}", inject_current_information(state))
        prompt = PromptTemplate(template=prompt_text, template_format="f-string")

        # Bind tools
        model_with_tools = model.bind_tools(self.tools)  # self.tools: list or dict of tool runnables

        # Compose a chain: prompt → model
        chain = RunnablePassthrough() | prompt | model_with_tools

        # Invoke the chain to get response
        response = chain.invoke(input={})

        # The model may have suggested tool calls
        tool_calls = getattr(response, 'tool_calls', []) or response.additional_kwargs.get("tool_calls", [])
        tool_results = []

        for i, call in enumerate(tool_calls):
            # Handle different tool call formats
            if hasattr(call, 'name'):
                tool_name = call.name
                args = call.args if hasattr(call, 'args') else {}
            else:
                tool_name = call["function"]["name"]
                args = call["function"].get("arguments", {})
                # Parse arguments if they're in string format
                if isinstance(args, str):
                    import json
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse tool arguments: {args}")
                        args = {}

            # Find the tool instance
            tool = None
            if isinstance(self.tools, dict):
                tool = self.tools.get(tool_name)
            else:
                # if self.tools is a list, match by name attribute
                for t in self.tools:
                    if getattr(t, "name", None) == tool_name:
                        tool = t
                        break

            if tool is None:
                # Unknown tool — record error
                logger.error(f"Unknown tool: {tool_name}")
                step_info = ToolInfo(
                    name=tool_name,
                    arguments=args,
                    output=f"Error: Unknown tool '{tool_name}'",
                    error=True,
                )
                self._executed_steps.append(step_info)
                continue

            try:
                logger.info(f"Executing tool: {tool_name} with args: {args}")
                tool_output = tool.invoke(args)
                logger.info(f"Tool {tool_name} executed successfully")
                
                step_info = ToolInfo(
                    name=tool_name,
                    arguments=args,
                    output=tool_output,
                    error=False,
                )
                self._executed_steps.append(step_info)
                tool_results.append((tool_name, tool_output))
            except Exception as e:
                logger.error(f"Tool {tool_name} failed with error: {str(e)}")
                step_info = ToolInfo(
                    name=tool_name,
                    arguments=args,
                    output=f"Error: {str(e)}",
                    error=True,
                )
                self._executed_steps.append(step_info)
                continue

    
        return Command(goto="__end__", update=state)
    
    def test_lightpanda_setup(self):
        """Test LightPanda API setup and connectivity"""
        from tools import scraper
        
        logger.info("Testing LightPanda API setup...")
        
        # Check if credentials are configured
        if not scraper.api_key:
            logger.error("LIGHTPANDA_API_KEY not found in environment variables")
            return False
            
        if not scraper.api_endpoint:
            logger.error("LIGHTPANDA_API_ENDPOINT not found in environment variables")
            return False
            
        logger.info("API credentials found, testing connection...")
        
        # Run network diagnostics
        scraper.diagnose_network_issues()
        
        # Test the connection
        success = scraper.test_lightpanda_connection()
        
        if success:
            logger.info("LightPanda API is working correctly!")
        else:
            logger.error("LightPanda API connection failed")
            
        return success

    def _get_openai_model(self):
        from langchain_openai.chat_models import ChatOpenAI

        model_param = {"model_provider": "openai",
                       "model": "gpt-4.1"}

        return init_chat_model(
                **model_param
        )

    def build(self):
        """Build the LangGraph workflow."""
        workflow = self.builder

        workflow.add_node("data_gatherer", self.data_gatherer)

        # Set entry point
        workflow.set_entry_point("data_gatherer")

        # Compile the graph
        logger.info("Graph built successfully with nodes and edges.")
        return workflow