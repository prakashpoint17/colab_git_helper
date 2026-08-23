import os
import json
import subprocess
from getpass import getpass


class GitRepo:
    """
    Google Colab Git workflow helper.

    First-time setup:
        repo = GitRepo()

    Same session:
        repo.push_again()
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

        # --------------------------------------------------
        # Project path
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Load previous configuration
        # --------------------------------------------------

        config = self._load_config()

        # --------------------------------------------------
        # GitHub username
        # --------------------------------------------------

        self.username = (
            username
            or config.get("username")
            or input("👤 Enter GitHub Username: ").strip()
        )

        if not self.username:
            raise ValueError(
                "GitHub username cannot be empty."
            )

        # --------------------------------------------------
        # Repository URL
        # --------------------------------------------------

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

        self.repo_url = raw_repo_url.rstrip("/")

        if not self.repo_url.startswith(
            "https://github.com/"
        ):
            raise ValueError(
                "Only HTTPS GitHub repository URLs "
                "are supported."
            )

        # --------------------------------------------------
        # Email
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Token
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Repository name
        # --------------------------------------------------

        self.repo_name = self._extract_repo_name(
            self.repo_url
        )

        # --------------------------------------------------
        # Save configuration
        # --------------------------------------------------

        self._save_config({
            "username": self.username,
            "repo_url": self.repo_url,
            "repo_name": self.repo_name,
            "email": self.email,
            "token": self.token,
        })

        # --------------------------------------------------
        # Initial setup
        # --------------------------------------------------

        self._setup_repo(initial_commit_msg)

    # ======================================================
    # CONFIG
    # ======================================================

    def _config_path(self):
        return os.path.join(
            self.path,
            self.CONFIG_FILE
        )

    def _load_config(self):

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
                f"Invalid configuration file: {config_path}"
            ) from error

    def _save_config(self, data):

        with open(
            self._config_path(),
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=2
            )

    # ======================================================
    # REPOSITORY NAME
    # ======================================================

    @staticmethod
    def _extract_repo_name(repo_url):

        name = repo_url.rstrip("/").split("/")[-1]

        if name.endswith(".git"):
            name = name[:-4]

        if not name:
            raise ValueError(
                "Could not determine repository name."
            )

        return name

    # ======================================================
    # COMMAND RUNNER
    # ======================================================

    def _run(self, command, env=None):

        result = subprocess.run(
            command,
            cwd=self.path,
            capture_output=True,
            text=True,
            env=env,
        )

        if result.stdout.strip():
            print(result.stdout.strip())

        if result.returncode != 0:
            if result.stderr.strip():
                print(
                    f"Notice: {result.stderr.strip()}"
                )

        return result

    # ======================================================
    # GIT CHECK
    # ======================================================

    def _is_git_repo(self):

        return os.path.isdir(
            os.path.join(
                self.path,
                ".git"
            )
        )

    # ======================================================
    # GITIGNORE
    # ======================================================

    def _ensure_gitignore(self):

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

        for entry in self.DEFAULT_GITIGNORE:

            if entry not in existing:

                existing.append(entry)
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

    # ======================================================
    # GIT INITIALIZATION
    # ======================================================

    def _ensure_git(self):

        if not self._is_git_repo():

            self._run(
                ["git", "init"]
            )

        self._run(
            [
                "git",
                "branch",
                "-M",
                self.DEFAULT_BRANCH
            ]
        )

        self._run(
            [
                "git",
                "config",
                "user.name",
                self.username
            ]
        )

        self._run(
            [
                "git",
                "config",
                "user.email",
                self.email
            ]
        )

    # ======================================================
    # REMOTE
    # ======================================================

    def _ensure_remote(self):

        result = self._run(
            [
                "git",
                "remote",
                "get-url",
                "origin"
            ]
        )

        current_remote = result.stdout.strip()

        if not current_remote:

            self._run(
                [
                    "git",
                    "remote",
                    "add",
                    "origin",
                    self.repo_url
                ]
            )

        elif current_remote != self.repo_url:

            self._run(
                [
                    "git",
                    "remote",
                    "set-url",
                    "origin",
                    self.repo_url
                ]
            )

    # ======================================================
    # CHANGES
    # ======================================================

    def _has_changes(self):

        result = self._run(
            [
                "git",
                "status",
                "--porcelain"
            ]
        )

        return bool(
            result.stdout.strip()
        )

    # ======================================================
    # PUSH
    # ======================================================

    def _push(self):

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
            env["COLABGIT_USERNAME"] = self.username
            env["COLABGIT_TOKEN"] = self.token

            print(
                f"🚀 Pushing to remote "
                f"'{self.DEFAULT_BRANCH}' branch..."
            )

            result = self._run(
                [
                    "git",
                    "push",
                    "-u",
                    "origin",
                    self.DEFAULT_BRANCH
                ],
                env=env
            )

            if result.returncode == 0:

                print("✓ Push successful!")

                return True

            print("❌ Push failed.")

            if result.stderr.strip():
                print(result.stderr.strip())

            return False

        finally:

            if os.path.exists(askpass_file):

                try:
                    os.remove(askpass_file)
                except OSError:
                    pass

    # ======================================================
    # INITIAL SETUP
    # ======================================================

    def _setup_repo(
        self,
        initial_commit_msg=None
    ):

        self._ensure_gitignore()

        self._ensure_git()

        self._ensure_remote()

        # --------------------------------------------------
        # Check whether initial commit is required
        # --------------------------------------------------

        if not self._has_changes():

            print(
                "✓ Repository is up-to-date."
            )

            return True

        # --------------------------------------------------
        # Initial commit message
        # --------------------------------------------------

        message = (
            initial_commit_msg
            or input(
                "💬 Enter initial commit message "
                "(Press Enter for 'Initial commit'): "
            ).strip()
        )

        if not message:
            message = "Initial commit"

        print(
            "📦 Staging and creating initial commit..."
        )

        self._run(
            [
                "git",
                "add",
                "."
            ]
        )

        commit = self._run(
            [
                "git",
                "commit",
                "-m",
                message
            ]
        )

        if commit.returncode != 0:

            print("❌ Initial commit failed.")

            return False

        return self._push()

    # ======================================================
    # SAME SESSION
    # ======================================================

    def push_again(
        self,
        message=None
    ):
        """
        Push changes during the same Colab session.

        Example:
            repo.push_again()

        or:
            repo.push_again("Updated model")
        """

        if not self._is_git_repo():

            print(
                "❌ Git repository not found."
            )

            return False

        self._ensure_gitignore()
        self._ensure_git()
        self._ensure_remote()

        # --------------------------------------------------
        # Nothing changed
        # --------------------------------------------------

        if not self._has_changes():

            print(
                "✓ Nothing to commit. "
                "Working tree is clean."
            )

            return True

        # --------------------------------------------------
        # Commit message
        # --------------------------------------------------

        commit_message = (
            message
            or input(
                "💬 Enter commit message "
                "(Press Enter for 'Update changes'): "
            ).strip()
        )

        if not commit_message:
            commit_message = "Update changes"

        # --------------------------------------------------
        # Stage
        # --------------------------------------------------

        self._run(
            [
                "git",
                "add",
                "."
            ]
        )

        # --------------------------------------------------
        # Commit
        # --------------------------------------------------

        commit = self._run(
            [
                "git",
                "commit",
                "-m",
                commit_message
            ]
        )

        if commit.returncode != 0:

            print("❌ Commit failed.")

            return False

        # --------------------------------------------------
        # Push
        # --------------------------------------------------

        return self._push()


# ==========================================================
# NEW SESSION
# ==========================================================

def push_again(
    path=None,
    message=None
):
    """
    Standalone push function for a new/restarted
    Google Colab session.

    Example:

        from colab_git import push_again

        push_again()

    Or:

        push_again(
            message="Updated model"
        )

    Or:

        push_again(
            path="/content/drive/MyDrive/project",
            message="Updated model"
        )
    """

    # ------------------------------------------------------
    # Resolve project path
    # ------------------------------------------------------

    if path:

        target_path = os.path.abspath(
            os.path.expanduser(path)
        )

    else:

        target_path = os.path.abspath(
            os.getcwd()
        )

    # ------------------------------------------------------
    # Find configuration
    # ------------------------------------------------------

    config_path = os.path.join(
        target_path,
        GitRepo.CONFIG_FILE
    )

    if not os.path.exists(config_path):

        entered_path = input(
            "📁 Enter project path: "
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
            GitRepo.CONFIG_FILE
        )

    # ------------------------------------------------------
    # Configuration must exist
    # ------------------------------------------------------

    if not os.path.exists(config_path):

        print(
            "❌ No .colabgit_config found."
        )

        print(
            "Run GitRepo() once first."
        )

        return False

    # ------------------------------------------------------
    # Git repository must exist
    # ------------------------------------------------------

    if not os.path.isdir(
        os.path.join(
            target_path,
            ".git"
        )
    ):

        print(
            "❌ Git repository not found."
        )

        print(
            "Run GitRepo() once first."
        )

        return False

    # ------------------------------------------------------
    # Load configuration
    # ------------------------------------------------------

    try:

        with open(
            config_path,
            "r",
            encoding="utf-8"
        ) as file:

            config = json.load(file)

    except json.JSONDecodeError:

        print(
            "❌ Invalid .colabgit_config."
        )

        return False

    # ------------------------------------------------------
    # Validate configuration
    # ------------------------------------------------------

    required = [
        "username",
        "repo_url",
        "repo_name",
        "email",
        "token"
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

    # ------------------------------------------------------
    # Recreate GitRepo object WITHOUT __init__
    # ------------------------------------------------------

    repo = GitRepo.__new__(GitRepo)

    repo.path = target_path
    repo.username = config["username"]
    repo.repo_url = config["repo_url"]
    repo.repo_name = config["repo_name"]
    repo.email = config["email"]
    repo.token = config["token"]

    os.chdir(repo.path)

    # ------------------------------------------------------
    # Restore Git setup
    # ------------------------------------------------------

    repo._ensure_gitignore()
    repo._ensure_git()
    repo._ensure_remote()

    # ------------------------------------------------------
    # Check changes
    # ------------------------------------------------------

    if not repo._has_changes():

        print(
            "✓ Nothing to commit. "
            "Working tree is clean."
        )

        return True

    # ------------------------------------------------------
    # Commit message
    # ------------------------------------------------------

    commit_message = (
        message
        or input(
            "💬 Enter commit message "
            "(Press Enter for 'Update changes'): "
        ).strip()
    )

    if not commit_message:
        commit_message = "Update changes"

    # ------------------------------------------------------
    # Stage
    # ------------------------------------------------------

    repo._run(
        [
            "git",
            "add",
            "."
        ]
    )

    # ------------------------------------------------------
    # Commit
    # ------------------------------------------------------

    commit = repo._run(
        [
            "git",
            "commit",
            "-m",
            commit_message
        ]
    )

    if commit.returncode != 0:

        print(
            "❌ Commit failed."
        )

        return False

    # ------------------------------------------------------
    # Push
    # ------------------------------------------------------

    return repo._push()