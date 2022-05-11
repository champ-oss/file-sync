package config

import (
	"github.com/stretchr/testify/assert"
	"os"
	"testing"
)

func Test_GetFiles(t *testing.T) {
	_ = os.Setenv("INPUT_FILES", "file1\nfile2\nfile3")
	assert.Equal(t, []string{"file1", "file2", "file3"}, GetFiles())
}

func Test_GetFiles_Newline(t *testing.T) {
	_ = os.Setenv("INPUT_FILES", "file1\nfile2\nfile3\n")
	assert.Equal(t, []string{"file1", "file2", "file3"}, GetFiles())
}

func Test_GetFiles_Extra_Space(t *testing.T) {
	_ = os.Setenv("INPUT_FILES", "file1\nfile2\nfile3\n ")
	assert.Equal(t, []string{"file1", "file2", "file3"}, GetFiles())
}

func Test_GetCommitMessage(t *testing.T) {
	_ = os.Setenv("INPUT_COMMIT_MESSAGE", "test123")
	assert.Equal(t, "test123", GetCommitMessage())
}

func Test_GetEmail(t *testing.T) {
	_ = os.Setenv("INPUT_EMAIL", "test123")
	assert.Equal(t, "test123", GetEmail())
}

func Test_GetOwnerName(t *testing.T) {
	_ = os.Setenv("GITHUB_REPOSITORY_OWNER", "test123")
	assert.Equal(t, "test123", GetOwnerName())
}

func Test_GetPullRequestBranch(t *testing.T) {
	_ = os.Setenv("INPUT_PULL_REQUEST_BRANCH", "test123")
	assert.Equal(t, "test123", GetPullRequestBranch())
}

func Test_GetRepoName(t *testing.T) {
	_ = os.Setenv("GITHUB_REPOSITORY", "owner1/repo1")
	assert.Equal(t, "repo1", GetRepoName())
}

func Test_GetSourceRepo(t *testing.T) {
	_ = os.Setenv("INPUT_REPO", "test123")
	assert.Equal(t, "test123", GetSourceRepo())
}

func Test_GetTargetBranch(t *testing.T) {
	_ = os.Setenv("INPUT_TARGET_BRANCH", "test123")
	assert.Equal(t, "test123", GetTargetBranch())
}

func Test_GetToken(t *testing.T) {
	_ = os.Setenv("INPUT_TOKEN", "test123")
	assert.Equal(t, "test123", GetToken())
}

func Test_GetUser(t *testing.T) {
	_ = os.Setenv("INPUT_USER", "test123")
	assert.Equal(t, "test123", GetUser())
}

func Test_GetWorkspace(t *testing.T) {
	_ = os.Setenv("GITHUB_WORKSPACE", "test123")
	assert.Equal(t, "test123", GetWorkspace())
}

func Test_getEnvOptional_Set(t *testing.T) {
	_ = os.Setenv("TEST_KEY", "test123")
	assert.Equal(t, "test123", getEnvOptional("TEST_KEY"))
}

func Test_getEnvOptional_Unset(t *testing.T) {
	os.Clearenv()
	assert.Equal(t, "", getEnvOptional("TEST_KEY"))
}

func Test_getEnvRequired_Set(t *testing.T) {
	_ = os.Setenv("TEST_KEY", "test123")
	assert.Equal(t, "test123", getEnvRequired("TEST_KEY"))
}
