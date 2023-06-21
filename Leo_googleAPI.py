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
    experiment_name="DocComp: googleAPI/Leo",
)
callbacks = [StdOutCallbackHandler(), aim_callback]

import json
file_path = "output/temp_g_prompt.json"
def append_answer_to_json(res, file_path=file_path):

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

    with open(file_path, "w", encoding="utf8") as file:
        json.dump(data, file, ensure_ascii=False)

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
PREFIX = """Answer the following questions as best you can. You have access to the following tools:"""
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

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import UnstructuredURLLoader
from langchain.chains import RetrievalQA, RetrievalQAWithSourcesChain
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ChatMessageHistory
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import messages_to_dict, AIMessage

with open(file_path, "r", encoding="utf8") as f:
    data = json.load(f)
documents = UnstructuredURLLoader(urls=data["link"]).load()

text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=0, separator="\n")
texts = text_splitter.split_documents(documents)
print(len(texts))

embeddings = OpenAIEmbeddings()

if(os.path.exists("./faiss_index_leo") == False):
    db = FAISS.from_documents(texts, embeddings)
    db.save_local("faiss_index_leo")
vectorDB = FAISS.load_local("faiss_index_leo", embeddings)

qa = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vectorDB.as_retriever())
history = ChatMessageHistory()
while True:
    input_txt = input("質問を入力してください: ")
    if(input_txt == "exit"):
        break
    elif(input_txt == ""):
        continue
    response = qa({"question": input_txt})
    print(response)
    history.add_user_message(input_txt)
    answer_message = AIMessage(content=response['answer'])
    answer_message.additional_kwargs['sources'] = response['sources']
    history.add_message(answer_message)

with open("output/leo_g_history.json", "w", encoding="utf8") as f:
    dicts = messages_to_dict(history.messages)
    formater = json.dumps(dicts, indent=2, ensure_ascii=False)
    print(formater)
    f.write(formater)

aim_callback.flush_tracker(langchain_asset=agent, reset=False, finish=True)
