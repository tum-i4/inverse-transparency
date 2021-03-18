package auth

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"revolori/whitelist"
	"time"

	"github.com/dgrijalva/jwt-go"
	"github.com/google/uuid"
)

// NewAuthToken returns a new JWT token signed with ECDSA that should only be used to authenticate user requests.
func (ac Controller) newAuthToken(userID string, expirationTime time.Time) (string, error) {
	b, err := ac.vault.GetKey("ecdsa")
	if err != nil {
		return "", err
	}

	key, err := jwt.ParseECPrivateKeyFromPEM(b)
	if err != nil {
		return "", err
	}

	issuer := "http://localhost:5429"

	return generateToken(jwt.SigningMethodES384, expirationTime, issuer, userID, key)
}

// NewRefreshToken returns a new JWT token signed with HMAC that should only be used as a refresh token to refresh auth tokens.
func (ac Controller) newRefreshToken(userID string, expirationTime time.Time) (string, error) {
	key, err := ac.vault.GetKey("hmac")
	if err != nil {
		return "", err
	}

	issuer := "http://localhost:5429"

	return generateToken(jwt.SigningMethodHS512, expirationTime, issuer, userID, key)
}

// generateToken generates a new JWT.
func generateToken(signingMethod jwt.SigningMethod, expirationTime time.Time, issuer string, userID string, key interface{}) (string, error) {
	tokenID := uuid.New().String()

	claims := jwt.StandardClaims{
		Subject:   userID,
		ExpiresAt: expirationTime.Unix(),
		NotBefore: time.Now().Unix(),
		IssuedAt:  time.Now().Unix(),
		Issuer:    issuer,
		Id:        tokenID,
	}
	token := jwt.NewWithClaims(signingMethod, claims)
	tokenString, err := token.SignedString(key)
	if err != nil {
		return "", err
	}

	return tokenString, nil
}

// createAndSendAuthToken creates a new auth token and returns it to the user in JSON format.
func (ac Controller) createAndSendAuthToken(w http.ResponseWriter, userID string, expirationTime time.Time) error {
	authToken, err := ac.newAuthToken(userID, expirationTime)
	if err != nil {
		return err
	}

	token := struct {
		Token string `json:"token"`
	}{
		Token: authToken,
	}

	w.Header().Set("Content-Type", "application/json")
	return json.NewEncoder(w).Encode(token)
}

// createRefreshTokenAndSetCookie creates a new refresh token and sets a cookie at the users end.
func (ac Controller) createRefreshTokenAndSetCookie(w http.ResponseWriter, userID string, expirationTime time.Time) error {
	refreshToken, err := ac.newRefreshToken(userID, expirationTime)
	if err != nil {
		return err
	}

	if err = ac.whitelistToken(refreshToken, userID, expirationTime); err != nil {
		return err
	}

	sameSite := http.SameSiteStrictMode
	secure := true
	if ac.devMode {
		sameSite = http.SameSiteNoneMode
		secure = false
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "token",
		Value:    refreshToken,
		Expires:  expirationTime,
		HttpOnly: true,
		SameSite: sameSite,
		Secure:   secure,
	})
	return nil
}

// validateRefreshToken checks the validity of a refresh token and returns the subject of the token (email of user).
// In case of an error, the appropriate HTTP status code is returned alongside the error.
func (ac Controller) validateRefreshToken(r *http.Request) (string, int, error) {
	key, err := ac.vault.GetKey("hmac")
	if err != nil {
		return "", http.StatusInternalServerError, err
	}

	c, err := r.Cookie("token")
	if err != nil {
		if err == http.ErrNoCookie {
			return "", http.StatusBadRequest, err
		}
		return "", http.StatusInternalServerError, err
	}

	if _, err = ac.vault.GetWhitelistEntry(c.Value); err != nil {
		return "", http.StatusUnauthorized, errors.New("token not whitelisted")
	}

	token, err := jwt.Parse(c.Value, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("invalid token signing method: %v", token.Header["alg"])
		}
		return key, nil
	})
	if err != nil {
		return "", http.StatusInternalServerError, err
	}

	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		return claims["sub"].(string), http.StatusOK, nil
	}
	return "", http.StatusUnauthorized, errors.New("invalid token")
}

// whitelistToken adds a token to the whitelist.
func (ac Controller) whitelistToken(token string, userID string, expirationTime time.Time) error {
	entry := whitelist.Entry{
		Token:      token,
		UserID:     userID,
		Expiration: expirationTime,
	}
	return ac.vault.CreateWhitelistEntry(entry)
}
