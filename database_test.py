import psycopg2
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
db_url = os.getenv('db_url')

def test_connection():
    conn = None
    cursor = None
    try:
        print("connecting..")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        cursor.execute('SELECT version();')

        db_version = cursor.fetchone()
        
        print('success! Connected to',db_version)
    except Exception as error:
        print(error)
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
        print('connection closed')

def insert(name):
    conn = None
    cursor = None
    try:
        print('inserting..')
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute('INSERT into learn (name) VALUES (%s)',(name,))
        conn.commit()
        return True
    except Exception as error:
        print("ERROR:", error)
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
        print('connection closed')

def embed_vector():
    client = OpenAI(api_key=os.getenv("api_key"))
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    text = "This is a confidential HR document"

    response = client.embeddings.create(
        model='text-embedding-3-small',
        input=text
    )

    embedding = response.data[0].embedding
    cursor.execute('Insert into docs (content,embedding) values (%s,%s)',(text,embedding))
    conn.commit()
    cursor.close()
    conn.close()
    
        


if __name__ == '__main__':
    test_connection()
