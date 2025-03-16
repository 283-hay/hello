# from tkinter import X
import streamlit as st
import sqlite3
# from pysqlcipher3 import dbapi2 as sqlite3
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# secrets.tomlからkeyを取得
keys = st.secrets["sqlite"]
sqlite_key = keys.get('key')
print(sqlite_key)

#####
# データベース連の定義
#####

# データベース接続関数
def get_connection():
    conn = sqlite3.connect('money.db')
    conn.execute(f"PRAGMA key = '{sqlite_key}';")  # パスワードを使用して複合
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
            note TEXT,
            entry_time DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, '+9 hours'))
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livings (
            date DATE NOT NULL,
            bill INTEGER NOT NULL,
            note TEXT,
            entry_time DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, '+9 hours'))
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS utilities (
            date DATE NOT NULL,
            item TEXT NOT NULL,
            bill INTEGER NOT NULL,
            note TEXT,
            entry_time DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, '+9 hours'))
        )
    ''')
    conn.commit()
    conn.close()

#####
# データをデータベースに保存する関数
#####

# 貯金データ保存
def save_saving(date, item, bill, note):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO savings (date, item, bill, note) VALUES (?, ?, ?, ?)
    ''', (date, item, bill, note))
    conn.commit()
    conn.close()

# 生活費データ保存
def save_living(date, bill, note):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO livings (date, bill, note) VALUES (?, ?, ?)
    ''', (date, bill, note))
    conn.commit()
    conn.close()

# 光熱費データ保存
def save_utility(date, item, bill, note):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO utilities (date, item, bill, note) VALUES (?, ?, ?, ?)
    ''', (date, item, bill, note))
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

def update_dreams(id=None, rank=None, item=None, progress=None, planned_start_date=None, start_date=None, planned_end_date=None, end_date=None):
    conn = get_connection()

    query = '''
    UPDATE dreams 
    SET
        rank = ?,
        item = ?,
        progress = ?,
        planned_start_date = ?,
        start_date = ?,
        planned_end_date = ?,
        end_date = ?,
        update_time = DATETIME('now', '+9 hours')
    WHERE id = ?
    '''

    conn.execute(query, (rank, item, progress, planned_start_date, start_date, planned_end_date, end_date, int(id)))
    conn.commit()
    conn.close()

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
# 目標データを取得する関数
#####
def get_dreams(select_year=None, user=None):
    conn = get_connection()

    base_query_first = '''
    SELECT
        id,
        rank,
        item,
        progress,
        planned_start_date,
        start_date,
        planned_end_date,
        end_date
    FROM dreams
    '''
    add_where = ' WHERE year = "' + select_year +'" AND user = "' + user +'"' 

    # 引数の有無の違いで処理
    if select_year is not None:
        query = base_query_first + add_where + " ORDER BY rank"
    else:
        query = base_query_first + " ORDER BY rank"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

#####
# 一覧データを取得する関数
#####

# 貯金データ取得(一覧)
def get_all_savings(start_year=None, end_year=None):
    conn = get_connection()

    base_query_first = '''
    WITH MonthlyTotals AS (
        SELECT 
            strftime('%Y-%m', date) AS year_month,
            SUM(CASE WHEN item = '銀行' THEN bill ELSE 0 END) AS bank,
            SUM(CASE WHEN item = 'NISA' THEN bill ELSE 0 END) AS nisa
        FROM 
            savings
        GROUP BY 
            strftime('%Y-%m', date)
    ),
    CumulativeTotals AS (
        SELECT 
            year_month,
            bank,
            nisa,
            SUM(bank) OVER (ORDER BY year_month) AS cumulative_bank,
            SUM(nisa) OVER (ORDER BY year_month) AS cumulative_nisa
        FROM 
            MonthlyTotals
    )
    SELECT 
        year_month,
        cumulative_bank AS bank,
        cumulative_nisa AS nisa,
        cumulative_bank + cumulative_nisa AS total
    FROM 
        CumulativeTotals
    '''

    base_query_last = ' ORDER BY year_month DESC'
    add_where = ' WHERE SUBSTR(year_month, 1, 4) BETWEEN "' + start_year + '" AND "' + end_year +'" '

    # 引数の有無の違いで処理
    if start_year is not None and end_year is not None:
        query = base_query_first + add_where + base_query_last
    else:
        query = base_query_first + base_query_last
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 光熱費データ取得(一覧)
def get_all_utilities(start_year=None, end_year=None):
    conn = get_connection()

    base_query_first = '''
    SELECT
        date AS year_month,
        SUM(CASE WHEN item = '電気' THEN bill ELSE 0 END) AS elec,
        SUM(CASE WHEN item = '水道' THEN bill ELSE 0 END) AS water,
        SUM(CASE WHEN item = 'ガス' THEN bill ELSE 0 END) AS gas
    FROM utilities
    '''
    base_query_last = '''
    GROUP BY year_month
    ORDER BY year_month DESC
    '''
    add_where = ' WHERE SUBSTR(year_month, 1, 4) BETWEEN "' + start_year + '" AND "' + end_year +'" '

    # 引数の有無の違いで処理
    if start_year is not None and end_year is not None:
        query = base_query_first + add_where + base_query_last
    else:
        query = base_query_first + base_query_last
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 生活費データ取得(一覧)
def get_all_livings(start_year=None, end_year=None):
    conn = get_connection()

    base_query_first = '''
    WITH MonthlyTotals AS (
        SELECT 
            strftime('%Y-%m', date) AS year_month,
            SUM(bill) AS monthly_total
        FROM 
            livings
        GROUP BY 
            strftime('%Y-%m', date)
    ),
    RunningTotals AS (
        SELECT 
            year_month,
            monthly_total,
            SUM(monthly_total) OVER (ORDER BY year_month) AS cumulative_total
        FROM 
            MonthlyTotals
    )
    SELECT 
        year_month,
        cumulative_total AS total
    FROM 
        RunningTotals
    '''
    base_query_last = ' ORDER BY year_month DESC'
    add_where = ' WHERE SUBSTR(year_month, 1, 4) BETWEEN "' + start_year + '" AND "' + end_year +'" '

    # 引数の有無の違いで処理
    if start_year is not None and end_year is not None:
        query = base_query_first + add_where + base_query_last
    else:
        query = base_query_first + base_query_last
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

#####
# 詳細データを取得する関数
#####
def get_detail(table=None, year_month=None):
    conn = get_connection()

    # 入力値の1か月前を計算し、整形
    last_month_pre = datetime.strptime(year_month, "%Y-%m") - relativedelta(months=1)
    lastmonth = last_month_pre.strftime('%Y-%m')

    # データ取得
    query = 'SELECT * FROM ' + table + ' WHERE SUBSTR(date, 1, 7) BETWEEN "' + lastmonth + '" AND "' + year_month +'" ' + 'ORDER BY date DESC'
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df