package cli

import (
	"github.com/champ-oss/file-sync/pkg/common"
	"github.com/champ-oss/file-sync/pkg/config"
	log "github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"io/ioutil"
	"os"
	"path/filepath"
	"testing"
)

const fixtureGitRepo = "git-fixtures/basic.git"
const fixtureGitRepoInvalid = "localhost/not-a-repo"

var token = os.Getenv("GITHUB_TOKEN")

func init() {
	log.SetLevel(log.DebugLevel)
}

func Test_Clone_Success(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}

	_, err = os.Stat(repoDir)
	assert.NoError(t, err)

	_, err = os.Stat(filepath.Join(repoDir, "LICENSE"))
	assert.NoError(t, err)
}

func Test_Clone_Error(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepoInvalid, token)
	defer common.RemoveDir(repoDir)
	assert.Contains(t, err.Error(), "error cloning repo")
}

func Test_Fetch_Success(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}

	err = Fetch(repoDir)
	assert.NoError(t, err)
}

func Test_Fetch_Error(t *testing.T) {
	repoDir, _ := CloneFromGitHub(fixtureGitRepoInvalid, token)
	defer common.RemoveDir(repoDir)

	err := Fetch(repoDir)
	assert.Contains(t, err.Error(), "not a git repository")
}

func Test_Branch_Success(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}
	err = Branch(repoDir, "test")
	assert.NoError(t, err)
}

func Test_Branch_Exists(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}
	err = Branch(repoDir, "master")
	assert.NoError(t, err)
}

func Test_Branch_Error(t *testing.T) {
	repoDir, _ := CloneFromGitHub(fixtureGitRepoInvalid, token)
	defer common.RemoveDir(repoDir)
	err := Branch(repoDir, "test")
	assert.Error(t, err)
}

func Test_Checkout_Success(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}
	err = Branch(repoDir, "test")
	if err != nil {
		panic(err)
	}

	err = Checkout(repoDir, "test")
	assert.NoError(t, err)

	output, err := common.RunCommand(repoDir, "git", "status")
	assert.NoError(t, err)
	assert.Contains(t, output, "On branch test")
}

func Test_Checkout_Error(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}

	err = Checkout(repoDir, "test")
	assert.Contains(t, err.Error(), "did not match any")
}

func Test_Status_Clean(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}
	output := Status(repoDir, "foo")
	assert.Equal(t, "", output)
}

func Test_Status_Modified(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}

	err = ioutil.WriteFile(filepath.Join(repoDir, "LICENSE"), []byte("test"), 0644)
	output := Status(repoDir, "LICENSE")
	assert.Equal(t, " M LICENSE\n", output)
	assert.Nil(t, err)
}

func Test_Status_Error(t *testing.T) {
	repoDir, _ := CloneFromGitHub(fixtureGitRepoInvalid, token)
	defer common.RemoveDir(repoDir)

	output := Status(repoDir, "foo")
	assert.Equal(t, "exit status 128", output)
}

func Test_Add_Success(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}

	err = ioutil.WriteFile(filepath.Join(repoDir, "LICENSE"), []byte("test"), 0644)
	if err != nil {
		panic(err)
	}

	err = Add(repoDir, "LICENSE")
	assert.Nil(t, err)

	output := Status(repoDir, "LICENSE")
	assert.Equal(t, "M  LICENSE\n", output)
}

func Test_Add_Error(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}

	err = Add(repoDir, "foo")
	assert.Contains(t, err.Error(), "did not match any files")
}

func Test_Commit_Success(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}

	err = SetAuthor(repoDir, "testuser", "testuser@example.com")
	if err != nil {
		panic(err)
	}

	err = ioutil.WriteFile(filepath.Join(repoDir, "LICENSE"), []byte("test"), 0644)
	if err != nil {
		panic(err)
	}

	err = Add(repoDir, "LICENSE")
	if err != nil {
		panic(err)
	}

	err = Commit(repoDir, "test commit")
	assert.Nil(t, err)
}

func Test_Commit_Clean(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}

	err = SetAuthor(repoDir, "testuser", "testuser@example.com")
	if err != nil {
		panic(err)
	}

	err = Commit(repoDir, "test commit")
	assert.Equal(t, "", err.Error())
}

func Test_Commit_Error(t *testing.T) {
	repoDir, _ := CloneFromGitHub(fixtureGitRepoInvalid, token)
	defer common.RemoveDir(repoDir)

	err := Commit(repoDir, "test commit")
	assert.Contains(t, err.Error(), "not a git repository")
}

func Test_Push_Success(t *testing.T) {
	rootRepoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(rootRepoDir)
	if err != nil {
		panic(err)
	}

	repoDir, err := Clone(rootRepoDir)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}

	err = SetAuthor(repoDir, "testuser", "testuser@example.com")
	if err != nil {
		panic(err)
	}

	err = Branch(repoDir, "test")
	if err != nil {
		panic(err)
	}

	err = Checkout(repoDir, "test")
	if err != nil {
		panic(err)
	}

	err = ioutil.WriteFile(filepath.Join(repoDir, "LICENSE"), []byte("test"), 0644)
	if err != nil {
		panic(err)
	}

	err = Add(repoDir, "LICENSE")
	if err != nil {
		panic(err)
	}

	err = Commit(repoDir, "test commit")
	if err != nil {
		panic(err)
	}

	err = Push(repoDir, "test")
	assert.Nil(t, err)
}

func Test_Push_Error(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}

	err = Push(repoDir, "test")
	assert.Contains(t, err.Error(), "src refspec test does not match any")
}

func Test_SetAuthor_Success(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}

	err = SetAuthor(repoDir, "testuser", "testuser@example.com")
	assert.Nil(t, err)
}

func Test_SetAuthor_Error(t *testing.T) {
	repoDir, _ := CloneFromGitHub(fixtureGitRepoInvalid, token)
	defer common.RemoveDir(repoDir)

	err := SetAuthor(repoDir, "testuser", "testuser@example.com")
	assert.Contains(t, err.Error(), "not in a git directory")
}

func Test_AnyModified_Clean(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}

	assert.False(t, AnyModified(repoDir, []config.File{
		{
			Source:      "",
			Destination: "LICENSE",
		},
	}))
}

func Test_AnyModified_Modified(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}

	err = ioutil.WriteFile(filepath.Join(repoDir, "CHANGELOG"), []byte("test"), 0644)
	if err != nil {
		panic(err)
	}

	assert.True(t, AnyModified(repoDir, []config.File{
		{
			Source:      "",
			Destination: "LICENSE",
		},
		{
			Source:      "",
			Destination: "CHANGELOG",
		},
	}))
}

func Test_Reset_Success(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}

	err = Reset(repoDir, "master")
	assert.NoError(t, err)
}

func Test_Reset_Invalid(t *testing.T) {
	repoDir, err := CloneFromGitHub(fixtureGitRepo, token)
	defer common.RemoveDir(repoDir)
	if err != nil {
		panic(err)
	}

	err = Reset(repoDir, "foo")
	assert.NoError(t, err)
}

func Test_Reset_Error(t *testing.T) {
	repoDir, _ := CloneFromGitHub(fixtureGitRepoInvalid, token)
	defer common.RemoveDir(repoDir)

	err := Reset(repoDir, "foo")
	assert.Contains(t, err.Error(), "not a git repository")
}
