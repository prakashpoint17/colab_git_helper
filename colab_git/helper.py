import os
import json
import subprocess
from getpass import getpass


class GitRepo:
    """
    Google Colab Git/GitHub workflow helper.

    First-time setup:
        repo = GitRepo()

    Same Colab session:
        repo.push_again()

    After Colab runtime restart/disconnect:
        from colab_git import push_again
        push_again()
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

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(
        self,
        path=None,
        username=None,
        repo_url=None,
        email=None,
        token=None,
        initial_commit_msg=None,
    ):
        """
        Initialize and configure a Git repository.

        If configuration already exists in .colabgit_config,
        previously saved values are reused automatically.
        """

        # --------------------------------------------------------
        # 1. Project path
        # --------------------------------------------------------

        entered_path = path or input(
            "📁 Enter project path "
            "(e.g. /content/drive/MyDrive/...): "
        ).strip()

        if not entered_path:
            raise ValueError("Project path cannot be empty.")

        self.path = os.path.abspath(
            os.path.expanduser(entered_path)
        )

        os.makedirs(self.path, exist_ok=True)
        os.chdir(self.path)

        # --------------------------------------------------------
        # 2. Load existing configuration
        # --------------------------------------------------------

        config = self._load_config()

        # --------------------------------------------------------
        # 3. GitHub username
        # --------------------------------------------------------

        self.username = (
            username
            or config.get("username")
            or input("👤 Enter GitHub Username: ").strip()
        )

        if not self.username:
            raise ValueError(
                "GitHub username cannot be empty."
            )

        # --------------------------------------------------------
        # 4. Repository URL
        # --------------------------------------------------------

        raw_repo_url = (
            repo_url
            or config.get("repo_url")
            or input(
                "🔗 Enter GitHub Repo URL (HTTPS): "
            ).strip()
        )

        if not raw_repo_url:
            raise ValueError(
                "GitHub repository URL cannot be empty."
            )

        self.repo_url = raw_repo_url.strip().rstrip("/")

        if not self.repo_url.startswith(
            "https://github.com/"
        ):
            raise ValueError(
                "Only HTTPS GitHub repository URLs "
                "are currently supported."
            )

        # --------------------------------------------------------
        # 5. Git email
        # --------------------------------------------------------

        default_email = (
            f"{self.username}@users.noreply.github.com"
        )

        entered_email = (
            email
            or config.get("email")
            or input(
                f"📧 Enter Git Email "
                f"(Press Enter for '{default_email}'): "
            ).strip()
        )

        self.email = (
            entered_email
            if entered_email
            else default_email
        )

        # --------------------------------------------------------
        # 6. GitHub Personal Access Token
        # --------------------------------------------------------

        self.token = (
            token
            or config.get("token")
            or getpass(
                "🔑 Enter GitHub Personal Access Token "
                "(hidden): "
            ).strip()
        )

        if not self.token:
            raise ValueError(
                "GitHub Personal Access Token cannot be empty."
            )

        # --------------------------------------------------------
        # 7. Repository name
        # --------------------------------------------------------

        self.repo_name = self._extract_repo_name(
            self.repo_url
        )

        # --------------------------------------------------------
        # 8. Save configuration
        # --------------------------------------------------------

        self._save_config(
            {
                "username": self.username,
                "repo_url": self.repo_url,
                "repo_name": self.repo_name,
                "email": self.email,
                "token": self.token,
            }
        )

        # --------------------------------------------------------
        # 9. Initial repository setup
        # --------------------------------------------------------

        self._setup_repo(initial_commit_msg)

    # ============================================================
    # CONFIGURATION
    # ============================================================

    def _config_path(self):
        """Return the configuration file path."""

        return os.path.join(
            self.path,
            self.CONFIG_FILE
        )

    def _load_config(self):
        """
        Load saved project configuration.

        Returns an empty dictionary when no configuration
        exists yet.
        """

        config_path = self._config_path()

        if not os.path.exists(config_path):
            return {}

        try:
            with open(
                config_path,
                "r",
                encoding="utf-8"
            ) as file:
                return json.load(file)

        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid configuration file: "
                f"{config_path}"
            ) from error

    def _save_config(self, data):
        """Save project configuration locally."""

        config_path = self._config_path()

        with open(
            config_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                data,
                file,
                indent=2
            )

    # ============================================================
    # REPOSITORY NAME
    # ============================================================

    @staticmethod
    def _extract_repo_name(repo_url):
        """Extract repository name from GitHub URL."""

        repo_name = repo_url.rstrip("/").split("/")[-1]

        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        if not repo_name:
            raise ValueError(
                "Could not determine repository name."
            )

        return repo_name

    # ============================================================
    # COMMAND EXECUTION
    # ============================================================

    def _run_cmd(
        self,
        command,
        check=False,
        env=None
    ):
        """
        Safely execute a command without shell=True.

        Example:
            self._run_cmd(
                ["git", "commit", "-m", message]
            )
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

            print(
                f"Notice: {stderr}"
            )

        if check and result.returncode != 0:
            raise RuntimeError(
                stderr
                or f"Command failed: {' '.join(command)}"
            )

        return result

    # ============================================================
    # GIT REPOSITORY CHECK
    # ============================================================

    def _is_git_repo(self):
        """Check whether the project is a Git repository."""

        return os.path.isdir(
            os.path.join(
                self.path,
                ".git"
            )
        )

    # ============================================================
    # GITIGNORE
    # ============================================================

    def _ensure_gitignore(self):
        """
        Create/update .gitignore without duplicating
        existing entries.
        """

        gitignore_path = os.path.join(
            self.path,
            ".gitignore"
        )

        existing = []

        if os.path.exists(gitignore_path):
            with open(
                gitignore_path,
                "r",
                encoding="utf-8"
            ) as file:
                existing = [
                    line.strip()
                    for line in file.read().splitlines()
                    if line.strip()
                ]

        changed = False

        for item in self.DEFAULT_GITIGNORE:
            if item not in existing:
                existing.append(item)
                changed = True

        if (
            changed
            or not os.path.exists(gitignore_path)
        ):
            with open(
                gitignore_path,
                "w",
                encoding="utf-8"
            ) as file:
                file.write(
                    "\n".join(existing) + "\n"
                )

            print("✓ .gitignore configured")

    # ============================================================
    # GIT INITIALIZATION
    # ============================================================

    def _ensure_git_repo(self):
        """Initialize and configure the Git repository."""

        if not self._is_git_repo():

            self._run_cmd(
                ["git", "init"],
                check=True
            )

        self._run_cmd(
            [
                "git",
                "branch",
                "-M",
                self.DEFAULT_BRANCH
            ],
            check=True
        )

        self._run_cmd(
            [
                "git",
                "config",
                "user.name",
                self.username
            ],
            check=True
        )

        self._run_cmd(
            [
                "git",
                "config",
                "user.email",
                self.email
            ],
            check=True
        )

    # ============================================================
    # REMOTE CONFIGURATION
    # ============================================================

    def _ensure_remote(self):
        """
        Ensure that origin exists and points to the
        configured GitHub repository.
        """

        result = self._run_cmd(
            [
                "git",
                "remote",
                "get-url",
                "origin"
            ],
            check=False
        )

        current_remote = result.stdout.strip()

        # No origin exists
        if not current_remote:

            self._run_cmd(
                [
                    "git",
                    "remote",
                    "add",
                    "origin",
                    self.repo_url
                ],
                check=True
            )

            return

        # Origin exists but points somewhere else
        if current_remote != self.repo_url:

            self._run_cmd(
                [
                    "git",
                    "remote",
                    "set-url",
                    "origin",
                    self.repo_url
                ],
                check=True
            )

    # ============================================================
    # CHANGE DETECTION
    # ============================================================

    def _has_changes(self):
        """
        Check whether the working tree contains changes.
        """

        result = self._run_cmd(
            [
                "git",
                "status",
                "--porcelain"
            ],
            check=True
        )

        return bool(
            result.stdout.strip()
        )

    # ============================================================
    # AUTHENTICATED PUSH
    # ============================================================

    def _push_to_remote(
        self,
        branch=None
    ):
        """
        Push changes to GitHub.

        The token is supplied through GIT_ASKPASS rather than
        being embedded directly into the Git remote URL.
        """

        branch = (
            branch
            or self.DEFAULT_BRANCH
        )

        askpass_file = os.path.join(
            self.path,
            ".colabgit_askpass.py"
        )

        askpass_code = """import os
import sys

prompt = " ".join(sys.argv[1:]).lower()

if "username" in prompt:
    print(os.environ.get("COLABGIT_USERNAME", ""))
else:
    print(os.environ.get("COLABGIT_TOKEN", ""))
"""

        try:

            with open(
                askpass_file,
                "w",
                encoding="utf-8"
            ) as file:
                file.write(askpass_code)

            try:
                os.chmod(
                    askpass_file,
                    0o700
                )
            except OSError:
                pass

            env = os.environ.copy()

            env["GIT_ASKPASS"] = askpass_file
            env["GIT_TERMINAL_PROMPT"] = "0"

            env["COLABGIT_USERNAME"] = (
                self.username
            )

            env["COLABGIT_TOKEN"] = (
                self.token
            )

            print(
                f"🚀 Pushing to remote "
                f"'{branch}' branch..."
            )

            result = self._run_cmd(
                [
                    "git",
                    "push",
                    "-u",
                    "origin",
                    branch
                ],
                check=False,
                env=env
            )

            if result.returncode == 0:

                print(
                    "✓ Push successful!"
                )

                return True

            print(
                "❌ Push failed."
            )

            if result.stderr.strip():
                print(
                    result.stderr.strip()
                )

            return False

        finally:

            if os.path.exists(
                askpass_file
            ):
                try:
                    os.remove(
                        askpass_file
                    )
                except OSError:
                    pass

    # ============================================================
    # INITIAL SETUP
    # ============================================================

    def _setup_repo(
        self,
        initial_commit_msg=None
    ):
        """
        Perform first-time repository setup.

        Steps:
            .gitignore
            Git initialization
            Git configuration
            Remote configuration
            Initial commit
            Initial push
        """

        self._ensure_gitignore()

        self._ensure_git_repo()

        self._ensure_remote()

        # --------------------------------------------------------
        # Check whether there is anything to commit
        # --------------------------------------------------------

        if not self._has_changes():

            print(
                "✓ Repository is up-to-date."
            )

            return

        # --------------------------------------------------------
        # Initial commit message
        # --------------------------------------------------------

        commit_msg = (
            initial_commit_msg
            or input(
                "💬 Enter initial commit message "
                "(Press Enter for 'Initial commit'): "
            ).strip()
        )

        if not commit_msg:
            commit_msg = "Initial commit"

        # --------------------------------------------------------
        # Stage files
        # --------------------------------------------------------

        print(
            "📦 Staging and creating initial commit..."
        )

        self._run_cmd(
            [
                "git",
                "add",
                "."
            ],
            check=True
        )

        # --------------------------------------------------------
        # Commit
        # --------------------------------------------------------

        commit_result = self._run_cmd(
            [
                "git",
                "commit",
                "-m",
                commit_msg
            ],
            check=False
        )

        if commit_result.returncode != 0:

            print(
                "❌ Initial commit failed."
            )

            return False

        # --------------------------------------------------------
        # Push
        # --------------------------------------------------------

        return self._push_to_remote()

    # ============================================================
    # SAME SESSION: repo.push_again()
    # ============================================================

    def push_again(
        self,
        message=None
    ):
        """
        Stage, commit and push changes.

        This method is intended for the SAME Colab session
        where the GitRepo object already exists.

        Example:
            repo = GitRepo()
            repo.push_again()

        Or:
            repo.push_again("Updated model")
        """

        if not self._is_git_repo():

            print(
                "❌ This directory is not a Git repository."
            )

            return False

        # --------------------------------------------------------
        # Ensure configuration is still correct
        # --------------------------------------------------------

        self._ensure_gitignore()
        self._ensure_git_repo()
        self._ensure_remote()

        # --------------------------------------------------------
        # Check changes
        # --------------------------------------------------------

        if not self._has_changes():

            print(
                "✓ Nothing to commit. "
                "Working tree is clean."
            )

            return True

        # --------------------------------------------------------
        # Commit message
        # --------------------------------------------------------

        commit_msg = (
            message
            or input(
                "💬 Enter commit message "
                "(Press Enter for 'Update changes'): "
            ).strip()
        )

        if not commit_msg:
            commit_msg = "Update changes"

        # --------------------------------------------------------
        # Stage
        # --------------------------------------------------------

        self._run_cmd(
            [
                "git",
                "add",
                "."
            ],
            check=True
        )

        # --------------------------------------------------------
        # Commit
        # --------------------------------------------------------

        commit_result = self._run_cmd(
            [
                "git",
                "commit",
                "-m",
                commit_msg
            ],
            check=False
        )

        if commit_result.returncode != 0:

            print(
                "❌ Commit failed."
            )

            return False

        # --------------------------------------------------------
        # Push
        # --------------------------------------------------------

        return self._push_to_remote()

    # ============================================================
    # NEW SESSION INTERNAL PUSH
    # ============================================================

    @classmethod
    def _push_from_config(
        cls,
        path=None,
        message=None
    ):
        """
        Internal method used by the package-level push_again()
        function after a Colab runtime restart/disconnect.

        It loads .colabgit_config from Google Drive and recreates
        the GitRepo state without asking for the configuration
        again.
        """

        # --------------------------------------------------------
        # 1. Resolve project path
        # --------------------------------------------------------

        if path:

            target_path = os.path.abspath(
                os.path.expanduser(path)
            )

        else:

            target_path = os.path.abspath(
                os.getcwd()
            )

        config_path = os.path.join(
            target_path,
            cls.CONFIG_FILE
        )

        # --------------------------------------------------------
        # 2. If configuration isn't found, ask for path
        # --------------------------------------------------------

        if not os.path.exists(
            config_path
        ):

            entered_path = input(
                "📁 Enter project path containing "
                f"{cls.CONFIG_FILE}: "
            ).strip()

            if not entered_path:

                print(
                    "❌ Project path cannot be empty."
                )

                return False

            target_path = os.path.abspath(
                os.path.expanduser(
                    entered_path
                )
            )

            config_path = os.path.join(
                target_path,
                cls.CONFIG_FILE
            )

        # --------------------------------------------------------
        # 3. Check configuration
        # --------------------------------------------------------

        if not os.path.exists(
            config_path
        ):

            print(
                "❌ No configuration found.\n"
                "Run GitRepo() once first."
            )

            return False

        # --------------------------------------------------------
        # 4. Check Git repository
        # --------------------------------------------------------

        git_dir = os.path.join(
            target_path,
            ".git"
        )

        if not os.path.isdir(
            git_dir
        ):

            print(
                "❌ Git repository not found.\n"
                "Run GitRepo() to initialize it."
            )

            return False

        # --------------------------------------------------------
        # 5. Load saved configuration
        # --------------------------------------------------------

        try:

            with open(
                config_path,
                "r",
                encoding="utf-8"
            ) as file:
                config = json.load(file)

        except json.JSONDecodeError:

            print(
                "❌ Invalid .colabgit_config file."
            )

            return False

        # --------------------------------------------------------
        # 6. Validate configuration
        # --------------------------------------------------------

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
            if not config.get(key)
        ]

        if missing:

            print(
                "❌ Configuration is incomplete."
            )

            print(
                "Missing: "
                + ", ".join(missing)
            )

            return False

        # --------------------------------------------------------
        # 7. Create GitRepo object WITHOUT calling __init__
        # --------------------------------------------------------

        repo = cls.__new__(cls)

        repo.path = target_path
        repo.username = config["username"]
        repo.repo_url = config["repo_url"]
        repo.repo_name = config["repo_name"]
        repo.email = config["email"]
        repo.token = config["token"]

        # --------------------------------------------------------
        # 8. Change working directory
        # --------------------------------------------------------

        os.chdir(
            repo.path
        )

        # --------------------------------------------------------
        # 9. Restore Git configuration
        # --------------------------------------------------------

        repo._ensure_gitignore()
        repo._ensure_git_repo()
        repo._ensure_remote()

        # --------------------------------------------------------
        # 10. Check changes
        # --------------------------------------------------------

        if not repo._has_changes():

            print(
                "✓ Nothing to commit. "
                "Working tree is clean."
            )

            return True

        # --------------------------------------------------------
        # 11. Commit message
        # --------------------------------------------------------

        commit_msg = (
            message
            or input(
                "💬 Enter commit message "
                "(Press Enter for 'Update changes'): "
            ).strip()
        )

        if not commit_msg:
            commit_msg = "Update changes"

        # --------------------------------------------------------
        # 12. Stage
        # --------------------------------------------------------

        repo._run_cmd(
            [
                "git",
                "add",
                "."
            ],
            check=True
        )

        # --------------------------------------------------------
        # 13. Commit
        # --------------------------------------------------------

        commit_result = repo._run_cmd(
            [
                "git",
                "commit",
                "-m",
                commit_msg
            ],
            check=False
        )

        if commit_result.returncode != 0:

            print(
                "❌ Commit failed."
            )

            return False

        # --------------------------------------------------------
        # 14. Push
        # --------------------------------------------------------

        return repo._push_to_remote()