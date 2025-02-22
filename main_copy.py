import streamlit as st
import pandas as pd
import json
import altair as alt
import sqlite3

key = "isNotLoggedIn"

#####
# データベース連の定義
#####

# データベース接続関数
def get_connection():
    conn = sqlite3.connect('example.db')
    return conn

# データベースとテーブルを初期化する関数
def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# データをデータベースに保存する関数
def save_user(name, age):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (name, age) VALUES (?, ?)
    ''', (name, age))
    conn.commit()
    conn.close()

# データを更新する関数
def update_user(user_id, name, age):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET name = ?, age = ? WHERE id = ?
    ''', (name, age, user_id))
    conn.commit()
    conn.close()

# データを削除する関数
def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM users WHERE id = ?
    ''', (user_id,))
    conn.commit()
    conn.close()

# データを取得する関数
def get_all_users():
    conn = get_connection()
    df = pd.read_sql_query('SELECT * FROM users', conn)
    conn.close()
    return df

# アプリの起動時にデータベースを初期化
initialize_database()

# StreamlitアプリのUI
st.title('User Management App')

# ユーザー情報の登録
st.header('Register New User')
name = st.text_input('Name')
age = st.number_input('Age', min_value=0)

if st.button('Register'):
    save_user(name, age)
    st.success('User registered successfully!')

# 登録されたユーザーを表示
st.header('Registered Users')
try:
    users_df = get_all_users()
    print(users_df)

    for index, row in users_df.iterrows():
        cols = st.columns([1, 2, 1, 2, 1, 1])  # カラムサイズを指定
        cols[0].write(row['id'])
        cols[1].write(row['name'])
        cols[2].write(row['age'])

        if cols[3].button(f"Edit {row['id']}"):
            new_name = st.text_input(f"New Name for ID {row['id']}", value=row['name'])
            new_age = st.number_input(f"New Age for ID {row['id']}", min_value=0, value=row['age'])
            if st.button(f"Save {row['id']}"):
                update_user(row['id'], new_name, new_age)
                st.success(f"User {row['id']} updated successfully!")

        if cols[4].button(f"Delete {row['id']}"):
            delete_user(row['id'])
            st.success(f"User {row['id']} deleted successfully!")

    st.dataframe(users_df)
except pd.io.sql.DatabaseError:
    st.error('Failed to access the database.')


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
    username = st.text_input("ユーザー名").upper()
    password = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        login(username, password)
else:
    if st.button("ログアウト"):
        logout()

#####
# 各制御関連の定義
#####

# ログイン前後、同意前後を制御するkey
if key not in st.session_state:
    st.session_state[key] = "isNotLoggedIn"

# 表示するページを制御するpage_id
if st.session_state[key] == "unchecked":
    page_id = "default"

#####
# page一覧関連
#####

# ページ一覧を定義
pages = dict(
    page_top="トップページ",
    page_saving="貯金",
    page_utility="光熱費",
    page_living="生活費",
)

# st.sidebar.*でサイドバーに表示
if st.session_state[key] not in ["isNotLoggedIn", "unchecked"]:
    page_id = st.sidebar.selectbox( 
        "ページ切替",
        ["page_saving", "page_utility", "page_living", "page_top"],
        # 描画する項目を日本語に変換
        format_func=lambda page_id: pages[page_id], 
    )    

#####
# title表示関連
#####

# titleの切替
def switch_title(value):
    switcher = {
        "default": "翼抱負",
        "page_top": "翼抱負",
        "page_saving": "貯金",
        "page_utility": "光熱費",
        "page_living": "生活費",
    }
    return switcher.get(value, "Invalid value")

#####
# body表示関連
#####

# 取得ファイルの切替
def switch_file(value):
    switcher = {
        "default": "plan2025_tsubasa.txt",
        "page_top": "plan2025_tsubasa.txt",
        "page_saving": "saving.txt",
        "page_utility": "utility.txt",
        "page_living": "living.txt"
    }
    return switcher.get(value, "Invalid value")

# 取得itemsの切替
def switch_item(value):
    switcher = {
        "default": "plans",
        "page_top": "plans",
        "page_saving": "savings",
        "page_utility": "utilities",
        "page_living": "livings"
    }
    return switcher.get(value, "Invalid value")

# JSONデータの取得
def load_json_data(page_id):
    with open(switch_file(page_id), 'r', encoding='utf-8') as file:
        data_item = json.loads(file.read())
        # キーのリストの取得、ここでやるべきでない
        keys = list(data_item[switch_item(page_id)][0].keys()) if switch_item(page_id) in data_item and len(data_item[switch_item(page_id)]) > 0 else []
        # 指定itemの取得、ここでやるべきでない
        data = data_item.get(switch_item(page_id), [])
        print(data)
    return keys, data

if st.session_state[key] != "isNotLoggedIn":
    keys, data = load_json_data(page_id)
    print(data)
    if st.session_state[key] == "unchecked" or page_id == "page_top":
        #  keys2, data2 = load_json_data(page_id)
        with open("plan2025_chika.txt", 'r', encoding='utf-8') as file: #冗長的、ベタ書きしただけ
            data_item = json.loads(file.read())
            keys2 = list(data_item[switch_item(page_id)][0].keys()) if switch_item(page_id) in data_item and len(data_item[switch_item(page_id)]) > 0 else []
            data2 = data_item.get(switch_item(page_id), [])

class ItemListPage:
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

        def format_number_with_commas(value):
            try:
                number = int(value)
                return "{:,}".format(number)
            except ValueError:
                return value

        # ヘッダーの表示
        for col, field_name in zip(columns, self.keys):
            col.write(field_name)

        # データの表示
        for index, item in enumerate(self.data):
            cols = st.columns(col_size)
            for i, key in enumerate(self.keys):
                cols[i].write(format_number_with_commas(item[key]))
            if cols[-1].button("編集", key=f"{self.title}_{index}"):
                st.session_state[f"edit_{self.title}_{index}"] = not st.session_state.get(f"edit_{self.title}_{index}", False)
            if st.session_state.get(f"edit_{self.title}_{index}", False):
                self._edit_item(index)

    def _edit_item(self, index: int) -> None:
        item = self.data[index]
        st.write(f"編集: {item[self.keys[0]]}")

        new_values = {}
        for key in self.keys:
            if isinstance(item[key], int):
                new_values[key] = int(st.text_input(key, value=item[key], key=f"{self.title}_{key}_{index}"))
            elif isinstance(item[key], float):
                new_values[key] = float(st.text_input(key, value=item[key], key=f"{self.title}_{key}_{index}"))
            else:
                new_values[key] = st.text_input(key, value=item[key], key=f"{self.title}_{key}_{index}")

        if st.button("保存", key=f"save_{self.title}_{index}"):
            for key in self.keys:
                self.data[index][key] = new_values[key]
            st.success("データが保存されました。")

            updated_data = {self.title: self.data}
            save_to_json(updated_data, switch_item(page_id))

            st.session_state[f"edit_{index}"] = False

# JSONデータの保存関数
def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# ページの作成と表示
if st.session_state[key] != "isNotLoggedIn":
    page = ItemListPage(switch_title(page_id), sorted(data, key=lambda x: x[keys[0]]), keys)
    page.render()

    # 抱負画面のみで追加表示
    if st.session_state[key] == "unchecked" or page_id == "page_top":
        page2 = ItemListPage("智香", sorted(data2, key=lambda x: x[keys2[0]]), keys2)
        page2.render()

# グラフの作成と表示
if st.session_state[key] != "isNotLoggedIn":
    if page_id in ["page_saving", "page_utility", "page_living"]:
        # データフレームに変換
        df = pd.DataFrame(data)

        # 各列値を設定、空の場合は0に設定
        # フィルターで表現したい、予定と実績表現も
        if page_id == "page_saving":
            df['銀行'] = pd.to_numeric(df['銀行'], errors='coerce').fillna(0)
            df['NISA'] = pd.to_numeric(df['NISA'], errors='coerce').fillna(0)
        elif page_id == "page_utility":
            df['電気'] = pd.to_numeric(df['電気'], errors='coerce').fillna(0)
            df['水道'] = pd.to_numeric(df['水道'], errors='coerce').fillna(0)
            df['ガス'] = pd.to_numeric(df['ガス'], errors='coerce').fillna(0)
        elif page_id == "page_living":
            df['電気'] = pd.to_numeric(df['電気'], errors='coerce').fillna(0)
            df['水道'] = pd.to_numeric(df['水道'], errors='coerce').fillna(0)
            df['ガス'] = pd.to_numeric(df['ガス'], errors='coerce').fillna(0)

        # データを長形式に変換
        df_long = df.melt(id_vars='年月', var_name='カテゴリ', value_name='金額')

        # グラフの作成
        chart = alt.Chart(df_long).mark_line(point=True).encode(
            x='年月',
            y='金額',
            color='カテゴリ',
            tooltip=['年月', 'カテゴリ', '金額']
        # ).properties(
        #     title='Savings Data'
        ).interactive()

        # Streamlitでグラフを表示
        # st.title('Savings Data Visualization')
        st.altair_chart(chart, use_container_width=True)

#####
# 初回画面の表示関連
#####

# 次へボタンが押されたときの処理
def next_button_click():
    st.session_state[key] = "checked"
   
# 内容確認チェック後に次へボタンを表示する
if st.session_state[key] == "unchecked":
    if st.checkbox('内容を確認した'): 
        st.button('次へ', on_click=next_button_click)