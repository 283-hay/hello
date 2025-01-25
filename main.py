import streamlit as st
import numpy as np
import pandas  as pd

st.title('Streamlit 超入門')

with open('requirements.txt', 'r', encoding='utf-8') as file:
    # ファイルの内容を読み込む
    content = file.read()

# ファイルの内容を表示する
print(content)

st.title(content)
