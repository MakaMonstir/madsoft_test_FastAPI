from fastapi import FastAPI

app = FastAPI(title='Memes App')

@app.get('/memes')
def list_memes():
    raise NotImplementedError

@app.get('/memes/{meme_id}')
def get_meme(meme_id: int):
    raise NotImplementedError

@app.post('/memes')
def post_meme(image, text: str):
    raise NotImplementedError

@app.put('/memes/{meme_id}')
def put_meme(meme_id: int):
    raise NotImplementedError

@app.delete('/memes/{meme_id}')
def delete_meme(meme_id: int):
    raise NotImplementedError
