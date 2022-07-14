package cli

import (
	"fmt"
	"github.com/champ-oss/file-sync/pkg/common"
	"github.com/champ-oss/file-sync/pkg/config"
	log "github.com/sirupsen/logrus"
	"io/ioutil"
	"strings"
)

func CloneFromGitHub(repo string, token string) (dir string, err error) {
	log.Infof("Cloning repository: %s", repo)
	repoWithToken := fmt.Sprintf("https://%s@github.com/%s", token, repo)
	dir, err = Clone(repoWithToken)
	if err != nil {
		return dir, err
	}
	return dir, nil
}

func Clone(repo string) (dir string, err error) {
	log.Debug("Creating temp directory for repository")
	dir, _ = ioutil.TempDir("", "repo")

	err = common.RunCommandNoLog("./", "git", "clone", repo, dir)
	if err != nil {
		return dir, fmt.Errorf("error cloning repo %s: %s", repo, err)
	}
	return dir, nil
}

func Fetch(repoDir string) error {
	output, err := common.RunCommand(repoDir, "git", "fetch")
	if err != nil {
		return fmt.Errorf(output)
	}
	return nil
}

func Branch(repoDir, branchName string) error {
	output, err := common.RunCommand(repoDir, "git", "branch", branchName)
	if err != nil {
		if strings.Contains(output, "already exists") {
			return nil
		}
		return fmt.Errorf(output)
	}
	return nil
}

func Checkout(repoDir, branchName string) error {
	output, err := common.RunCommand(repoDir, "git", "checkout", branchName)
	if err != nil {
		return fmt.Errorf(output)
	}
	return nil
}

func Status(repoDir, fileName string) string {
	output, err := common.RunCommand(repoDir, "git", "status", "--porcelain", fileName)
	if err != nil {
		return err.Error()
	}
	return output
}

func AnyModified(repoDir string, files []config.File) bool {
	for _, f := range files {
		if status := Status(repoDir, f.Destination); status != "" {
			return true
		}
	}
	return false
}

func Add(repoDir, fileName string) error {
	output, err := common.RunCommand(repoDir, "git", "add", fileName)
	if err != nil {
		return fmt.Errorf(output)
	}
	return nil
}

func Commit(repoDir, message string) error {
	output, err := common.RunCommand(repoDir, "git", "commit", "-m", message)
	if err != nil {
		return fmt.Errorf(output)
	}
	return nil
}

func Push(repoDir, branchName string) error {
	output, err := common.RunCommand(repoDir, "git", "push", "--set-upstream", "origin", branchName)
	if err != nil {
		return fmt.Errorf(output)
	}
	return nil
}

func SetAuthor(repoDir, name, email string) error {
	output, err := common.RunCommand(repoDir, "git", "config", "user.name", name)
	if err != nil {
		return fmt.Errorf(output)
	}
	output, err = common.RunCommand(repoDir, "git", "config", "user.email", email)
	if err != nil {
		return fmt.Errorf(output)
	}
	return nil
}

func Reset(repoDir, branchName string) error {
	output, err := common.RunCommand(repoDir, "git", "reset", "--hard", fmt.Sprintf("origin/%s", branchName))
	if err != nil && !strings.Contains(output, "unknown revision or path not in the working tree") {
		return fmt.Errorf(output)
	}
	return nil
}
