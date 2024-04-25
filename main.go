package main

import (
	"github.com/champ-oss/file-sync/pkg/common"
	"github.com/champ-oss/file-sync/pkg/config"
	"github.com/champ-oss/file-sync/pkg/git/cli"
	"github.com/champ-oss/file-sync/pkg/github"
	log "github.com/sirupsen/logrus"
)

func main() {
	log.SetLevel(log.DebugLevel)

	workspace := config.GetWorkspace()
	token := config.GetToken()
	repoName := config.GetRepoName()
	ownerName := config.GetOwnerName()
	sourceRepo := config.GetSourceRepo()
	files := config.GetFiles()
	targetBranch := config.GetTargetBranch()
	pullRequestBranch := config.GetPullRequestBranch()
	user := config.GetUser()
	email := config.GetEmail()
	commitMsg := config.GetCommitMessage()
	deleteFiles := config.GetDeleteFiles()

	sourceDir, err := cli.CloneFromGitHub(sourceRepo, token)
	if err != nil {
		log.Fatal(err)
	}

	err = cli.SetAuthor(workspace, user, email)
	if err != nil {
		panic(err)
	}

	err = cli.Fetch(workspace)
	if err != nil {
		panic(err)
	}

	err = cli.Branch(workspace, pullRequestBranch)
	if err != nil {
		panic(err)
	}

	err = cli.Checkout(workspace, pullRequestBranch)
	if err != nil {
		panic(err)
	}

	err = cli.Reset(workspace, pullRequestBranch)
	if err != nil {
		panic(err)
	}

	if err := common.CopySourceFiles(files, sourceDir, workspace); err != nil {
		log.Fatal(err)
	}

	if err := common.RemoveFiles(deleteFiles, workspace); err != nil {
		log.Fatal(err)
	}

	if modified := cli.AnyModified(workspace, append(files, deleteFiles...)); !modified {
		log.Info("all files are up to date")
	} else {
		for _, f := range append(files, deleteFiles...) {
			err = cli.Add(workspace, f.Destination)
			if err != nil {
				log.Error(err)
			}
		}

		err = cli.Commit(workspace, commitMsg)
		if err != nil {
			log.Fatal(err)
		}

		err = cli.Push(workspace, pullRequestBranch)
		if err != nil {
			log.Fatal(err)
		}
	}

	client := github.GetClient(token)
	err = github.CreatePullRequest(client, ownerName, repoName, "file-sync", pullRequestBranch, targetBranch)
	if err != nil {
		log.Fatal(err)
	}
}
