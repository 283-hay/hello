import streamlit as st
import numpy as np
import pandas  as pd

st.title('Streamlit 超入門')

with open('requirements.txt', 'r', encoding='utf-8') as file:
    # ファイルの内容を読み込む
    content = file.read()

st.title(content)

# 追記モードでファイルを開く
with open('requirements.txt', 'a', encoding='utf-8') as file:
    # 追記する内容
    file.write('\n新しい内容を追記します。')