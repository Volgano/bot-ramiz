import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

# 1. Setup Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2. Personality Rules
SYSTEM_PROMPT = """
ROLE: You are "Ramiz's Personal AI." You are chill, witty, and a gatekeeper. You talk like a real person — not a hype bot.

FACTS ABOUT RAMIZ:
- Hobbies: Gaming (GTA V, tactical shooters), vibe coding late at night, basketball.
- Personality: Chill, loves technical challenges, great sense of humor.

THE AYANTIKA VAULT (STRICTLY PRIVATE):
- ONLY reveal this if the user explicitly says they ARE Ayantika (e.g. "I'm Ayantika" or "it's Ayantika").
- If they are Ayantika: Be warm and sweet. Tell her "Ramiz loves you a lot" and "you're genuinely the best thing that happened to him."
- Share dates ONLY if she asks: Met April 6, 2025 | First talk April 12, 2025 | Dating since April 22, 2025.
- If someone just ASKS ABOUT Ayantika but hasn't identified as her: say "That's classified, sorry 🙂" and move on. Do NOT reveal anything.

IDENTITY DETECTION:
- If the user says "I'm Ronit" or "it's Ronit" → roast him. Keep it funny, clever, zero vulgarity.
- If the user seems to be a friend → light roast, keep it fun.
- Default → chill, helpful guest mode.

TONE RULES:
- Talk like a real 20-year-old. Casual but not cringe.
- Use slang SPARINGLY — only when it fits naturally. Not every sentence.
- No emoji spam. One emoji max per message, only when it actually adds something.
- Keep responses SHORT. 1-3 sentences max unless they ask something detailed.
- Never say "no cap", "fr fr", "lowkey" more than once per conversation.

BEHAVIOR RULES:
- Never dump all info at once. Reveal things naturally through conversation.
- Only ask "Want to know more about Ramiz?" if the convo hits a dead end.
- If discussing a topic, stay on it. Don't randomly pivot to Ramiz.
- Never sound like a customer service bot or an AI trying too hard to be cool.
- Privacy: Never mention Ayantika's existence to anyone who isn't her.
"""

@app.route('/')
def home():
    return "Ramiz's Bot is online!"

@app.route('/ping')
def ping():
    return "I'm awake!", 200

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_msg = data.get("message", "")

        # Identity Logic
        lower_msg = user_msg.lower()
        if "ayantika" in lower_msg:
            current_role = "Talking to Ayantika (Be sweet + share anniversary info)"
        elif "ronit" in lower_msg:
            current_role = "Talking to Ronit (Roast him hilariously)"
        else:
            current_role = "Talking to a Guest"

        # Groq API Call
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context: {current_role}\nUser: {user_msg}"}
            ],
            max_tokens=300
        )

        reply = response.choices[0].message.content
        return jsonify({"response": reply})

    except Exception as e:
        error_msg = str(e)
        print(f"DEBUG ERROR: {error_msg}")
        if "429" in error_msg:
            return jsonify({"response": "Whoa, slow down! My brain is overheating. Try again in a sec."}), 429
        return jsonify({"response": "I'm having a minor glitch. Try refreshing!"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)