// Package server defines functionality to start and initialize the HTTP server.
package server

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"revolori/auth"
	"revolori/store"
	"time"

	"github.com/julienschmidt/httprouter"
	"github.com/rs/cors"
)

// StartServer initializes and starts the HTTP server.
func StartServer() {
	c := cors.New(cors.Options{
		AllowedOrigins: []string{"http://localhost:*", "https://localhost:*",
			"https://*.sse.in.tum.de", "http://0.0.0.0:*", "https://0.0.0.0:*"},
		AllowedMethods: []string{http.MethodGet, http.MethodPost, http.MethodDelete,
			http.MethodPut},
		AllowCredentials: true,
	})

	r, err := initRouter()
	if err != nil {
		log.Fatalln(err)
	}

	handler := c.Handler(r)

	server := http.Server{
		ReadHeaderTimeout: 1 * time.Minute,
		ReadTimeout:       1 * time.Minute,
		WriteTimeout:      1 * time.Minute,
		IdleTimeout:       1 * time.Minute,
		Handler:           handler,
		Addr:              ":5429",
	}

	fmt.Println("Revolori is up and running on http://localhost:5429.")
	log.Fatal(server.ListenAndServe())
}

// initRouter initializes a router with its dependencies and routes.
func initRouter() (*httprouter.Router, error) {
	logger := log.New(os.Stdout, "", log.Ldate|log.Ltime|log.LUTC|log.Lshortfile)
	vaultAddress, vaultToken, authName, authPassword, devMode := createAndParseFlags()
	client, err := store.New(vaultToken, vaultAddress)
	if err != nil {
		return nil, err
	}
	ac := auth.New(logger, client, devMode)
	r := httprouter.New()

	r.POST("/user", ac.BasicAuth(ac.CreateUser, authName, authPassword))
	r.GET("/user", ac.BasicAuth(ac.GetAllUsers, authName, authPassword))
	r.GET("/user/:id", ac.BasicAuth(ac.GetUser, authName, authPassword))
	r.PUT("/user/:id", ac.BasicAuth(ac.UpdateUser, authName, authPassword))
	r.DELETE("/user/:id", ac.BasicAuth(ac.DeleteUser, authName, authPassword))
	r.POST("/login", ac.Login)
	r.DELETE("/login", ac.Logout)
	r.GET("/refresh", ac.Refresh)
	r.GET("/id", ac.GetID)
	r.GET("/health", ac.CheckHealth)

	return r, nil
}

// createAndParseFlags creates and parses command line flags and returns their values.
func createAndParseFlags() (vaultAddress string, vaultToken string, authName string, authPassword string, devMode bool) {
	vaultAddressPtr := flag.String("vault-address", "http://127.0.0.1:5430", "address of Vault")
	vaultTokenPtr := flag.String("vault-token", "default_token", "access token of Vault")
	authNamePtr := flag.String("auth-name", "user", "username for basic authentication")
	authPasswordPtr := flag.String("auth-password", "password", "password for basic authentication")
	devModePtr := flag.Bool("dev", false, "whether dev mode should be enabled")
	flag.Parse()
	return *vaultAddressPtr, *vaultTokenPtr, *authNamePtr, *authPasswordPtr, *devModePtr
}
