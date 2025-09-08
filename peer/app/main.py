import threading
import typer
from .server import peer_server
from . import cli
import asyncio
from .cli import _announce
import time

app = typer.Typer()
app.add_typer(cli.app, name="peer")

@app.command()
def run(ip: str, port: int, folder: str):
    """Run peer server and announce to tracker."""
    threading.Thread(target=peer_server, args=(port, folder), daemon=True).start()
    asyncio.run(_announce(ip, port, folder))

    typer.echo(f"Peer listening on {port}, sharing {folder}")
    typer.echo("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)  # giữ cho process sống
    except KeyboardInterrupt:
        typer.echo("Shutting down...")

if __name__ == "__main__":
    app()