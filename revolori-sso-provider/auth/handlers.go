// Package auth implements functionality for user authentication.
package auth

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
	"revolori/store"
	"revolori/user"
	"time"

	"github.com/julienschmidt/httprouter"
	"golang.org/x/crypto/bcrypt"
)

const validityDurationAuth = 10 * time.Minute
const validityDurationRefresh = 7 * 24 * time.Hour

// Controller contains functionality for user authentication.
type Controller struct {
	logger  *log.Logger
	vault   *store.Client
	devMode bool
}

// New creates a new controller for user authentication.
func New(logger *log.Logger, vault *store.Client, devMode bool) *Controller {
	return &Controller{
		logger,
		vault,
		devMode,
	}
}

// CreateUser handles POST requests to the route '/user' and creates a new user based on the data
// sent in the request body.
func (ac Controller) CreateUser(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
	var transmittedUser user.User

	if err := decodeJSON(w, r, &transmittedUser); err != nil {
		var ir *invalidRequestBody
		if errors.As(err, &ir) {
			ac.logAndReturnMessage(w, ir.msg, ir.status)
		} else {
			ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	if err := transmittedUser.VerifySignup(); err != nil {
		ac.logAndReturnMessage(w, err.Error(), http.StatusBadRequest)
		return
	}

	exists, err := ac.userExists(transmittedUser)
	if err != nil {
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}
	if exists {
		ac.logAndReturnMessage(w, "user with given ID already exists", http.StatusBadRequest)
		return
	}

	duplicatedSecondaryID, id, err := ac.secondaryIDExists(transmittedUser)
	if err != nil {
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}
	if duplicatedSecondaryID {
		logMsg := fmt.Sprintf("user with secondary ID (%s) already exists", id)
		ac.logAndReturnMessage(w, logMsg, http.StatusBadRequest)
		return
	}

	storedUser, err := hashPassword(transmittedUser)
	if err != nil {
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if err := ac.vault.CreateUser(storedUser); err != nil {
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

// GetAllUsers handles GET requests to the route 'user' and returns the data of all available users.
func (ac Controller) GetAllUsers(w http.ResponseWriter, _ *http.Request, _ httprouter.Params) {
	users, err := ac.vault.GetAllUserData()
	switch {
	case err == store.ErrNoSecrets:
		users = []user.Data{}
	case err != nil:
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(users); err != nil {
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

// GetUser handles GET requests to the route 'user/:id' and returns the user specified by the id.
func (ac Controller) GetUser(w http.ResponseWriter, _ *http.Request, p httprouter.Params) {
	id := p.ByName("id")
	ud, err := ac.vault.GetUserData(id)
	switch {
	case err == user.ErrUserNotFound:
		ac.logAndReturnMessage(w, err.Error(), http.StatusBadRequest)
		return
	case err != nil:
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(ud); err != nil {
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

// UpdateUser handles PUT requests to the route 'user/:id' and updates the specified user based on the data
// sent in the request body.
func (ac Controller) UpdateUser(w http.ResponseWriter, r *http.Request, p httprouter.Params) {
	var newUser user.User

	if err := decodeJSON(w, r, &newUser); err != nil {
		var ir *invalidRequestBody
		if errors.As(err, &ir) {
			ac.logAndReturnMessage(w, ir.msg, ir.status)
		} else {
			ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	id := p.ByName("id")
	if id != newUser.GetPrimaryID() {
		ac.logAndReturnMessage(w, "provided IDs don't match", http.StatusBadRequest)
		return
	}

	if err := newUser.VerifySignup(); err != nil {
		ac.logAndReturnMessage(w, err.Error(), http.StatusBadRequest)
		return
	}

	duplicatedSecondaryID, duplicatedID, err := ac.secondaryIDExists(newUser)
	if err != nil {
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}
	if duplicatedSecondaryID {
		logMsg := fmt.Sprintf("user with secondary ID (%s) already exists", duplicatedID)
		ac.logAndReturnMessage(w, logMsg, http.StatusBadRequest)
		return
	}

	newUser, err = hashPassword(newUser)
	if err != nil {
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}

	switch err = ac.vault.UpdateUser(id, newUser); {
	case err == user.ErrUserNotFound:
		ac.logAndReturnMessage(w, err.Error(), http.StatusBadRequest)
		return
	case err != nil:
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

// DeleteUser handles DELETE requests to the route '/user' and deletes the specified user if it exists.
func (ac Controller) DeleteUser(w http.ResponseWriter, _ *http.Request, p httprouter.Params) {
	id := p.ByName("id")
	if err := ac.vault.DeleteUser(id); err != nil {
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

// Login handles POST requests to the route '/login' and issues an access token (short TTL) and a refresh token
// (long TTL) if the user data provided in the request body is valid. The access token is returned to the client
// in JSON format. The refresh token is set as an HTTP only cookie. Login also cleans up expired refresh tokens on
// the whitelist.
func (ac Controller) Login(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
	var transmittedUser user.User

	if err := decodeJSON(w, r, &transmittedUser); err != nil {
		var ir *invalidRequestBody
		if errors.As(err, &ir) {
			ac.logAndReturnMessage(w, ir.msg, ir.status)
		} else {
			ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	if err := transmittedUser.VerifyLogin(); err != nil {
		ac.logAndReturnMessage(w, err.Error(), http.StatusBadRequest)
		return
	}

	errorInvalidCredentials := "the entered credentials are invalid"
	passwordPlain := transmittedUser.Password
	storedUser, err := ac.vault.GetUser(transmittedUser.Email)
	if err != nil {
		if err == user.ErrUserNotFound {
			ac.logger.Println(err.Error())
			http.Error(w, errorInvalidCredentials, http.StatusBadRequest)
			return
		}
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = bcrypt.CompareHashAndPassword([]byte(storedUser.Password), []byte(passwordPlain))
	if err != nil {
		ac.logger.Println(err.Error())
		http.Error(w, errorInvalidCredentials, http.StatusBadRequest)
		return
	}
	storedUser.Password = ""

	expirationTimeRefresh := time.Now().Add(validityDurationRefresh)
	if err = ac.createRefreshTokenAndSetCookie(w, storedUser.Email, expirationTimeRefresh); err != nil {
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}

	expirationTimeAuth := time.Now().Add(validityDurationAuth)
	if err = ac.createAndSendAuthToken(w, storedUser.Email, expirationTimeAuth); err != nil {
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}

	go func() {
		if err = ac.vault.DeleteExpiredWhitelistEntries(); err != nil {
			ac.logger.Println(err.Error())
		}
	}()
}

// Logout handles DELETE requests to the route '/login' and logs out users by removing the cookie that contains the refresh token
// and the whitelist entry of said token. Alternatively, all whitelisted refresh tokens of the requesting user can be deleted by
// setting 'all=true' as a query parameter. The auth token needs to be removed by the client.
func (ac Controller) Logout(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
	params, ok := r.URL.Query()["all"]
	var all string
	if ok && len(params) == 1 {
		all = params[0]
	}
	if all == "true" {
		id, status, err := ac.validateRefreshToken(r)
		if err != nil {
			ac.logAndReturnStatus(w, err.Error(), status)
			return
		}
		if err = ac.vault.DeleteUsersWhitelistEntries(id); err != nil {
			ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
			return
		}
	} else {
		c, err := r.Cookie("token")
		if err != nil {
			if err == http.ErrNoCookie {
				ac.logAndReturnMessage(w, err.Error(), http.StatusBadRequest)
				return
			}
			ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
			return
		}
		if err = ac.vault.DeleteWhitelistEntry(c.Value); err != nil {
			ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "token",
		MaxAge:   -1,
		HttpOnly: true,
	})

	w.WriteHeader(http.StatusOK)
}

// Refresh handles GET requests to the route '/refresh' and returns a new auth token in case of an authenticated request.
// For a request to be authenticated, a valid refresh token must be provided in a cookie named 'token'.
func (ac Controller) Refresh(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
	id, status, err := ac.validateRefreshToken(r)
	if err != nil {
		ac.logAndReturnStatus(w, err.Error(), status)
		return
	}
	expirationTimeAuth := time.Now().Add(validityDurationAuth)
	if err = ac.createAndSendAuthToken(w, id, expirationTimeAuth); err != nil {
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

// GetID handles GET requests to the route '/id' and returns a matching of provided secondary IDs to a user's primary ID.
func (ac Controller) GetID(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
	var receivedIDs map[string][]string
	if err := decodeJSON(w, r, &receivedIDs); err != nil {
		var ir *invalidRequestBody
		if errors.As(err, &ir) {
			ac.logAndReturnMessage(w, ir.msg, ir.status)
		} else {
			ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	users, err := ac.vault.GetAllUserData()
	if err != nil {
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}

	var primaryIDs = make(map[string]map[string]string)
	for tool, secondaryIDs := range receivedIDs {
		primaryIDs[tool] = map[string]string{}
		for _, secondaryID := range secondaryIDs {
			primaryID, err := user.MatchID(tool, secondaryID, users)
			if err != nil {
				ac.logAndReturnMessage(w, err.Error(), http.StatusBadRequest)
				return
			}
			primaryIDs[tool][secondaryID] = primaryID
		}
	}

	w.Header().Set("Content-Type", "application/json")
	if err = json.NewEncoder(w).Encode(primaryIDs); err != nil {
		ac.logAndReturnStatus(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

// CheckHealth handles GET requests to the route '/health' and returns HTTP status ok if the server is running.
func (ac Controller) CheckHealth(w http.ResponseWriter, _ *http.Request, _ httprouter.Params) {
	w.WriteHeader(http.StatusOK)
}

// hashPassword hashes a users password and returns the user with hashed password field.
func hashPassword(u user.User) (user.User, error) {
	hash, err := bcrypt.GenerateFromPassword([]byte(u.Password), bcrypt.DefaultCost)
	if err != nil {
		return user.User{}, err
	}
	u.Password = string(hash)
	return u, nil
}

// logAndReturnStatus logs the error to the logger attached to the Controller and returns an HTTP status code.
func (ac Controller) logAndReturnStatus(w http.ResponseWriter, msg string, status int) {
	ac.logger.Println(msg)
	w.WriteHeader(status)
}

// logAndReturnMessage logs the error to the logger attached to the Controller and returns an HTTP
// status code and a response message.
func (ac Controller) logAndReturnMessage(w http.ResponseWriter, msg string, status int) {
	ac.logger.Println(msg)
	http.Error(w, msg, status)
}
