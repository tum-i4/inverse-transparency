package test

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"revolori/user"
	"sort"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

// TestGetUser tests the function GetUser in handlers.go
func testGetUser(t *testing.T) {
	tests := map[string]struct {
		email              string
		wantedFirstName    string
		wantedLastName     string
		wantedSecondaryIDs map[string][]string
		authUser           string
		authPassword       string
		wantedStatus       string
	}{
		"#01_normalGetUserRequest": {
			email:              "mm@example.com",
			wantedFirstName:    "Max",
			wantedLastName:     "Mustermann",
			wantedSecondaryIDs: map[string][]string{"slack": {"mm1", "mm2"}},
			authUser:           "admin",
			authPassword:       "password",
			wantedStatus:       "200 OK"},
		"#02_falseCredentials": {
			email:              "mm@example.com",
			wantedFirstName:    "Max",
			wantedLastName:     "Mustermann",
			wantedSecondaryIDs: map[string][]string{"slack": {"mm1", "mm2"}},
			authUser:           "admin",
			authPassword:       "wrong",
			wantedStatus:       "401 Unauthorized"},
		"#03_inexistingID": {
			email:              "inexistence@example.com",
			wantedFirstName:    "Max",
			wantedLastName:     "Mustermann",
			wantedSecondaryIDs: map[string][]string{"slack": {"mm1", "mm2"}},
			authUser:           "admin",
			authPassword:       "password",
			wantedStatus:       "400 Bad Request"},
		"#04_existingIDdifferentCapitalization": {
			email:              "mM@exaMple.com",
			wantedFirstName:    "Max",
			wantedLastName:     "Mustermann",
			wantedSecondaryIDs: map[string][]string{"slack": {"mm1", "mm2"}},
			authUser:           "admin",
			authPassword:       "password",
			wantedStatus:       "200 OK"},
	}

	client := &http.Client{}
	var testNames []string
	for testName := range tests {
		testNames = append(testNames, testName)
	}
	sort.Strings(testNames)
	for _, name := range testNames {
		tc := tests[name]
		wantedData := user.Data{
			Email:        tc.email,
			FirstName:    tc.wantedFirstName,
			LastName:     tc.wantedLastName,
			SecondaryIDs: tc.wantedSecondaryIDs}

		req, err := http.NewRequest("GET", fmt.Sprintf("%s:%s/user/%s", os.Getenv("HOST"), os.Getenv("PORT"), tc.email), nil)
		if err != nil {
			t.Fail()
		}

		req.SetBasicAuth(tc.authUser, tc.authPassword)
		res, err := client.Do(req)
		if err != nil {
			t.Fail()
		}

		t.Run(name, func(t *testing.T) {
			assert.Equal(t, tc.wantedStatus, res.Status)

			if !strings.HasPrefix(tc.wantedStatus, "2") {
				return
			}
			defer res.Body.Close()
			body, err := ioutil.ReadAll(res.Body)
			if err != nil {
				t.Fail()
			}

			actualData := user.Data{}
			jsonErr := json.Unmarshal(body, &actualData)
			if jsonErr != nil {
				t.Fail()
			}
			wantedData.Email = strings.ToLower(wantedData.Email)

			assert.Equal(t, wantedData, actualData)
		})
	}
}
