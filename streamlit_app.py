import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# パスワードをハッシュ化する関数
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ハッシュ化されたパスワードをチェックする関数
def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# テーブルを作成（存在しない場合）
def create_user_table(conn):
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS user_data(username TEXT PRIMARY KEY, text_content TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS study_data(username TEXT, date TEXT, study_hours REAL, score INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS class_data(username TEXT PRIMARY KEY, class_grade TEXT)')
    conn.commit()

# 新しいユーザーを追加する関数
def add_user(conn, username, password):
    c = conn.cursor()
    c.execute('INSERT INTO userstable(username, password) VALUES (?, ?)', (username, password))
    conn.commit()

# クラスデータを追加または更新する関数
def update_class_data(conn, username, class_grade):
    c = conn.cursor()
    c.execute('DELETE FROM class_data WHERE username = ?', (username,))
    c.execute('INSERT INTO class_data(username, class_grade) VALUES (?, ?)', (username, class_grade))
    conn.commit()

# ユーザー名の存在を確認する関数
def check_user_exists(conn, username):
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE username = ?', (username,))
    return c.fetchone() is not None

# ユーザーをログインさせる関数
def login_user(conn, username, password):
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE username = ? AND password = ?', (username, password))
    return c.fetchall()

# 学習データを保存する関数
def save_study_data(conn, username, date, study_hours, score):
    c = conn.cursor()
    c.execute('INSERT INTO study_data(username, date, study_hours, score) VALUES (?, ?, ?, ?)',
              (username, date, study_hours, score))
    conn.commit()

# ユーザーの学習データを取得する関数
def get_study_data(conn, username):
    c = conn.cursor()
    c.execute('SELECT date, study_hours, score FROM study_data WHERE username = ?', (username,))
    return c.fetchall()

# クラスデータを取得する関数
def get_class_data(conn, username):
    c = conn.cursor()
    c.execute('SELECT class_grade FROM class_data WHERE username = ?', (username,))
    data = c.fetchone()
    return data[0] if data else ""

# 指定したユーザーのデータを削除する関数
def delete_user_data(conn, username):
    c = conn.cursor()
    c.execute('DELETE FROM study_data WHERE username = ?', (username,))
    c.execute('DELETE FROM class_data WHERE username = ?', (username,))
    c.execute('DELETE FROM user_data WHERE username = ?', (username,))
    conn.commit()

# すべてのユーザーのデータを削除する関数
def delete_all_users(conn):
    c = conn.cursor()
    c.execute('DELETE FROM userstable')
    c.execute('DELETE FROM study_data')
    c.execute('DELETE FROM class_data')
    c.execute('DELETE FROM user_data')
    conn.commit()

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
    try:
        conn = sqlite3.connect('database.db')  # Establish connection to the SQLite database
        create_user_table(conn)  # Create user-related tables if they don't exist
        create_chat_table(conn)  # Create chat table if it doesn't exist
    except Exception as e:
        st.error(f"データベース接続エラー: {e}")
        return  # Exit if there's a database connection error

    if choice == "ホーム":
        st.subheader("ホーム画面です")
        if 'username' in st.session_state:
            username = st.session_state['username']
            st.write(f"ようこそ、{username}さん！")

            # クラスや学年の入力フォーム
            class_grade = get_class_data(conn, username)  # データベースからクラスを取得
            class_grade_input = st.sidebar.text_input("クラス/学年を入力してください", value=class_grade)

            if st.sidebar.button("クラス/学年を変更"):
                if class_grade_input:
                    update_class_data(conn, username, class_grade_input)
                    st.sidebar.success('クラス/学年が変更されました！')
                else:
                    st.sidebar.warning('クラス/学年を入力してください。')

            # 学習データ入力フォーム
            with st.form(key='study_form'):
                date = st.date_input('学習日', value=datetime.now())
                study_hours = st.number_input('学習時間（時間）', min_value=0.0, step=0.5)
                score = st.number_input('テストのスコア', min_value=0, max_value=100, step=1)
                submit_button = st.form_submit_button(label='データを保存')

            if submit_button:
                save_study_data(conn, username, date.strftime('%Y-%m-%d'), study_hours, score)
                st.success('データが保存されました！')

            study_data = get_study_data(conn, username)
            if study_data:
                df = pd.DataFrame(study_data, columns=['Date', 'Study Hours', 'Score'])
                st.write('### 現在の学習データ')
                st.dataframe(df)

                st.write('### グラフ表示')
                plot_type = st.selectbox('表示するグラフを選択してください', ['学習時間', 'スコア'])

                fig, ax = plt.subplots()
                if plot_type == '学習時間':
                    ax.plot(df['Date'], df['Study Hours'], marker='o')
                    ax.set_title('日別学習時間の推移')
                    ax.set_xlabel('日付')
                    ax.set_ylabel('学習時間（時間）')
                elif plot_type == 'スコア':
                    ax.plot(df['Date'], df['Score'], marker='o', color='orange')
                    ax.set_title('日別スコアの推移')
                    ax.set_xlabel('日付')
                    ax.set_ylabel('スコア')
                st.pyplot(fig)

            else:
                st.write('データがまだ入力されていません。')

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

                if username == "さとうはお":
                    st.success("こんにちは、佐藤葉緒さん！")
                    if st.button("すべてのユーザーのデータを削除"):
                        delete_all_users(conn)
                        st.success("すべてのユーザーのデータが削除されました。")
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

    conn.close()

if __name__ == '__main__':
    main()
