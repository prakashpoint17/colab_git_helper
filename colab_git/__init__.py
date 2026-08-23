from .helper import GitRepo

# Standalone shortcut for pushing after a Colab
# runtime restart/disconnect.
quick_push = GitRepo.push_again

__all__ = [
    "GitRepo",
    "quick_push",
]