import asyncio
import aiohttp
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # ब्राउजर ब्लकिङ समस्या हटाउन

# API लिङ्क
FRIEND_API = "https://pnl-frind-add-api.vercel.app/adding_friend"

async def send_req(session, uid, pwd, target):
    url = f"{FRIEND_API}?uid={uid}&password={pwd}&friend_uid={target}"
    try:
        async with session.get(url, timeout=15) as r:
            return r.status == 200
    except:
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/spam', methods=['POST'])
async def start_spam():
    try:
        data = request.get_json()
        target = data.get('target')
        
        if not os.path.exists("bulk.txt"):
            return jsonify({"error": "bulk.txt file missing!"}), 404
        
        with open("bulk.txt", "r") as f:
            accs = [l.strip() for l in f if "|" in l]

        if not accs:
            return jsonify({"error": "bulk.txt is empty!"}), 400

        success = 0
        async with aiohttp.ClientSession() as session:
            # १०-१० वटाको ब्याचमा पठाउने ताकि Render ले नकाटोस्
            batch_size = 10 
            for i in range(0, len(accs), batch_size):
                batch = accs[i:i+batch_size]
                tasks = []
                for line in batch:
                    u, p = line.split("|")
                    tasks.append(send_req(session, u, p, target))
                results = await asyncio.gather(*tasks)
                success += sum(1 for x in results if x)
                await asyncio.sleep(0.1) # सानो ग्याप
        
        return jsonify({"success": success, "total": len(accs)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Render को पोर्ट १०००० हुन्छ
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
