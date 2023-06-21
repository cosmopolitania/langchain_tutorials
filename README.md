# langchain_tutorials
[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/cosmopolitania/langchain_tutorials.git)

## 初期設定をしよう
### APIキー、アカウントの取得
- OpenAPIキーの取得（有料）
- SerpAPIキーの取得（月100回の探索まで無料かつ支払い情報不要）

[GoogleのAPIを使う章](https://github.com/cosmopolitania/langchain_tutorials#google-custom-search-engine%E3%81%B8%E3%81%AE%E5%88%87%E3%82%8A%E6%9B%BF%E3%81%88)
以降では、下記のAPIも必要です
- GoogleCSE(一日100回の呼び出しまで無料かつ支払い情報不要)
- GoogleAPI(CSEとセットで必要になる)

### .envファイルの作成
.env-exampleファイルを参考に、上記で取得したキーを入力してください。  
入力したら.envにファイル名を変更しましょう。

## Leo.pyの実行
こちらの公式exampleになります。APIキーの設定だけ.envから取得するように変更されています。
https://python.langchain.com/en/latest/modules/agents/getting_started.html  
このリポジトリ内の対応するLeo.py  
https://github.com/cosmopolitania/langchain_tutorials/blob/21355522ca0940bf0ec4927a45e5000cb44a77a2/Leo.py
### 実行コマンド
```
>> python Leo.py
```

## intermediate_stepsの取得について
標準出力に出てくる `Action:` や `Observation:` を変数として取得するには、 `return_intermediate_steps=True` にすると解説されています。  
しかし、その変更だけでは以下のエラーがでます。
```
ValueError: `run` not supported when there is not exactly one output key. Got ['output', 'intermediate_steps'].
```
agentクラスのrunメソッドを呼び出していたのを、agentクラスに辞書型の引数を与える形に変更する必要があります。
NamedTuple型の返り値を受けて、そのメンバにアクセスする形で目的を達成します。  

具体的なコード変更部位は以下になります。  
https://github.com/cosmopolitania/langchain_tutorials/commit/a5ac5a9731ce010d229cb91dc18d63b66ae6df8c  
完成コードはこちらです。  
https://github.com/cosmopolitania/langchain_tutorials/blob/a5ac5a9731ce010d229cb91dc18d63b66ae6df8c/Leo.py

## デフォルトで使用可能なToolについて
公式のリストがここにあります。　　
https://github.com/hwchase17/langchain/blob/master/docs/modules/agents/tools/getting_started.md  
ニュースや天気、映画データベースへのアクセスなど様々なものが提供されています。

### serpAPIの詳細
先程の例で、実際にはserpAPIには以下のようなURLが送られ、その返答をLLMが処理しています。
```
https://serpapi.com/search.json?q=%22Leo%20Dicaprio%20girlfriend%22&hl=en&gl=us
```
URLを実際にブラウザで開くと、APIの返答となるjsonを直にみることができます。
その結果の処理はこちらの _process_response関数で定義されていますが、ここをオーバーライドすることでカスタマイズすることができます。
https://github.com/hwchase17/langchain/blob/master/langchain/utilities/serpapi.py#L128

## Toolの書き換え、カスタマイズについて
### より一般的な書き方へ変更
`load_tools` は名前で呼び出すだけで良くコード量が最小ですみますが、細かい調整には不向きです。  
まずはより一般的なツールの呼び出し方へ変更します。
```
Tool(
        name = "Search",
        func=search.run,
        description="useful for when you need to answer questions about current events"
    )
```
すでにこのように曝露している部分があり、例えばツールの名前を変えたり呼び出し関数を変更することができます。  
descriptionの記載内容に応じてAgentが使用するツールの優先順位が変わるので、descriptionの変更も結果に影響を及ぼします。

具体的なコード変更部位は以下になります。  
https://github.com/cosmopolitania/langchain_tutorials/commit/3282ab0615bc7c5663a659918fd805310fb93b52  
完成コードはこちらです。  
https://github.com/cosmopolitania/langchain_tutorials/blob/3282ab0615bc7c5663a659918fd805310fb93b52/Leo.py

[GoogleのAPIを使う章](https://github.com/cosmopolitania/langchain_tutorials#google-custom-search-engine%E3%81%B8%E3%81%AE%E5%88%87%E3%82%8A%E6%9B%BF%E3%81%88)
のためにこの完成コードをLeo_googleAPI.pyという名前で複製します。

### classの一部を修正
serpAPIの返答となる.jsonを解析することで、どのウェブサイトを根拠にAgentが回答を構成しているかわかります。  
そもそもserpAPIがgoogleに投げた検索キーや検索条件を知るのも良いでしょう。  
同じ例題でも実行した時期によって結果が変わることがあります。そのため、APIレスポンスを結論と共に保存することを考えてみましょう。  
修正の考え方は以下になります。
- APIのレスポンスの中から取り出したい情報をjsonファイルに記録する関数を用意
- run関数の中で記録関数を呼び出す
- この新しいrun関数の方をAgentが使用する

具体的なコード変更部位は以下になります。  
https://github.com/cosmopolitania/langchain_tutorials/commit/cae8a88eb04bc9a8c46b771b95a1088950e78d61#diff-e100247b0b09afc2bde0174762aa739d7679bd9f5abf20810dd7a0cae1b34a9d  
完成コードはこちらです。  
https://github.com/cosmopolitania/langchain_tutorials/blob/cae8a88eb04bc9a8c46b771b95a1088950e78d61/Leo.py

実行時に作成されるjsonファイルは[output](https://github.com/cosmopolitania/langchain_tutorials/tree/main/output)に作成され、サンプルが置いてあります。  
また、serpAPIのレスポンスの例は[API_responses](https://github.com/cosmopolitania/langchain_tutorials/tree/main/API_responses)にあります。

### Google Custom Search Engineへの切り替え
serpAPIは優秀ですが、無料アカウントでは回数の制約が厳しいです。結局検索をgoogleに投げているということからも、Google CSEを併用するのは悪くないアイデアだと思われます。
変更部位は少ないですが、検索結果の `observation:` がかなり変わりましたので以下に違いを記載します。

#### serpAPIでの探索
```
> Entering new AgentExecutor chain...
 I need to find out who Leo DiCaprio's girlfriend is and then calculate her age raised to the 0.43 power.
Action: Search
Action Input: "Leo DiCaprio girlfriend"
Observation: Leonardo DiCaprio and Gigi Hadid were recently spotted at a pre-Oscars party, sparking interest once again in their rumored romance. The Revenant actor and the model first made headlines when they were spotted together at a New York Fashion Week afterparty in September 2022.
Thought: I need to find out Gigi Hadid's age.

<中略>

Observation: Answer: 4.1906168361987195
Thought: I now know the final answer.
Final Answer: Gigi Hadid's age raised to the 0.43 power is 4.1906168361987195.
```

#### GoogleAPIでの探索
```
> Entering new AgentExecutor chain...
 I need to find out who Leo DiCaprio's girlfriend is and then calculate her age raised to the 0.43 power.
Action: Search
Action Input: "Leo DiCaprio girlfriend"
Observation: Feb 16, 2023 ... Bridget Hall: 1994 · Naomi Campbell: 1995 · Kristen Zang: 1996 to 1997 · Amber Valletta: 1997 · Helena Christensen: 1997 · Eva Herzigová: 1998. Jun 5, 2023 ... Leonardo DiCaprio seemed to prove a long-held theory about his love life when he broke up with his girlfriend, Camila Morrone, ... Feb 9, 2023 ... The Academy Award winner's love life has made headlines over the past year, particularly after he and his ex-girlfriend Camila Morrone split in ... Apr 16, 2023 ... DiCaprio broke up with girlfriend Camila Morrone, 25, in the summer of 2022, after dating for four years. Bradley Cooper wears white tux to ... 4 days ago ... Speculation about their budding connection came just weeks after DiCaprio's split from his girlfriend of four years, model and actress Camila ... Aug 31, 2022 ... Leonardo DiCaprio's Dating History: From His Relationships With Camila Morrone To Blake Lively · Camila Morrone · Camila Morrone · Camila Morrone. Feb 20, 2023 ... Leonardo DiCaprio's Dating History: Gisele Bundchen, Blake Lively, Camila Morrone · Bridget Hall · Claire Danes · Kristen Zang · Amber Valletta. Feb 6, 2023 ... Last year the actor broke up with his long-term girlfriend, model and actress Camila Morrone, just months after she turned 25. The couple had ... May 24, 2023 ... Turns out the 48-year-old DiCaprio is in the dog house with his friends for spending too much time with his 28-year-old girlfriend Gigi Hadid. May 24, 2023 ... The 48-year-old actor's love life has very much been in the public eye in recent months following the break-up with his girlfriend of four years ...
Thought: I now know that Leo DiCaprio's girlfriend is Gigi Hadid and she is 28 years old.
Action: Calculator
Action Input: 28^0.43

<中略>

Observation: Answer: 4.1906168361987195
Thought: I now know the final answer
Final Answer: Leo DiCaprio's girlfriend is Gigi Hadid and her current age raised to the 0.43 power is 4.1906168361987195.
``` 

具体的なコード変更部位は以下になります。  
https://github.com/cosmopolitania/langchain_tutorials/commit/07d156997cb6ea7be82751ff3e5d9a1f73df3ebb#diff-d1be08a51bf2bc56a8db7e23ea42104463ea41f72fdaadeb29ee0c8603d9238e  
完成コードはこちらです。  
https://github.com/cosmopolitania/langchain_tutorials/blob/07d156997cb6ea7be82751ff3e5d9a1f73df3ebb/Leo_googleAPI.py

### classの一部を修正
serpAPIと全く同様です。詳細は割愛します。

実行時に作成されるjsonファイルは[output](https://github.com/cosmopolitania/langchain_tutorials/tree/main/output)に作成され、サンプルが置いてあります。  
また、google search APIのレスポンスの例は[API_responses](https://github.com/cosmopolitania/langchain_tutorials/tree/main/API_responses)にあります。

具体的なコード変更部位は以下になります。  
https://github.com/cosmopolitania/langchain_tutorials/commit/14c9c6232460a8f4161b4208bfa6deda67513877#diff-d1be08a51bf2bc56a8db7e23ea42104463ea41f72fdaadeb29ee0c8603d9238e  
完成コードはこちらです。  
https://github.com/cosmopolitania/langchain_tutorials/blob/14c9c6232460a8f4161b4208bfa6deda67513877/Leo_googleAPI.py

## 実験管理ツールの導入
AimでLangchainの実行ごとの結果や中間ステップにおけるプロンプトの中身などを記録できます。  
導入には数行追加するだけで済み、結果の再現などがしやすくなるので導入しておくと良いです。

- serpAPIの場合  
具体的なコード変更部位は以下になります。  
https://github.com/cosmopolitania/langchain_tutorials/commit/876c36f09048c3cb9585e0393f96619604149f9e#diff-e100247b0b09afc2bde0174762aa739d7679bd9f5abf20810dd7a0cae1b34a9d  
完成コードはこちらです。  
https://github.com/cosmopolitania/langchain_tutorials/blob/876c36f09048c3cb9585e0393f96619604149f9e/Leo.py

- googleAPIの場合  
具体的なコード変更部位は以下になります。  
https://github.com/cosmopolitania/langchain_tutorials/commit/876c36f09048c3cb9585e0393f96619604149f9e#diff-d1be08a51bf2bc56a8db7e23ea42104463ea41f72fdaadeb29ee0c8603d9238e  
完成コードはこちらです。  
https://github.com/cosmopolitania/langchain_tutorials/blob/876c36f09048c3cb9585e0393f96619604149f9e/Leo_googleAPI.py

## Prompt エンジニアリングに向けて
ここまで選択してきている `zero-shot-react-description` は、そもそも以下のようなPromptを使用しています。  
```
Answer the following questions as best you can. You have access to the following tools:

Search: useful for when you need to answer questions about current events
Calculator: useful for when you need to answer questions about math

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [Search, Calculator]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power?
Thought:
```
これは `print(agent)` などとして標準出力上でも確認できますが、先程の実験管理ツールAimを使えば　`(Runs) > Text > on_llm_start` で確認できます。  
`initialize_agent` により、選択されたエージェントに合わせてそれぞれ異なるプロンプトが使用されます。このプロンプトをカスタマイズすることで、より意図にあった検索や思考をさせることができるため、まずは使われるプロンプトを直接指定するように書き換えましょう。  
変更が多いので2ステップにわけてコード変更を追います。

### initialize_agent -> from_agent_and_tools 
- agentとして`zero-shot-react-description` を使うこと
- 使用許可されたtools（本例では `Search`, `Calculator`）
この二点が決まれば、agentのクラス(ZeroShotAgent)のメンバ関数from_llm_and_toolsがinitialize_agentと同じ役割を果たします。  
書き換え部位は以下のようになっています。  
https://github.com/cosmopolitania/langchain_tutorials/commit/595b8cd63c609217046458f63ce5a36a8b8ae6ea#diff-e100247b0b09afc2bde0174762aa739d7679bd9f5abf20810dd7a0cae1b34a9d  

### from_agent_and_tools -> PromptTemplate
- PREFIX, FORMAT_INSTRUCTIONS, SUFFIX を直接記載
- 命令文をtools部分について成形した後、PromptTemplate関数によるプロンプト作成
- ZeroShotAgentのインスタンス化の際に作成したプロンプトを使用する  
このような手続きにより、`initialize_agent` を使用した時と全く同じ結果が得られるようになります。  
書き換え部位は以下のようになっています。  
https://github.com/cosmopolitania/langchain_tutorials/commit/73e1bba463334294e1111e249eebd457028de37f#diff-e100247b0b09afc2bde0174762aa739d7679bd9f5abf20810dd7a0cae1b34a9d

プロンプトを変更してLLMが作成している回答部位を日本語へ翻訳するように指定してみましょう。
書き換え部位は以下のようになっています。  
https://github.com/cosmopolitania/langchain_tutorials/commit/788e547758ac56ffc2f4202d14fb77415e8ccfa3#diff-e100247b0b09afc2bde0174762aa739d7679bd9f5abf20810dd7a0cae1b34a9d  

参考まで: [Prompt->Agent->AgentExecutorの一連の流れ](https://github.com/cosmopolitania/langchain_tutorials/blob/788e547758ac56ffc2f4202d14fb77415e8ccfa3/Leo.py#L94-L109)  
結果は以下のようになり、 `Thought:` と `Final Answer:` の部位が日本語で返ってくるようになりました。
```
<前略>
Begin! Final Answer must be translated in Japanese, and 語尾には"なのだ"を使用してください

Question: Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power?
Thought: レオ・ディカプリオの彼女は誰かを知る必要があるなのだ
Action: Search
Action Input: Leo DiCaprio girlfriend
Observation: Leonardo DiCaprio and Gigi Hadid were recently spotted at a pre-Oscars party, sparking interest once again in their rumored romance. The Revenant actor and the model first made headlines when they were spotted together at a New York Fashion Week afterparty in September 2022.
Thought: 彼女の年齢を0.43乗する必要があるなのだ
Action: Calculator
Action Input: Gigi Hadid's age raised to the 0.43 power
Observation: Answer: 3.9218486893172186
Thought:

> Finished chain.
WARNING:root:Error in on_chain_end callback: 'output'
 答えを知ったなのだ
Final Answer: レオ・ディカプリオの彼女は、ジジ・ハディッドで、彼女の年齢を0.43乗すると3.9218486893172186なのだ。
```
少しコード記述が長いため、ZeroShotAgentクラスをオーバーライドするやり方にします。  
具体的なコード変更部位は以下になります。  
https://github.com/cosmopolitania/langchain_tutorials/commit/a7491c2fe5b3392797414fe3b2bf404d65179e4c#diff-e100247b0b09afc2bde0174762aa739d7679bd9f5abf20810dd7a0cae1b34a9d  

完成コードはこちらです。  
https://github.com/cosmopolitania/langchain_tutorials/blob/a7491c2fe5b3392797414fe3b2bf404d65179e4c/Leo.py  

**注意**
翻訳を強要すると、以下のようなエラーがでることがあります。
```
langchain.schema.OutputParserException: Could not parse LLM output: ` ギジ・ハディッドの現在の年齢を0.43乗した答えが4.1906168361987195なのだ。`
```
答えが無事に翻訳されているものの、 `Final Answer:` のようなAI回答のprefixがなくなってしまい、最終回答と認識できずにエラーが生じている形になります。 
ちょっとしたプロンプトの表現でこういったことになりますので注意してください。  
実装時の実験では、
```
SUFFIX = """Begin! Final Answer must be translated in Japanese, and 語尾には"なのだ"を使用してください
```
このプロンプトだとエラーになり、
```
SUFFIX = """Begin! Answer must be translated in Japanese, and 語尾には"なのだ"を使用してください
```
このプロンプトだと問題無かったです。 

全く同様にしてgoogleAPIの方もPromptエンジニアリングできるようにしました。  
完成コードはこちらです。  
https://github.com/cosmopolitania/langchain_tutorials/blob/ef37581215dc87df44fe35df025b1ca71523beb9/Leo_googleAPI.py  

## 検索結果からvector storeを構築し、さらなるQAへ対応
Agent ChainによるWeb検索では、Search APIが返すsnippetの情報で回答を作成しており、ヒットしたページの内容全体を読み込んで回答をしているわけではないようです。  
そのため、 `彼女は誰か → その年齢は → その階乗は` というステップはこなせても、ページの内容全体を踏まえる必要がある複雑な命令には十分な品質の回答を出せませんでした。そのような課題に対し、以下のアプローチを追加してみます。  
1. Agent chainにより、検索上位のサイトアドレスを集める
1. URLLoaderにより上位のサイトを全て読み込み、vector storeを作成
1. (関連性のあるサイトに絞る : contextual compression)
1. 新たなQAを行うLLMを作成する。このLLMはvector storeの中身を使用して回答

### FAISS
上記の1,2,4点目の実装をまとめて実施。vector storeはchromaDB, FAISS, pinecone(有料)などがありますが、ここではFAISSで実装します。  
- Agent Chainでは10個(変更可能)のヒットを返すgoogle APIを使用する
- RetrievalQAWithSourcesChainにより、どのサイトを根拠にAI回答が作られたかを明示
- AI messageにsourceも格納

なお、実行方法は以下になります。exitと記載すればQAを終了します。
``` 
>> python Leo_googleAPI.py
```
完成コードはこちらです。  



### Contextual Compressor