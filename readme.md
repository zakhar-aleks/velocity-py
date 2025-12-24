# Create Py App ⚡️

The fastest way to scaffold a strictly typed, modern Python project. 

Think of this as **"Vite for Python"**. It sets up a high-performance toolchain (**uv**, **Ruff**, **Ty**) with zero configuration, so you can stop fighting `pyproject.toml` and start coding.

## 🚀 Features

* **Instant Setup:** Scaffolds a project in milliseconds.
* **Modern Stack:** Pre-configured with [Astral's](https://astral.sh) high-performance tools (`uv`, `ruff`, `ty`).
* **Strict by Default:** Enforces type safety and clean code from line one.
* **Hot Reloading:** Includes a `dev` server that lints, type-checks, and restarts your app on every save.
* **Interactive CLI:** A beautiful, easy-to-use interface for selecting your tools.

## 📦 Installation

### Via Homebrew (macOS & Linux)
The easiest way to install is via my custom tap:

```bash
brew tap zakhar-aleks/tap
brew install create-py-app
```

### Windows (via WSL)

The recommended way to use this tool on Windows is via **WSL (Windows Subsystem for Linux)**.

1.  **Install Homebrew:**
    Paste this into your Ubuntu terminal to install the package manager:
    ```bash
    /bin/bash -c "$(curl -fsSL [https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh](https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh))"
    ```

2.  **Add to Path:**
    Run these commands to activate Homebrew:
    ```bash
    (echo; echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"') >> /home/$USER/.bashrc
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    ```

3.  **Install the Tool:**
    ```bash
    brew tap zakhar-aleks/tap
    brew install create-py-app
    ```