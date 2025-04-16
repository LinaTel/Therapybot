import requests

print("Hello, how are you feeling today? : ")
print("Type 'quit' to exit.\n")

while True:
    user_input = input()
    
    if user_input.lower() == "quit":
        break

    prompt = f"""
    A student is feeling: "{user_input}"
    
    Please provide kind, helpful, and practical advice to help them cope with their emotions.
    """
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mentalcoach",
            "prompt": prompt,
            "stream": False
        }
    )

    print("\n Response from the therapy bot:\n")
    print(response.json()["response"])
    print("\n" + "-"*60 + "\n")
