import sqlite3
con=sqlite3.connect("db.db")
cur=con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,username TEXT, role TEXT DEFAULT 'citizen',mafia_vote INTEGER DEFAULT 0,
    citizen_vote INTEGER DEFAULT 0,
    voted INTEGER DEFAULT 0,
    dead INTEGER DEFAULT 0)"""
)

def insert_player(player_id, username):
    con=sqlite3.connect("db.db")
    cur=con.cursor()
    
    sql=f"INSERT INTO players (player_id, username) VALUES ('{player_id}', '{username}') ON CONFLICT(player_id) DO NOTHING"
    cur.execute(sql)
    
    con.commit()
    con.close()
    
def get_all_players():
    con=sqlite3.connect("db.db")
    cur=con.cursor()
    
def vote(type, username, player_id):
    con=sqlite3.connect("db.db")
    cur=con.cursor()
        
    cur.execute("SELECT username FROM players WHERE player_id = ? AND dead=0 AND voted=0",(player_id,))
    voter=cur.fetchone()
    
    if not voter:
        con.close()
        return False
    
    try:
        cur.execute(f"UPDATE players SET {type} = {type} + 1 WHERE username =?",(username,))
        
        cur.execute("UPDATE players SET voted = 1 WHERE player_id=?",(player_id,))
        
        con.commit()
        con.close()
        return True
    except sqlite3.Error:
        con.close()
        return False
    
def mafia_kill():
    con=sqlite3.connect("db.db")
    cur=con.cursor()
    
    cur.execute("SELECT MAX(mafia_vote) FROM players")
    res_max=cur.fetchone()
    max_votes=res_max[0] if res_max else 0
    
    cur.execute("SELECT COUNT(*) FROM players WHERE dead=0 AND role='mafia'")
    res_alive=cur.fetchone()
    mafia_alive=res_alive[0] if res_alive else 0
    
    username_killed='никого'
    
    if max_votes == mafia_alive and max_votes > 0:
        cur.execute("SELECT username FROM players WHERE mafia_vote= ?",(max_votes,))
        res_user=cur.fetchone()
        if res_user:
            username_killed=res_user[0]
            cur.execute("UPDATE players SET dead=1 WHERE username=?",(username_killed,))
            con.commit()
            
    con.close()
    return username_killed

def citizen_kill():
    con =sqlite3.connect("db.db")
    cur=con.cursor()
    
    cur.execute("SELECT MAX(citizen_vote) FROM players")
    res_max=cur.fetchone()
    max_votes=res_max[0] if res_max else 0
    
    username_killed='никого'
    
    if max_votes>0:
        cur.execute("SELECT COUNT(*) FROM players WHERE citizen_vote=?",(max_votes,))
        res_count=cur.fetchone()
        max_votes_count=res_count[0] if res_count else 0
        
        if max_votes_count == 1:
            cur.execute("SELECT username FROM players WHERE citizen_vote=?",(max_votes,))
            res_user=cur.fetchone()
            if res_user:
                username_killed=res_user[0]
                cur.execute("UPDATE players SET dead=1 WHERE username=?",(username_killed,))
                con.commit()
    
    con.close()
    return username_killed

def reset_votes():
    con=sqlite3.connect("db.db")
    cur=con.cursor()
    cur.execute("UPDATE players SET mafia_vote=0,citizen_vote=0,voted=0")
    con.commit()
    con.close()
                
    
    sql="SELECT * FROM players"
    cur.execute(sql)
    
    data=cur.fetchall()
    con.close()
    return data

def get_all_player_ids():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    
    sql="SELECT player_id FROM players"
    cur.execute(sql)
    
    data=cur.fetchall()
    con.close()
    return data

def get_player_ids_and_roles():
    con=sqlite3.connect("db.db")
    cur=con.cursor()
    
    sql="SELECT player_id, role FROM players"
    cur.execute(sql)
    
    data=cur.fetchall()
    con.close()
    return data

def get_mafia_usernames():
    con=sqlite3.connect("db.db")
    cur=con.cursor()
    
    sql="SELECT username FROM players WHERE role = 'mafia'"
    cur.execute(sql)
    
    data=cur.fetchall()
    con.close()
    return data

def players_amount():
    con=sqlite3.connect("db.db")
    cur=con.cursor()
    
    sql="SELECT * FROM players"
    cur.execute(sql)
        
    res=cur.fetchall()
    con.close()
    return len(res)

from random import shuffle
def set_roles(players_count):
    mafia_count=int(players_count * 0.3)
    if mafia_count == 0:
        mafia_count = 1
        
    game_roles = ["mafia"] * mafia_count
    game_roles.append("sheriff")
    
    while len(game_roles) < players_count:
        game_roles.append("citizen")
        
    shuffle(game_roles)
    
    con=sqlite3.connect("db.db")
    cur=con.cursor()
    cur.execute("SELECT player_id FROM players")
    player_ids=[row[0] for row in cur.fetchall()]
    
    for role,player_id in zip(game_roles, player_ids):
        sql=f"UPDATE players SET role='{role}' WHERE player_id= {player_id}"
        cur.execute(sql)
        
    con.commit()
    con.close()
    
def check_winner():
    con=sqlite3.connect("db.db")
    cur=con.cursor()
    
    cur.execute("SELECT COUNT(*) FROM players WHERE role='mafia' AND (dead=0)")
    mafia_alive=cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM players WHERE role != 'mafia' AND (dead=0)")
    citizen_alive=cur.fetchone()[0]
    
    con.close()
    
    if mafia_alive == 0:
        return 'Горожане'
    elif mafia_alive >= citizen_alive:
        return 'Мафия'
    return None

def clear(dead=False):
    con=sqlite3.connect("db.db")
    cur=con.cursor()
    
    sql=f"UPDATE players SET citizen_vote=0,mafia_vote=0,voted='0'"
    if dead:
        sql +=", dead = 0"
    
    cur.execute(sql)
    con.commit()
    con.close()
    
def get_all_alive():
    con=sqlite3.connect("db.db")
    cur=con.cursor()
    sql="SELECT username FROM players WHERE dead=0"
    cur.execute(sql)
    data=[row[0] for row in cur.fetchall()]
    con.close()
    return data
