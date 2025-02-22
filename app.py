import streamlit as st
import sqlite3
import pandas as pd

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
    st.dataframe(users_df)
except pd.io.sql.DatabaseError:
    st.error('Failed to access the database.')
