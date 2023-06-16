from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI

from langchain import SerpAPIWrapper
from langchain import LLMMathChain
from langchain.agents.tools import Tool

from dotenv import load_dotenv
load_dotenv()

import os
from datetime import datetime
from langchain.callbacks import AimCallbackHandler, StdOutCallbackHandler
session_group = datetime.now().strftime("%m.%d.%Y_%H.%M.%S")
aim_callback = AimCallbackHandler(
    repo=".",
    experiment_name="Prompt 1: serpAPI/Leo",
)
callbacks = [StdOutCallbackHandler(), aim_callback]

import json

def append_answer_to_json(res):
    file_path = "output/temp_s_prompt.json"

    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        # ファイルが存在しない場合は、空の辞書を作成
        data = {}

    # 回答を追加
    data.setdefault("search_metadata", []).append(res["search_metadata"]["google_url"])
    data.setdefault("answer_box", []).append(res["answer_box"])

    # ファイルに書き込む
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)

from typing import Any
def my_run(self, query: str, **kwargs: Any) -> str:
    """Run query through SerpAPI and parse result."""
    res = self.results(query)
    append_answer_to_json(res)
    return self._process_response(res)

llm = OpenAI(temperature=0, callbacks=callbacks)
search = SerpAPIWrapper()
# 自作関数を追加
SerpAPIWrapper.my_run = my_run
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True, callbacks=callbacks)
tools = [
    Tool(
        name = "Search",
        func=search.my_run,
        description="useful for when you need to answer questions about current events"
    ),
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="useful for when you need to answer questions about math"
    ),
]
# agent = initialize_agent(tools, llm, agent="zero-shot-react-description",
#                          verbose=True, return_intermediate_steps=True, callbacks=callbacks)
from langchain.agents.agent import AgentExecutor
from langchain.agents.mrkl.output_parser import MRKLOutputParser
from langchain import PromptTemplate, LLMChain
from langchain.agents.mrkl.base import ZeroShotAgent
PREFIX = """Answer the following questions in Japanese as best you can. You have access to the following tools:"""
FORMAT_INSTRUCTIONS = """Use the following format:

Question: the input question you must answer.
Thought: you should always think about what to do, must be translated in Japanese
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer, must be translated in Japanese
Final Answer: the final answer to the original input question"""
SUFFIX = """Begin! Final Answer must be translated in Japanese, and 語尾には"なのだ"を使用してください

Question: {input}
Thought:{agent_scratchpad}"""

tool_strings = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
tool_names = ", ".join([tool.name for tool in tools])
format_instructions = FORMAT_INSTRUCTIONS.format(tool_names=tool_names)
template = "\n\n".join([PREFIX, tool_strings, format_instructions, SUFFIX])

llm_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(template=template, input_variables=["input", "agent_scratchpad"]),
    callbacks=callbacks,
)
zero_shot = ZeroShotAgent(
    llm_chain=llm_chain,
    allowed_tools=[tool.name for tool in tools],
    output_parser=MRKLOutputParser()
)
agent = AgentExecutor.from_agent_and_tools(
        agent=zero_shot,
        tools=tools,
        callbacks=callbacks,
        verbose=True, return_intermediate_steps=True
    )

response = agent({"input":"Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power?"})

print(json.dumps(response["intermediate_steps"], indent=2))
aim_callback.flush_tracker(langchain_asset=agent, reset=False, finish=True)
