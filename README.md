# file-sync

A GitHub Action which synchronizes files from another repository

[![.github/workflows/gotest.yml](https://github.com/champ-oss/file-sync/actions/workflows/gotest.yml/badge.svg?branch=main)](https://github.com/champ-oss/file-sync/actions/workflows/gotest.yml)
[![.github/workflows/golint.yml](https://github.com/champ-oss/file-sync/actions/workflows/golint.yml/badge.svg?branch=main)](https://github.com/champ-oss/file-sync/actions/workflows/golint.yml)
[![.github/workflows/release.yml](https://github.com/champ-oss/file-sync/actions/workflows/release.yml/badge.svg)](https://github.com/champ-oss/file-sync/actions/workflows/release.yml)
[![.github/workflows/sonar.yml](https://github.com/champ-oss/file-sync/actions/workflows/sonar.yml/badge.svg)](https://github.com/champ-oss/file-sync/actions/workflows/sonar.yml)

[![SonarCloud](https://sonarcloud.io/images/project_badges/sonarcloud-black.svg)](https://sonarcloud.io/summary/new_code?id=file-sync_champ-oss)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=file-sync_champ-oss&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=file-sync_champ-oss)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=file-sync_champ-oss&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=file-sync_champ-oss)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=file-sync_champ-oss&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=file-sync_champ-oss)

## Features
- Keep files across multiple repositories up to date automatically
- Opens a pull request for file sync updates
- Easily configurable
- Optionally deletes files

## Example Usage

```yaml
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      - uses: champ-oss/file-sync@main
        with:
         token: ${{ secrets.GITHUB_TOKEN }}
         repo: champ-oss/terraform-module-template
         destination-repos: |
           champ-oss/repo1
           champ-oss/repo2
         destination-repos-regex: |
           champ-oss/terraform-.*
         files: |
           .gitignore
           Makefile
           templates/LICENSE-template=LICENSE
           myworkflow.yml=.github/workflows/build.yml
         delete-files: |
           .github/workflows/old-workflow.yml
```

## Token
By default the `GITHUB_TOKEN` should be passed to the `actions/checkout` step as well as this action (see example usage). This is necessary for the action to be allowed to push changes to a branch as well as open a pull request.

*Important:*

If you are syncing workflow files (`.github/workflows`) then you will need to generate and use a Personal Access Token (PAT) with `repo` and `workflow` permissions. 

## Destination Repos

The destination repositories to sync to can be specified as a list using the `destination-repos` parameter.
Alternatively, you can use a regex to match multiple destination repositories using the `destination-repos-regex`
parameter. Destination repos should be specified in the format `owner/repo`.
If both parameters are specified then the list of repos will be combined. If both parameters are omitted then the
repository
where the action is running will be used as the destination.

## File list
One file should be specified per-line. You can specify the file in the format `<source_path>=<destination_path`. The paths are relative to the root of the source and destination repositories. 
For example:
```yaml
  files: |
    templates/mystuff/.gitignore.tmpl=.gitignore
    myworkflow.yml=.github/workflows/build.yml
```

Or, if only a filename is specified then file will be copied from the source to the destination in the same directory path and name.
For example:
```yaml
  files: |
    .gitignore
```


## Parameters

| Parameter               | Required | Description                           |
|-------------------------|----------|---------------------------------------|
| token                   | false    | GitHub Token or PAT                   |
| repo                    | true     | Source GitHub repo                    |
| repo-branch             | true     | Source GitHub repo branch name        |
| destination-repos       | false    | List of destination repos             |
| destination-repos-regex | false    | Regex to match destination repos      |
| files                   | true     | List of files to sync                 |
| delete-files            | false    | List of files to delete               |
| target-branch           | false    | Target branch for pull request        |
| pull-request-branch     | false    | Branch to push changes                |
| pull-request-draft      | false    | Open the pull request in draft status |
| user                    | false    | Git username                          |
| email                   | false    | Git email                             |
| commit-message          | false    | Updated by file-sync                  |

## Contributing

