from flask import Flask, render_template, request, jsonify, session
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
    therapy_docs = [
       "When feeling anxious, try deep breathing exercises. Focus on slow, deep breaths to calm the nervous system and reduce immediate tension.",
    "Cognitive Behavioral Therapy helps identify and challenge negative thought patterns, replacing them with more balanced and realistic thoughts.",
    "It's important to maintain a regular sleep schedule to support emotional regulation and overall mental health.",
    "Practicing mindfulness meditation daily can improve present-moment awareness and reduce rumination.",
    "Journaling your thoughts and feelings can help process emotions and track progress over time.",
    "Setting small, achievable goals can build confidence and help overcome feelings of overwhelm.",
    "Physical activity like walking, yoga, or stretching releases endorphins that boost mood and decrease stress.",
    "Connecting with supportive friends or family members provides emotional support and reduces feelings of isolation.",
    "If experiencing persistent sadness or hopelessness, consider seeking professional help from a therapist or counselor.",
    "Developing a self-care routine, including hobbies and relaxation techniques, supports sustained mental wellness.",
    "Learning to recognize early signs of stress allows for timely coping strategies to prevent burnout.",
    "Gratitude practices, such as listing things you are thankful for each day, can improve overall outlook and resilience.",
    "Challenging perfectionism by accepting mistakes as learning opportunities promotes self-compassion.",
    "Breathing techniques like the 4-7-8 method can quickly reduce anxiety symptoms during moments of panic.",
    "Engaging in social activities, even virtually, helps maintain a sense of community and belonging.",
    "Limiting exposure to negative news and social media can reduce anxiety and prevent information overload.",
    "Eating a balanced diet supports brain function and emotional stability.",
    "Avoiding excessive caffeine and alcohol intake helps maintain balanced mood and sleep quality.",
    ]
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

    # For first user message, keep your existing behavior
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
    prompt = "\n".join(flat_docs) + "\n" + history_text + f"\nuser: {user_prompt}\nassistant:"

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