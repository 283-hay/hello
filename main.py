import streamlit as st
import pandas  as pd
import json
# import saving

page_id = []

# ページ一覧を定義
pages = dict(
    page_top="Top",
    page_saving="Saving",
)

# st.sidebar.*でサイドバーに表示
# if page_id != "page_top":
if page_id == []:
    page_id = st.sidebar.selectbox( 
        "ページ名",
        ["page_top", "page_saving"],
        # 描画する項目を日本語に変換
        format_func=lambda page_id: pages[page_id], 
    )

#####
# title関連
#####

# titleの切替
def switch_title(value):
    switcher = {
        "page_top": "Dashboard of family",
        "page_saving": "saving Page",
    }
    return switcher.get(value, "Invalid value")

# titleを取得し表示
st.title(switch_title(page_id))

#####
# 表示情報関連
#####

# 取得ファイルの切替
def switch_info(value):
    switcher = {
        "page_top": "plan2025_tsubasa.txt",
        "page_saving": "saving.txt",
    }
    return switcher.get(value, "Invalid value")

# 取得itemsの切替
def switch_item(value):
    switcher = {
        "page_top": "plans",
        "page_saving": "saving",
    }
    return switcher.get(value, "Invalid value")

# titleを取得し表示
with open(switch_info(page_id), 'r', encoding='utf-8') as file:
    # ファイルの内容を読み込みJSONデータを辞書に変換
    data = json.loads(file.read())
    # データフレームに変換
    df = pd.json_normalize(data[switch_item(page_id)])

# データフレームを表示
top_body = st.empty()
top_body.write(df)
# st.title(switch_title(page_id))


# ページの状態を定義
# Page = ["top"]

# タイトルを設定する関数
# def set_title(page):
#     titles = {
#         "top": "Dashboard of family",
#         "saving": "saving Page"
#     }
#     return titles.get(page, "Default Title")

# タイトルを表示
# top_title = st.title(set_title(Page[0]))

# img = Image.open('.jpg')
# st.image(img, caption='', use_column_sidth=True)

# with open('plan2025_tsubasa.txt', 'r', encoding='utf-8') as file:
#     # ファイルの内容を読み込みJSONデータを辞書に変換
#     data = json.loads(file.read())
#     # データフレームに変換
#     df = pd.json_normalize(data['plans'])

# データフレームを表示
# top_body = st.empty()
# top_body.write(df)

# st.write(df)

# 次へボタンが押されたときの処理
def next_button_click():
    # subprocess.run(["python", "saving.py"])

    st.session_state.checkbox = False
    # saving.greet()
    print("動いた")

# セッションステートの初期化
# if 'checkbox' not in st.session_state:
#     st.session_state.checkbox = False
    
# 内容確認後に次へボタンを表示する
if st.checkbox('内容を確認した'): 
# if st.checkbox('内容を確認した', key='checkbox'): 
    if st.button('次へ', on_click=next_button_click):
        st.session_state.checkbox = False
