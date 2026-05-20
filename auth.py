import bcrypt
from db import get_connection


def hash_pw(p):
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()


def verify_pw(p, h):
    return bcrypt.checkpw(p.encode(), h.encode())


def signup(name, meter_id, phone, email, password, pin):
    conn = get_connection(); cur = conn.cursor()
    cur.execute('INSERT INTO users(full_name,meter_id,phone,email,password_hash,pin) VALUES(%s,%s,%s,%s,%s,%s)',
                (name,meter_id,phone,email,hash_pw(password),pin))
    conn.commit(); conn.close()


def login(user, password):
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM users WHERE email=%s OR meter_id=%s', (user,user))
    row = cur.fetchone(); conn.close()
    if row and verify_pw(password, row['password_hash']):
        return row
    return None


def reset_pin(meter_id, new_pin):
    conn=get_connection(); cur=conn.cursor()
    cur.execute('UPDATE users SET pin=%s WHERE meter_id=%s',(new_pin,meter_id))
    conn.commit(); conn.close()