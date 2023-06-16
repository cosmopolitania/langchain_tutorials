from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI

from langchain.utilities import GoogleSearchAPIWrapper
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
    experiment_name="scenario 2: googleAPI/Leo",
)
callbacks = [StdOutCallbackHandler(), aim_callback]

import json

def append_answer_to_json(res):
    file_path = "output/temp_g_prompt.json"

    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        # ファイルが存在しない場合は、空の辞書を作成
        data = {}

    # 回答を追加
    data.setdefault("title", []).append(res["title"])
    data.setdefault("link", []).append(res["link"])
    data.setdefault("snippet", []).append(res["snippet"])

    with open(file_path, "w") as file:
        json.dump(data, file)

def my_run(self, query: str) -> str:
    """Run query through GoogleSearch and parse result."""
    snippets = []
    results = self._google_search_results(query, num=self.k)
    if len(results) == 0:
        return "No good Google Search Result was found"
    for result in results:
        if "snippet" in result:
            snippets.append(result["snippet"])
        append_answer_to_json(result)

    return " ".join(snippets)

llm = OpenAI(temperature=0, callbacks=callbacks)
search = GoogleSearchAPIWrapper()
GoogleSearchAPIWrapper.my_run = my_run
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
SUFFIX = """Begin! Answer must be translated in Japanese, and 語尾には"なのだ"を使用してください

Question: {input}
Thought:{agent_scratchpad}"""

agent = AgentExecutor.from_agent_and_tools(
        agent=ZeroShotAgent.from_llm_and_tools(llm, tools,
        prefix=PREFIX, suffix=SUFFIX, format_instructions=FORMAT_INSTRUCTIONS),
        tools=tools,
        callbacks=callbacks,
        verbose=True, return_intermediate_steps=True
    )

response = agent({"input":"Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power?"})

print(json.dumps(response["intermediate_steps"], indent=2, ensure_ascii=False))

aim_callback.flush_tracker(langchain_asset=agent, reset=False, finish=True)
