import typer
from typer.testing import CliRunner

app = typer.Typer()


@app.command()
def main() -> None:
    # uncomment the following line and at the pdb prompt, "c" for continue, and
    # the following error is encountered, same as in test_users, same location,
    # except without invoking pdb:
    #> ValueError: I/O operation on a closed file
    # breakpoint()
    pass


def test_click_output_capture():
    runner = CliRunner()
    result = runner.invoke(app)
