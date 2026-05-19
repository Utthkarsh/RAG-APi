from fastapi import FastAPI
import database_test
app = FastAPI()

@app.get('/')
async def root():
    return {'message':'Hello World!'}

@app.post('/add/')
async def add_user(name: str):
    success = database_test.insert(name)
    if success:
        return {"message": "added"}
    return {"message": "failed"}


    