import nox

files = ["rplugin/python3", "noxfile.py"]


@nox.session
def format(session):
    session.install("black", "isort")
    session.run("isort", *files)
    session.run("black", *files)


@nox.session
def lint(session):
    session.install("flake8", "black")
    session.run("black", "--check", *files)
    session.run("flake8", *files)
