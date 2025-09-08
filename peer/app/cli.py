import asyncio
import httpx
import typer
from .utils import list_shared_files
from .downloader import download_file, TRACKER_URL

app = typer.Typer()

async def _announce(ip: str, port: int, folder: str):
    files = list_shared_files(folder)
    async with httpx.AsyncClient() as client:
        body = {"ip": ip, "port": port, "files": files}
        res = await client.post(f"{TRACKER_URL}/announce", json=body)
        typer.echo(f"Announce: {res.json()}")


async def _list():
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{TRACKER_URL}/files")
        typer.echo("Files on tracker:")
        for f in res.json():
            typer.echo(f"- {f['name']} ({f['size']} bytes)")


async def _info(filename: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{TRACKER_URL}/file/{filename}")
        typer.echo(res.json())

async def _download(ip: str, port: int, folder: str, filename: str):
    import httpx

    try:
        with httpx.Client() as client:
            res = client.get(f"{TRACKER_URL}/file/{filename}")
            data = res.json()
    except Exception as e:
        typer.echo(f"Failed to query tracker: {e}")
        return

    if not data.get("file"):
        typer.echo("File not found on tracker")
        return

    peers = data.get("peers", [])
    if not peers:
        typer.echo("No peers available")
        return

    # Gọi đồng bộ download_file
    result = download_file(
        filename=data["file"]["name"],
        total_size=data["file"]["size"],
        peers=peers,
        save_folder=folder,
        self_ip=ip,
        self_port=port,
    )

    typer.echo(f"Complete notify: {result}")


@app.command()
def announce(ip: str, port: int, folder: str):
    """Announce this peer and start sharing files."""
    asyncio.run(_announce(ip, port, folder))


@app.command()
def list():
    """List files available on tracker."""
    asyncio.run(_list())


@app.command()
def info(filename: str):
    """Get info about a specific file."""
    asyncio.run(_info(filename))


@app.command()
def download(ip: str, port: int, folder: str, filename: str):
    """Download a file from peers."""
    asyncio.run(_download(ip, port, folder, filename))
