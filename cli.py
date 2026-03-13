import typer
import subprocess
import asyncio

from main import run_pipeline, URLS
from config import settings

app = typer.Typer(help="Sentiment & NLP pipeline CLI")


@app.command()
def run(urls: list[str] = typer.Argument(None)):
    if not urls:
        urls_to_use = URLS
    else:
        urls_to_use = urls

    asyncio.run(run_pipeline(urls_to_use))


@app.command()
def api(host: str = None, port: int = None):
    host = host or settings.api_host
    port = port or settings.api_port
    subprocess.run(["uvicorn", "api:app", "--host", host, "--port", str(port)], check=True)


@app.command()
def dashboard():
    subprocess.run(["streamlit", "run", "dashboard.py"], check=True)


if __name__ == "__main__":
    app()
