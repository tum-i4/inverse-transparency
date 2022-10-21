package test

import (
	"bytes"
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

// testUpdateUser tests the function UpdateUser in handlers.go
func testUpdateUser(t *testing.T) {
	tests := map[string]struct {
		email        string
		firstName    string
		lastName     string
		password     string
		secondaryIDs map[string][]string
		authUser     string
		authPassword string
		wantedStatus string
	}{
		"#01_normalUpdateUserRequest": {
			email:        "mm@example.com",
			firstName:    "Changed_Max",
			lastName:     "Changed_Mustermann",
			password:     "passwd",
			secondaryIDs: map[string][]string{"slack": {"changed_mm1", "changed_mm2"}},
			authUser:     "admin",
			authPassword: "password",
			wantedStatus: "201 Created"},
		"#02_falseCredentials": {
			email:        "mm@example.com",
			firstName:    "Max",
			lastName:     "Mustermann",
			password:     "passwd",
			secondaryIDs: map[string][]string{"slack": {"mm1", "mm2"}},
			authUser:     "admin",
			authPassword: "wrong",
			wantedStatus: "401 Unauthorized"},
		"#03_inexistingID": {
			email:        "inexistence@example.com",
			firstName:    "Max",
			lastName:     "Mustermann",
			password:     "passwd",
			secondaryIDs: map[string][]string{"slack": {"mm1", "mm2"}},
			authUser:     "admin",
			authPassword: "password",
			wantedStatus: "400 Bad Request"},
		"#04_existingIDdifferentCapitalization": {
			email:        "mM@exaMple.com",
			firstName:    "Max",
			lastName:     "Mustermann",
			password:     "passwd",
			secondaryIDs: map[string][]string{"slack": {"mm1", "mm2"}},
			authUser:     "admin",
			authPassword: "password",
			wantedStatus: "201 Created"},
	}

	client := &http.Client{}
	var testNames []string
	for testName := range tests {
		testNames = append(testNames, testName)
	}
	sort.Strings(testNames)
	for _, name := range testNames {
		tc := tests[name]
		buf := new(bytes.Buffer)
		sentData := user.Data{
			Email:        tc.email,
			FirstName:    tc.firstName,
			LastName:     tc.lastName,
			SecondaryIDs: tc.secondaryIDs}
		sendUser := user.User{
			Data:     sentData,
			Password: tc.password,
		}
		json.NewEncoder(buf).Encode(sendUser)
		req, err := http.NewRequest("PUT", fmt.Sprintf("%s:%s/user/%s", os.Getenv("HOST"), os.Getenv("PORT"), tc.email), buf)
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

			// Check if the server is giving back the updated User data
			req, err := http.NewRequest("GET", fmt.Sprintf("%s:%s/user/%s", os.Getenv("HOST"), os.Getenv("PORT"), tc.email), nil)
			if err != nil {
				t.Fail()
			}

			req.SetBasicAuth(tc.authUser, tc.authPassword)
			res, err := client.Do(req)
			if err != nil {
				t.Fail()
			}

			defer res.Body.Close()
			body, err := ioutil.ReadAll(res.Body)
			if err != nil {
				t.Fail()
			}

			returnedData := user.Data{}
			jsonErr := json.Unmarshal(body, &returnedData)
			if jsonErr != nil {
				t.Fail()
			}
			sentData.Email = strings.ToLower(sentData.Email)

			assert.Equal(t, sentData, returnedData)
		})
	}
}
