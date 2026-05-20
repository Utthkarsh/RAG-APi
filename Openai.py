
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

import psycopg2
import os


load_dotenv()
key = os.getenv("api_key")
client = OpenAI(api_key=key)

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
class DocumentRequest(BaseModel):
    text: str

def getEmbedding(text:str):
    response = client.embeddings.create(model='text-embedding-3-small',input=text)
    embedding = response.data[0].embedding
    return embedding


def findEmbeddings(query):
    embedding = getEmbedding(query)
    conn = psycopg2.connect(os.getenv('db_url'))
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT content
        FROM docs
        ORDER BY embedding <=> %s::vector
        LIMIT 3
        ''',
        (embedding,)
    )
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in res]

@app.post('/search')
def search(query:QueryRequest):
    res = findEmbeddings(query.query)
    return {"Question":query.query,"Results":res}

@app.post('/ask')
def send(query:QueryRequest):
    res = findEmbeddings(query.query)
    context = "\n\n".join(res)
    response = client.chat.completions.create(model='gpt-4.1-mini',messages=[
        {'role':'system','content':"Answer using only the provided context. If the answer is not in the context, say you don't know."},
        {'role':'user','content': f'''
        Context: {context}

        Question: {query.query}
        '''
        }
    ])
    ans = response.choices[0].message.content
    return {"Answer":ans,"Sources":context}

@app.post('/documents')
def documents(request:DocumentRequest):
    
    response = client.embeddings.create(model='text-embedding-3-small',input=request.text)
    embedding = response.data[0].embedding
    conn = psycopg2.connect(os.getenv('db_url'))
    cursor = conn.cursor()
    cursor.execute('Insert into docs (text,embedding) values (%s,%s)',(request.text,embedding))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "stored"}
    

