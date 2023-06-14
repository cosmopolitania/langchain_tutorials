from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI

from langchain.utilities import GoogleSearchAPIWrapper
from langchain import LLMMathChain
from langchain.agents.tools import Tool

from dotenv import load_dotenv
load_dotenv()

import json

def append_answer_to_json(res):
    file_path = "output/temp_g.json"

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

llm = OpenAI(temperature=0)
search = GoogleSearchAPIWrapper()
GoogleSearchAPIWrapper.my_run = my_run
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