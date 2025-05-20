from flask import Flask, render_template, request, jsonify, session
import requests
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32) 

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME_MENTALCOACH = "mentalcoach"

def get_history():
    return session.get("chat_history", [])

def update_history(role, content):
    history = get_history()
    history.append({"role": role, "content": content})
    session["chat_history"] = history

@app.route("/")
def index():
    session["chat_history"] = [] 
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_prompt = request.json.get("prompt", "")

    # Update history with user message
    update_history("user", user_prompt)

    history = get_history()

    if len(history) == 1 and history[0]["role"] == "user":
        initial_reply = "Solution? Listening ear? Or rationalize?"
        update_history("assistant", initial_reply)
        return jsonify({"response": initial_reply})

    prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME_MENTALCOACH,
            "prompt": prompt,
            "stream": False
        }
    )

    if response.status_code == 200:
        ai_response = response.json().get("response", "").strip()
        update_history("assistant", ai_response)
        return jsonify({"response": ai_response})
    else:
        return jsonify({"error": "There was an error processing the request."}), 500

if __name__ == "__main__":
    app.run(debug=True)

