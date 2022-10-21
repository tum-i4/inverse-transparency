package auth

import (
	"net/http"

	"github.com/julienschmidt/httprouter"
)

// BasicAuth allows to protect routes with basic authentication with the given ID and password.
func (ac Controller) BasicAuth(h httprouter.Handle, expectedName string, expectedPw string) httprouter.Handle {
	return func(w http.ResponseWriter, r *http.Request, p httprouter.Params) {
		name, pw, ok := r.BasicAuth()

		if ok && name == expectedName && pw == expectedPw {
			h(w, r, p)
		} else {
			w.Header().Set("WWW-Authenticate", "Basic realm=Restricted")
			logAndReturnJsonError(w, "missing or invalid credentials for basic authentication provided", http.StatusUnauthorized)
		}
	}
}
