import typer
import os

app = typer.Typer()

@app.command()
def hello(name: str):
    typer.echo(f"Hello {name}")
    os.system('ls -l')

@app.command()
def gen_urls():
    tmp = "python backend/manage.py runscript gen_urls --chdir /project/backend/scripts/scrapper"
    os.system('docker exec -it psg_mvp_backend_web_1 bash -c "{}"'.format(tmp))

@app.command()
def scrape_urls():
    tmp = "cd scrapper; python run_all.py"
    os.system(tmp)

@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        typer.echo(f"Goodbye Ms. {name}. Have a good day.")
    else:
        typer.echo(f"Bye {name}!")


if __name__ == "__main__":
    app()