package native

import (
	"fmt"
	"github.com/go-git/go-git/v5"
	"github.com/go-git/go-git/v5/plumbing"
	"github.com/go-git/go-git/v5/plumbing/object"
	"github.com/go-git/go-git/v5/plumbing/transport/http"
	log "github.com/sirupsen/logrus"
	"os"
	"strings"
	"time"
)

func cloneSourceRepo(sourceRepo string) (dir string, err error) {
	log.Debug("Creating temp directory for source repository")
	dir, _ = os.MkdirTemp("", "source")

	log.Infof("Cloning source repository %s to %s", sourceRepo, dir)
	if _, err := git.PlainClone(dir, false, &git.CloneOptions{URL: sourceRepo, Progress: os.Stdout}); err != nil {
		log.Error("error cloning source repository")
		return dir, err
	}
	return dir, nil
}

func openLocalRepo(path string) (repo *git.Repository, err error) {
	log.Infof("Opening local repository: %s", path)
	repo, err = git.PlainOpen(path)
	if err != nil {
		log.Error("error opening local directory as git repository")
		return nil, err
	}
	return repo, nil
}

func isWorktreeModified(worktree *git.Worktree) (bool, error) {
	status, err := worktree.Status()
	if err != nil {
		log.Error("error running git status")
		return false, err
	}
	log.Info("git status")
	fmt.Print(status)
	return !status.IsClean(), nil
}

func checkOutBranch(worktree *git.Worktree, branchName string) error {
	log.Infof("Checking out branch: %s", branchName)
	err := worktree.Checkout(&git.CheckoutOptions{
		Branch: plumbing.NewBranchReferenceName(branchName),
		Create: true,
		Keep:   true,
	})

	if err != nil && strings.Contains(err.Error(), "already exists") {

		log.Debugf("Branch already exists. Switching to existing branch: %s", branchName)
		if err := worktree.Checkout(&git.CheckoutOptions{
			Branch: plumbing.NewBranchReferenceName(branchName),
			Create: false,
			Keep:   true,
		}); err != nil {
			return err
		} else {
			return nil
		}
	}

	if err != nil {
		log.Errorf("Error checking out branch: %s", branchName)
		return err
	}
	return nil
}
func gitAddFiles(files []string, worktree *git.Worktree) error {
	for _, f := range files {
		log.Debugf("git add %s", f)
		if _, err := worktree.Add(f); err != nil {
			log.Errorf("error running git add %s", f)
			return err
		}
	}
	return nil
}

func createCommit(worktree *git.Worktree, msg, name, email string) (plumbing.Hash, error) {
	log.Infof("Creating commit as user %s", name)
	hash, err := worktree.Commit(msg, &git.CommitOptions{
		Author: &object.Signature{
			Name:  name,
			Email: email,
			When:  time.Now(),
		},
	})
	if err != nil {
		log.Error("error creating commit")
		return hash, err
	}
	log.Infof("Created commit: %s", hash)
	return hash, nil
}

func gitPush(repo *git.Repository, username, password string) error {
	log.Info("Running git push")
	err := repo.Push(&git.PushOptions{
		Progress: os.Stdout,
		Auth: &http.BasicAuth{
			Username: username,
			Password: password,
		},
	})
	if err != nil {
		log.Error("error running git push")
		return err
	}
	log.Infof("Successfully pushed")
	return nil
}
