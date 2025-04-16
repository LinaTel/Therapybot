import json

#loading our dataset
file_path = r"C:\Users\linat\Downloads\archive\intents.json"
with open(file_path, 'r') as file:
    data = json.load(file)


print(type(data))

#print first few entries
print(json.dumps(data, indent=4)[:500])  
