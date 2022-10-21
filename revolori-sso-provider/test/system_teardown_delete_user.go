package test

import (
	"fmt"
	"net/http"
	"os"
	"sort"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

// testDeleteUser tests the function DeleteUser in handlers.go
func testDeleteUser(t *testing.T) {
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
		"#01_normalDeleteUserRequest": {
			email:        "mm@example.com",
			authUser:     "admin",
			authPassword: "password",
			wantedStatus: "204 No Content"},
		"#02_falseCredentials": {
			email:        "mm@example.com",
			authUser:     "admin",
			authPassword: "wrong",
			wantedStatus: "401 Unauthorized"},
		"#03_existingIDdifferentCapitalization": {
			email:        "mM@eXamPle.cOm",
			authUser:     "admin",
			authPassword: "password",
			wantedStatus: "204 No Content"},
	}

	client := &http.Client{}
	var testNames []string
	for testName := range tests {
		testNames = append(testNames, testName)
	}
	sort.Strings(testNames)
	for _, name := range testNames {
		tc := tests[name]

		req, err := http.NewRequest("DELETE", fmt.Sprintf("%s:%s/user/%s", os.Getenv("HOST"), os.Getenv("PORT"), tc.email), nil)
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

			// Check if the server is giving back 400 Bad Request on GET
			req, err := http.NewRequest("GET", fmt.Sprintf("%s:%s/user/%s", os.Getenv("HOST"), os.Getenv("PORT"), tc.email), nil)
			if err != nil {
				t.Fail()
			}

			req.SetBasicAuth(tc.authUser, tc.authPassword)
			res, err := client.Do(req)
			if err != nil {
				t.Fail()
			}

			assert.Equal(t, "400 Bad Request", res.Status)
		})
	}
}
