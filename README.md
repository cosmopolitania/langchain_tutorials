# langchain_tutorials
[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/cosmopolitania/langchain_tutorials.git)

## 初期設定をしよう
### APIキー、アカウントの取得
- OpenAPIキーの取得（有料）
- SerpAPIキーの取得（月100回の探索まで無料かつ支払い情報不要）

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

完成コードはこちらです。  


### classの一部を修正