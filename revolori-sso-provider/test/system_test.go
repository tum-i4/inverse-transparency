package test

import (
	"net/http"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

// testsHealth tests the function health in handlers.go and sees if the server is running
func testHealth(t *testing.T) {
	res, err := http.Get(os.Getenv("HOST") + ":" + os.Getenv("PORT") + "/health")
	if err != nil {
		t.Errorf(err.Error())
	}
	assert.Equal(t, "200 OK", res.Status)
}

// TestMain runs all other tests in the correct sequence
func TestMain(t *testing.T) {
	t.Run("01_Health", testHealth)
	t.Run("02_CreateUser", testCreateUser)
	t.Run("03_Login", testLogin)
	t.Run("04_GetUser", testGetUser)
	t.Run("05_GetAllUsers", testGetAllUsers)
	t.Run("06_UpdateUser", testUpdateUser)
	t.Run("07_DeleteUser", testDeleteUser)
}
