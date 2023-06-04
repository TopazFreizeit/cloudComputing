import json

# Assuming `data` contains your JSON data
buffer = json.dumps("snakjnslkjnljnslkjns").encode('utf-8')
if buffer is not None:
    with open('file.json', 'wb') as file:
        file.write(buffer)