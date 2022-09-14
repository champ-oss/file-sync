package github

import (
	"context"
	"github.com/google/go-github/v44/github"
	log "github.com/sirupsen/logrus"
	"golang.org/x/oauth2"
	"strings"
)

func GetClient(token string) *github.Client {
	tokenSource := oauth2.StaticTokenSource(
		&oauth2.Token{AccessToken: token},
	)
	httpClient := oauth2.NewClient(context.Background(), tokenSource)
	return github.NewClient(httpClient)
}

func CreatePullRequest(client *github.Client, owner, repo, title, head, base string) error {
	log.Infof("creating pull request for %s -> %s", head, base)
	_, _, err := client.PullRequests.Create(context.Background(), owner, repo, &github.NewPullRequest{
		Title: github.String(title),
		Head:  github.String(head),
		Base:  github.String(base),
	})
	if err != nil {
		if strings.Contains(err.Error(), "A pull request already exists") {
			log.Info("pull request already open")
			return nil
		}
		if strings.Contains(err.Error(), "Field:head Code:invalid Message") {
			log.Info("pull request not needed")
			return nil
		}
		if strings.Contains(err.Error(), "Message:No commits between") {
			log.Info("pull request not needed")
			return nil
		}
		return err
	}
	return nil
}
