from .helper import GitRepo


def push_again(path=None, message=None):
    """
    Push changes after a Colab runtime restart/disconnect.

    Example:
        from colab_git import push_again
        push_again()
    """

    return GitRepo._push_from_config(
        path=path,
        message=message
    )


__all__ = [
    "GitRepo",
    "push_again",
]