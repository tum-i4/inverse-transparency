package test

import (
	"bytes"
	"encoding/json"
	"io/ioutil"
	"net/http"
	"os"
	"revolori/auth"
	"revolori/user"
	"sort"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

// testLogin tests the function Login in handlers.go
func testLogin(t *testing.T) {
	tests := map[string]struct {
		email        string
		password     string
		wantedStatus string
	}{
		"#01_normalLogin": {
			email:        "mm@example.com",
			password:     "passwd",
			wantedStatus: "200 OK",
		},
		"#02_withBlankEmail": {
			email:        "",
			password:     "passwd",
			wantedStatus: "400 Bad Request",
		},
		"#03_withBlankPassword": {
			email:        "mm@example.com",
			password:     "",
			wantedStatus: "400 Bad Request",
		},
		"#04_withDifferentCapitalization": {
			email:        "mM@exaMple.com",
			password:     "passwd",
			wantedStatus: "200 OK",
		},
		"#05_wrongPassword": {
			email:        "mm@example.com",
			password:     "wrong",
			wantedStatus: "401 Unauthorized",
		},
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
		data := user.Data{
			Email: tc.email,
		}

		user := &user.User{
			Data:     data,
			Password: tc.password}

		json.NewEncoder(buf).Encode(user)
		req, err := http.NewRequest("POST", os.Getenv("HOST")+":"+os.Getenv("PORT")+"/login", buf)
		if err != nil {
			t.Fail()
		}

		res, err := client.Do(req)
		if err != nil {
			t.Fail()
		}

		t.Run(name, func(t *testing.T) {
			assert.Equal(t, tc.wantedStatus, res.Status)
			//check if a refresh cookie is set
			if !strings.HasPrefix(tc.wantedStatus, "2") {
				return
			}
			// TODO: Add a real JWT validation
			assert.NotEqual(t, "", res.Cookies()[0].Value)

			// very simple check to see if an auth token has been successfully sent back
			defer res.Body.Close()
			body, err := ioutil.ReadAll(res.Body)
			if err != nil {
				t.Fail()
			}

			token := auth.Token{}
			jsonErr := json.Unmarshal(body, &token)
			if jsonErr != nil {
				t.Fail()
			}

			//check if token isn't blank
			assert.NotEqual(t, "", token.Token)
		})
	}
}
