import psycopg2

def create_user_db():
    with psycopg2.connect(database="userinfo_db", user="postgres", password="lala") as conn:
        with conn.cursor() as cur:
            # cur.execute("""
            # DROP TABLE User;
            # DROP TABLE UserPhone;
            # """)
            cur.execute("""
                   CREATE TABLE IF NOT EXISTS User(
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
                        user_id INTEGER REFERENCES User(id)
                   );
                   """)
            conn.commit()
    conn.close()

def get_user_id(cursor, email):
    cursor.execute("""
    SELECT id 
    FROM User
    WHERE email = %s;
    """, (email, ))
    return cursor.fetchone()[0]

def get_user_phone_ids(cursor, user_id):
    cursor.execute("""
    SELECT id 
    FROM UserPhone
    WHERE user_id = %s;
    """, (user_id, ))
    return cursor.fetchall()

def add_new_user(name, surname, email, phone = ''):
    with psycopg2.connect(database="userinfo_db", user="postgres", password="lala") as conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO User(name, surname, email) VALUES(%s, %s, %s);
            """, (name, surname, email))
            conn.commit()

            user_id = get_user_id(cur, email)

            cur.execute("""
            INSERT INTO UserPhone(phone, user_id) VALUES(%s, %s, %s);
            """, (user_id, phone))
            conn.commit()

    conn.close()

def change_user_info(email, user_dict):
    with psycopg2.connect(database="userinfo_db", user="postgres", password="lala") as conn:
        with conn.cursor() as cur:
            user_id = get_user_id(cur, email)
            for col, value in user_dict.items():
                if col == 'phone':
                    user_phone_ids = get_user_phone_ids(cur, user_id)
                    cur.execute("""
                    UPDATE UserPhone 
                    SET %s = %s
                    WHERE id = %s ;
                    """, (col, value, user_phone_ids[0][0]))
                    conn.commit()
                elif value != '':
                    cur.execute("""
                    UPDATE User 
                    SET %s = %s
                    WHERE id = %s ;
                    """, (col, value, user_id))
                    conn.commit()

    conn.close()

def delete_user_phone(email):
    with psycopg2.connect(database="userinfo_db", user="postgres", password="lala") as conn:
        with conn.cursor() as cur:
            user_id = get_user_id(cur, email)
            user_phone_ids = get_user_phone_ids(cur, user_id)
            for user_phone_id in user_phone_ids:
                cur.execute("""
                DELETE FROM UserPhone 
                WHERE id = %s;
                """, (user_phone_id[0], ))
            conn.commit()
    conn.close()

def delete_user(email):
    delete_user_phone(email)

    with psycopg2.connect(database="userinfo_db", user="postgres", password="lala") as conn:
        with conn.cursor() as cur:
            user_id = get_user_id(cur, email)
            cur.execute("""
                DELETE FROM User
                WHERE id = %s;
                """, (user_id[0], ))
            conn.commit()
    conn.close()

def user_from_email_or_phone(name, surname, email, phone=None):
        with psycopg2.connect(database="userinfo_db", user="postgres", password="lala") as conn:
            with conn.cursor() as cur:
                if phone != None:
                    cur.execute("""
                    SELECT user_id 
                    FROM UserPhone
                    WHERE phone = %s;
                    """, (phone,))
                else:
                    cur.execute("""
                    SELECT id 
                    FROM User
                    WHERE name = %s, surname = %s, email = %s;
                    """, (name, surname, email))

                print(f"Found user with Id = {cur.fetchone()[0]}")
                return cur.fetchone()[0]
        conn.close()

if __name__ == '__main__':
    create_user_db()

