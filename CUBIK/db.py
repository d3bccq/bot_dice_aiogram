#Это файл для работы с бд
import sqlite3 as sq

db = sq.connect('db/database.db', check_same_thread=False)
cur = db.cursor()

#Создание таблицы
cur.execute("CREATE TABLE IF NOT EXISTS winka(user_id INTEGER UNIQUE PRIMARY KEY NOT NULL, username TEXT, losse INTEGER, win INTEGER)")
db.commit()

#Добавление в таблицу
def db_table_val(user_id: int, username: str, losse: int, win: int):
        cur.execute('REPLACE INTO winka (user_id, username, losse, win) VALUES (?, ?, ?, ?)', (user_id, username, losse, win))
        db.commit()