package github

import (
	"github.com/google/go-github/v44/github"
	"github.com/stretchr/testify/assert"
	"testing"
)

func Test_GetClient(t *testing.T) {
	assert.NotNil(t, GetClient("token123"))
}

func Test_CreatePullRequest(t *testing.T) {
	client := github.NewClient(nil)
	err := CreatePullRequest(client, "owner1", "repo1", "my pull request", "test-branch", "main")
	assert.Contains(t, err.Error(), "404 Not Found")
}
