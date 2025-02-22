import sqlite3
import pandas as pd

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
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS utilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            item TEXT NOT NULL,
            bill INTEGER
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
        INSERT INTO saving (date, item, bill, memo) VALUES (?, ?, ?, ?)
    ''', (date, item, bill, memo))
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

# データを更新する関数
# def update_user(user_id, name, age):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute('''
#         UPDATE users SET name = ?, age = ? WHERE id = ?
#     ''', (name, age, user_id))
#     conn.commit()
#     conn.close()

# データを削除する関数
# def delete_user(user_id):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute('''
#         DELETE FROM users WHERE id = ?
#     ''', (user_id,))
#     conn.commit()
#     conn.close()

#####
# データを取得する関数
#####

# ユーザーデータ取得
def get_all_users():
    conn = get_connection()
    df = pd.read_sql_query('SELECT * FROM users', conn)
    conn.close()
    return df

# 貯金データ取得
def get_all_savings():
    conn = get_connection()

    query = '''
    WITH bank_summary AS (
        SELECT strftime('%Y-%m', date) AS year_month,
            SUM(bill) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS bank,
            ROW_NUMBER() OVER (PARTITION BY strftime('%Y-%m', date) ORDER BY date DESC) AS rn
        FROM saving
        WHERE item = "銀行"
    ),
    nisa_summary AS (
        SELECT strftime('%Y-%m', date) AS year_month,
            SUM(bill) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS nisa,
            ROW_NUMBER() OVER (PARTITION BY strftime('%Y-%m', date) ORDER BY date DESC) AS rn
        FROM saving
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
    UNION
    SELECT n.year_month, COALESCE(b.bank, 0) AS bank, n.nisa
    FROM nisa_latest n
    LEFT JOIN bank_latest b ON n.year_month = b.year_month
    ORDER BY year_month;
    '''

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 光熱費データ取得
def get_all_utilities():
    conn = get_connection()
    df = pd.read_sql_query('SELECT * FROM utilities', conn)
    conn.close()
    return df

