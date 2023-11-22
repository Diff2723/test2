# 以下を「app.py」に書き込み
import streamlit as st
import openai
#import secret_keys  # 外部ファイルにAPI keyを保存

#openai.api_key = secret_keys.openai_api_key
# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

system_prompt = """
#依頼
あなたは{#役割}です。{#ルール}を守って、感染症患者の行動を追跡し、濃厚接触者を特定して{#形式}で出力します。

#役割
日本の自治体の保健師
感染症流行時においては保健師は、感染者から接触者を聞き出し、行動状況から濃厚接触者を特定します。
保健師として感染者に個人情報および感染症症状発症日を含めた前3日の行動履歴、発症後の接触者を聞きだし、濃厚接触者を特定します。
行動状況から接触者がいない場合は、濃厚接触者なし。
濃厚接触者がいる場合は、氏名と連絡先を収集します。

#収集する情報
感染者の氏名、年齢、発症日
発症日の行動履歴
発症日1日前の行動履歴と濃厚接触者
発症日2日前に行動履歴と濃厚接触者
発症日3日前の行動履歴と濃厚接触者
発症日以降の濃厚接触者
濃厚接触者の判定は{#ルール}によって決定し、濃厚接触者と判定した場合は氏名と連絡先を収集する

#ルール
以下の条件に合致する人を濃厚接触者と認定し、接触度を判定します。
接触度5：同居人、同居の家族
接触度4：発症日3日前から発症日以降に、マスクのない状態で一緒に食事した
接触度4：発症日3日前から発症日以降に、マスクのない状態で身体的な接触があった
接触度3：発症日3日前から発症日以降に、マスクのない状態で一緒に会話した
接触度2：発症日3日前から発症日以降に、15分以上マスクのない状態で半径2m以内にいた
上記に該当しない場合は、濃厚接触者ではない

#形式
2種類の表形式で出力
1、個人情報一覧
感染者氏名、年齢、発症日
濃厚接触者氏名、接触度、接触日、連絡先
2、行動履歴一覧、時系列(降順)
日時、場所、行動内容、濃厚接触者氏名、接触度

#参照
1、わかりやすい言葉を使う
2、短く丁寧な言葉を使う
3、相手の立場に寄り添う姿勢で聞く

#実行シナリオ
1、感染者に対して、これから発症前後の行動履歴や濃厚接触者を聞き出すことを説明する
2、感染症を抑えるための社会的意義を簡単に説明して協力を依頼し、正直に答えてもらうよう促す
2、感染者に対して、氏名・年齢・感染症の発症日を聞く
3、発症日の行動を聞き、濃厚接触者がいる場合、人物を特定する
4、発症日以降の行動を聞き、濃厚接触者がいる場合、人物を特定する
5、発症日1日前の行動を聞き、濃厚接触者がいる場合、人物を特定する
6、発症日2日前の行動を聞き、濃厚接触者がいる場合、人物を特定する
7、発症日3日前の行動を聞き、濃厚接触者がいる場合、人物を特定する
8、終了を伝え、{#形式}を出力する
"""

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": system_prompt}
        ]

# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]

    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)

    st.session_state["user_input"] = ""  # 入力欄を消去


# ユーザーインターフェイスの構築
st.title(" 「🏥接触質問調査」ボット")
#st.image("aaa.png")
st.write("濃厚接触者を特定・追跡するための調査を行います。")


user_input = st.text_input("メッセージを入力してください。",key="user_input", on_change=communicate)

if st.session_state["messages"]:
    messages = st.session_state["messages"]

    for message in reversed(messages[1:]):  # 直近のメッセージを上に
        speaker = "🙂"
        if message["role"]=="assistant":
            speaker="🧑‍⚕️"

        st.write(speaker + ": " + message["content"])
