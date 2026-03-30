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
        # Timeout लाई बढाएर १५ सेकेन्ड बनाइएको छ
        async with session.get(url, timeout=15) as r:
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

    success = 0
    total = len(accs)

    # Render Timeout बाट बच्न धेरै Requests लाई सानो ब्याचमा बाडिएको छ
    async with aiohttp.ClientSession() as session:
        batch_size = 20 # एक पटकमा २० वटा मात्र पठाउने
        for i in range(0, total, batch_size):
            batch = accs[i:i+batch_size]
            tasks = []
            for line in batch:
                try:
                    u, p = line.split("|")
                    tasks.append(send_req(session, u, p, target))
                except: continue
            
            results = await asyncio.gather(*tasks)
            success += sum(1 for x in results if x)
            # सर्भरलाई थोरै सास फेर्न समय दिने (0.1s gap)
            await asyncio.sleep(0.1)

    return jsonify({"success": success, "total": total})

if __name__ == "__main__":
    # Render को लागि Port ५००० मा रन गर्ने
    app.run(host="0.0.0.0", port=5000)
