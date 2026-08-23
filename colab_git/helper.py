import os
import json
import subprocess
from getpass import getpass

class GitRepo:
    CONFIG_FILE = ".colabgit_config"

    def __init__(self, path=None, username=None, repo_url=None, email=None, token=None, initial_commit_msg=None):
        self.path = os.path.abspath(path or input("📁 Enter project path (e.g. /content/drive/MyDrive/...): ").strip())
        os.makedirs(self.path, exist_ok=True)
        os.chdir(self.path)

        # Check for existing config to avoid re-asking if already configured
        cfg = self._load_config()

        self.username = username or cfg.get("username") or input("👤 Enter GitHub Username: ").strip()
        
        raw_url = repo_url or cfg.get("repo_url") or input("🔗 Enter GitHub Repo URL (HTTPS): ").strip().rstrip("/")
        self.repo_url = raw_url
        
        default_email = f"{self.username}@users.noreply.github.com"
        entered_email = email or cfg.get("email") or input(f"📧 Enter Git Email (Press Enter for '{default_email}'): ").strip()
        self.email = entered_email if entered_email else default_email
        
        self.token = token or cfg.get("token") or getpass("🔑 Enter GitHub Personal Access Token (hidden): ").strip()

        # Parse repository name
        self.repo_name = self.repo_url.split("/")[-1]
        if not self.repo_name.endswith(".git"):
            self.repo_name += ".git"

        # Save config locally in project folder
        self._save_config({
            "username": self.username,
            "repo_url": self.repo_url,
            "repo_name": self.repo_name,
            "email": self.email,
            "token": self.token
        })

        # Run initial setup and push
        self._setup_repo(initial_commit_msg)

    def _load_config(self):
        config_path = os.path.join(self.path, self.CONFIG_FILE)
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        return {}

    def _save_config(self, data):
        config_path = os.path.join(self.path, self.CONFIG_FILE)
        with open(config_path, "w") as f:
            json.dump(data, f)

    def _run_cmd(self, cmd):
        result = subprocess.run(cmd, shell=True, cwd=self.path, capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.returncode != 0 and result.stderr.strip():
            print(f"Notice: {result.stderr.strip()}")
        return result.returncode == 0

    def _setup_repo(self, initial_commit_msg):
        # 1. Manage .gitignore
        gitignore_path = os.path.join(self.path, ".gitignore")
        ignore_entries = {".ipynb_checkpoints/", "__pycache__/", "*.pyc", ".env", self.CONFIG_FILE}
        existing = set()
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                existing = set(f.read().splitlines())

        with open(gitignore_path, "a" if os.path.exists(gitignore_path) else "w") as f:
            for item in ignore_entries:
                if item not in existing:
                    f.write(f"\n{item}")

        # 2. Initialize and configure git
        self._run_cmd("git init")
        self._run_cmd("git branch -M main")
        self._run_cmd(f'git config user.name "{self.username}"')
        self._run_cmd(f'git config user.email "{self.email}"')
        self._run_cmd("git remote remove origin")
        self._run_cmd(f'git remote add origin "{self.repo_url}"')

        # 3. Initial commit and push
        status_res = subprocess.run("git status --porcelain", shell=True, cwd=self.path, capture_output=True, text=True)
        if status_res.stdout.strip():
            commit_msg = initial_commit_msg or input("💬 Enter initial commit message (Press Enter for 'Initial commit'): ").strip()
            if not commit_msg:
                commit_msg = "Initial commit"

            print("📦 Staging and creating initial commit...")
            self._run_cmd("git add .")
            self._run_cmd(f'git commit -m "{commit_msg}"')
            self._push_to_remote()
        else:
            print("✓ Repository is up-to-date. No new files to commit.")

    def _push_to_remote(self, branch="main"):
        auth_url = f"https://{self.username}:{self.token}@github.com/{self.username}/{self.repo_name}"
        print(f"🚀 Pushing to remote '{branch}' branch...")
        if self._run_cmd(f"git push {auth_url} HEAD:{branch}"):
            print("✓ Push successful!")

    def quick_push(self, message=None):
        """Instance method: pushes updates when 'repo' object is still alive in memory."""
        msg = message or input("💬 Enter commit message (Press Enter for 'Update changes'): ").strip()
        if not msg:
            msg = "Update changes"

        self._run_cmd("git add .")
        self._run_cmd(f'git commit -m "{msg}"')
        self._push_to_remote()

    @classmethod
    def push_again(cls, path=None, message=None):
        """Class method: call directly even if Colab session reloaded and 'repo' variable was wiped."""
        target_path = os.path.abspath(path or os.getcwd())
        config_path = os.path.join(target_path, cls.CONFIG_FILE)

        if not os.path.exists(config_path):
            target_path = os.path.abspath(input("📁 Enter project path: ").strip())
            config_path = os.path.join(target_path, cls.CONFIG_FILE)
            if not os.path.exists(config_path):
                print("❌ No configuration found. Run GitRepo() once first.")
                return

        with open(config_path, "r") as f:
            cfg = json.load(f)

        msg = message or input("💬 Enter commit message (Press Enter for 'Update changes'): ").strip()
        if not msg:
            msg = "Update changes"

        result = subprocess.run("git add .", shell=True, cwd=target_path, capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout.strip())

        result = subprocess.run(f'git commit -m "{msg}"', shell=True, cwd=target_path, capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout.strip())

        auth_url = f"https://{cfg['username']}:{cfg['token']}@github.com/{cfg['username']}/{cfg['repo_name']}"
        print("🚀 Pushing updates to GitHub...")
        push_res = subprocess.run(f"git push {auth_url} HEAD:main", shell=True, cwd=target_path, capture_output=True, text=True)
        if push_res.stdout.strip():
            print(push_res.stdout.strip())
        if push_res.returncode == 0:
            print("✓ Successfully pushed!")
        else:
            print(f"Notice/Error: {push_res.stderr.strip()}")