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

## Example Usage

```yaml
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - uses: champ-oss/file-sync
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          repo: champ-oss/terraform-module-template
          files: |
            .gitignore
            Makefile
            templates/LICENSE-template=LICENSE
            myworkflow.yml=.github/workflows/build.yml
```

## Token
By default the `GITHUB_TOKEN` should be passed to the `actions/checkout` step as well as this action (see example usage). This is necessary for the action to be allowed to push changes to a branch as well as open a pull request.

*Important:*

If you are syncing workflow files (`.github/workflows`) then you will need to generate and use a Personal Access Token (PAT) with `repo` and `workflow` permissions. 


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
| Parameter | Required | Description |
| --- | --- | --- |
| token | false | GitHub Token or PAT |
| repo | true | Source GitHub repo |
| files | true | List of files to sync |
| target-branch | false | Target branch for pull request |
| pull-request-branch | false | Branch to push changes |
| user | false | Git username |
| email | false | Git email |
| commit-message | false | Updated by file-sync |

## Contributing

