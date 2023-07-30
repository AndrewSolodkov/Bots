import sqlite3


class DBlya:
    def __init__(self):
        self.con = sqlite3.connect("db.sqlite3")
        self.cur = self.con.cursor()
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS logins (
            id INTEGER CONSTRAINT logins_pk PRIMARY KEY,
            "email" TEXT,
            password TEXT
        );"""
        )

        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS user_logins(
            id TEXT,
            login_id int CONSTRAINT login_fk REFERENCES logins(id)
        )
        """
        )

        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS need_extension(
                id integer PRIMARY KEY,
                login_id integer NOT NULL,
                extensioned integer DEFAULT 0
            );
         """
        )

        self.con.commit()

    def get_free_login(self, telegram_id: str) -> (str, str):
        self.cur = self.con.cursor()
        res = self.cur.execute(
            """
        SELECT logins.id, logins.email, logins.password 
        FROM logins 
        LEFT JOIN user_logins ul ON ul.login_id = logins.id 
        WHERE ul.id is NULL"""
        )

        row = res.fetchone()
        if row is None:
            return "Нет", "свободных"

        login: str = ""
        password: str = ""
        login_id: int = 0

        try:
            login = row[1]
            password = row[2]
            login_id = row[0]
        except IndexError:
            pass

        self.cur.execute(
            f"""
            INSERT INTO user_logins (id, login_id) VALUES (?,?)
        """,
            (telegram_id, login_id),
        )

        self.con.commit()
        return login, password

    def add_login(self, login: str, password: str, telegram_id: str):
        prev_row = self.cur.lastrowid
        self.cur = self.con.cursor()
        self.cur.execute(
            """
            INSERT INTO need_extension (login_id) SELECT id FROM logins WHERE email = ? and password = ? 
        """,
            (login, password),
        )
        self.con.commit()
        next_row = self.cur.lastrowid
        print(f"next {next_row} prev {prev_row}")

    def get_credentials(self, telegram_id: str) -> (str, str):
        self.cur = self.con.cursor()
        res = self.cur.execute(
            """
            SELECT email, password 
            FROM logins
            JOIN user_logins on logins.id = user_logins.login_id
            WHERE user_logins = ?""",
            (telegram_id,),
        )
        row = res.fetchone()
        login = ""
        password = ""

        try:
            login = row[0]
            password = row[1]
        except IndexError:
            pass

        return login, password
