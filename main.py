import streamlit as st
import pandas as pd
import altair as alt
import db
import datetime

# キーの初期値を設定
key = "isNotLoggedIn"

# 今日の日付を初期値として設定
default_date = datetime.date.today()

# アプリの起動時にデータベースを初期化
db.initialize_database()

# secrets.tomlから夫のkeyを取得
keys = st.secrets["husband"]
husband_key = keys.get('key')

# secrets.tomlから妻のkeyを取得
keys = st.secrets["wife"]
wife_key = keys.get('key')


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

    # 年のリストを作成
    detail_years = [str(year) for year in range(2023, 2030)]

    if page_id == "page_top":
        pass
        # 表示年指定関連
        # select_year = st.sidebar.selectbox("選択年", detail_years, index=detail_years.index(str(default_date)[:4]))

        # # 新規登録関連
        # # 区切り線とサブヘッダーを表示
        # st.sidebar.markdown("---")
        # st.sidebar.subheader("新規登録")

        # # 登録項目を表示
        # date = st.sidebar.date_input('日付', value=default_date)
        # items = ["銀行", "NISA"]
        # item = st.sidebar.selectbox('項目', items)
        # bill = st.sidebar.number_input('金額', step=1)
        # note = st.sidebar.text_input('備考')

        # # 登録ボタン
        # if st.sidebar.button('登録'):
        #     # 登録処理
        #     db.save_saving(date, item, bill, note)
        #     st.sidebar.success('登録完了!')
    else:
        #####
        # 一覧表示範囲指定関連
        #####

        # 区切り線とサブヘッダーを表示
        st.sidebar.markdown("---")
        st.sidebar.subheader("一覧表示範囲指定")

        # 開始年と終了年のプルダウンリストを表示
        start_year = st.sidebar.selectbox("開始年", detail_years, index=detail_years.index(str(default_date - datetime.timedelta(days=365))[:4]))
        end_year = st.sidebar.selectbox("終了年", detail_years, index=detail_years.index(str(default_date)[:4]))

        #####
        # 詳細表示範囲指定関連
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
                note = st.sidebar.text_input('備考')
            case "page_utility":
                date = st.sidebar.date_input('日付', value=default_date)
                items = ["電気", "ガス", "水道"]
                item = st.sidebar.selectbox('項目', items)
                bill = st.sidebar.number_input('金額', step=1)
                note = st.sidebar.text_input('備考')
            case "page_living":
                date = st.sidebar.date_input('日付', value=default_date)
                # items = ["固定費", "食費", "その他生活費", "特別費", "雑費", "分類不能", "未登録"]
                # item = st.sidebar.selectbox('項目', items)
                bill = st.sidebar.number_input('金額', step=1)
                note = st.sidebar.text_input('備考')
            case _:
                st.sidebar.text('非該当ページです。')

        # 登録ボタン
        if st.sidebar.button('登録'):
            # 登録処理
            if page_id in ["page_saving", "page_saving", "page_utility"] and bill == 0:
                st.sidebar.error('金額には0以外を入力してね。')
            else:
                match page_id:
                    case "page_saving":
                        db.save_saving(date, item, bill, note)
                    case "page_living":
                        db.save_living(date, bill, note)
                    case "page_utility":
                        db.save_utility(date, item, bill, note)
                    case _:
                        st.sidebar.error('非該当ページです。')
                st.sidebar.success('登録完了!')

        # 注意文言を表示
        st.sidebar.markdown("※ 入力誤り時の相殺処理にも利用。")




#####
# titleの表示
#####

# titleの切替
def switch_title(value):
    switcher = {
        "default": "抱負",
        "page_top": "抱負",
        "page_saving": "貯金",
        "page_utility": "光熱費",
        "page_living": "生活費",
    }
    return switcher.get(value, "Invalid value")

if st.session_state[key] != "isNotLoggedIn":
    if page_id in ["page_saving", "page_utility", "page_living"]:
        st.title(switch_title(page_id))



#####
# ページの作成と表示
#####
def display_and_edit_goals(df, section_title, user_key):
    st.subheader(section_title)

    # セッション状態を使用してどの行が編集対象かを追跡
    editing_row_key = f"editing_row_{user_key}"
    if editing_row_key not in st.session_state:
        st.session_state[editing_row_key] = None

    # 項目タイトル行の作成
    header_col1, header_col2, header_col3, header_col4, header_col5, header_col6, header_col7, header_col8 = st.columns([1, 4, 1, 2, 2, 2, 2, 1])  # レイアウト調整
    header_col1.write("優先順位")
    header_col2.write("項目")
    header_col3.write("進捗")
    header_col4.write("開始予定")
    header_col5.write("開始実績")
    header_col6.write("終了予定")
    header_col7.write("終了実績")
    header_col8.write("編集")

    # 各行のデータと編集ボタンの作成
    for index, row in df.iterrows():
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 4, 1, 2, 2, 2, 2, 1])  # レイアウト調整
        col1.write(row['rank'])
        col2.write(row['item'])
        col3.write(row['progress'])
        col4.write(row['planned_start_date'])
        col5.write(row['start_date'])
        col6.write(row['planned_end_date'])
        col7.write(row['end_date'])
        
        # 編集ボタン
        if col8.button("編集", key=f"edit_{user_key}_{index}"):
            st.session_state[editing_row_key] = index

    # 編集項目の表示
    if st.session_state[editing_row_key] is not None:
        row = df.iloc[st.session_state[editing_row_key]]
        st.write(f"Editing row {st.session_state[editing_row_key]}:")
        id = row['id']
        rank = int(st.text_input("Rank", value=row['rank'], key=f"rank_{user_key}_{st.session_state[editing_row_key]}"))
        item = st.text_input("Item", value=row['item'], key=f"item_{user_key}_{st.session_state[editing_row_key]}")
        progress = int(st.text_input("Progress", value=row['progress'], key=f"progress_{user_key}_{st.session_state[editing_row_key]}"))
        planned_start_date = st.date_input("Planned Start Date", value=pd.to_datetime(row['planned_start_date']), key=f"planned_start_date_{user_key}_{st.session_state[editing_row_key]}")
        start_date = st.date_input("Start Date", value=pd.to_datetime(row['start_date']), key=f"start_date_{user_key}_{st.session_state[editing_row_key]}")
        planned_end_date = st.date_input("Planned End Date", value=pd.to_datetime(row['planned_end_date']), key=f"planned_end_date_{user_key}_{st.session_state[editing_row_key]}")
        end_date = st.date_input("End Date", value=pd.to_datetime(row['end_date']), key=f"end_date_{user_key}_{st.session_state[editing_row_key]}")

        # 保存ボタン
        if st.button("保存", key=f"save_{user_key}"):
            db.update_dreams(id, rank, item, progress, planned_start_date, start_date, planned_end_date, end_date)
            st.write("保存成功！")
            st.session_state[editing_row_key] = None
            # 更新のため
            # df = db.get_dreams(str(default_date)[:4], user_key)
            # display_and_edit_goals(df, section_title, user_key)

if st.session_state[key] != "isNotLoggedIn":
    if st.session_state[key] == "unchecked" or page_id == "page_top":
        # 編集状態の初期化
        # st.session_state.editing_row = None
        #### 夫 ####
        df_husband = db.get_dreams(str(default_date)[:4], husband_key)
        display_and_edit_goals(df_husband, "夫抱負", husband_key)

        #### 妻 ####
        df_wife = db.get_dreams(str(default_date)[:4], wife_key)
        display_and_edit_goals(df_wife, "妻抱負", wife_key)

    else:
        # データを取得(グラフと一覧/詳細)
        try:
            # データ取得
            match page_id:
                case "page_saving":
                    df_all = db.get_all_savings(start_year, end_year)
                    df_detail = db.get_detail('savings', selected_year_month)
                case "page_living":
                    df_all = db.get_all_livings(start_year, end_year)
                    df_detail = db.get_detail('livings', selected_year_month)
                case "page_utility":
                    df_all = db.get_all_utilities(start_year, end_year)
                    df_detail = db.get_detail('utilities', selected_year_month)
                case _:
                    st.sidebar.error('非該当ページです。')
        except pd.io.sql.DatabaseError:
            st.error('Failed to access the database.')
        # except pd.io.sql.DatabaseError as e: # デバッグ用
        #     st.error(f'Failed to access the database. Error details: {e}')

        # 各列値を設定、空の場合は0に設定
        match page_id:
            case "page_saving":
                df_all['bank'] = pd.to_numeric(df_all['bank'], errors='coerce').fillna(0)
                df_all['nisa'] = pd.to_numeric(df_all['nisa'], errors='coerce').fillna(0)
                df_all['total'] = pd.to_numeric(df_all['total'], errors='coerce').fillna(0)
            case "page_living":
                df_all['total'] = pd.to_numeric(df_all['total'], errors='coerce').fillna(0)
            case "page_utility":
                df_all['elec'] = pd.to_numeric(df_all['elec'], errors='coerce').fillna(0)
                df_all['water'] = pd.to_numeric(df_all['water'], errors='coerce').fillna(0)
                df_all['gas'] = pd.to_numeric(df_all['gas'], errors='coerce').fillna(0)
            case _:
                st.sidebar.error('非該当ページです。')

        # データを長形式に変換し、グラフを作成
        df_long = df_all.melt(id_vars='year_month', var_name='category', value_name='amount')
        chart = alt.Chart(df_long).mark_line(point=True).encode(
            x='year_month',
            y='amount',
            color='category',
            tooltip=['year_month', 'category', 'amount']
        ).interactive()

        # Streamlitでグラフを表示
        st.altair_chart(chart, use_container_width=True)

        # 区切り線とヘッダーと一覧を表示
        st.markdown("---")
        st.header('一覧')
        st.dataframe(df_all)

        # 区切り線とヘッダーを表示
        st.markdown("---")
        st.header('詳細')
        # 詳細のentry_time以外の項目を表示
        filtered_df_detail = df_detail.drop(columns=["entry_time"])
        st.dataframe(filtered_df_detail)



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