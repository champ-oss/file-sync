"""Syncs files across repositories."""
import logging

from config_util.config_util import ConfigUtil as Config
from github_util.github_util import GitHubUtil

logging.basicConfig(
    format='%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Handle the main execution of the script.

    :return: None
    """
    source_repo = GitHubUtil(Config.token(), Config.source_repo_name())
    destination_repos = _get_destination_repo_list()
    sync_files = source_repo.get_sync_files_from_source_repo(Config.files(), Config.source_repo_branch())
    delete_files = Config.parse_files_config_from_input(Config.delete_files())

    for destination_repo_name in destination_repos:
        destination_repo = GitHubUtil(Config.token(), destination_repo_name)
        destination_repo.sync_files_for_repo(sync_files=sync_files, file_sync_branch=Config.pull_request_branch(),
                                             main_branch=Config.target_branch(), commit_message=Config.commit_message())

        destination_repo.delete_files_for_repo(delete_files=delete_files, message=Config.commit_message(),
                                               file_sync_branch=Config.pull_request_branch(),
                                               main_branch=Config.target_branch())

        destination_repo.create_pull_request(head_branch=Config.pull_request_branch(),
                                             base_branch=Config.target_branch(),
                                             title=Config.pull_request_title(), draft=Config.pull_request_draft())


def _get_destination_repo_list() -> list[str]:
    """
    Load the list of repositories to sync files to.

    :return: List of repositories.
    """
    destination_repos_specified = Config.parse_list_from_input(Config.destination_repos())

    destination_repos_found = GitHubUtil.get_repo_list_from_regex_patterns(
        access_token=Config.token(), repo_regex_patterns=Config.parse_list_from_input(Config.destination_repos_regex())
    )

    destination_repos_to_exclude = Config.parse_list_from_input(Config.destination_repos_exclude())

    return sorted([
        repo for repo in set(destination_repos_specified + destination_repos_found)
        if repo not in destination_repos_to_exclude
    ])


if __name__ == '__main__':
    main()
