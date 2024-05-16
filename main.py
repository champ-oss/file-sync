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
    source_repo = GitHubUtil(access_token=Config.token(), repository_name=Config.source_repo_name())

    destination_repos = Config.parse_list_from_input(Config.destination_repos())
    destination_repos_found = GitHubUtil.get_repo_list_from_regex_patterns(
        access_token=Config.token(), repo_regex_patterns=Config.parse_list_from_input(Config.destination_repos_regex())
    )

    sync_files = source_repo.get_sync_files_from_source_repo(action_input_files=Config.files(),
                                                             branch=Config.source_repo_branch())

    delete_files = Config.parse_files_config_from_input(Config.delete_files())

    for destination_repo_name in set(destination_repos + destination_repos_found):
        destination_repo = GitHubUtil(access_token=Config.token(), repository_name=destination_repo_name)
        destination_repo.sync_files_for_repo(sync_files)
        destination_repo.delete_files_for_repo(delete_files)
        destination_repo.create_pull_request(head_branch=Config.pull_request_branch(),
                                             draft=Config.pull_request_draft())


if __name__ == '__main__':
    main()
