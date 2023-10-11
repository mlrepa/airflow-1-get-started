import git
from pathlib import Path
import shutil
from typing import Text

from utils.utils import repo_url_with_credentials


def clone_repo_task(repo_url: Text,
                    branch: Text,
                    repo_local_path: Text,
                    repo_username: Text,
                    repo_password: Text,
                    ) -> None:
    """Clone Git repo

    Args:
        repo_url: Remote Git repo URL
        branch: Target branch  to source code
        repo_local_path: Local directory for DAG running
        repo_username: Username
        repo_password: Password (personal access token

    Returns: None

    """
    print(f'Cloning {repo_url}')
    print(f'Repo clone to {repo_local_path}')
    repo_url_with_creds = repo_url_with_credentials(repo_url, repo_username, repo_password)
    repo_local_path = Path(repo_local_path)

    if repo_local_path.exists():
        try:
            shutil.rmtree(repo_local_path)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

    git.Repo.clone_from(repo_url_with_creds, repo_local_path)
    repo = git.Repo(repo_local_path)
    repo.git.checkout(branch)
    repo.git.pull('origin', branch)

    print(f'Repository cloned to: {repo_local_path}')
