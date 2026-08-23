
# Colab Git Helper

A lightweight Python utility designed for Google Colab to automate repository initialization, authentication, commits, and pushes directly from Google Drive in simple, decoupled functions.

---

> **Note:** Open a Google Colab notebook, mount your Google Drive, and follow the steps below.

---

## 📦 Installation

Install directly into your Google Colab runtime:

```bash
!pip install git+[https://github.com/prakashpoint17/colab_git_helper.git](https://github.com/prakashpoint17/colab_git_helper.git)

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
from colab_git import setup_repo

# Runs fully interactively
setup_repo()

```

#### What happens automatically during setup:

* Configures your project directory in Google Drive.
* Generates a tailored `.gitignore` (ignoring `.ipynb_checkpoints/`, `__pycache__/`, `.env`, and config files).
* Initializes local git and sets default branch to `main`.
* Configures git username, email, and remote origin URL.
* Saves a secure local config so you never have to re-enter credentials for this folder across disconnected sessions.
* Stages all files, creates your initial commit, and pushes to GitHub.

---

### Step 2: Push Ongoing Changes (`quick_push`)

After modifying code, saving models, or generating artifacts, push your changes in one line. **This works even after the runtime disconnects or restarts without rerunning `setup_repo()`:**

```python
from colab_git import quick_push

# Prompts for commit message and pushes immediately
quick_push()

```

You can also pass the message and path directly without prompts:

```python
quick_push(message="Updated model hyperparameters and loss curves")

```

---

## 🖥️ Interactive Console Walkthrough

### When running `setup_repo()`:

```text
📁 Enter project path (e.g. /content/drive/MyDrive/...): /content/drive/MyDrive/Health_insurance_prediction_ML
👤 Enter GitHub Username: prakashpoint17
🔗 Enter GitHub Repo URL (HTTPS): [https://github.com/prakashpoint17/Health_insurance_prediction_ML.git](https://github.com/prakashpoint17/Health_insurance_prediction_ML.git)
📧 Enter Git Email (Press Enter for 'prakashpoint17@users.noreply.github.com'): prakashpoint2005@gmail.com
🔑 Enter GitHub Personal Access Token (hidden): ········
💬 Enter initial commit message (Press Enter for 'Initial commit'): Initial pipeline setup

```

### When running `quick_push()`:

```text
💬 Enter commit message (Press Enter for 'Update changes'): Added evaluate_metrics script
🚀 Pushing updates to GitHub...
✓ Successfully pushed!

```

---

## ⚙️ Function Reference

### `setup_repo(...)`

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `path` | `str` | `None` (Prompted) | Absolute path to project folder in Google Drive. |
| `username` | `str` | `None` (Prompted) | Your GitHub username. |
| `repo_url` | `str` | `None` (Prompted) | HTTPS clone URL of your GitHub repository. |
| `email` | `str` | `None` (Prompted) | Git config email (defaults to noreply GitHub email). |
| `token` | `str` | `None` (Prompted) | GitHub Personal Access Token (hidden password input). |
| `initial_commit_msg` | `str` | `None` (Prompted) | Initial commit description. |

### `quick_push(...)`

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `path` | `str` | `None` (Current dir / Prompted) | Project directory containing saved config. |
| `message` | `str` | `None` (Prompted) | Commit message for this update batch. |

---
