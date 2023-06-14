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

完成コードはこちらです。  