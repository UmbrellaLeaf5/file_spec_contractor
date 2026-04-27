import typer

from fsc.commands.generate import generate_command
from fsc.commands.init import init_command

app = typer.Typer(help="FileSpecContractor (fsc) CLI")
app.command(name="generate")(generate_command)
app.command(name="init")(init_command)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
