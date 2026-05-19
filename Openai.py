
from openai import OpenAI
import os
from dotenv import load_dotenv
from fastapi import FastAPI
import psycopg2
load_dotenv()
key = os.getenv("api_key")
client = OpenAI(api_key=key)

app = FastAPI()

def test_chat():
    print("Sending message to OpenAI...")
    response = client.chat.completions.create(
        model='gpt-4.1-mini',
        messages=[
            {
                'role':'system','content':'You are a sarcastic but helpful assistant'
            },
            {
                'role':'user','content':'Explain what a Java Developer is in one sentence.'
            }
        ]
    )
    ans = response.choices[0].message.content
    print('Ai says', ans)
def test_embedding():
    response = client.embeddings.create(
        model='text-embedding-3-small',
        input='This is a confidential HR document'
    )
    embedding = response.data[0].embedding
    print(embedding)
    print("Length of embedding:", len(embedding))

@app.post('/search')
def search(query):
    response = client.embeddings.create(
        model='text-embedding-3-small',input=query
    )
    embedding = response.data[0].embedding
    conn = psycopg2.connect(os.getenv('db_url'))
    cursor = conn.cursor()
    cursor.execute('Select content from docs order by embedding <=> %s::vector  limit 3',(embedding,))
    res = cursor.fetchall()
    cursor.close()
    conn.close()

    return res

@app.post('/send')
def send(query):
    res = search(query)
    response = client.chat.completions.create(model='gpt-4.1-mini',
    messages=[
        {'role':'system','content':'You are a senior tech assistant'},
        {'role':'user','content':[query,res]}
    ])
    ans = response.choices[0].message.content
    return ans





if __name__ == '__main__':
    test_chat()
