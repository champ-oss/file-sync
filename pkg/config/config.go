package config

import (
	log "github.com/sirupsen/logrus"
	"os"
	"strings"
)

type File struct {
	Source      string
	Destination string
}

func GetWorkspace() string {
	value := getEnvRequired("GITHUB_WORKSPACE")
	log.Debugf("github workspace: %s", value)
	return value
}

func GetToken() string {
	return getEnvOptional("INPUT_TOKEN")
}

func GetSourceRepo() string {
	value := getEnvRequired("INPUT_REPO")
	log.Debugf("source repo: %s", value)
	return value
}

func GetOwnerName() string {
	value := getEnvRequired("GITHUB_REPOSITORY_OWNER")
	log.Debugf("owner: %s", value)
	return value
}

func GetTargetBranch() string {
	value := getEnvRequired("INPUT_TARGET_BRANCH")
	log.Debugf("target branch: %s", value)
	return value
}

func GetPullRequestBranch() string {
	value := getEnvRequired("INPUT_PULL_REQUEST_BRANCH")
	log.Debugf("pull request branch: %s", value)
	return value
}

func GetUser() string {
	value := getEnvRequired("INPUT_USER")
	log.Debugf("user: %s", value)
	return value
}

func GetEmail() string {
	value := getEnvRequired("INPUT_EMAIL")
	log.Debugf("email: %s", value)
	return value
}

func GetCommitMessage() string {
	value := getEnvRequired("INPUT_COMMIT_MESSAGE")
	log.Debugf("commit message: %s", value)
	return value
}

func GetRepoName() string {
	key := "GITHUB_REPOSITORY"
	ownerRepo := getEnvRequired(key)
	parts := strings.Split(ownerRepo, "/")
	if len(parts) != 2 {
		log.Fatalf("%s is in unexpected format: %s", key, ownerRepo)
	}
	log.Debugf("repo name: %s", parts[1])
	return parts[1]
}

// GetFiles parses the list of files from environment variable.
// Files should be specified one per line, optionally with an equal sign separating source and destination
func GetFiles() []File {
	value := getEnvRequired("INPUT_FILES")
	var files []File

	for _, f := range strings.Split(value, "\n") {
		if strings.TrimSpace(f) == "" {
			continue
		}
		if strings.Contains(f, "=") {
			files = append(files, File{
				Source:      strings.Split(strings.TrimSpace(f), "=")[0],
				Destination: strings.Split(strings.TrimSpace(f), "=")[1],
			})
		} else {
			files = append(files, File{
				Source:      strings.TrimSpace(f),
				Destination: strings.TrimSpace(f),
			})
		}
	}
	log.Debugf("files: %s", files)
	return files
}

func getEnvRequired(key string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	log.Fatalf("env variable %s is empty", key)
	return ""
}

func getEnvOptional(key string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	log.Warningf("env variable %s is empty", key)
	return ""
}
