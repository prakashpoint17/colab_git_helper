import os
import subprocess
from getpass import getpass

class GitRepo:
    def __init__(self, path, usename, repo_url, email=None, token=None, initial_commit_msg="Initial commit"):
        self.path = os.path.abspath(path)
        self.username = username
        self.repo_url = repo_url.rstrip("/")
        self.email = email or f"{username}@users.noreply.github.com"
        self.token = token
        
        # Extract repository name (e.g., 'Health_insurance_prediction_ML.git')
        self.repo_name = self.repo_url.split("/")[-1]
        if not self.repo_name.endswith(".git"):
            self.repo_name += ".git"
        
        # Change directory to target project path
        os.makedirs(self.path, exist_ok=True)
        os.chdir(self.path)
        
        # Get token securely if not provided
        if not self.token:
            self.token = getpass("Enter Github Personal Access Token: ")
            
        # Perform complete initial setup
        self._setup_repo(initial_commit_msg)
        
    def _run(self, cmd):
        result = subprocess.run(cmd, shell=True, cwd = self.path,capture_output = True,text=True)
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.returncode != 0 and result.stderr.strip():
            print(f"Error/Warning: {result.stderr.strip()}")
        return result.returncode == 0
    
    def _setup_repo(self,initial_commit_msg):
        # 1. Create .gitignore if not exists
        gitignore_path = os.path.join(self.path, ".gitignore")
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, "w") as f:
                f.write(".ipynb_checkpoints/\n__pycache__/\n*.pyc\n.env\n")
            print("✓ Generated .gitignore")
            
        # 2. Git init & branch rename
        self._run("git init")
        self._run("git branch -M main")
        
        # 3. Set configs
        self._run(f'git config user.name "{self.username}"')
        self._run(f'git config user.email "{self.email}"')
        
        # 4. Link origin remote
        self._run("git remote remove origin")
        self._run(f'git remote add origin "{self.repo_url}"')
        
        # 5. Check if repo needs initial commit & push
        status_res = subprocess.run("git status --porcelain", shell=True, cwd=self.path, capture_output=True, text=True)
        if status_res.stdout.strip():
            print("Staging and creating initial commit...")
            self._run("git add .")
            self._run(f'git commit -m "{initial_commit_msg}"')
            self._push_to_remote()
        else:
            print("No new files to commit. Repository is up-to-date.")
            
        def _push_to_remote(self,branch="main"):
            auth_url = f"https://{self.username}:{self.token}@github.com/{self.username}/{self.repo_name}"
            print(f"Pushing to remote {branch} branch...")
            if self._run(f"git push {auth_url} HEAD:{branch}"):
                print("✓ Push successful!")
                
        def quick_push(self, message="Update changes"):
            """Stages all modified/new files, commits with the given message, and pushes."""
            self._run("git add .")
            self._run(f'git commit -m "{message}"')
            self._push_to_remote()