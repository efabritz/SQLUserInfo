import psycopg2


class DBObject:
    def __init__(self, database, user, password):
        self.database = database
        self.user = user
        self.password = password

    def create_user_db(self):
        with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                 DROP TABLE UserPhone;
                 DROP TABLE UserClient;
                 """)

                cur.execute("""
                 CREATE TABLE IF NOT EXISTS UserClient(
                 id SERIAL PRIMARY KEY,
                 name VARCHAR(60) NOT NULL,
                 surname VARCHAR(60) NOT NULL,
                 email VARCHAR(60) UNIQUE NOT NULL
                 );
                 """)

                cur.execute("""
                CREATE TABLE IF NOT EXISTS UserPhone(
                id SERIAL PRIMARY KEY,
                phone VARCHAR(20),
                user_id INTEGER REFERENCES UserClient(id)
                );
                """)
                conn.commit()
        conn.close()

    def find_user(self, dict):
        with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
            with conn.cursor() as cur:
                if len(dict) == 1:
                    col = list(dict.items())[0][0]
                    value = list(dict.items())[0][1]
                    if col == 'name':
                        cur.execute("""
                        SELECT * FROM UserClient
                        WHERE name = %s;
                        """, (value,))
                        print(cur.fetchall())
                    elif col == 'surname':
                        cur.execute("""
                        SELECT * 
                        FROM UserClient
                        WHERE surname = %s;
                        """, (value, ))
                        print(cur.fetchall())
                    elif col == 'email':
                        cur.execute("""
                        SELECT * 
                        FROM UserClient
                        WHERE email = %s;
                        """, (value, ))
                        print(cur.fetchall())
                    elif col == 'phone':
                        cur.execute("""
                        SELECT user_id 
                        FROM UserPhone
                        WHERE phone = %s;
                        """, (value, ))
                        user_id = cur.fetchone()
                        if user_id:
                            cur.execute("""
                            SELECT * 
                            FROM UserClient
                            WHERE id = %s;
                            """, (user_id, ))
                            print(cur.fetchone())
                        else:
                            print('Error. User not found')
        conn.close()


class User:
    phones = []

    def __init__(self, name, surname, email):
        self.name = name
        self.surname = surname
        self.email = email


class UserInfo:
    def __init__(self, user: User, dbconn: DBObject):
        self.user = user
        self.dbconn = dbconn

    def get_user_id(self, cursor):
        cursor.execute("""
        SELECT id 
        FROM UserClient
        WHERE email = %s;
        """, (self.user.email,))
        return cursor.fetchone()[0]

    def get_user_phone_ids(self, cursor, user_id):
        cursor.execute("""
        SELECT id 
        FROM UserPhone
        WHERE user_id = %s;
        """, (user_id,))
        return cursor.fetchall()

    def add_new_user(self):
        with psycopg2.connect(database=self.dbconn.database, user=self.dbconn.user, password=self.dbconn.password) as conn:
            with conn.cursor() as cur:
                print('in cur')
                cur.execute("""
                INSERT INTO UserClient(name, surname, email) VALUES(%s, %s, %s);
                """, (self.user.name, self.user.surname, self.user.email))
                conn.commit()

                if self.user.phones:
                    print('in phones')
                    for phone in self.user.phones:
                        user_id = self.get_user_id(cur)
                        cur.execute("""
                        INSERT INTO UserPhone(phone, user_id) VALUES(%s, %s);
                        """, (phone, user_id))
                    conn.commit()
        conn.close()

    def change_user_info(self, user_dict):
        with psycopg2.connect(database=self.dbconn.database, user=self.dbconn.user, password=self.dbconn.password) as conn:
            with conn.cursor() as cur:
                user_id = self.get_user_id(cur)
                print(f'user id: {user_id}')
                for col, value in user_dict.items():
                    if col == 'phone' and value:
                        user_phone_ids = self.get_user_phone_ids(cur, user_id)
                        if not user_phone_ids:
                            print('User phone is added: ')
                            cur.execute("""
                            INSERT INTO UserPhone(phone, user_id) VALUES(%s, %s);
                            """, (value, user_id))
                            conn.commit()
                        else:
                            print(f'phone ids: {user_phone_ids}')
                            cur.execute("""
                            UPDATE UserPhone 
                            SET phone = %s
                            WHERE id = %s ;
                            """, (value, user_phone_ids[0][0]))
                    elif value:
                        if col == 'name':
                            cur.execute("""
                            UPDATE UserClient 
                            SET name = %s
                            WHERE id = %s ;
                            """, (value, user_id))
                        elif col == 'surname':
                            cur.execute("""
                            UPDATE UserClient 
                            SET surname = %s
                            WHERE id = %s ;
                            """, (value, user_id))
                        elif col == 'email':
                            cur.execute("""
                            UPDATE UserClient 
                            SET email = %s
                            WHERE id = %s ;
                            """, (value, user_id))
                conn.commit()
        conn.close()

    def delete_user_phone(self):
        with psycopg2.connect(database=self.dbconn.database, user=self.dbconn.user, password=self.dbconn.password) as conn:
            with conn.cursor() as cur:
                user_id = self.get_user_id(cur)
                user_phone_ids = self.get_user_phone_ids(cur, user_id)
                print(f'user id: {user_id}, phone ids: {user_phone_ids}')
                for user_phone_id in user_phone_ids:
                    cur.execute("""
                    DELETE FROM UserPhone 
                    WHERE id = %s;
                    """, (user_phone_id[0],))
                conn.commit()
        conn.close()

    def delete_user(self):
        self.delete_user_phone()
        with psycopg2.connect(database=self.dbconn.database, user=self.dbconn.user, password=self.dbconn.password) as conn:
            with conn.cursor() as cur:
                user_id = self.get_user_id(cur)
                cur.execute("""
                    DELETE FROM UserClient
                    WHERE id = %s;
                    """, (user_id,))
                conn.commit()
        conn.close()


if __name__ == '__main__':
    db_obj = DBObject('userinfo_db', 'postgres', 'lala')
   # db_obj.create_user_db()

    user1 = User('Alice', 'Aliceson', 'alice@gmail.com')
    user1.phones = ['12345', '123', '123456']
    user2 = User('Bob', 'Bobson', 'bob@gmail.com')
    user2.phones = ['987']
    user3 = User('Tom', 'Tomson', 'tom@tmob.com')

    userinf1 = UserInfo(user1, db_obj)
    userinf2 = UserInfo(user2, db_obj)
    userinf3 = UserInfo(user3, db_obj)

    #userinf1.add_new_user()
    #userinf2.add_new_user()
    #userinf3.add_new_user()

    dict1 = {"name": 'frr', "surname": 'brr', "email": 'em1ail@df.df', "phone": '01123'}
    dict2 = {"phone": '01123'}

    #userinf2.change_user_info(dict1)
    #userinf3.change_user_info(dict2)
    #dict3 = {"phone": '0001123'}
    #userinf3.change_user_info(dict3)

    #userinf1.delete_user_phone()
    #userinf3.delete_user()

    # поиск c помощью словаря с 1м элементом
    search_dict1 = {'name': 'Alice'}
    search_dict2 = {'email': 'alice@gmail.com'}
    search_dict3 = dict2

    user4 = User('Tom', 'brr', 'tom@tmob.com')
    userinf4 = UserInfo(user4, db_obj)
    #userinf4.add_new_user()

    search_dict4 = {'surname': 'brr'}

    db_obj.find_user(search_dict1)
    db_obj.find_user(search_dict2)
    db_obj.find_user(search_dict3)
    db_obj.find_user(search_dict4)








