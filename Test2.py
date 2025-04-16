import random
import json

file_path = r"C:\Users\linat\Downloads\archive\intents.json"
with open(file_path, 'r') as file:
    data = json.load(file)


def chatbot_response(user_input):
    user_input = user_input.lower()  
    
    for intent in data['intents']:
        for pattern in intent['patterns']:
            if any(keyword.lower() in user_input for keyword in pattern.lower().split()):
                return random.choice(intent['responses'])
    
    return "Sorry, I didn't understand that."

while True:
    user_input = input("You: ")
    
    if user_input.lower() == "end":
        print("Bot: Goodbye! Take care.")
        break

    response = chatbot_response(user_input)
    print("Bot:", response)
