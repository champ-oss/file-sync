package common

import (
	"bytes"
	"github.com/champ-oss/file-sync/pkg/config"
	"github.com/stretchr/testify/assert"
	"os"
	"path/filepath"
	"testing"
)

func Test_RemoveDir(t *testing.T) {
	dir, _ := os.MkdirTemp("", "test")
	assert.NotPanics(t, func() {
		RemoveDir(dir)
	})
}

func Test_copyFile_Success(t *testing.T) {
	// Write a test file to a test source directory
	sourceDir, _ := os.MkdirTemp("", "source")
	defer RemoveDir(sourceDir)
	sourceFile := filepath.Join(sourceDir, "test.txt")
	err := os.WriteFile(sourceFile, []byte("test"), 0644)
	assert.NoError(t, err)

	// Copy file and check if it exists in destination
	assert.NoError(t, CopyFile(sourceFile, "test.txt"))
	defer os.Remove("test.txt")
	_, err = os.Stat("test.txt")
	assert.NoError(t, err)
}

func Test_copyFile_Bad_Source(t *testing.T) {
	assert.Error(t, CopyFile("/foo/invalid.txt", "/foo/invalid.txt"))
}

func Test_copyFile_Bad_Destination(t *testing.T) {
	// Write a test file to a test source directory
	sourceDir, _ := os.MkdirTemp("", "source")
	defer RemoveDir(sourceDir)
	sourceFile := filepath.Join(sourceDir, "test.txt")
	err := os.WriteFile(sourceFile, []byte("test"), 0644)
	assert.NoError(t, err)
	_, err = os.Stat(sourceFile)
	assert.NoError(t, err)

	// Assert an error when copying to a bad destination
	assert.Error(t, CopyFile(sourceFile, "/foo/invalid.txt"))
}

func Test_copyFile_Create_Dir(t *testing.T) {
	// Write a test file to a test source directory
	sourceDir, _ := os.MkdirTemp("", "source")
	defer RemoveDir(sourceDir)
	sourceFile := filepath.Join(sourceDir, "test.txt")
	err := os.WriteFile(sourceFile, []byte("test"), 0644)
	assert.NoError(t, err)
	_, err = os.Stat(sourceFile)
	assert.NoError(t, err)

	// Create a test destination directory
	destDir, _ := os.MkdirTemp("", "dest")
	defer RemoveDir(sourceDir)

	// Use a nested directory that does not exist
	destFile := filepath.Join(destDir, "somedirectory", "test.txt")
	// Copy file and check if it exists in destination
	assert.NoError(t, CopyFile(sourceFile, destFile))
	_, err = os.Stat(destFile)
	assert.NoError(t, err)
}

func Test_copySourceFiles_Success(t *testing.T) {
	// Write a test file to a test source directory
	sourceDir, _ := os.MkdirTemp("", "source")
	defer RemoveDir(sourceDir)
	sourceFile := filepath.Join(sourceDir, "test.txt")
	err := os.WriteFile(sourceFile, []byte("test"), 0644)
	assert.NoError(t, err)
	_, err = os.Stat(sourceFile)
	assert.NoError(t, err)

	// Create a test destination directory
	destDir, _ := os.MkdirTemp("", "dest")
	defer RemoveDir(sourceDir)

	assert.NoError(t, CopySourceFiles([]config.File{
		{
			Source:      "test.txt",
			Destination: "test1/test2/test.txt",
		},
	}, sourceDir, destDir))
}

func Test_copySourceFiles_Error(t *testing.T) {
	assert.Error(t, CopySourceFiles([]config.File{
		{
			Source:      "foo.txt",
			Destination: "test1/test2/foo.txt",
		},
	}, "/foo", "/foo"))
}

func Test_RunCommand_Success(t *testing.T) {
	dir, _ := os.MkdirTemp("", "test")
	output, err := RunCommand(dir, "echo", "foo")
	assert.Contains(t, output, "foo")
	assert.NoError(t, err)
}

func Test_RunCommand_Error(t *testing.T) {
	dir, _ := os.MkdirTemp("", "test")
	output, err := RunCommand(dir, "foo", "foo")
	assert.Contains(t, output, "")
	assert.Error(t, err)
}

func Test_RunCommandNoLog_Success(t *testing.T) {
	dir, _ := os.MkdirTemp("", "test")
	err := RunCommandNoLog(dir, "echo", "foo")
	assert.NoError(t, err)
}

func Test_RunCommandNoLog_Error(t *testing.T) {
	dir, _ := os.MkdirTemp("", "test")
	err := RunCommandNoLog(dir, "foo", "foo")
	assert.Error(t, err)
}

func Test_LogCommand(t *testing.T) {
	assert.NotPanics(t, func() {
		LogCommand("cd", "foo")
	})
}

func Test_LogOutput(t *testing.T) {
	var test bytes.Buffer
	test.Write([]byte("test\n"))

	assert.NotPanics(t, func() {
		LogOutput(test)
	})
}

func Test_LogOutput_Empty(t *testing.T) {
	var test bytes.Buffer
	test.Write([]byte(""))

	assert.NotPanics(t, func() {
		LogOutput(test)
	})
}
