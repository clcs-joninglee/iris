import typer
import uvicorn

_DEFAULT_HOST = "0.0.0.0"
_DEFAULT_PORT = 8080

app = typer.Typer(
    name="iris",
    help="Iris API command-line interface.",
    no_args_is_help=True,
)

server_app = typer.Typer(
    name="server",
    help="Server management commands.",
    no_args_is_help=True,
)
app.add_typer(server_app, name="server")


@server_app.command("run")
def server_run(
    host: str = typer.Option(_DEFAULT_HOST, "-h", "--host"),
    port: int = typer.Option(_DEFAULT_PORT, "-p", "--port"),
) -> None:
    """Start the Iris API HTTP server."""
    from iris.config import settings

    typer.echo(f"Starting Iris API on http://{host}:{port}")
    typer.echo(f"Swagger UI: http://{host}:{port}/docs")
    uvicorn.run(
        "iris.main:app",
        host=host,
        port=port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    app()
    