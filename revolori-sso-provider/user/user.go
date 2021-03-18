// Package user defines the type for users and provides utility functions to manipulate users.
package user

import (
	"errors"
	"fmt"
)

// Data represents user data excluding the user's password.
type Data struct {
	FirstName    string              `json:"firstName"`
	LastName     string              `json:"lastName"`
	Email        string              `json:"email"`
	SecondaryIDs map[string][]string `json:"secondaryIDs"`
}

// User represents a user account.
type User struct {
	Data
	Password string `json:"password"`
}

// ErrUserNotFound is thrown in case a user account was not found.
var ErrUserNotFound = errors.New("user not found")

// VerifySignup verifies if the data of a user contains all required fields for signing up.
func (u User) VerifySignup() error {
	if u.FirstName == "" {
		return errors.New("empty first name")
	}
	if u.LastName == "" {
		return errors.New("empty last name")
	}
	if u.Password == "" {
		return errors.New("empty password")
	}
	if u.Email == "" {
		return errors.New("empty email")
	}
	if u.hasDuplicatedID() {
		return errors.New("the same secondary ID was provided at least twice")
	}
	return nil
}

// VerifyLogin verifies if the data of a user contains all required fields for logging in.
func (u User) VerifyLogin() error {
	if u.Password == "" {
		return errors.New("empty password")
	}
	if u.GetPrimaryID() == "" {
		return errors.New("empty user id")
	}
	return nil
}

// GetPrimaryID returns the primary ID of a user.
func (ud Data) GetPrimaryID() string {
	return ud.Email
}

// HasID returns true if the user data contains the given secondary ID as primary ID or a matching tool, secondary ID pair.
func (ud Data) HasID(key string, value string) bool {
	if value == ud.GetPrimaryID() {
		return true
	}
	return ud.HasSecondaryID(key, value)
}

// HasSecondaryID returns true if a user data contains the given secondary ID.
func (ud Data) HasSecondaryID(key string, value string) bool {
	if ids, ok := ud.SecondaryIDs[key]; ok {
		for _, id := range ids {
			if id == value {
				return true
			}
		}
	}
	return false
}

// hasDuplicatedID checks if a secondary ID is included twice within the user data.
func (ud Data) hasDuplicatedID() bool {
	for _, ids := range ud.SecondaryIDs {
		idMap := map[string]struct{}{}
		for _, id := range ids {
			idMap[id] = struct{}{}
		}
		if len(idMap) < len(ids) {
			return true
		}
	}
	return false
}

// MatchID maps the given key value pair of a secondary ID to a primary ID (email) of the appropriate user of users.
func MatchID(key string, value string, users []Data) (string, error) {
	for _, ud := range users {
		if ud.HasID(key, value) {
			return ud.GetPrimaryID(), nil
		}
	}
	return "", fmt.Errorf("ID '{%s : %s}' could not be matched to a user", key, value)
}
