import streamlit as st
import sqlite3
from datetime import datetime

# Create a table to store chat messages
def create_chat_table(conn):
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS chat_data(username TEXT, message TEXT, timestamp TEXT)')
    conn.commit()

# Save a new chat message
def save_chat_message(conn, username, message, timestamp):
    c = conn.cursor()
    c.execute('INSERT INTO chat_data(username, message, timestamp) VALUES (?, ?, ?)', (username, message, timestamp))
    conn.commit()

# Retrieve all chat messages
def get_chat_messages(conn):
    c = conn.cursor()
    c.execute('SELECT username, message, timestamp FROM chat_data ORDER BY timestamp ASC')
    return c.fetchall()

# Display chat messages in Streamlit
def display_chat(conn):
    st.subheader("オープンチャット")
    
    # Retrieve and display all chat messages
    chat_data = get_chat_messages(conn)
    if chat_data:
        for username, message, timestamp in chat_data:
            st.write(f"[{timestamp}] {username}: {message}")
    else:
        st.write("まだメッセージがありません。")

    # Allow logged-in users to send new messages
    if 'username' in st.session_state:
        message_input = st.text_input("メッセージを入力してください", key="message_input")
        if st.button("送信"):
            if message_input:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                save_chat_message(conn, st.session_state['username'], message_input, timestamp)
                st.experimental_rerun()  # Refresh the app to display the new message
            else:
                st.warning("メッセージを入力してください。")
    else:
        st.warning("チャットに参加するにはログインしてください。")

def main():
    st.title("ログイン機能テスト")

    menu = ["ホーム", "ログイン", "サインアップ", "オープンチャット"]
    choice = st.sidebar.selectbox("メニュー", menu)

    # データベースに接続
    conn = sqlite3.connect('database.db')
    create_user_table(conn)
    create_chat_table(conn)  # Create the chat table

    if choice == "ホーム":
        st.subheader("ホーム画面です")
        if 'username' in st.session_state:
            username = st.session_state['username']
            st.write(f"ようこそ、{username}さん！")

            # (Existing features...)

        else:
            st.warning("ログインしていません。")

    elif choice == "ログイン":
        st.subheader("ログイン画面です")
        username = st.sidebar.text_input("ユーザー名を入力してください")
        password = st.sidebar.text_input("パスワードを入力してください", type='password')

        if st.sidebar.checkbox("ログイン"):
            result = login_user(conn, username, make_hashes(password))
            if result:
                st.session_state['username'] = username
                st.success(f"{username}さんでログインしました")
            else:
                st.warning("ユーザー名かパスワードが間違っています")

    elif choice == "サインアップ":
        st.subheader("新しいアカウントを作成します")
        new_user = st.text_input("ユーザー名を入力してください")
        new_password = st.text_input("パスワードを入力してください", type='password')

        if st.button("サインアップ"):
            if check_user_exists(conn, new_user):
                st.error("このユーザー名は既に使用されています。")
            else:
                try:
                    add_user(conn, new_user, make_hashes(new_password))
                    st.success("アカウントの作成に成功しました")
                    st.info("ログイン画面からログインしてください")
                except Exception as e:
                    st.error(f"アカウントの作成に失敗しました: {e}")

    elif choice == "オープンチャット":
        st.subheader("オープンチャット画面")
        display_chat(conn)  # Display the chat section

    # コネクションを閉じる
    conn.close()

if __name__ == '__main__':
    main()
