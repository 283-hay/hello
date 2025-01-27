import streamlit as st
import pandas  as pd
import json
# from st_aggrid import AgGrid, GridUpdateMode
# from st_aggrid.grid_options_builder import GridOptionsBuilder

key = "default"

#####
# 各制御関連の定義
#####

# 初回画面か否かの判定に使用するkey
if key not in st.session_state:
    st.session_state[key] = "unchecked"

# ページ切替に使用するpage_id
if st.session_state[key] == "unchecked":
    page_id = "default"

#####
# page一覧関連
#####

# ページ一覧を定義
pages = dict(
    page_top="トップページ",
    page_saving="貯金",
    page_living="生活費",
)

# st.sidebar.*でサイドバーに表示
if st.session_state[key] != "unchecked":
    page_id = st.sidebar.selectbox( 
        "ページ切替",
        ["page_saving", "page_living", "page_top"],
        # 描画する項目を日本語に変換
        format_func=lambda page_id: pages[page_id], 
    )

#####
# title表示関連
#####

# titleの切替
def switch_title(value):
    switcher = {
        "default": "トップページ",
        "page_top": "トップページ",
        "page_saving": "貯金",
        "page_living": "生活費",
    }
    return switcher.get(value, "Invalid value")

# titleを取得し表示
if st.session_state[key] == "unchecked":
    st.title("初回ページ")
else:
    st.title(switch_title(page_id))

#####
# body表示関連
#####

# 取得ファイルの切替
def switch_info(value):
    switcher = {
        "default": "plan2025_tsubasa.txt",
        "page_top": "plan2025_tsubasa.txt",
        "page_saving": "saving.txt",
        "page_living": "living.txt"
    }
    return switcher.get(value, "Invalid value")

# 取得itemsの切替
def switch_item(value):
    switcher = {
        "default": "plans",
        "page_top": "plans",
        "page_saving": "savings",
        "page_living": "livings"
    }
    return switcher.get(value, "Invalid value")

# データフレームの取得
with open(switch_info(page_id), 'r', encoding='utf-8') as file:
    # ファイルの内容を読み込みJSONデータを辞書に変換
    # data = json.loads(file.read())
    data = json.loads(file.read()).get(switch_item(page_id), [])
    # データフレームに変換
    # df = pd.json_normalize(data[switch_item(page_id)])
    
# カラム名の切替
# def switch_columns(value):
#     switcher = {
#         "default": ['優先順位', '項目名', '開始日（予定）'],
#         "page_top": ['優先順位', '項目名', '開始日（予定）'],
#         "page_saving": ['年月', '銀行', 'NISA'],
#         "page_living": ['年月', '電気', '水道', 'ガス']
#     }
#     return switcher.get(value, "Invalid value")

# カラム名の設定
# df.columns = switch_columns(page_id)

# df = st.empty()
# df.write(df)

class ItemListPage:
    def __init__(self, title, data):
        self.title = title
        self.data = data

    def render(self) -> None:
        # タイトルの表示
        st.title(self.title)

        # テーブルの表示
        col_size = [1, 2, 2, 2, 2]
        columns = st.columns(col_size)
        headers = ["優先順位", "項目名", "開始日（予定）", "開始日（実績）", ""]
        for col, field_name in zip(columns, headers):
            col.write(field_name)

        for index, item in enumerate(self.data):
            (
                priority_col,
                name_col,
                start_col,
                started_col,
                button_col,
            ) = st.columns(col_size)
            priority_col.write(item["優先順位"])
            name_col.write(item["項目名"])
            start_col.write(item["開始日（予定）"])
            started_col.write(item["開始日（実績）"])
            if button_col.button("編集", key=index):
                st.session_state[f"edit_{index}"] = not st.session_state.get(f"edit_{index}", False)

            if st.session_state.get(f"edit_{index}", False):
                self._edit_item(index)

    def _edit_item(self, index: int) -> None:
        item = self.data[index]
        st.write(f"編集: {item['優先順位']}")
        new_priority_col = int(st.text_input("優先順位", value=item["優先順位"]))
        new_name_col = st.text_input("項目名", value=item["項目名"])
        new_start_col = st.text_input("開始日（予定）", value=item["開始日（予定）"])
        new_started_col = st.text_input("開始日（実績）", value=item["開始日（実績）"])

        if st.button("保存", key=f"save_{index}"):
            self.data[index]["優先順位"] = new_priority_col
            self.data[index]["項目名"] = new_name_col
            self.data[index]["開始日（予定）"] = new_start_col
            self.data[index]["開始日（実績）"] = new_started_col
            st.success("データが保存されました。")
            
            # JSONファイルに保存する関数
            def save_to_json(data, filename):
                with open(filename, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
            # 元のJSONデータを更新
            updated_data = {switch_item(page_id): self.data}
            # JSONファイルに保存
            save_to_json(updated_data, switch_info(page_id))

            # 編集状態をリセット
            st.session_state[f"edit_{index}"] = False
            # st.session_state.get(f"edit_{index}", False)

# ページの作成と表示
page = ItemListPage("翼2025抱負", sorted(data, key=lambda x: x['優先順位']))
page.render()

# if page_id in ["default", "page_top"]:
#     st.write("智香ちゃん")
#     df2 = st.empty()
#     df2.write(df)

# img = Image.open('.jpg')
# st.image(img, caption='', use_column_sidth=True)

#####
# 初回画面の表示関連
#####

# 次へボタンが押されたときの処理
def next_button_click():
    st.session_state[key] = "checked"
   
# 内容確認チェック後に次へボタンを表示する
if page_id == "default":
    if st.checkbox('内容を確認した'): 
        st.button('次へ', on_click=next_button_click)