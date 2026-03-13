import typer
import subprocess
import asyncio

from main import run_pipeline, URLS
from config import settings

app = typer.Typer(help="Sentiment & NLP pipeline CLI")


@app.command()
def run(urls: list[str] = typer.Argument(None)):
    """
    Run the pipeline on default URLs or a provided list.
    """
    if not urls:
        urls_to_use = URLS
    else:
        urls_to_use = urls

    asyncio.run(run_pipeline(urls_to_use))


@app.command()
def api(host: str = None, port: int = None):
    """
    Start the FastAPI backend.
    """
    host = host or settings.api_host
    port = port or settings.api_port
    cmd = ["uvicorn", "api:app", "--host", host, "--port", str(port)]
    subprocess.run(cmd, check=True)


@app.command()
def dashboard():
    """
    Start the Streamlit dashboard.
    """
    cmd = ["streamlit", "run", "dashboard.py"]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    app()
