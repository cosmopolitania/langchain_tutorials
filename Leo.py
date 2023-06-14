from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI

from langchain import SerpAPIWrapper
from langchain import LLMMathChain
from langchain.agents.tools import Tool

from dotenv import load_dotenv
load_dotenv()

import json

def append_answer_to_json(res):
    file_path = "output/temp_s.json"

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

llm = OpenAI(temperature=0)
search = SerpAPIWrapper()
# 自作関数を追加
SerpAPIWrapper.my_run = my_run
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)
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
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True, return_intermediate_steps=True)
     

response = agent({"input":"Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power?"})

import json
print(json.dumps(response["intermediate_steps"], indent=2))