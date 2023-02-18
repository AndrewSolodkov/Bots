import sqlite3


class DBlya:
    def __init__(self):
        self.con = sqlite3.connect("db.sqlite3")
        self.cur = self.con.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS logins (
            id serial CONSTRAINT logins_pk PRIMARY KEY,
            "email" TEXT,
            password TEXT
        );

        CREATE TABLE IF NOT EXISTS user_logins(
            id TEXT,
            login_id int CONSTRAINT login_fk REFERENCES logins(id)
        )
        ''')
        self.con.commit()

    def get_free_login(self, telegram_id: str) -> (str, str):
        self.cur = self.con.cursor()
        res = self.cur.execute('''
        SELECT id, login, password 
        FROM logins 
        LEFT JOIN user_logins ul ON ul.id is null''')

        row = res.fetchone()

        login: str = ""
        password: str = ""
        login_id: int = 0

        try:
            login = row[1]
            password = row[2]
        except IndexError:
            pass

        self.cur.execute(f'''
            INSERT INTO user_logins (id, login_id) VALUES (?,?)
        ''', (telegram_id, login_id))

        self.con.commit()
        return login, password

    def add_login(self, login: str, password: str, telegram_id: str):
        self.cur = self.con.cursor()
        self.cur.execute('''
            INSERT INTO logins (email, password) VALUES (?, ?) 
        ''', (login, password))

        lid = self.cur.lastrowid

        self.cur.execute('''
        INSERT INTO user_logins (id, login_id) VALUES (?,?)
        ''', (telegram_id, lid))
