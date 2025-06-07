# mypy: disable-error-code="no-untyped-def"

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from src.routers import auth, users

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)


@app.get('/')
async def root() -> dict[str, str]:
    return {'message': 'Hello World!'}


@app.get('/html', response_class=HTMLResponse)
async def html() -> str:
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>
    <body>
        <h1>Hello World!</h1>
    </body>
    </html>
    """
