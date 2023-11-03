import git
import os
from pathlib import Path
import shutil
from typing import Text 


def create_dag_run_dir(dag_run_dir: Text) -> bool:
    """Create temporary directory for DAG running
    Args:
        dag_run_dir {Text}: path to local repository
    Returns:
        bool: True if ok
    """
    print(f"Create temporary directory: {dag_run_dir}")
    os.makedirs(dag_run_dir, exist_ok=True)
    return True


# TODO: remove - moved to src/utils/utils.py
def extract_repo_name(repo_url: Text) -> Text:
    """Extracts repository name from its URL.
    Args:
        repo_url {Text}: repository URL
    Returns:
        Text: repository name
    """

    return repo_url.split('/')[-1].replace('.git', '')


def repo_url_with_credentials(repo_url: Text, user: Text, password: Text) -> Text:
    """Generate repo URL with credentials user:password
    Args:
        repo_url {Text}: repository URL
        user {Text}: repository username
        password {Text}: repository password or access token
    Returns:
        Text: repository URL with credentials:
            https://<user>:<password>@gitlab.com/group/project.git
    """

    creds = f'{user}:{password}@'
    schema_len = len('https://')
    repo_url_with_creds = repo_url[:schema_len] + creds + repo_url[schema_len:]
    return repo_url_with_creds


def clone_git_repo(repo_url: Text,
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