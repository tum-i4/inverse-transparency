package test

import (
	"encoding/json"
	"io/ioutil"
	"net/http"
	"os"
	"revolori/user"
	"testing"

	"github.com/stretchr/testify/assert"
)

// testGetAllUsers tests the function GetAllUsers in handlers.go
func testGetAllUsers(t *testing.T) {
	wantedData := []user.Data{
		{
			FirstName:    "Max",
			LastName:     "Mustermann",
			Email:        "mm@example.com",
			SecondaryIDs: map[string][]string{"slack": {"mm1", "mm2"}},
		},
	}

	client := &http.Client{}
	req, err := http.NewRequest("GET", os.Getenv("HOST")+":"+os.Getenv("PORT")+"/user", nil)
	if err != nil {
		t.Fail()
	}

	req.SetBasicAuth("admin", "password")
	res, err := client.Do(req)
	if err != nil {
		t.Fail()
	}

	assert.Equal(t, "200 OK", res.Status)

	defer res.Body.Close()
	body, err := ioutil.ReadAll(res.Body)
	if err != nil {
		t.Fail()
	}

	actualData := []user.Data{}
	jsonErr := json.Unmarshal(body, &actualData)
	if jsonErr != nil {
		t.Fail()
	}

	assert.Equal(t, wantedData, actualData)
}
