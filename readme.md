# Create Py App

A high-performance scaffolding tool for strictly typed, modern Python projects.

Designed as a streamlined solution for initializing Python applications, this tool establishes a robust toolchain using **uv**, **Ruff**, and **Ty** with zero manual configuration. It eliminates the need to manage `pyproject.toml` boilerplate, allowing developers to focus on implementation immediately.

## Features

* **Rapid Initialization:** Scaffolds complete project structures in milliseconds.
* **Modern Toolchain:** Comes pre-configured with high-performance tools from Astral (`uv`, `ruff`, `ty`).
* **Strict Type Safety:** Enforces type checking and code quality standards by default.
* **Integrated Development Environment:** Includes a development server with hot-reloading that automatically lints and type-checks code upon saving.
* **Interactive CLI:** Features a streamlined command-line interface for customized tool selection.

## Installation and Usage

This tool is designed to be executed directly via `uvx` (the command-line tool runner included with `uv`). This method ensures you always run the latest version without requiring a permanent global installation.

### Prerequisites

Ensure that `uv` is installed on your system.
For intallation guides refer to https://docs.astral.sh/uv/

## Creating a Project

To scaffold a new project, execute the following command in your terminal:

**macOS/Linux:**
```bash
uvx create-py-app
```

**Windows:**
```powershell
uvx create-py-app
```

This command will download and execute the tool in an isolated environment and guide you through the setup process interactively.