#!/usr/bin/env python3

import sys
import os
import subprocess
from pathlib import Path
from typing import Optional
import typer
import questionary
from questionary import Style
from rich.console import Console
from rich.theme import Theme

RUBY_RED = "#F70018"

custom_theme = Theme({
    "ruby": f"bold {RUBY_RED}",
    "dim": "dim",
    "success": "green",
    "error": "bold red",
})

prompt_style = Style([
    ('qmark', f'fg:{RUBY_RED} bold'),       
    ('question', 'bold'),                   
    ('answer', f'fg:{RUBY_RED} bold'),      
    ('pointer', f'fg:{RUBY_RED} bold'),    
    ('highlighted', f'fg:{RUBY_RED} bold noreverse'),
    ('instruction', 'fg:gray'),           
])

app = typer.Typer(help="Scaffold a strictly typed Python project.", add_completion=False)
console = Console(theme=custom_theme)

def get_system_python() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}"

def generate_toml(name: str, linter: str, type_checker: str, py_ver: str, framework: str) -> str:
    config = ""
    ruff_ver = f"py{py_ver.replace('.', '')}"

    if "Ruff" in linter:
        config += f"""
[tool.ruff]
line-length = 88
target-version = "{ruff_ver}"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B"]
fixable = ["ALL"]

[tool.ruff.format]
quote-style = "double"
"""

    if "Ty" in type_checker:
        config += """
[tool.ty]
# Ty defaults
"""

    elif "Mypy" in type_checker:
        config += """
[tool.mypy]
strict = true
ignore_missing_imports = true
disallow_untyped_defs = true
"""
    
    dev_cmd = ""

    if framework == "Vanilla":
        dev_cmd = "python -m watchfiles 'python main.py' ."

    elif framework == "FastAPI":  
        dev_cmd = "python -m uvicorn main:app --reload"

    elif framework == "Flask":
        dev_cmd = "python -m flask --app main run --debug"

    elif framework == "Streamlit":
        dev_cmd = "python -m streamlit run main.py"

    elif framework == "Typer":
        dev_cmd = "python main.py --help"

    elif framework == "NiceGUI":
        dev_cmd = "python main.py"

    config += f"""
[tool.poe.tasks]
dev = "{dev_cmd}"
"""

    return f"""[project]
name = "{name}"
version = "0.1.0"
description = "Project generated with create-py-app"
readme = "README.md"
requires-python = ">={py_ver}"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["."]

{config}
"""

def generate_main_py(name: str, framework: str) -> str:
    if framework == "Vanilla":
        return f"""def main() -> None:
    print("Hello from {name}!")

if __name__ == "__main__":
    main()
"""
    
    elif framework == "FastAPI":
        return """from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def main():
    return {"Hello": "World", "Framework": "FastAPI"}
"""

    elif framework == "Flask":
        return """from flask import Flask

app = Flask(__name__)

@app.route("/")
def main():
    return {"Hello": "World", "Framework": "Flask"}
"""

    elif framework == "Streamlit":
        return """import streamlit as st

st.write("Welcome to your new Streamlit app!")
"""

    elif framework == "Typer":
        return f"""import typer

app = typer.Typer()

@app.command()
def main(name: str):
    print("Welcome to your new Typer app!")

if __name__ == "__main__":
    main()
"""
    
    elif framework == "NiceGUI":
        return f"""from nicegui import ui

def main():
    ui.label('Hello from {name}!')
    ui.button('Click me!', on_click=lambda: ui.notify('You clicked me!'))
    ui.run(reload=True)

if __name__ in {"__main__", "__mp_main__"}:
    main()
"""
    return ""

@app.command()
def create(
    project_name: Optional[str] = typer.Argument(None, help="The name of the project directory"),
    git: bool = typer.Option(True, help="Initialize a git repository"),
):
    detected_ver = get_system_python()
    
    console.print(f"\n[ruby]Create Py App[/]")
    console.print(f"[dim]Detected System Python: {detected_ver}[/]\n")

    if not project_name:
        project_name = questionary.text(
            "Project name",
            instruction="(default: my-py-app)", 
            qmark="◇",
            style=prompt_style
        ).ask()
        
        if project_name is None: raise typer.Exit()
        if not project_name: project_name = "my-py-app"

    path = Path(project_name)

    if path.exists():
        console.print(f"\n[error]Directory '{project_name}' already exists.[/]")
        raise typer.Exit(code=1)

    framework = questionary.select(
        "Select a framework",
        choices=["Vanilla", "FastAPI", "Flask", "Streamlit", "Typer", "NiceGUI"],
        qmark="◇",
        pointer="❯",
        style=prompt_style,
    ).ask()

    if framework is None: raise typer.Exit()

    linter_choice = questionary.select(
        "Select a linter",
        choices=["Ruff (Fast, Recommended)", "None"],
        qmark="◇",
        pointer="❯",
        style=prompt_style,
    ).ask()

    if linter_choice is None: raise typer.Exit()

    type_choice = questionary.select(
        "Select a type checker",
        choices=["Ty (Astral - Fast)", "Mypy (Standard)", "None"],
        qmark="◇",
        pointer="❯",
        style=prompt_style,
    ).ask()

    if type_choice is None: raise typer.Exit()

    should_install = questionary.confirm(
        "Install dependencies now?",
        default=True,
        qmark="◇",
        style=prompt_style
    ).ask()

    if should_install is None: raise typer.Exit()

    console.print(f"Scaffolding project in [bold white]{project_name}[/]...")

    path.mkdir()
    
    subprocess_env = os.environ.copy()
    subprocess_env.pop("VIRTUAL_ENV", None)

    subprocess.run(["uv", "init", "--python", detected_ver, "--quiet"], cwd=path, env=subprocess_env, check=True)

    if (path / "hello.py").exists():
        (path / "hello.py").unlink()

    (path / "main.py").write_text(generate_main_py(project_name, framework))

    deps = []
    dev_deps = ["poethepoet"] 

    if "Ruff" in linter_choice: dev_deps.append("ruff")
    if "Ty" in type_choice: dev_deps.append("ty")
    if "Mypy" in type_choice: dev_deps.append("mypy")

    if framework == "Vanilla":
        dev_deps.append("watchfiles")

    elif framework == "FastAPI":
        deps.extend(["fastapi", "uvicorn[standard]"])

    elif framework == "Flask":
        deps.append("flask")

    elif framework == "Streamlit":
        deps.append("streamlit")

    elif framework == "Typer":
        deps.append("typer")

    elif framework == "NiceGUI":
        deps.append("nicegui")

    (path / "pyproject.toml").write_text(
        generate_toml(project_name, linter_choice, type_choice, detected_ver, framework)
    )

    if should_install:
        if deps:
            console.print(f"    [dim]Installing app deps: {', '.join(deps)}...[/]")
            subprocess.run(["uv", "add"] + deps + ["--quiet"], cwd=path, env=subprocess_env)
        
        if dev_deps:
            console.print(f"    [dim]Installing dev deps: {', '.join(dev_deps)}...[/]")
            subprocess.run(["uv", "add", "--dev"] + dev_deps + ["--quiet"], cwd=path, env=subprocess_env)

        console.print(f"    [dim]Installing project...[/]")
        subprocess.run(["uv", "sync", "--quiet"], cwd=path, env=subprocess_env)

        if "Ruff" in linter_choice:
            console.print("    [dim]Running initial format...[/]")
            subprocess.run(["uv", "run", "ruff", "format", ".", "--quiet"], cwd=path, env=subprocess_env)

        if git:
            console.print("    [dim]Initializing Git...[/]")
            subprocess.run(["git", "init", "-q"], cwd=path, env=subprocess_env)
            with (path / ".gitignore").open("a") as f:
                f.write(".ruff_cache\n.mypy_cache\n__pycache__\n")
            subprocess.run(["git", "add", "."], cwd=path, env=subprocess_env)
            subprocess.run(["git", "commit", "-q", "-m", "Init"], cwd=path, env=subprocess_env)

    else:
        console.print("[dim]  Skipping install.[/]")

    console.print(f"\n[ruby]Done! Now run:[/]")
    console.print(f"  cd {project_name}")
    console.print(f"  uv run poe dev")

if __name__ == "__main__":
    app()