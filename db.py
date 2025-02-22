import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# secrets.tomlからkeyを取得
# keys = st.secrets["sqlite"]
# sqlite_key = keys.get('key')

#####
# データベース連の定義
#####

# データベース接続関数
def get_connection():
    conn = sqlite3.connect('money.db')
    return conn

# データベースとテーブルを初期化する関数
def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS savings (
            date DATE NOT NULL,
            item TEXT NOT NULL,
            bill INTEGER NOT NULL,
            memo TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livings (
            date DATE NOT NULL,
            bill INTEGER NOT NULL,
            memo TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS utilities (
            date DATE NOT NULL,
            item TEXT NOT NULL,
            bill INTEGER NOT NULL,
            memo TEXT
        )
    ''')
    conn.commit()
    conn.close()

#####
# データをデータベースに保存する関数
#####

# ユーザーデータ保存
def save_user(name, age):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (name, age) VALUES (?, ?)
    ''', (name, age))
    conn.commit()
    conn.close()

# 貯金データ保存
def save_saving(date, item, bill, memo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO savings (date, item, bill, memo) VALUES (?, ?, ?, ?)
    ''', (date, item, bill, memo))
    conn.commit()
    conn.close()

# 生活費データ保存
def save_living(date, item, bill, memo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO livings (date, bill, memo) VALUES (?, ?, ?)
    ''', (date, bill, memo))
    conn.commit()
    conn.close()

# 光熱費データ保存
def save_utility(date, item, bill, memo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO utilities (date, item, bill, memo) VALUES (?, ?, ?, ?)
    ''', (date, item, bill, memo))
    conn.commit()
    conn.close()

#####
# データベースのデータを更新する関数
#####
# def update_user(user_id, name, age):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute('''
#         UPDATE users SET name = ?, age = ? WHERE id = ?
#     ''', (name, age, user_id))
#     conn.commit()
#     conn.close()

#####
# データベースのデータを削除する関数
#####
# def delete_user(user_id):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute('''
#         DELETE FROM users WHERE id = ?
#     ''', (user_id,))
#     conn.commit()
#     conn.close()

#####
# 一覧データを取得する関数
#####

# ユーザーデータ取得
def get_all_users():
    conn = get_connection()
    df = pd.read_sql_query('SELECT * FROM users', conn)
    conn.close()
    return df

# 貯金データ取得(一覧)
def get_all_savings(start_year=None, end_year=None):
    conn = get_connection()

    base_query_first = '''
    WITH bank_summary AS (
        SELECT strftime('%Y-%m', date) AS year_month,
            SUM(bill) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS bank,
            ROW_NUMBER() OVER (PARTITION BY strftime('%Y-%m', date) ORDER BY date DESC) AS rn
        FROM savings
        WHERE item = "銀行"
    ),
    nisa_summary AS (
        SELECT strftime('%Y-%m', date) AS year_month,
            SUM(bill) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS nisa,
            ROW_NUMBER() OVER (PARTITION BY strftime('%Y-%m', date) ORDER BY date DESC) AS rn
        FROM savings
        WHERE item <> "銀行"
    ),
    bank_latest AS (
        SELECT year_month, bank
        FROM bank_summary
        WHERE rn = 1
    ),
    nisa_latest AS (
        SELECT year_month, nisa
        FROM nisa_summary
        WHERE rn = 1
    )
    SELECT COALESCE(b.year_month, n.year_month) AS year_month,
        COALESCE(b.bank, 0) AS bank,
        COALESCE(n.nisa, 0) AS nisa
    FROM bank_latest b
    LEFT JOIN nisa_latest n ON b.year_month = n.year_month
    '''

    base_query_middle = '''
    UNION
    SELECT n.year_month, COALESCE(b.bank, 0) AS bank, n.nisa
    FROM nisa_latest n
    LEFT JOIN bank_latest b ON n.year_month = b.year_month
    '''
    base_query_last = ' ORDER BY year_month DESC'

    add_where = ' WHERE  SUBSTR(COALESCE(b.year_month, n.year_month), 1, 4) BETWEEN "' + start_year + '" AND "' + end_year +'" '
    if start_year is not None and end_year is not None:
        query = base_query_first + add_where + base_query_middle + add_where + base_query_last
    else:
        query = base_query_first + base_query_middle + base_query_last
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 光熱費データ取得(一覧)
def get_all_utilities(start_year=None, end_year=None):
    conn = get_connection()

    base_query_first = '''
    SELECT
        strftime('%Y-%m', date) AS year_month,
        SUM(CASE WHEN item = '電気' THEN bill ELSE 0 END) AS elec,
        SUM(CASE WHEN item = '水道' THEN bill ELSE 0 END) AS water,
        SUM(CASE WHEN item = 'ガス' THEN bill ELSE 0 END) AS gas
    FROM utilities
    GROUP BY year_month
    '''

    base_query_last = ' ORDER BY year_month DESC'

    # add_where = ' WHERE strftime('%Y-%m', date) BETWEEN "' + start_year + '" AND "' + end_year +'" '
    # add_where = ' WHERE year_month BETWEEN "' + start_year + '" AND "' + end_year +'" '

    if start_year is not None and end_year is not None:
        # query = base_query_first + add_where + base_query_last
        query = base_query_first + base_query_last
    else:
        query = base_query_first + base_query_last
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

#####
# 一覧データを取得する関数
#####

# 貯金データ取得(詳細)
def get_detail_savings(year_month=None):
    conn = get_connection()
    base_query_first = '''
    SELECT *
    FROM savings
    '''

    base_query_last = ' ORDER BY date DESC'

    # 入力値の1か月前を計算し、整形
    last_month_pre = datetime.strptime(year_month, "%Y-%m") - relativedelta(months=1)
    lastmonth = last_month_pre.strftime('%Y-%m')

    if year_month:
        query = base_query_first + ' WHERE SUBSTR(date, 1, 7) BETWEEN "' + lastmonth + '" AND "' + year_month +'" ' + base_query_last
    else:
        query = base_query_first + base_query_last
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 光熱費データ取得(詳細)
def get_detail_utilities(year_month=None):
    conn = get_connection()
    base_query_first = '''
    SELECT *
    FROM utilities
    '''

    base_query_last = ' ORDER BY date DESC'

    # 入力値の1か月前を計算し、整形
    last_month_pre = datetime.strptime(year_month, "%Y-%m") - relativedelta(months=1)
    lastmonth = last_month_pre.strftime('%Y-%m')

    if year_month:
        query = base_query_first + ' WHERE SUBSTR(date, 1, 7) BETWEEN "' + lastmonth + '" AND "' + year_month +'" ' + base_query_last
    else:
        query = base_query_first + base_query_last
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

