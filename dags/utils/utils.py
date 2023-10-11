from datetime import date
from pathlib import Path
from typing import Text


def create_dag_run_dir(dag_run_dir: Text) -> bool:
    """Create temporary directory for DAG running
    Args:
        dag_run_dir {Text}: path to local repository
    Returns:
        bool: True if ok
    """
    print(f"Create temporary directory: {dag_run_dir}")
    Path(dag_run_dir).mkdir(exist_ok=True, parents=True)
    return True


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

