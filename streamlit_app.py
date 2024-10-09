import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# MySQL接続関数
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",  # MySQLサーバーのホスト名
            user="your_username",  # MySQLのユーザー名
            password="your_password",  # MySQLのパスワード
            database="chat_db"  # データベース名
        )
    except Error as e:
        st.error(f"Error: '{e}'")
    return connection

# メッセージをデータベースに保存
def save_message(username, message):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        query = "INSERT INTO messages (username, message) VALUES (%s, %s)"
        cursor.execute(query, (username, message))
        connection.commit()
        cursor.close()
        connection.close()

# チャット履歴を取得
def load_messages():
    connection = create_connection()
    messages = []
    if connection:
        cursor = connection.cursor()
        query = "SELECT username, message, timestamp FROM messages ORDER BY timestamp DESC"
        cursor.execute(query)
        messages = cursor.fetchall()
        cursor.close()
        connection.close()
    return messages

# Streamlitでのチャットインターフェース
st.title("💬 Open Chat")

# ユーザー名とメッセージ入力
username = st.text_input("Enter your username", key="username")
message = st.text_area("Type your message", key="message")

# 送信ボタン
if st.button("Send"):
    if username and message:
        save_message(username, message)
        st.success("Message sent!")
    else:
        st.error("Username and message cannot be empty")

# チャット履歴表示
st.header("Chat History")
messages = load_messages()
if messages:
    for user, msg, timestamp in messages:
        st.write(f"**{user}** [{timestamp}]: {msg}")
else:
    st.write("No messages yet. Start the conversation!")
