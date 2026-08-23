import os
import subprocess
from getpass import getpass

class GitRepo:
    def __init__(self, path=None, username=None, repo_url=None, email=None, token=None, initial_commit_msg=None):
        # 1. Prompt interactively if parameters are not provided
        self.path = os.path.abspath(path or input("📁 Enter project path (e.g. /content/drive/MyDrive/...): ").strip())
        self.username = username or input("👤 Enter GitHub Username: ").strip()
        
        raw_repo_url = repo_url or input("🔗 Enter GitHub Repo URL (HTTPS): ").strip()
        self.repo_url = raw_repo_url.rstrip("/")
        
        default_email = f"{self.username}@users.noreply.github.com"
        entered_email = email or input(f"📧 Enter Git Email (Press Enter for '{default_email}'): ").strip()
        self.email = entered_email if entered_email else default_email
        
        self.token = token or getpass("🔑 Enter GitHub Personal Access Token (hidden): ").strip()
        self.initial_commit_msg = initial_commit_msg or input("💬 Enter initial commit message (Press Enter for 'Initial commit'): ").strip()
        if not self.initial_commit_msg:
            self.initial_commit_msg = "Initial commit"

        # 2. Extract repository name
        self.repo_name = self.repo_url.split("/")[-1]
        if not self.repo_name.endswith(".git"):
            self.repo_name += ".git"

        # 3. Switch to directory and run setup
        os.makedirs(self.path, exist_ok=True)
        os.chdir(self.path)
        self._setup_repo()

    def _run(self, cmd):
        result = subprocess.run(cmd, shell=True, cwd=self.path, capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.returncode != 0 and result.stderr.strip():
            print(f"Notice/Error: {result.stderr.strip()}")
        return result.returncode == 0

    def _setup_repo(self):
        # Create .gitignore if not exists
        gitignore_path = os.path.join(self.path, ".gitignore")
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, "w") as f:
                f.write(".ipynb_checkpoints/\n__pycache__/\n*.pyc\n.env\n")
            print("✓ Generated .gitignore")

        # Git init & branch configuration
        self._run("git init")
        self._run("git branch -M main")

        # Set user config
        self._run(f'git config user.name "{self.username}"')
        self._run(f'git config user.email "{self.email}"')

        # Link remote
        self._run("git remote remove origin")
        self._run(f'git remote add origin "{self.repo_url}"')

        # Check if initial commit is required
        status_res = subprocess.run("git status --porcelain", shell=True, cwd=self.path, capture_output=True, text=True)
        if status_res.stdout.strip():
            print("📦 Staging and creating initial commit...")
            self._run("git add .")
            self._run(f'git commit -m "{self.initial_commit_msg}"')
            self._push_to_remote()
        else:
            print("✓ Repository is up-to-date. No new files to commit.")

    def _push_to_remote(self, branch="main"):
        auth_url = f"https://{self.username}:{self.token}@github.com/{self.username}/{self.repo_name}"
        print(f"🚀 Pushing to remote '{branch}' branch...")
        if self._run(f"git push {auth_url} HEAD:{branch}"):
            print("✓ Push successful!")

    def quick_push(self, message=None):
        """Stages all modified/new files, prompts for commit message if omitted, and pushes."""
        commit_msg = message or input("💬 Enter commit message: ").strip()
        if not commit_msg:
            commit_msg = "Update changes"
            
        self._run("git add .")
        self._run(f'git commit -m "{commit_msg}"')
        self._push_to_remote()