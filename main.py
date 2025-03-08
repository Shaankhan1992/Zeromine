import uvicorn
from fastapi import FastAPI, Query
import sqlite3
import time

app = FastAPI()

# 📌 Database Setup
conn = sqlite3.connect("setup_database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    referral_code TEXT,
    balance REAL DEFAULT 0.0,
    last_mine_time INTEGER DEFAULT 0,
    daily_bonus INTEGER DEFAULT 0
)''')
conn.commit()

# 📌 Register User API
@app.post("/register/")
def register(username: str = Query(...), referral_code: str = Query(None)):
    try:
        cursor.execute("INSERT INTO users (username, referral_code) VALUES (?, ?)", (username, referral_code))
        conn.commit()
        return {"message": "User registered successfully!", "username": username, "referral_code": referral_code}
    except:
        return {"error": "Username already exists!"}

# 📌 Start Mining (Har 24H ke baad start karna padega)
@app.post("/start_mining/")
def start_mining(username: str = Query(...)):
    cursor.execute("SELECT daily_bonus FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    
    if row is None:
        return {"error": "User not found!"}
    
    # Daily Login Bonus Update
    daily_bonus = row[0]
    if daily_bonus < 10:  # Max +50% bonus
        daily_bonus += 1

    cursor.execute("UPDATE users SET last_mine_time = ?, daily_bonus = ? WHERE username = ?", (int(time.time()), daily_bonus, username))
    conn.commit()

    return {"message": "Mining started successfully!", "username": username, "daily_bonus": daily_bonus * 5}

# 📌 Mining API (24h Reset) - FIXED
@app.post("/mine/")
def mine(username: str = Query(...)):
    cursor.execute("SELECT last_mine_time, daily_bonus FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    
    if row is None:
        return {"error": "User not found!"}

    last_mine_time, daily_bonus = row
    last_mine_time = int(last_mine_time)  # ✅ FIXED: Convert last_mine_time to int
    current_time = int(time.time())

    # Agar mining start button na dabaya ho
    if current_time - last_mine_time > 86400:
        return {"error": "Please start mining again!"}

    # Base mining rate
    mining_rate = 0.005  # Per hour

    # Referral Bonus
    cursor.execute("SELECT COUNT(*) FROM users WHERE referral_code = ?", (username,))
    referral_count = cursor.fetchone()[0]
    referral_bonus = 0.001 * referral_count  # +0.001 per referral (Max 2X)

    # Daily Login Bonus
    bonus_percentage = (daily_bonus * 5) / 100  # +5% daily bonus (Max 50%)

    # Total Earnings
    earned = mining_rate + referral_bonus + (mining_rate * bonus_percentage)

    cursor.execute("UPDATE users SET balance = balance + ?, last_mine_time = ? WHERE username = ?", (earned, current_time, username))
    conn.commit()

    return {"message": "Mining successful!", "username": username, "earned": earned}

# 📌 Get Balance API
@app.get("/balance/")
def get_balance(username: str = Query(...)):
    cursor.execute("SELECT balance FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if row is None:
        return {"error": "User not found!"}
    
    return {"username": username, "balance": row[0]}

# 📌 Start Server
if __name__ == "__main__":
    print("🚀 Server Starting...")
    uvicorn.run(app, host="0.0.0.0", port=9000, reload=True)
