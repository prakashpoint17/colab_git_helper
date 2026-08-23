import os
import json
import subprocess
from getpass import getpass

CONFIG_FILE = ".colabgit_config"

def _load_config(path):
    config_path = os.path.join(path, CONFIG_FILE)
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {}

def _save_config(path, data):
    config_path = os.path.join(path, CONFIG_FILE)
    with open(config_path, "w") as f:
        json.dump(data, f)

def _run_cmd(cmd, cwd):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.returncode != 0 and result.stderr.strip():
        print(f"Notice: {result.stderr.strip()}")
    return result.returncode == 0

def setup_repo(path=None, username=None, repo_url=None, email=None, token=None, initial_commit_msg=None):
    """Step 1 & 2: Sets up Git configuration, links remote, and creates initial commit."""
    target_path = os.path.abspath(path or input("📁 Enter project path (e.g. /content/drive/MyDrive/...): ").strip())
    os.makedirs(target_path, exist_ok=True)

    user = username or input("👤 Enter GitHub Username: ").strip()
    raw_url = repo_url or input("🔗 Enter GitHub Repo URL (HTTPS): ").strip().rstrip("/")
    
    default_email = f"{user}@users.noreply.github.com"
    entered_email = email or input(f"📧 Enter Git Email (Press Enter for '{default_email}'): ").strip()
    mail = entered_email if entered_email else default_email
    
    pat = token or getpass("🔑 Enter GitHub Personal Access Token (hidden): ").strip()
    
    repo_name = raw_url.split("/")[-1]
    if not repo_name.endswith(".git"):
        repo_name += ".git"

    # Save credentials locally for seamless future pushes
    _save_config(target_path, {
        "username": user,
        "repo_name": repo_name,
        "token": pat
    })

    # .gitignore handling
    gitignore_path = os.path.join(target_path, ".gitignore")
    ignore_entries = {".ipynb_checkpoints/", "__pycache__/", "*.pyc", ".env", CONFIG_FILE}
    existing = set()
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            existing = set(f.read().splitlines())
    
    with open(gitignore_path, "a" if os.path.exists(gitignore_path) else "w") as f:
        for item in ignore_entries:
            if item not in existing:
                f.write(f"\n{item}")

    # Git init and configurations
    _run_cmd("git init", cwd=target_path)
    _run_cmd("git branch -M main", cwd=target_path)
    _run_cmd(f'git config user.name "{user}"', cwd=target_path)
    _run_cmd(f'git config user.email "{mail}"', cwd=target_path)
    _run_cmd("git remote remove origin", cwd=target_path)
    _run_cmd(f'git remote add origin "{raw_url}"', cwd=target_path)

    # Initial commit & push
    commit_msg = initial_commit_msg or input("💬 Enter initial commit message (Press Enter for 'Initial commit'): ").strip()
    if not commit_msg:
        commit_msg = "Initial commit"

    _run_cmd("git add .", cwd=target_path)
    _run_cmd(f'git commit -m "{commit_msg}"', cwd=target_path)
    
    auth_url = f"https://{user}:{pat}@github.com/{user}/{repo_name}"
    print("🚀 Pushing initial commit to remote 'main'...")
    if _run_cmd(f"git push {auth_url} HEAD:main", cwd=target_path):
        print("✓ Initial setup and push complete!")

def quick_push(path=None, message=None):
    """Step 3: Can be called anytime, even across disconnected Colab sessions."""
    target_path = os.path.abspath(path or os.getcwd())
    cfg = _load_config(target_path)

    if not cfg:
        target_path = os.path.abspath(input("📁 Enter project path: ").strip())
        cfg = _load_config(target_path)
        if not cfg:
            print("❌ No config found. Run setup_repo() once first.")
            return

    msg = message or input("💬 Enter commit message (Press Enter for 'Update changes'): ").strip()
    if not msg:
        msg = "Update changes"

    _run_cmd("git add .", cwd=target_path)
    _run_cmd(f'git commit -m "{msg}"', cwd=target_path)

    auth_url = f"https://{cfg['username']}:{cfg['token']}@github.com/{cfg['username']}/{cfg['repo_name']}"
    print("🚀 Pushing updates to GitHub...")
    if _run_cmd(f"git push {auth_url} HEAD:main", cwd=target_path):
        print("✓ Successfully pushed!")