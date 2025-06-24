from flask import Flask, render_template, request, jsonify, session
from therapy_docs import therapy_docs
from better_profanity import profanity
from sensitive_topics import SENSITIVE_TOPICS
import requests
import secrets
import ollama
import chromadb


app = Flask(__name__)
app.secret_key = secrets.token_hex(32) 
profanity.load_censor_words()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME_MENTALCOACH = "mental_helper"


chroma_client = chromadb.Client()
collection_name = "therapy_docs"

if collection_name in [c.name for c in chroma_client.list_collections()]:
    collection = chroma_client.get_collection(name=collection_name)
else:
    collection = chroma_client.create_collection(name=collection_name)

if collection.count() == 0:
    for i, doc in enumerate(therapy_docs):
        resp = ollama.embed(model="mxbai-embed-large", input=doc)
        embedding = resp["embeddings"]
        collection.add(ids=[str(i)], embeddings=embedding, documents=[doc])

def get_history():
    return session.get("chat_history", [])

def update_history(role, content):
    history = get_history()
    history.append({"role": role, "content": content})
    session["chat_history"] = history

@app.route("/")
def index():
    session["chat_history"] = [
     {"role": "assistant", "content": "Hey! I'm your Headspace Helper. How can I support you today?"}
    ]
    return render_template("index.html")

@app.route("/session-history", methods=["GET"])
def session_history():
    return jsonify({"history": get_history()})

@app.route("/chat", methods=["POST"])
def chat():
    user_prompt = request.json.get("prompt", "")

    #filter curse words
    if profanity.contains_profanity(user_prompt):
        return jsonify({"response": "Let's keep things respectful, please."}), 200
    
    #filter for any sensitive topics that goes beyond our use cases
    lower_prompt = user_prompt.lower()
    if any(topic in lower_prompt for topic in SENSITIVE_TOPICS):
        return jsonify({
            "response": (
                "I'm really sorry you're feeling this way but this goes beyond what I can help with.\n\n"
                "If you're in crisis or need help, please reach out to a therapist, doctor, or a mental health support line in your country."
            )
        }), 200

    update_history("user", user_prompt)
    history = get_history()

    resp = ollama.embed(model="mxbai-embed-large", input=user_prompt)
    query_embedding = resp["embeddings"]

    results = collection.query(query_embeddings=query_embedding, n_results=3)
    retrieved_docs = results["documents"]  

    flat_docs = [doc for sublist in retrieved_docs for doc in sublist]

    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    prompt = (
        "You are an assistant who answers questions ONLY based on the following documents:\n\n"
        + "\n\n".join(flat_docs)
        + "\n\nConversation history:\n"
        + history_text
        + f"\n\nUser question: {user_prompt}\nAssistant:"
    )

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
        
        #censor potential profanity for safety reasons
        ai_response = profanity.censor(ai_response)
        update_history("assistant", ai_response)
        return jsonify({"response": ai_response})
    else:
        return jsonify({"error": "There was an error processing the request."}), 500

if __name__ == "__main__":
    app.run(debug=True)