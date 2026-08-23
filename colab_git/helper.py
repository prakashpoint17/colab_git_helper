import os
import json
import subprocess
from getpass import getpass


class GitRepo:
    """
    Google Colab Git/GitHub helper.

    First-time setup:
        repo = GitRepo()

    Same Colab session:
        repo.quick_push()

    After Colab runtime restart/disconnect:
        from colab_git import quick_push
        quick_push()
    """

    CONFIG_FILE = ".colabgit_config"
    DEFAULT_BRANCH = "main"

    DEFAULT_GITIGNORE = [
        ".ipynb_checkpoints/",
        "__pycache__/",
        "*.pyc",
        ".env",
        ".colabgit_config",
    ]

    def __init__(
        self,
        path=None,
        username=None,
        repo_url=None,
        email=None,
        token=None,
        initial_commit_msg=None,
    ):
        # ---------------------------------------------------------
        # 1. Resolve project path
        # ---------------------------------------------------------
        entered_path = path or input(
            "📁 Enter project path (e.g. /content/drive/MyDrive/...): "
        ).strip()

        if not entered_path:
            raise ValueError("Project path cannot be empty.")

        self.path = os.path.abspath(os.path.expanduser(entered_path))

        os.makedirs(self.path, exist_ok=True)

        # Move Python working directory to project
        os.chdir(self.path)

        # ---------------------------------------------------------
        # 2. Load existing configuration if available
        # ---------------------------------------------------------
        cfg = self._load_config()

        # ---------------------------------------------------------
        # 3. GitHub username
        # ---------------------------------------------------------
        self.username = (
            username
            or cfg.get("username")
            or input("👤 Enter GitHub Username: ").strip()
        )

        if not self.username:
            raise ValueError("GitHub username cannot be empty.")

        # ---------------------------------------------------------
        # 4. Repository URL
        # ---------------------------------------------------------
        raw_url = (
            repo_url
            or cfg.get("repo_url")
            or input("🔗 Enter GitHub Repo URL (HTTPS): ").strip()
        )

        if not raw_url:
            raise ValueError("GitHub repository URL cannot be empty.")

        self.repo_url = raw_url.strip().rstrip("/")

        if not self.repo_url.startswith("https://github.com/"):
            raise ValueError(
                "Only HTTPS GitHub repository URLs are currently supported."
            )

        # ---------------------------------------------------------
        # 5. Git email
        # ---------------------------------------------------------
        default_email = f"{self.username}@users.noreply.github.com"

        entered_email = (
            email
            or cfg.get("email")
            or input(
                f"📧 Enter Git Email (Press Enter for '{default_email}'): "
            ).strip()
        )

        self.email = entered_email if entered_email else default_email

        # ---------------------------------------------------------
        # 6. GitHub Personal Access Token
        # ---------------------------------------------------------
        self.token = (
            token
            or cfg.get("token")
            or getpass(
                "🔑 Enter GitHub Personal Access Token (hidden): "
            ).strip()
        )

        if not self.token:
            raise ValueError("GitHub Personal Access Token cannot be empty.")

        # ---------------------------------------------------------
        # 7. Extract repository name
        # ---------------------------------------------------------
        self.repo_name = self._extract_repo_name(self.repo_url)

        # ---------------------------------------------------------
        # 8. Save configuration
        # ---------------------------------------------------------
        self._save_config(
            {
                "username": self.username,
                "repo_url": self.repo_url,
                "repo_name": self.repo_name,
                "email": self.email,
                "token": self.token,
            }
        )

        # ---------------------------------------------------------
        # 9. Initial repository setup
        # ---------------------------------------------------------
        self._setup_repo(initial_commit_msg)

    # =============================================================
    # CONFIGURATION
    # =============================================================

    def _config_path(self):
        return os.path.join(self.path, self.CONFIG_FILE)

    def _load_config(self):
        """
        Load saved configuration from the project directory.
        """
        config_path = self._config_path()

        if not os.path.exists(config_path):
            return {}

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid configuration file: {config_path}"
            ) from exc

    def _save_config(self, data):
        """
        Save configuration locally.

        IMPORTANT:
        The configuration contains the GitHub token.
        The file is automatically added to .gitignore.
        """
        config_path = self._config_path()

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # =============================================================
    # REPOSITORY NAME
    # =============================================================

    @staticmethod
    def _extract_repo_name(repo_url):
        """
        Extract repository name from GitHub URL.
        """
        name = repo_url.rstrip("/").split("/")[-1]

        if name.endswith(".git"):
            name = name[:-4]

        if not name:
            raise ValueError("Could not determine repository name.")

        return name

    # =============================================================
    # COMMAND EXECUTION
    # =============================================================

    def _run_cmd(self, command, check=False, env=None):
        """
        Run a command safely without shell=True.

        command must be a list, e.g.
            ["git", "commit", "-m", "Initial commit"]
        """

        result = subprocess.run(
            command,
            cwd=self.path,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if stdout:
            print(stdout)

        if result.returncode != 0 and stderr:
            if check:
                raise RuntimeError(stderr)

            print(f"Notice: {stderr}")

        if check and result.returncode != 0:
            raise RuntimeError(
                stderr or f"Command failed: {' '.join(command)}"
            )

        return result

    # =============================================================
    # GIT REPOSITORY CHECK
    # =============================================================

    def _is_git_repo(self):
        return os.path.isdir(os.path.join(self.path, ".git"))

    # =============================================================
    # GITIGNORE
    # =============================================================

    def _ensure_gitignore(self):
        """
        Create/update .gitignore without duplicating entries.
        """

        gitignore_path = os.path.join(self.path, ".gitignore")

        existing = []

        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r", encoding="utf-8") as f:
                existing = [
                    line.strip()
                    for line in f.read().splitlines()
                    if line.strip()
                ]

        changed = False

        for item in self.DEFAULT_GITIGNORE:
            if item not in existing:
                existing.append(item)
                changed = True

        if changed or not os.path.exists(gitignore_path):
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write("\n".join(existing) + "\n")

            print("✓ .gitignore configured")

    # =============================================================
    # GIT INITIALIZATION
    # =============================================================

    def _ensure_git_repo(self):
        """
        Initialize Git repository if necessary.
        """

        if not self._is_git_repo():
            self._run_cmd(
                ["git", "init"],
                check=True,
            )

        self._run_cmd(
            ["git", "branch", "-M", self.DEFAULT_BRANCH],
            check=True,
        )

        self._run_cmd(
            ["git", "config", "user.name", self.username],
            check=True,
        )

        self._run_cmd(
            ["git", "config", "user.email", self.email],
            check=True,
        )

    # =============================================================
    # REMOTE
    # =============================================================

    def _ensure_remote(self):
        """
        Make sure origin points to the configured repository.
        """

        result = self._run_cmd(
            ["git", "remote", "get-url", "origin"],
            check=False,
        )

        current_remote = result.stdout.strip()

        if current_remote == self.repo_url:
            return

        if current_remote:
            self._run_cmd(
                ["git", "remote", "set-url", "origin", self.repo_url],
                check=True,
            )
        else:
            self._run_cmd(
                ["git", "remote", "add", "origin", self.repo_url],
                check=True,
            )

    # =============================================================
    # STATUS
    # =============================================================

    def _has_changes(self):
        """
        Check whether there are staged or unstaged changes.
        """

        result = self._run_cmd(
            ["git", "status", "--porcelain"],
            check=True,
        )

        return bool(result.stdout.strip())

    # =============================================================
    # AUTHENTICATED PUSH
    # =============================================================

    def _push_to_remote(self, branch=None):
        """
        Push using GitHub token without storing the token in the
        Git remote URL.

        Git's GIT_ASKPASS mechanism supplies credentials only for
        the current Git command.
        """

        branch = branch or self.DEFAULT_BRANCH

        askpass_file = os.path.join(
            self.path,
            ".colabgit_askpass.py",
        )

        # Temporary authentication helper.
        askpass_code = """import os
import sys

if "username" in sys.argv[1].lower():
    print(os.environ.get("COLABGIT_USERNAME", ""))
else:
    print(os.environ.get("COLABGIT_TOKEN", ""))
"""

        try:
            with open(askpass_file, "w", encoding="utf-8") as f:
                f.write(askpass_code)

            os.chmod(askpass_file, 0o700)

            env = os.environ.copy()

            env["GIT_ASKPASS"] = askpass_file
            env["GIT_TERMINAL_PROMPT"] = "0"
            env["COLABGIT_USERNAME"] = self.username
            env["COLABGIT_TOKEN"] = self.token

            print(
                f"🚀 Pushing to remote '{branch}' branch..."
            )

            result = self._run_cmd(
                [
                    "git",
                    "push",
                    "-u",
                    "origin",
                    branch,
                ],
                check=False,
                env=env,
            )

            if result.returncode == 0:
                print("✓ Push successful!")
                return True

            print("❌ Push failed.")

            if result.stderr.strip():
                print(result.stderr.strip())

            return False

        finally:
            # Remove temporary authentication helper.
            if os.path.exists(askpass_file):
                os.remove(askpass_file)

    # =============================================================
    # INITIAL SETUP
    # =============================================================

    def _setup_repo(self, initial_commit_msg=None):
        """
        Configure repository and perform initial commit/push if
        required.
        """

        self._ensure_gitignore()

        self._ensure_git_repo()

        self._ensure_remote()

        # Check whether there are files/changes to commit.
        if not self._has_changes():
            print("✓ Repository is up-to-date.")
            return

        # Initial commit message
        commit_msg = initial_commit_msg

        if not commit_msg:
            commit_msg = input(
                "💬 Enter initial commit message "
                "(Press Enter for 'Initial commit'): "
            ).strip()

        if not commit_msg:
            commit_msg = "Initial commit"

        print("📦 Staging and creating initial commit...")

        self._run_cmd(
            ["git", "add", "."],
            check=True,
        )

        commit_result = self._run_cmd(
            ["git", "commit", "-m", commit_msg],
            check=False,
        )

        if commit_result.returncode != 0:
            print("❌ Initial commit failed.")
            return

        self._push_to_remote()

    # =============================================================
    # SAME SESSION QUICK PUSH
    # =============================================================

    def quick_push(self, message=None):
        """
        Stage, commit and push project changes.

        Works while the GitRepo object exists in the current
        Python/Colab runtime.
        """

        if not self._is_git_repo():
            print("❌ This directory is not a Git repository.")
            return False

        if not self._has_changes():
            print("✓ Nothing to commit. Working tree is clean.")

            # Still synchronize with remote if required.
            return self._push_to_remote()

        msg = message

        if not msg:
            msg = input(
                "💬 Enter commit message "
                "(Press Enter for 'Update changes'): "
            ).strip()

        if not msg:
            msg = "Update changes"

        self._run_cmd(
            ["git", "add", "."],
            check=True,
        )

        commit_result = self._run_cmd(
            ["git", "commit", "-m", msg],
            check=False,
        )

        if commit_result.returncode != 0:
            print("❌ Commit failed.")
            return False

        return self._push_to_remote()

    # =============================================================
    # NEW SESSION PUSH
    # =============================================================

    @classmethod
    def push_again(cls, path=None, message=None):
        """
        Push project changes after a Colab runtime restart/disconnect.

        Loads the saved configuration from .colabgit_config.
        """

        # ---------------------------------------------------------
        # Resolve path
        # ---------------------------------------------------------

        if path:
            target_path = os.path.abspath(
                os.path.expanduser(path)
            )
        else:
            target_path = os.path.abspath(os.getcwd())

        config_path = os.path.join(
            target_path,
            cls.CONFIG_FILE,
        )

        # ---------------------------------------------------------
        # If config isn't found, ask for project path
        # ---------------------------------------------------------

        if not os.path.exists(config_path):

            entered_path = input(
                "📁 Enter project path containing "
                f"{cls.CONFIG_FILE}: "
            ).strip()

            if not entered_path:
                print("❌ Project path cannot be empty.")
                return False

            target_path = os.path.abspath(
                os.path.expanduser(entered_path)
            )

            config_path = os.path.join(
                target_path,
                cls.CONFIG_FILE,
            )

        # ---------------------------------------------------------
        # Verify config
        # ---------------------------------------------------------

        if not os.path.exists(config_path):
            print(
                "❌ No configuration found.\n"
                "Run GitRepo() once to initialize this project."
            )
            return False

        # ---------------------------------------------------------
        # Verify Git repository
        # ---------------------------------------------------------

        git_dir = os.path.join(
            target_path,
            ".git",
        )

        if not os.path.isdir(git_dir):
            print(
                "❌ Git repository not found in this directory.\n"
                "Run GitRepo() to initialize the repository."
            )
            return False

        # ---------------------------------------------------------
        # Load configuration
        # ---------------------------------------------------------

        try:
            with open(
                config_path,
                "r",
                encoding="utf-8",
            ) as f:
                cfg = json.load(f)

        except json.JSONDecodeError:
            print("❌ Invalid .colabgit_config file.")
            return False

        required = [
            "username",
            "repo_url",
            "repo_name",
            "email",
            "token",
        ]

        missing = [
            key
            for key in required
            if not cfg.get(key)
        ]

        if missing:
            print(
                "❌ Configuration is incomplete. "
                f"Missing: {', '.join(missing)}"
            )
            return False

        # ---------------------------------------------------------
        # Create object without running __init__
        # ---------------------------------------------------------

        repo = cls.__new__(cls)

        repo.path = target_path
        repo.username = cfg["username"]
        repo.repo_url = cfg["repo_url"]
        repo.repo_name = cfg["repo_name"]
        repo.email = cfg["email"]
        repo.token = cfg["token"]

        os.chdir(repo.path)

        # ---------------------------------------------------------
        # Ensure Git configuration
        # ---------------------------------------------------------

        repo._ensure_gitignore()
        repo._ensure_git_repo()
        repo._ensure_remote()

        # ---------------------------------------------------------
        # Check changes
        # ---------------------------------------------------------

        if not repo._has_changes():
            print("✓ Nothing to commit. Working tree is clean.")
            return repo._push_to_remote()

        # ---------------------------------------------------------
        # Commit message
        # ---------------------------------------------------------

        msg = message

        if not msg:
            msg = input(
                "💬 Enter commit message "
                "(Press Enter for 'Update changes'): "
            ).strip()

        if not msg:
            msg = "Update changes"

        # ---------------------------------------------------------
        # Stage
        # ---------------------------------------------------------

        repo._run_cmd(
            ["git", "add", "."],
            check=True,
        )

        # ---------------------------------------------------------
        # Commit
        # ---------------------------------------------------------

        commit_result = repo._run_cmd(
            ["git", "commit", "-m", msg],
            check=False,
        )

        if commit_result.returncode != 0:
            print("❌ Commit failed.")
            return False

        # ---------------------------------------------------------
        # Push
        # ---------------------------------------------------------

        return repo._push_to_remote()