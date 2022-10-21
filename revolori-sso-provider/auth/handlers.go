// Package auth implements functionality for user authentication.
package auth

import (
	"crypto/rsa"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"reflect"
	"revolori/log"
	"revolori/p3"
	"revolori/store"
	"revolori/user"
	"strings"
	"time"

	"github.com/julienschmidt/httprouter"
	"golang.org/x/crypto/bcrypt"
)

const validityDurationAuth = 10 * time.Minute
const validityDurationRefresh = 7 * 24 * time.Hour

// Controller contains functionality for user authentication.
type Controller struct {
	vault    *store.Client
	devMode  bool
	hostAddr string
}

// New creates a new controller for user authentication.
func New(vault *store.Client, devMode bool, hostAddr string) *Controller {
	return &Controller{
		vault,
		devMode,
		hostAddr,
	}
}

// @Summary Signup a new user
// @Accept  json
// @Router /user [POST]
// @Param Request body user.User true "Parameters specifying the user. 'secondaryIDs' are key-value pairs of the type string->[string], where the key describes the tool and the list of strings contains the secondary IDs for the specified tool"
// @securityDefinitions.basic BasicAuth
// @Success 201 "Created"
// @Failure 400 "Bad request"
// @Failure 409 "Conflict"
// @Failure 500 "Internal error"
func (ac Controller) CreateUser(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
	var transmittedUser user.User

	if err := decodeJSON(w, r, &transmittedUser); err != nil {
		var ir *invalidRequestBody
		if errors.As(err, &ir) {
			logAndReturnJsonError(w, ir.msg, ir.status)
		} else {
			logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	transmittedUser.Email = strings.ToLower(transmittedUser.Email)

	if err := transmittedUser.VerifySignup(); err != nil {
		logAndReturnJsonError(w, err.Error(), http.StatusBadRequest)
		return
	}

	exists, err := ac.userExists(transmittedUser)
	if err != nil {
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}
	if exists {
		logAndReturnJsonError(w, "user with given ID already exists", http.StatusConflict)
		return
	}

	duplicatedSecondaryID, id, err := ac.secondaryIDExists(transmittedUser)
	if err != nil {
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}
	if duplicatedSecondaryID {
		logMsg := fmt.Sprintf("user with secondary ID (%s) already exists", id)
		logAndReturnJsonError(w, logMsg, http.StatusBadRequest)
		return
	}

	storedUser, err := hashPassword(transmittedUser)
	if err != nil {
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if err := ac.vault.CreateUser(storedUser); err != nil {
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}

	message := fmt.Sprintf("User (ID: %s) succesfully created", storedUser.GetPrimaryID())
	logAndReturnJson(w, message, http.StatusCreated)
}

// @Summary Get the data of all available users.
// @Description Get the data of all available users. Gets back a list of users in a JSON format.
// @Description If no user exists, an empty list is returned.
// @Produce json
// @Router /user [GET]
// @securityDefinitions.basic BasicAuth
// @Success 200 {array} user.Data "Keep in mind that 'secondaryIDs' are key-value pairs of the type string->[string], where the key describes the tool and the list of strings contains the secondary IDs for the specified tool"
// @Failure 500 "Internal error"
func (ac Controller) GetAllUsers(w http.ResponseWriter, _ *http.Request, _ httprouter.Params) {
	users, err := ac.vault.GetAllUserData()
	switch {
	case err == store.ErrNoSecrets:
		users = []user.Data{}
	case err != nil:
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}

	logAndReturnJson(w, users, http.StatusOK)
}

// @Summary Get the data of the user with the specified id
// @Produce json
// @Router /user/{id} [GET]
// @securityDefinitions.basic BasicAuth
// @Param id path integer true "The ID of the user we want to get the data for"
// @Success 200 {object} user.Data "'secondaryIDs' are key-value pairs of the type string->[string], where the key describes the tool and the list of strings contains the secondary IDs for the specified tool"
// @Failure 400 "Bad request"
// @Failure 500 "Internal error"
func (ac Controller) GetUser(w http.ResponseWriter, _ *http.Request, p httprouter.Params) {
	lowercaseId := strings.ToLower(p.ByName("id"))
	ud, err := ac.vault.GetUserData(lowercaseId)
	switch {
	case err == user.ErrUserNotFound:
		logAndReturnJsonError(w, err.Error(), http.StatusBadRequest)
		return

	case err != nil:
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}

	logAndReturnJson(w, ud, http.StatusOK)
}

// @Summary Update an available user
// @Description Email needs to match the {id} in the URL parameter and can't be changed
// @Accept  json
// @Router /user/{id} [PUT]
// @Param id path integer true "The ID of the user we want to change the data for"
// @Param Request body user.Data true "'secondaryIDs' are key-value pairs of the type string->[string], where the key describes the tool and the list of strings contains the secondary IDs for the specified tool"
// @securityDefinitions.basic BasicAuth
// @Success 201 "Created"
// @Failure 400 "Bad request"
// @Failure 500 "Internal Error"
func (ac Controller) UpdateUser(w http.ResponseWriter, r *http.Request, p httprouter.Params) {
	var newUser user.User

	if err := decodeJSON(w, r, &newUser); err != nil {
		var ir *invalidRequestBody
		if errors.As(err, &ir) {
			logAndReturnJsonError(w, ir.msg, ir.status)
		} else {
			logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	newUser.Email = strings.ToLower(newUser.Email)

	lowercaseId := strings.ToLower(p.ByName("id"))
	if lowercaseId != newUser.GetPrimaryID() {
		logAndReturnJsonError(w, "provided IDs don't match", http.StatusBadRequest)
		return
	}

	if err := newUser.VerifySignup(); err != nil {
		logAndReturnJsonError(w, err.Error(), http.StatusBadRequest)
		return
	}

	duplicatedSecondaryID, duplicatedID, err := ac.secondaryIDExists(newUser)
	if err != nil {
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}
	if duplicatedSecondaryID {
		logMsg := fmt.Sprintf("user with secondary ID (%s) already exists", duplicatedID)
		logAndReturnJsonError(w, logMsg, http.StatusBadRequest)
		return
	}

	newUser, err = hashPassword(newUser)
	if err != nil {
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}

	switch err = ac.vault.UpdateUser(lowercaseId, newUser); {
	case err == user.ErrUserNotFound:
		logAndReturnJsonError(w, err.Error(), http.StatusBadRequest)
		return
	case err != nil:
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}

	message := fmt.Sprintf("User (ID: %s) succesfully updated", newUser.GetPrimaryID())
	logAndReturnJson(w, message, http.StatusCreated)
}

// @Summary Delete an available user
// @Router /user/{id} [DELETE]
// @Param id path integer true "The ID of the user we want to delete"
// @securityDefinitions.basic BasicAuth
// @Success 204 "No Content"
// @Failure 500 "Internal Error"
func (ac Controller) DeleteUser(w http.ResponseWriter, _ *http.Request, p httprouter.Params) {
	lowercaseId := strings.ToLower(p.ByName("id"))
	if err := ac.vault.DeleteUser(lowercaseId); err != nil {
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}

	logAndReturnJson(w, "", http.StatusNoContent)
}

// @Summary Login an available user
// @Description Issues an access token(short TTL) and a refresh token(long TTL) if the user data provided in the request body is valid.
// @Description The access token is returned to the client in JSON format. The refresh token is set as an HTTP only cookie.
// @Description Login also cleans up expired refresh tokens on the whitelist.
// @Accept  json
// @Produce  json
// @Router /login [POST]
// @Param Request body user.User true "Email and Password fields are mandatory the others field are optional and are not actually used"
// @Success 200 {object} auth.Token "Also sets a refresh cookie"
// @Failure 400 "Bad request"
// @Failure 401 "Unauthorized"
// @Failure 500 "Internal Error"
func (ac Controller) Login(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
	var transmittedUser user.User

	if err := decodeJSON(w, r, &transmittedUser); err != nil {
		var ir *invalidRequestBody
		if errors.As(err, &ir) {
			logAndReturnJsonError(w, ir.msg, ir.status)
		} else {
			logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	storedUser, err, statusCode := ac.verifyLogin(transmittedUser)
	if err != nil {
		logAndReturnJsonError(w, err.Error(), statusCode)
		return
	}

	expirationTimeRefresh := time.Now().Add(validityDurationRefresh)
	if err = ac.createRefreshTokenAndSetCookie(w, storedUser.Email, expirationTimeRefresh); err != nil {
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}

	expirationTimeAuth := time.Now().Add(validityDurationAuth)
	if err = ac.createAndSendAuthToken(w, storedUser.Email, expirationTimeAuth); err != nil {
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// return token
	go func() {
		if err = ac.vault.DeleteExpiredWhitelistEntries(); err != nil {
			log.ErrorLogger.Println(err.Error())
		}
	}()
}

// @Summary Logout a user
// @Description This function removes the cookie that holds the refresh token and removes the entry related to the token from the whitelist.
// @Description Note that only the cookie with the refresh token and whitelist entries are deleted. The removal of the authentication token is up to the client.
// @Router /login [DELETE]
// @Param all query boolean false "In case a query parameter `all=true` is added to the request, all whitelist entries of the user that sends the request are deleted.  The query parameter can be omitted(default is false) if a user only wants to logout from the current session and wants to keep other session, e.g. on different devices, alive."
// @Success 200 "OK"
// @Failure 400 "Bad Request"
// @Failure 500 "Internal Error"
func (ac Controller) Logout(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
	params, ok := r.URL.Query()["all"]
	var all string
	if ok && len(params) == 1 {
		all = params[0]
	}
	if all == "true" {
		id, status, err := ac.validateRefreshToken(r)
		if err != nil {
			logAndReturnJsonError(w, err.Error(), status)
			return
		}
		if err = ac.vault.DeleteUsersWhitelistEntries(id); err != nil {
			logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
			return
		}
	} else {
		c, err := r.Cookie("token")
		if err != nil {
			if err == http.ErrNoCookie {
				logAndReturnJsonError(w, err.Error(), http.StatusBadRequest)
				return
			}
			logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
			return
		}
		if err = ac.vault.DeleteWhitelistEntry(c.Value); err != nil {
			logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "token",
		MaxAge:   -1,
		HttpOnly: true,
	})

	logAndReturnJson(w, "", http.StatusOK)
}

// @Summary Refreshes authentication token
// @Description Returns a new JWT authentication token in case of an authenticated request.
// @Description For a request to be authenticated, a valid refresh token must be provided in a cookie named 'token'.
// @Router /refresh [GET]
// @securityDefinitions.basic BasicAuth
// @Accept json
// @Param all query boolean false "In case a query parameter `all=true` is added to the request, all whitelist entries of the user that sends the request are deleted.  The query parameter can be omitted(default is false) if a user only wants to logout from the current session and wants to keep other session, e.g. on different devices, alive."
// @Success 200 {object} auth.Token "Authentication token"
// @Failure 400 "Bad request"
// @Failure 500 "Internal Error"
func (ac Controller) Refresh(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
	id, status, err := ac.validateRefreshToken(r)
	if err != nil {
		logAndReturnJsonError(w, err.Error(), status)
		return
	}
	// return refresh token
	expirationTimeAuth := time.Now().Add(validityDurationAuth)
	if err = ac.createAndSendAuthToken(w, id, expirationTimeAuth); err != nil {
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

// GetID handles GET requests to the route '/id' and returns a matching of provided secondary IDs to a user's primary ID.
// @Summary Matches secondary IDs to their primary IDs
// @Description For a request to be authenticated, a valid refresh token must be provided in a cookie named 'token'.
// @Router /id [GET]
// @Accept json
// @Param secondaryIDs body string true "Key-value pairs of the type string->[string], where the key describes the tool and the list of strings contains the secondary IDs for the specified tool"
// @Success 200 {object} string "Mapping of transmitted secondary IDs to primary IDs for each provided tool"
// @Failure 400 "Bad request"
// @Failure 500 "Internal Error"
func (ac Controller) GetID(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
	var receivedIDs map[string][]string
	if err := decodeJSON(w, r, &receivedIDs); err != nil {
		var ir *invalidRequestBody
		if errors.As(err, &ir) {
			logAndReturnJsonError(w, ir.msg, ir.status)
		} else {
			logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	users, err := ac.vault.GetAllUserData()
	if err != nil {
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}

	var primaryIDs = make(map[string]map[string]string)
	for tool, secondaryIDs := range receivedIDs {
		primaryIDs[tool] = map[string]string{}
		for _, secondaryID := range secondaryIDs {
			primaryID, err := user.MatchID(tool, secondaryID, users)
			if err != nil {
				logAndReturnJsonError(w, err.Error(), http.StatusBadRequest)
				return
			}
			primaryIDs[tool][secondaryID] = primaryID
		}
	}

	logAndReturnJson(w, primaryIDs, http.StatusOK)
}

// @Summary Check if Revolori is running
// @Router /health [GET]
// @Success 200 "OK"
func (ac Controller) CheckHealth(w http.ResponseWriter, _ *http.Request, _ httprouter.Params) {
	logAndReturnJson(w, "", http.StatusOK)
}

// @Summary Show Revolori's public key
// @Description Displays Revolori's public key in JSON
// @Router /key/show [GET]
// @Accept json
// @Success 200 {object} string "Returns Revolori's public key"
// @Failure 500 "Internal Error"
func (ac Controller) ShowPublicKey(w http.ResponseWriter, _ *http.Request, _ httprouter.Params) {
	key, err := p3.LoadRSAPublicKey()
	if err != nil {
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}

	logAndReturnJson(w, key, http.StatusOK)
}

// @Summary Revolori will sign the passed public key
// @Router /key/sign [POST]
// @Accept json
// @Param publicKey body string true "The public key to be signed"
// @Param token body string false "A valid authentication token"
// @Param username body string false "If no token is given, then a valid username is expected"
// @Param password body string false "If no token is given, then a valid password is expected"
// @Success 200 {object} p3.SignedMessage "An identity card containing the public key and signed by Revolori"
// @Failure 400 "Bad request"
// @Failure 500 "Internal Error"
func (ac Controller) SignKey(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
	// Check if user is already logged in
	var userPublicKey rsa.PublicKey

	userID, _, err := ac.validateRefreshToken(r)
	if err == nil {
		// The token is valid => Get the public key from the request body
		var transmittedUser = struct {
			PublicKey rsa.PublicKey `json:"publicKey"`
		}{}

		if err = decodeJSON(w, r, &transmittedUser); err != nil {
			var ir *invalidRequestBody
			if errors.As(err, &ir) {
				logAndReturnJsonError(w, ir.msg, ir.status)
			} else {
				logAndReturnJsonError(w, err.Error(), http.StatusBadRequest)
			}

			return
		}

		userPublicKey = transmittedUser.PublicKey
	} else {
		// Token is invalid => Check for username/password in request
		var transmittedUser = struct {
			Email     string        `json:"email"`
			Password  string        `json:"password"`
			PublicKey rsa.PublicKey `json:"publicKey"`
		}{}

		if err = decodeJSON(w, r, &transmittedUser); err != nil {
			var ir *invalidRequestBody
			if errors.As(err, &ir) {
				logAndReturnJsonError(w, ir.msg, ir.status)
			} else {
				logAndReturnJsonError(w, err.Error(), http.StatusBadRequest)
			}

			return
		}

		if transmittedUser.Email == "" && transmittedUser.Password == "" && !reflect.DeepEqual(transmittedUser.PublicKey, rsa.PublicKey{}) {
			logAndReturnJsonError(w, "invalid token - no email or password, only a public key was given", http.StatusBadRequest)
			return
		}

		dummyUser := user.User{
			Data: user.Data{
				Email: transmittedUser.Email,
			},
			Password: transmittedUser.Password,
		}

		_, err, statusCode := ac.verifyLogin(dummyUser)
		if err != nil {
			logAndReturnJsonError(w, err.Error(), statusCode)
			return
		}

		userID = transmittedUser.Email
		userPublicKey = transmittedUser.PublicKey
	}

	identityCard := p3.IdentityCard{
		SSOID:     userID,
		PublicKey: userPublicKey,
	}

	revoloriPrivateKey, err := p3.LoadRSAPrivateKey()
	if err != nil {
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}

	signedCard, err := p3.CreateSignedIdentityCard(identityCard, &revoloriPrivateKey)
	if err != nil {
		logAndReturnJsonError(w, err.Error(), http.StatusInternalServerError)
		return
	}

	logAndReturnJson(w, signedCard, http.StatusOK)
}

// verifyLogin returns the stored user associated with the passed user
func (ac Controller) verifyLogin(passedUser user.User) (user.User, error, int) {
	passedUser.Email = strings.ToLower(passedUser.Email)

	if err := passedUser.VerifyLogin(); err != nil {
		return user.User{}, err, http.StatusBadRequest
	}

	errorInvalidCredentials := "the entered credentials are invalid"
	passwordPlain := passedUser.Password
	storedUser, err := ac.vault.GetUser(passedUser.Email)
	if err != nil {
		if err == user.ErrUserNotFound {
			return user.User{}, errors.New(errorInvalidCredentials), http.StatusUnauthorized
		}

		return user.User{}, err, http.StatusInternalServerError
	}

	err = bcrypt.CompareHashAndPassword([]byte(storedUser.Password), []byte(passwordPlain))
	if err != nil {
		return user.User{}, errors.New(errorInvalidCredentials), http.StatusUnauthorized
	}
	storedUser.Password = ""

	return storedUser, nil, http.StatusOK
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

// logAndReturnJson logs the response, returns a succesful HTTP status code and returns the data
// object in JSON format
func logAndReturnJson(w http.ResponseWriter, data interface{}, status int) {
	log.InfoLogger.Printf("%d - Response: %+v\n", status, data)
	setJsonResponse(w, status, data)
}

// logAndReturnJsonError logs the error, returns a bad HTTP status code and returns an error
// object in JSON format
func logAndReturnJsonError(w http.ResponseWriter, msg string, status int) {
	log.ErrorLogger.Printf("%d - ERROR: %s\n", status, msg)
	setJsonError(w, status, msg)
}

// setJsonResponse sets the given http.ResponseWriter up for a successful response by writing a
// JSON response and setting the header accordingly.
func setJsonResponse(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)

	jsn, err := json.Marshal(data)
	if err != nil {
		setJsonError(w, http.StatusInternalServerError, "") // logs error
		return
	}
	w.Write(jsn)
}

type jsonErrorEnvelope struct {
	Error jsonResponseError `json:"error"`
}

type jsonResponseError struct {
	Message string `json:"message,omitempty"`
}

// setJsonError sets the given http.ResponseWriter up for an error response (see `setJsonResponse`).
// Importantly, it handles potential JSON marshalling errors.
func setJsonError(w http.ResponseWriter, status int, message string) {
	if message == "" {
		message = http.StatusText(status)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)

	envelope := jsonErrorEnvelope{jsonResponseError{message}}
	jsn, err := json.Marshal(envelope)
	if err != nil {
		log.ErrorLogger.Println(err.Error())
	}
	w.Write(jsn)
}
