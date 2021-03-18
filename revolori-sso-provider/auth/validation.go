package auth

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"revolori/store"
	"revolori/user"
	"strings"
)

type invalidRequestBody struct {
	status int
	msg    string
}

func (ir *invalidRequestBody) Error() string {
	return ir.msg
}

// decodeJSON decodes a request body and handles errors related to malformed JSON.
func decodeJSON(w http.ResponseWriter, r *http.Request, dst interface{}) error {
	r.Body = http.MaxBytesReader(w, r.Body, 1048576)

	dec := json.NewDecoder(r.Body)
	dec.DisallowUnknownFields()

	err := dec.Decode(&dst)
	if err != nil {
		var syntaxError *json.SyntaxError
		var unmarshalTypeError *json.UnmarshalTypeError

		switch {
		case errors.As(err, &syntaxError):
			msg := fmt.Sprintf("request body contains invalid JSON at position %d", syntaxError.Offset)
			return &invalidRequestBody{status: http.StatusBadRequest, msg: msg}

		case errors.Is(err, io.ErrUnexpectedEOF):
			msg := fmt.Sprintf("request body contains invalid JSON")
			return &invalidRequestBody{status: http.StatusBadRequest, msg: msg}

		case errors.As(err, &unmarshalTypeError):
			msg := fmt.Sprintf("request body contains an invalid value for the %q field at position %d", unmarshalTypeError.Field, unmarshalTypeError.Offset)
			return &invalidRequestBody{status: http.StatusBadRequest, msg: msg}

		case errors.Is(err, io.EOF):
			msg := "request body cannot be empty"
			return &invalidRequestBody{status: http.StatusBadRequest, msg: msg}

		case err.Error() == "http: request body too large":
			msg := "request body is larger than maximum size of 1MB"
			return &invalidRequestBody{status: http.StatusRequestEntityTooLarge, msg: msg}

		case strings.HasPrefix(err.Error(), "json: unknown field "):
			fieldName := strings.TrimPrefix(err.Error(), "json: unknown field ")
			msg := fmt.Sprintf("request body contains unknown field %s", fieldName)
			return &invalidRequestBody{status: http.StatusBadRequest, msg: msg}

		default:
			return err
		}
	}

	err = dec.Decode(&struct{}{})
	if err != io.EOF {
		msg := "only one JSON object is allowed in the request body"
		return &invalidRequestBody{status: http.StatusBadRequest, msg: msg}
	}

	return nil
}

// userExists returns whether a given user already exists based on the primary ID of the user.
func (ac Controller) userExists(u user.User) (bool, error) {
	_, err := ac.vault.GetUser(u.Email)
	if err == nil {
		return true, nil
	}
	if err != user.ErrUserNotFound {
		return false, err
	}
	return false, nil
}

// secondaryIDExists returns whether any secondary ID of the given user already exists.
func (ac Controller) secondaryIDExists(u user.User) (bool, string, error) {
	users, err := ac.vault.GetAllUserData()
	switch {
	case err == store.ErrNoSecrets:
		return false, "", nil
	case err != nil:
		return false, "", err
	}
	for _, storedUser := range users {
		if storedUser.GetPrimaryID() == u.GetPrimaryID() {
			continue
		}
		for tool, ids := range u.Data.SecondaryIDs {
			for _, id := range ids {
				if storedUser.HasSecondaryID(tool, id) {
					return true, fmt.Sprintf("Tool: %s | ID: %s", tool, id), nil
				}
			}
		}

	}
	return false, "", nil
}
