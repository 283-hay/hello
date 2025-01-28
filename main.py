import streamlit as st
import pandas as pd
import json

# カスタムCSSを追加
st.markdown(
    """
    <style>
    @media screen and (max-width: 600px) {
        .custom-font {
            font-size: 12px;
        }
    }
    @media screen and (min-width: 601px) and (max-width: 1200px) {
        .custom-font {
            font-size: 16px;
        }
    }
    @media screen and (min-width: 1201px) {
        .custom-font {
            font-size: 20px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
        "default": "初回ページ",
        "page_top": "トップページ",
        "page_saving": "貯金",
        "page_living": "生活費",
    }
    return switcher.get(value, "Invalid value")

# titleを取得し表示
# st.title(switch_title(page_id))

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
    # ファイルの内容をJSONとして読み込む
    data_item = json.loads(file.read())
    def get_keys(data_item):
        if switch_item(page_id) in data_item and len(data_item[switch_item(page_id)]) > 0:
            return list(data_item[switch_item(page_id)][0].keys())
        return []

    # 関数を使用してキーのリストを取得
    keys = get_keys(data_item)
    
    # JSONデータを辞書に変換
    data = data_item.get(switch_item(page_id), [])
    # データフレームに変換
    df = pd.DataFrame(data)

class ItemListPage:
    def __init__(self, title, data, keys):
        self.title = title
        self.data = data
        self.keys = keys

    def render(self) -> None:
        # タイトルの表示
        st.title(self.title)

        # データフレームの表示
        st.dataframe(df, width=1000, height=500)

        for index, item in enumerate(self.data):
            cols = st.columns(len(self.keys) + 1)
            for i, key in enumerate(self.keys):
                if isinstance(item[key], int):
                    cols[i].write(f"{item[key]:,}")
                else:
                    cols[i].write(item[key])
            if cols[-1].button("編集", key=index):
                st.session_state[f"edit_{index}"] = not st.session_state.get(f"edit_{index}", False)

            if st.session_state.get(f"edit_{index}", False):
                self._edit_item(index)

    def _edit_item(self, index: int) -> None:
        item = self.data[index]
        st.write(f"編集: {item[self.keys[0]]}")
        new_values = {}
        for key in self.keys:
            new_values[key] = st.text_input(key, value=item[key])

        if st.button("保存", key=f"save_{index}"):
            for key in self.keys:
                self.data[index][key] = new_values[key]
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

            # ページを再レンダリング
            st.experimental_rerun()

# ページの作成と表示
page = ItemListPage(switch_title(page_id), sorted(data, key=lambda x: x[keys[0]]), keys)
page.render()

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
