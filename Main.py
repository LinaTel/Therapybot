from flask import Flask, render_template, request, jsonify, session
from therapy_docs import therapy_docs
import requests
import secrets
import ollama
import chromadb


app = Flask(__name__)
app.secret_key = secrets.token_hex(32) 

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME_MENTALCOACH = "mentalcoach"



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
    session["chat_history"] = []
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_prompt = request.json.get("prompt", "")

    update_history("user", user_prompt)
    history = get_history()

    if len(history) == 1 and history[0]["role"] == "user":
        initial_reply = "Solution? Listening ear? Or rationalize?"
        update_history("assistant", initial_reply)
        return jsonify({"response": initial_reply})

    # 1. Embed user prompt to get vector for retrieval
    resp = ollama.embed(model="mxbai-embed-large", input=user_prompt)
    query_embedding = resp["embeddings"]

    # 2. Query ChromaDB for top 3 relevant therapy docs
    results = collection.query(query_embeddings=query_embedding, n_results=3)
    retrieved_docs = results["documents"]  # This is a list of lists

    # Flatten the list (in case each doc is wrapped in a list)
    flat_docs = [doc for sublist in retrieved_docs for doc in sublist]

    # 3. Build prompt: retrieved docs + chat history
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    prompt = (
        "You are an assistant who answers questions ONLY based on the following documents:\n\n"
        + "\n\n".join(flat_docs)
        + "\n\nConversation history:\n"
        + history_text
        + f"\n\nUser question: {user_prompt}\nAssistant:"
    )

    print("=== Prompt sent to Ollama ===")
    print(prompt)  # Optional: debug print to verify the prompt

    # 4. Send prompt to Ollama mentalcoach model
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