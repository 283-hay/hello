import streamlit as st
import pandas as pd
import json
import altair as alt
import db
import datetime

# キーの初期値を設定
key = "isNotLoggedIn"

# 今日の日付を初期値として設定
default_date = datetime.date.today()

# アプリの起動時にデータベースを初期化
db.initialize_database()

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
# サイドバー関連
#####

# ページ一覧を定義
pages = dict(
    page_top="トップページ",
    page_saving="貯金",
    page_utility="光熱費",
    page_living="生活費",
)

if st.session_state[key] not in ["isNotLoggedIn", "unchecked"]:
    #####
    # ログアウトボタンを表示
    #####
    if st.sidebar.button("ログアウト"):
        logout()

    #####
    # ページ切替情報欄
    #####

    # 区切り線とサブヘッダーを表示
    st.sidebar.markdown("---")
    st.sidebar.subheader("ページ切替")

    page_id = st.sidebar.selectbox( 
        "ページ",
        ["page_saving", "page_utility", "page_living", "page_top"],
        # 描画する項目を日本語に変換
        format_func=lambda page_id: pages[page_id], 
    )

    if page_id != "page_top":
        #####
        # 一覧表示範囲指定
        #####

        # 区切り線とサブヘッダーを表示
        st.sidebar.markdown("---")
        st.sidebar.subheader("一覧表示範囲指定")

        # 年のリストを作成
        detail_years = [str(year) for year in range(2023, 2030)]

        # 開始年と終了年のプルダウンリストを表示
        start_year = st.sidebar.selectbox("開始年", detail_years, index=detail_years.index(str(default_date - datetime.timedelta(days=365))[:4]))
        end_year = st.sidebar.selectbox("終了年", detail_years, index=detail_years.index(str(default_date)[:4]))

        #####
        # 一覧表示範囲指定
        #####

        # 区切り線とサブヘッダーを表示
        st.sidebar.markdown("---")
        st.sidebar.subheader("詳細表示指定")

        # 月のリストを作成
        detail_months = [f'{month:02}' for month in range(1, 13)]

        # 年と月のプルダウンリストを表示
        selected_year = st.sidebar.selectbox("年", detail_years, index=detail_years.index(str(default_date)[:4]))
        selected_month = st.sidebar.selectbox("月", detail_months, index=detail_months.index(str(default_date)[5:7]))

        # 注意文言を表示
        st.sidebar.markdown("※ 前月から表示されます。")

        # 選択された年月を結合
        selected_year_month = selected_year + "-" + selected_month

        #####
        # 新規登録関連
        #####
        # 区切り線とサブヘッダーを表示
        st.sidebar.markdown("---")
        st.sidebar.subheader("新規登録")

        # 登録項目を表示
        match page_id:
            case "page_saving":
                date = st.sidebar.date_input('日付', value=default_date)
                items = ["銀行", "NISA"]
                item = st.sidebar.selectbox('項目', items)
                bill = st.sidebar.number_input('金額', step=1)
                memo = st.sidebar.text_input('備考')
            case "page_utility":
                date = st.sidebar.date_input('日付', value=default_date)
                items = ["電気", "ガス", "水道"]
                item = st.sidebar.selectbox('項目', items)
                bill = st.sidebar.number_input('金額', step=1)
                memo = st.sidebar.text_input('備考')
            case "page_living":
                date = st.sidebar.date_input('日付', value=default_date)
                items = ["固定費", "食費", "その他生活費", "特別費", "雑費", "分類不能", "未登録"]
                item = st.sidebar.selectbox('項目', items)
                bill = st.sidebar.number_input('金額', step=1)
                memo = st.sidebar.text_input('備考')
            case _:
                name = st.sidebar.text_input('名前')
                age = st.sidebar.number_input('年齢', min_value=0)

        # 登録ボタン
        if st.sidebar.button('登録'):
            # 登録処理
            if page_id in ["page_saving", "page_saving", "page_utility"] and bill == 0:
                st.sidebar.error('金額には0以外を入力してね。')
            else:
                match page_id:
                    case "page_saving":
                        db.save_saving(date, item, bill, memo)
                    case "page_living":
                        db.save_living(date, bill, memo)
                    case "page_utility":
                        db.save_utility(date, item, bill, memo)
                    case _:
                        db.save_user(name, age)
                st.sidebar.success('登録完了!')

        # 注意文言を表示
        st.sidebar.markdown("※ 入力誤り時の相殺処理にも利用。")


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
# Json関連
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
    return keys, data

if st.session_state[key] != "isNotLoggedIn":
    if st.session_state[key] == "unchecked" or page_id == "page_top":
        keys, data = load_json_data(page_id)
        keys2, data2 = load_json_data(page_id)
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

#####
# ページの作成と表示
#####
if st.session_state[key] != "isNotLoggedIn":
    if st.session_state[key] == "unchecked" or page_id == "page_top":
        # 翼
        page = ItemListPage(switch_title(page_id), sorted(data, key=lambda x: x[keys[0]]), keys)
        page.render()
        # 智香
        page2 = ItemListPage("智香", sorted(data2, key=lambda x: x[keys2[0]]), keys2)
        page2.render()

    else:
        # タイトルを表示
        st.title(switch_title(page_id))
        # データを取得(グラフと一覧/詳細)
        try:
            # データ取得 #Todo Filter
            # if page_id == "page_saving":
            if page_id in ["page_saving", "page_living"]: # 一時的に
                df_all = db.get_all_savings(start_year, end_year)
                df_detail = db.get_detail_savings(selected_year_month)
            elif page_id == "page_utility":
                df_all = db.get_all_utilities(start_year, end_year)
                df_detail = db.get_detail_utilities(selected_year_month)
            else:
                df_all = db.get_all_users()
                df_detail = db.get_detail_users()
        # except pd.io.sql.DatabaseError:
        #     st.error('Failed to access the database.')
        except pd.io.sql.DatabaseError as e: # デバッグ用
            st.error(f'Failed to access the database. Error details: {e}')

        # 各列値を設定、空の場合は0に設定
        # if page_id == "page_saving":
        if page_id in ["page_saving", "page_living"]: # 一時的に
            df_all['bank'] = pd.to_numeric(df_all['bank'], errors='coerce').fillna(0)
            df_all['nisa'] = pd.to_numeric(df_all['nisa'], errors='coerce').fillna(0)
        elif page_id == "page_utility":
            df_all['elec'] = pd.to_numeric(df_all['elec'], errors='coerce').fillna(0)
            df_all['water'] = pd.to_numeric(df_all['water'], errors='coerce').fillna(0)
            df_all['gas'] = pd.to_numeric(df_all['gas'], errors='coerce').fillna(0)
        elif page_id == "page_living":
            df_all['電気'] = pd.to_numeric(df_all['電気'], errors='coerce').fillna(0)
            df_all['水道'] = pd.to_numeric(df_all['水道'], errors='coerce').fillna(0)
            df_all['ガス'] = pd.to_numeric(df_all['ガス'], errors='coerce').fillna(0)

        # データを長形式に変換し、グラフを作成
        df_long = df_all.melt(id_vars='year_month', var_name='category', value_name='amount')
        chart = alt.Chart(df_long).mark_line(point=True).encode(
            x='year_month',
            y='amount',
            color='category',
            tooltip=['year_month', 'category', 'amount']
        # ).properties(
        #     title='Savings Data'
        ).interactive()

        # Streamlitでグラフを表示
        st.altair_chart(chart, use_container_width=True)

        # 区切り線とヘッダーと一覧を表示
        st.markdown("---")
        st.header('一覧')
        st.dataframe(df_all)

        # 区切り線とヘッダーと詳細を表示
        st.markdown("---")
        st.header('詳細')
        st.dataframe(df_detail)

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