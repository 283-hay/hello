import streamlit as st
import pandas  as pd
import json
# from st_aggrid import AgGrid, GridUpdateMode
# from st_aggrid.grid_options_builder import GridOptionsBuilder

key = "isNotLoggedIn"

#####
# ログイン関連の定義
#####

# secrets.tomlからユーザー名とパスワードの一覧を取得
users = st.secrets["users"]

# セッションステートにログイン状態を保存
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ログイン関数
def login(username, password):
    if username in users and users[username] == password:
        st.session_state.logged_in = True
        st.success("ログイン成功！")
        st.session_state[key] = "unchecked"
    else:
        st.error("ユーザー名またはパスワードが間違っています。")

# ログアウト関数
def logout():
    st.session_state.logged_in = False
    st.session_state[key] = "isNotLoggedIn"
    st.success("ログアウトしました。")

# ログイン画面の表示
if not st.session_state.logged_in:
    st.title("ログイン画面")
    username = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        login(username, password)
else:
    if st.button("ログアウト"):
        logout()

#####
# 各制御関連の定義
#####

# 初回画面か否かの判定に使用するkey
if key not in st.session_state:
    st.session_state[key] = "isNotLoggedIn"

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
    page_living="光熱費",
)

# st.sidebar.*でサイドバーに表示
if st.session_state[key] not in ["isNotLoggedIn", "unchecked"]:
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
        "isNotLoggedIn": "",
        "default": "2025抱負",
        "page_top": "トップページ",
        "page_saving": "貯金",
        "page_living": "光熱費",
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
if st.session_state[key] != "isNotLoggedIn":
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
        # df = pd.json_normalize(data[switch_item(page_id)])

# データフレームを表示する場合
# df = st.empty()
# df.write(df)





# サンプルデータ
data1 = {
    "savings": [
        {"date": "2024年10月", "bank": "2377829", "nisa": "1949990"},
        {"date": "2024年11月", "bank": "2287829", "nisa": "2249990"},
        {"date": "2024年12月", "bank": "2607829", "nisa": "2549990"},
        {"date": "2025年01月", "bank": "2547808", "nisa": "2689990"},
        {"date": "2025年02月", "bank": "", "nisa": ""},
        {"date": "2025年03月", "bank": "", "nisa": ""}
    ]
}

data2 = {
    "expenses": [
        {"date": "2024年10月", "food": "50000", "rent": "100000"},
        {"date": "2024年11月", "food": "55000", "rent": "100000"},
        {"date": "2024年12月", "food": "60000", "rent": "100000"},
        {"date": "2025年01月", "food": "65000", "rent": "100000"},
        {"date": "2025年02月", "food": "70000", "rent": "100000"},
        {"date": "2025年03月", "food": "75000", "rent": "100000"}
    ]
}

# キーのリストを取得する関数
def get_keys(data_item):
    if len(data_item) > 0:
        return list(data_item[0].keys())
    return []



class ItemListPage:
    # def __init__(self, title, data):
    #     self.title = title
    #     self.data = data



    def __init__(self, title, data, keys):
        self.title = title
        self.data = data
        self.keys = keys


    def render(self) -> None:
        # タイトルの表示
        st.title(self.title)

        # テーブルの表示
        col_size = [1, 2, 2, 2, 2]
        columns = st.columns(col_size)
        # JSONから取得したkey名を項目名とする
        headers = keys

        def format_number_with_commas(value):
            try:
                # 文字列を整数に変換
                number = int(value)
                # カンマ区切りの形式で表示
                formatted_number = "{:,}".format(number)
                return formatted_number
            except ValueError:
                # 変換できない場合は元の文字列を返す
                return value

        for col, field_name in zip(columns, headers):
            col.write(field_name)

        for index, item in enumerate(self.data):
            cols = st.columns(col_size)
            cols[0].write(item[keys[0]]) # ループで取得したい 数字の時にカンマ欲しい
            cols[1].write(format_number_with_commas(item[keys[1]])) # 数字の時はカンマにする例
            cols[2].write(format_number_with_commas(item[keys[2]]))
            if len(keys) > 3:
                cols[3].write(format_number_with_commas(item[keys[3]]))
            if cols[-1].button("編集", key=index):
                st.session_state[f"edit_{index}"] = not st.session_state.get(f"edit_{index}", False)

            if st.session_state.get(f"edit_{index}", False):
                self._edit_item(index)

    def _edit_item(self, index: int) -> None:
        item = self.data[index]
        st.write(f"編集: {item[keys[0]]}")
        # ループで生成できないか valueの型考慮が難しい
        if page_id in ["isNotLoggedIn", "default", "page_top"]:
            new_priority_col = int(st.text_input(keys[0], value=item[keys[0]])) 
        else:
            new_priority_col = st.text_input(keys[0], value=item[keys[0]])
        new_col_0 = st.text_input(keys[1], value=item[keys[1]])
        new_col_1 = st.text_input(keys[2], value=item[keys[2]])
        if len(keys) > 3:
            new_col_2 = st.text_input(keys[3], value=item[keys[3]])

        if st.button("保存", key=f"save_{index}"):
            self.data[index][keys[0]] = new_priority_col  # ループで取得できないか いける
            self.data[index][keys[1]] = new_col_0
            self.data[index][keys[2]] = new_col_1
            if len(keys) > 3:
                self.data[index][keys[3]] = new_col_2
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
            # st.experimental_set_query_params()
            # 保存処理時に状態のリセットが行われないのか、描画が元に戻らない

# ページの作成と表示
if st.session_state[key] != "isNotLoggedIn":
    # page = ItemListPage(switch_title(page_id), sorted(data, key=lambda x: x[keys[0]]))
    # page.render()





    keys1 = get_keys(data)
    page = ItemListPage(switch_title(page_id), sorted(data, key=lambda x: x[keys[0]]), keys1)
    page.render()

    # keys2 = get_keys(data)
    # page2 = ItemListPage(switch_title(page_id), sorted(data, key=lambda x: x[keys[0]]), keys2)
    # page2.render()

# keys1 = get_keys(data1["savings"])
# page1 = ItemListPage("貯金", data1["savings"], keys1)
# page1.render()

# keys2 = get_keys(data2["expenses"])
# page2 = ItemListPage("生活費", data2["expenses"], keys2)




#####
# 初回画面の表示関連
#####

# 次へボタンが押されたときの処理
def next_button_click():
    st.session_state[key] = "checked"
   
# 内容確認チェック後に次へボタンを表示する
if st.session_state[key] != "isNotLoggedIn" and st.session_state[key] == "unchecked":
    if st.checkbox('内容を確認した'): 
        st.button('次へ', on_click=next_button_click)