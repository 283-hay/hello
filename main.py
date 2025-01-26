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

if page_id in ["default", "page_top"]:
    st.write("翼")

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
    data = json.loads(file.read())
    # データフレームに変換
    df = pd.json_normalize(data[switch_item(page_id)])

# カラム名の切替
def switch_columns(value):
    switcher = {
        "default": ['優先順位', '項目名', '開始日（予定）'],
        "page_top": ['優先順位', '項目名', '開始日（予定）'],
        "page_saving": ['年月', '銀行', 'NISA'],
        "page_living": ['年月', '電気', '水道', 'ガス']
    }
    return switcher.get(value, "Invalid value")

# カラム名の設定
df.columns = switch_columns(page_id)

# データフレームの表示
# df1 = st.empty()
# df1.write(df)

# 行単位で編集ボタンを追加
for i in range(len(df)):
    cols = st.columns(len(df.columns) + 1)
    for j, col in enumerate(df.columns):
        cols[j].write(df.at[i, col])
    if cols[-1].button(f'編集 (行 {i+1})'):
        # 編集可能なデータフレームを表示する関数
        def editable_dataframe(df, row_index):
            edited_df = df.copy()
            cols = st.columns(len(df.columns))
            for j, col in enumerate(df.columns):
                edited_df.at[row_index, col] = cols[j].text_input(f'{col} (行 {row_index+1})', value=df.at[row_index, col])
            return edited_df

        # 編集可能なデータフレームを表示
        edited_df = editable_dataframe(df, i)

        # 編集後のデータフレームを表示
        st.write('編集後のデータフレーム:')
        st.write(edited_df)

        # 保存ボタンを配置
        if st.button('保存'):
            # データフレームを辞書に変換
            updated_data = edited_df.to_dict(orient='records')
            # JSONファイルに保存する関数
            def save_to_json(data, filename):
                with open(filename, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
            # 元のJSONデータを更新
            data[switch_item(page_id)] = updated_data
            # JSONファイルに保存
            save_to_json(data, switch_info(page_id))
            st.success('データが保存されました。')

if page_id in ["default", "page_top"]:
    st.write("智香ちゃん")
    df2 = st.empty()
    df2.write(df)

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