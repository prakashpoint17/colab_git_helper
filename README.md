# Colab Git Helper

A lightweight Python utility designed for Google Colab to automate repository initialization, authentication, commits, and pushes directly from Drive in just two methods.

---

## Installation

Install directly into your Colab notebook session:

```bash
pip install git+[https://github.com/prakashpoint17/colab_git_helper.git](https://github.com/prakashpoint17/colab_git_helper.git)
```

# Project Setup 

# Install from GitHub
**In a new cell in Colab:**

```Python
# 1. Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# 2. Install the package directly from your GitHub repo
!pip install git+https://github.com/prakashpoint17/colab_git_helper.git

# 3. Import and run
from colab_git import GitRepo

# Runs fully interactively (prompts you for path, username, token, etc.)
repo = GitRepo()
```

### When you make changes to files later in the notebook, run:

```Python
# Prompts you for the commit message and pushes immediately
repo.quick_push()
```

# Interactive Flow in Colab
When you run `repo = GitRepo()`, the terminal prompts appear sequentially:

## Input Parameters

* 📁 Enter **project path** (e.g. /content/drive/MyDrive/...): /content/drive/MyDrive/Health_insurance_prediction_ML

* 👤 Enter **GitHub Username**: username

* 🔗 Enter **GitHub Repo URL** (HTTPS): https://github.com/prakashpoint17/Health_insurance_prediction_ML.git

* 📧 Enter **Git Email** : mailid@gmail.com
* 🔑 Enter GitHub **Personal Access Token** (hidden): ········

* 💬 Enter **initial commit message** (Press Enter for 'Initial commit'): "commit message"