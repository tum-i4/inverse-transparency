package test

import (
	"bytes"
	"encoding/json"
	"net/http"
	"os"
	"revolori/user"
	"sort"
	"testing"

	"github.com/stretchr/testify/assert"
)

// testCreateUser tests the function CreateUser in handlers.go
func testCreateUser(t *testing.T) {
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
		"#01_normalCreateUserRequest": {
			email:        "mm@example.com",
			firstName:    "Max",
			lastName:     "Mustermann",
			password:     "passwd",
			secondaryIDs: map[string][]string{"slack": {"mm1", "mm2"}},
			authUser:     "admin",
			authPassword: "password",
			wantedStatus: "201 Created"},
		"#02_withBlankField": {
			email:        "maria@molewsko.com",
			firstName:    "",
			lastName:     "Molewsko",
			password:     "passwd",
			secondaryIDs: map[string][]string{"gitlab": {"mariamolewsko1"}},
			authUser:     "admin",
			authPassword: "password",
			wantedStatus: "400 Bad Request"},
		"#03_withBlankSecondaryIDTool": {
			email:        "maria2@molewsko.com",
			firstName:    "Maria",
			lastName:     "Molewsko",
			password:     "passwd",
			secondaryIDs: map[string][]string{"gitlab": {"mariamolewsko2"}, "": {"mariamolewsko2"}},
			authUser:     "admin",
			authPassword: "password",
			wantedStatus: "400 Bad Request"},
		"#04_withBlankSecondaryID": {
			email:        "maria3@molewsko.com",
			firstName:    "Maria",
			lastName:     "Molewsko",
			password:     "passwd",
			secondaryIDs: map[string][]string{"gitlab": {""}},
			authUser:     "admin",
			authPassword: "password",
			wantedStatus: "400 Bad Request"},
		"#05_alreadyExistingMail": {
			email:        "mm@example.com",
			firstName:    "Maria",
			lastName:     "Molewsko",
			password:     "passwd",
			secondaryIDs: map[string][]string{"gitlab": {"mariamolewsko4"}},
			authUser:     "admin",
			authPassword: "password",
			wantedStatus: "409 Conflict"},
		"#06_alreadyExistingSecondaryID": {
			email:        "maria5@molewsko.com",
			firstName:    "Maria",
			lastName:     "Molewsko",
			password:     "passwd",
			secondaryIDs: map[string][]string{"slack": {"mm1"}},
			authUser:     "admin",
			authPassword: "password",
			wantedStatus: "400 Bad Request"},
		"#07_existingIDdifferentCapitalization": {
			email:        "mM@eXamPle.cOm",
			firstName:    "Max",
			lastName:     "Mustermann",
			password:     "passwd",
			secondaryIDs: map[string][]string{"slack": {"mm3"}},
			authUser:     "admin",
			authPassword: "password",
			wantedStatus: "409 Conflict"},
		"#08_falseAuthentication": {
			email:        "maria6@molewsko.com",
			firstName:    "Maria",
			lastName:     "Molewsko",
			password:     "passwd",
			secondaryIDs: map[string][]string{"gitlab": {"mariamolewsko7"}},
			authUser:     "admin",
			authPassword: "wrong",
			wantedStatus: "401 Unauthorized"},
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
			Email:        tc.email,
			FirstName:    tc.firstName,
			LastName:     tc.lastName,
			SecondaryIDs: tc.secondaryIDs}

		user := &user.User{
			Data:     data,
			Password: tc.password}

		json.NewEncoder(buf).Encode(user)
		req, err := http.NewRequest("POST", os.Getenv("HOST")+":"+os.Getenv("PORT")+"/user", buf)
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
		})
	}
}
