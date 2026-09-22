
# Colab Git Helper

A lightweight Python utility designed for Google Colab to automate repository initialization, authentication, commits, and pushes directly from Google Drive in simple, decoupled methods.

---

> **Quick Demo:** Check out [`sample_setup_git_colab.ipynb`](sample_setup_git_colab.ipynb) in this repository for a complete end-to-end interactive demo in Google Colab.

---

## 📦 Installation

Install directly into your Google Colab runtime:

```bash
!pip install --upgrade git+https://github.com/prakashpoint17/colab_git_helper.git

```

---

## 🚀 Quickstart

### Step 1: Initial Repository Setup & First Push

Run this **once** when creating or linking your project repository.

```python
# 1. Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# 2. Import and initialize
from colab_git import GitRepo

# Runs fully interactively (prompts for path, username, repo URL, token, etc.)
repo = GitRepo()

```

#### What happens automatically during setup:

* Configures and switches to your project directory in Google Drive.
* Generates a tailored `.gitignore` (ignoring `.ipynb_checkpoints/`, `__pycache__/`, `.env`, and `.colabgit_config`).
* Initializes local git and sets the default branch to `main`.
* Configures git username, email, and remote origin URL.
* Saves a secure local configuration (`.colabgit_config`) inside your project directory.
* Stages all files, creates your initial commit, and pushes to GitHub using secure runtime credentials.

---

### Step 2: Push Subsequent Changes

#### Scenario A: Same Colab Session (using the active instance)

```python
# Stages changes, prompts for commit message, and pushes immediately
repo.push_again()

# Or pass the commit message directly:
repo.push_again("Updated model hyperparameters and loss curves")

```

#### Scenario B: New / Disconnected Session (after runtime restart)

When your Colab session disconnects or restarts, the `repo` variable is wiped from memory. You do **not** need to run `GitRepo()` again — just import the standalone `push_again` function:

```python
from google.colab import drive
drive.mount('/content/drive')

from colab_git import push_again

# Reads saved project config and pushes updates
push_again()

# Or specify project path and message explicitly:
push_again(path="/content/drive/MyDrive/MyProject", message="Updated dataset preprocessing")

```

---

## 🖥️ Interactive Console Walkthrough

### Initial Setup (`repo = GitRepo()`):

```text
📁 Enter project path (e.g. /content/drive/MyDrive/...): /content/drive/MyDrive/Health_insurance_prediction_ML

👤 Enter GitHub Username: 

🔗 Enter GitHub Repo URL (HTTPS): https://github.com/prakashpoint17/Health_insurance_prediction_ML.git

📧 Enter Git Email (Press Enter for 'gmail@users.noreply.github.com'): mailid@gmail.com

🔑 Enter GitHub Personal Access Token (hidden): ········

💬 Enter initial commit message (Press Enter for 'Initial commit'): Initial pipeline setup

📦 Staging and creating initial commit...
🚀 Pushing to remote 'main' branch...
✓ Push successful!

```

### Subsequent Pushes (`push_again()`):

```text
💬 Enter commit message (Press Enter for 'Update changes'): Added evaluation metrics script
🚀 Pushing to remote 'main' branch...
✓ Push successful!

```

---

## ⚙️ Reference

### `GitRepo(...)`

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `path` | `str` | `None` (Prompted) | Absolute path to project folder in Google Drive. |
| `username` | `str` | `None` (Prompted) | Your GitHub username. |
| `repo_url` | `str` | `None` (Prompted) | HTTPS clone URL of your GitHub repository. |
| `email` | `str` | `None` (Prompted) | Git config email (defaults to noreply GitHub email). |
| `token` | `str` | `None` (Prompted) | GitHub Personal Access Token (hidden password input). |
| `initial_commit_msg` | `str` | `None` (Prompted) | Initial commit description. |

### `push_again(...)` / `repo.push_again(...)`

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `path` | `str` | `None` (Current dir / Prompted) | Project directory containing saved `.colabgit_config`. |
| `message` | `str` | `None` (Prompted) | Commit message for this update batch. |

---
