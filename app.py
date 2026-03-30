import asyncio
import aiohttp
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# API CONFIG
FRIEND_API = "https://pnl-frind-add-api.vercel.app/adding_friend"

async def send_req(session, uid, pwd, target):
    url = f"{FRIEND_API}?uid={uid}&password={pwd}&friend_uid={target}"
    try:
        async with session.get(url, timeout=12) as r:
            return r.status == 200
    except:
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/spam', methods=['POST'])
async def start_spam():
    target = request.json.get('target')
    
    if not os.path.exists("bulk.txt"):
        return jsonify({"error": "bulk.txt file not found!"}), 404
    
    with open("bulk.txt", "r") as f:
        accs = [l.strip() for l in f if "|" in l]

    if not accs:
        return jsonify({"error": "No accounts in bulk.txt"}), 400

    async with aiohttp.ClientSession() as session:
        tasks = [send_req(session, line.split("|")[0], line.split("|")[1], target) for line in accs]
        results = await asyncio.gather(*tasks)
    
    success = sum(1 for x in results if x)
    return jsonify({"success": success, "total": len(accs)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
