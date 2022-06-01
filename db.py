import sqlite3


def init_db():
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    # Если таблицы не существует создать ее
    cursor.execute("""CREATE TABLE IF NOT EXISTS 'users'(id TEXT UNIQUE, tz TEXT)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS 'tasklist'
                                  (id text, number text, time text, text text, uid text)
                               """)
    conn.commit()


def user_time(chatid):
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    user = cursor.execute(f"""SELECT tz FROM 'users' WHERE id={chatid}""")
    row = cursor.fetchone()
    if row[0] is None:
        return 'none'
    return row[0]

def add_user(chatid,timezone):
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    info = cursor.execute('SELECT * FROM users WHERE id=?', (chatid, ))
    if info.fetchone() is None: #Создаем пользователя если нету
        ins = f"""INSERT INTO 'users'  VALUES ('{chatid}', '{timezone}')"""
        cursor.execute(ins)
    conn.commit()


def change_tz(id, tz):
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    cursor.execute(f"""INSERT OR IGNORE INTO users(id) VALUES({id});""")
    cursor.execute(f"""UPDATE users SET tz = '{tz}' WHERE id = '{id}';""")
    conn.commit()


def get_user_tz(chatid):
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    cursor.execute(f"""SELECT tz FROM 'users' WHERE id={chatid}""")
    row = cursor.fetchone()
    if row[0] is None:
        return 'none'
    return row[0]


def add_to_db_tasklist(chatid, number, time, text):  # Функция добавляет данные в таблицу 'tasklist'
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    cursor.execute(f'SELECT COUNT(*) as number FROM tasklist WHERE id= {chatid}').rowcount
    count = cursor.fetchall()
    uid = int(count[0][0]) + 1
    ins = f"""INSERT INTO 'tasklist'  VALUES ('{chatid}', '{number}', '{time}', '{text}', '{uid}')"""
    cursor.execute(ins)
    conn.commit()


def read_data_in_task(chatid):  # Чтение данных из таблицы 'tasklist'
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    c = cursor.execute(f"""SELECT number,time,text FROM 'tasklist' WHERE id={chatid}""")
    result = '*Номер задачи | Время | Задача* \n' + '\n'.join(['| '.join(map(str, x)) for x in c])
    return result

def show_tasks(chatid):
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    c = cursor.execute(f"""SELECT uid,time,text FROM 'tasklist' WHERE id={chatid}""")
    result = '*Номер задачи | Время | Задача* \n' + '\n'.join(['| '.join(map(str, x)) for x in c])
    return result

def all_task():
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    arr = cursor.execute(f"""SELECT * FROM 'tasklist' WHERE time != '0'""")
    result = arr.fetchall()
    return result

def delete_task(uid):  # Удаление данных из таблицы 'tasklist'
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    try:
        delete = f"""DELETE FROM 'tasklist' WHERE uid = '{uid}' """
        cursor.execute(delete)
        conn.commit()
    except:
        conn.commit()
