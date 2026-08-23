from .helper import GitRepo

# Expose quick_push directly as a shortcut to GitRepo.push_again
quick_push = GitRepo.push_again