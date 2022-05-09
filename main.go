package main

import (
	"fmt"
	"github.com/champ-oss/file-sync/pkg/common"
	"github.com/champ-oss/file-sync/pkg/git/cli"
	"github.com/champ-oss/file-sync/pkg/github"
	log "github.com/sirupsen/logrus"
	"os"
)

const localRepoDir = "./"
const branchName = "file-sync"
const commitMsg = "file-sync"
const user = "file-sync"
const email = "file-sync@example.com"

var files = []string{
	".tflint.hcl",
	"test/src/go.mod",
	"examples/complete/main.tf",
	".github/CODEOWNERS",
	".github/workflows/release.yml",
}

func main() {
	log.SetLevel(log.DebugLevel)
	sourceDir, err := cli.Clone(fmt.Sprintf("https://%s@github.com/champ-oss/terraform-module-template", os.Getenv("GITHUB_TOKEN")))
	if err != nil {
		log.Fatal(err)
	}

	destDir, err := cli.Clone(fmt.Sprintf("https://%s@github.com/reeves122/file-sync", os.Getenv("GITHUB_TOKEN")))
	if err != nil {
		log.Fatal(err)
	}

	err = cli.SetAuthor(destDir, user, email)
	if err != nil {
		panic(err)
	}

	err = cli.Fetch(destDir)
	if err != nil {
		panic(err)
	}

	err = cli.Branch(destDir, branchName)
	if err != nil {
		panic(err)
	}

	err = cli.Checkout(destDir, branchName)
	if err != nil {
		panic(err)
	}

	err = cli.Reset(destDir, branchName)
	if err != nil {
		panic(err)
	}

	if err := common.CopySourceFiles(files, sourceDir, destDir); err != nil {
		log.Fatal(err)
	}

	if modified := cli.AnyModified(destDir, files); modified == false {
		log.Info("all files are up to date")
		os.Exit(0)
	}

	for _, f := range files {
		err = cli.Add(destDir, f)
		if err != nil {
			panic(err)
		}
	}

	err = cli.Commit(destDir, commitMsg)
	if err != nil {
		log.Fatal(err)
	}

	_, err = common.RunCommand(destDir, "git", "remote", "-v")
	if err != nil {
		log.Fatal(err)
	}

	err = cli.Push(destDir, branchName)
	if err != nil {
		log.Fatal(err)
	}

	client := github.GetClient(os.Getenv("GITHUB_TOKEN"))
	err = github.CreatePullRequest(client)
	if err != nil {
		log.Fatal(err)
	}
}
