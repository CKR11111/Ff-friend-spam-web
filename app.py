import asyncio
import aiohttp
import os
import threading
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# API CONFIG
FRIEND_API = "https://free-fire-add-friend-api-and-other.onrender.com/add_friend"

def run_spam_in_background(accs, target):
    async def process():
        connector = aiohttp.TCPConnector(limit=100, ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            # ५०-५० वटा रिक्वेस्टको ब्याच बनाएर एकैपटक प्रहार गर्ने
            for i in range(0, len(accs), 50):
                batch = accs[i:i+50]
                tasks = []
                for line in batch:
                    try:
                        u, p = line.split("|")
                        url = f"{FRIEND_API}?player_id={target}&uid={u}&password={p}"
                        tasks.append(session.get(url, timeout=10))
                    except: continue
                await asyncio.gather(*tasks, return_exceptions=True)
                await asyncio.sleep(0.01)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process())

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/spam', methods=['POST'])
def start_spam():
    try:
        data = request.get_json()
        target = data.get('target')
        if not os.path.exists("bulk.txt"):
            return jsonify({"error": "bulk.txt file missing"}), 404
        with open("bulk.txt", "r") as f:
            accs = [l.strip() for l in f if "|" in l and l.strip()]
        if not accs:
            return jsonify({"error": "No accounts found"}), 400

        threading.Thread(target=run_spam_in_background, args=(accs, target)).start()
        return jsonify({"status": "success", "total": len(accs)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
