package common

import (
	"bytes"
	"fmt"
	"github.com/champ-oss/file-sync/pkg/config"
	log "github.com/sirupsen/logrus"
	"os"
	"os/exec"
	"path/filepath"
)

func RemoveDir(dir string) {
	if err := os.RemoveAll(dir); err != nil {
		log.Error(err)
	}
}

func CopySourceFiles(files []config.File, sourceDir, destDir string) error {
	for _, f := range files {
		sourcePath := filepath.Join(sourceDir, f.Source)
		destPath := filepath.Join(destDir, f.Destination)
		log.Debugf("Copying %s to %s", sourcePath, destPath)
		if err := CopyFile(sourcePath, destPath); err != nil {
			log.Errorf("error copying file %s from source: %s", sourcePath, err.Error())
		}
	}
	return nil
}

func CopyFile(source, dest string) error {
	input, err := os.ReadFile(source)
	if err != nil {
		return err
	}

	if baseDir, _ := filepath.Split(dest); baseDir != "" {
		if err := os.MkdirAll(baseDir, os.ModePerm); err != nil {
			return err
		}
	}

	err = os.WriteFile(dest, input, 0644)
	return err
}

func RunCommand(dir, cmd string, args ...string) (output string, err error) {
	LogCommand(cmd, args...)
	command := exec.Command(cmd, args...)

	var stdout bytes.Buffer
	command.Stdout = &stdout
	var stderr bytes.Buffer
	command.Stderr = &stderr
	command.Dir = dir

	err = command.Run()
	LogOutput(stdout)
	LogOutput(stderr)

	if err != nil {
		return stderr.String(), err
	}
	return stdout.String(), nil
}

func RunCommandNoLog(dir, cmd string, args ...string) error {
	command := exec.Command(cmd, args...)
	command.Dir = dir

	err := command.Run()

	if err != nil {
		return fmt.Errorf("error running command")
	}
	return nil
}

func LogCommand(cmd string, args ...string) {
	logMessage := cmd
	for _, a := range args {
		logMessage += " " + a
	}
	log.Info(logMessage)
}

func LogOutput(output bytes.Buffer) {
	if output.String() == "" {
		return
	}
	fmt.Print(output.String())
}

func RemoveFile(name string) error {
	if err := os.Remove(name); err != nil {
		return err
	}
	return nil
}

func RemoveFiles(files []config.File, workingDir string) error {
	for _, f := range files {
		filePath := filepath.Join(workingDir, f.Destination)
		log.Debugf("Removing %s", filePath)
		if err := RemoveFile(filePath); err != nil {
			log.Errorf("error removing file %s: %s", filePath, err.Error())
		}
	}
	return nil
}
