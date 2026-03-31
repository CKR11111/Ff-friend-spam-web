import asyncio
import aiohttp
import os
import threading
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# API CONFIG
FRIEND_API = "https://pnl-frind-add-api.vercel.app/adding_friend"

def run_spam_in_background(accs, target):
    async def process():
        connector = aiohttp.TCPConnector(limit=10) # एकपटकमा १० कनेक्सन मात्र
        async with aiohttp.ClientSession(connector=connector) as session:
            for i in range(0, len(accs), 5):
                batch = accs[i:i+5]
                tasks = []
                for line in batch:
                    try:
                        u, p = line.split("|")
                        url = f"{FRIEND_API}?uid={u}&password={p}&friend_uid={target}"
                        tasks.append(session.get(url, timeout=15))
                    except: continue
                await asyncio.gather(*tasks, return_exceptions=True)
                await asyncio.sleep(0.3) # सर्भर जोगाउन सानो ग्याप
    
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
            return jsonify({"error": "bulk.txt missing"}), 404
        
        with open("bulk.txt", "r") as f:
            accs = [l.strip() for l in f if "|" in l]

        if not accs:
            return jsonify({"error": "bulk.txt empty"}), 400

        # थ्रेड सुरु गर्ने (यसले तत्काल रेस्पोन्स दिन्छ र एरर आउँदैन)
        thread = threading.Thread(target=run_spam_in_background, args=(accs, target))
        thread.start()

        return jsonify({"status": "success", "total": len(accs)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
