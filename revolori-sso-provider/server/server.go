// Package server defines functionality to start and initialize the HTTP server.
package server

import (
	"flag"
	"fmt"
	"net/http"
	"revolori/auth"
	"revolori/log"
	"revolori/store"
	"time"

	"github.com/julienschmidt/httprouter"
	"github.com/rs/cors"
	"github.com/swaggo/http-swagger"
	_ "revolori/docs"
)

// StartServer initializes and starts the HTTP server and parses stdin flags.
func StartServer() {
	vaultAddress, vaultToken, authName, authPassword, devMode, addr, hostAddr := createAndParseFlags()

	ac, err := initStore(vaultAddress, vaultToken, devMode, hostAddr)
	if err != nil {
		log.ErrorLogger.Fatalln(err)
	}

	c := cors.New(cors.Options{
		AllowedOrigins: []string{
			"https://*.sse.in.tum.de",
			"http://127.0.0.1:*", "https://127.0.0.1:*",
		},
		AllowedMethods: []string{http.MethodGet, http.MethodPost, http.MethodDelete,
			http.MethodPut},
		AllowCredentials: true,
	})

	r, err := initRouter(authName, authPassword, ac)
	if err != nil {
		log.ErrorLogger.Fatalln(err)
	}

	handler := c.Handler(r)

	server := http.Server{
		ReadHeaderTimeout: 1 * time.Minute,
		ReadTimeout:       1 * time.Minute,
		WriteTimeout:      1 * time.Minute,
		IdleTimeout:       1 * time.Minute,
		Handler:           handler,
		Addr:              addr,
	}

	fmt.Println("Revolori is up and running on " + addr + ".")
	log.ErrorLogger.Fatal(server.ListenAndServe())
}

// initStore initializes the client to communicate with vault storage and returns a authentication client
func initStore(vaultAddress, vaultToken string, devMode bool, hostAddr string) (*auth.Controller, error) {
	client, err := store.New(vaultToken, vaultAddress)
	if err != nil {
		return nil, err
	}
	ac := auth.New(client, devMode, hostAddr)

	return ac, nil
}

// initRouter initializes a router with its dependencies and routes.
func initRouter(authName, authPassword string, ac *auth.Controller) (*httprouter.Router, error) {
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
	r.POST("/key/sign", ac.SignKey)
	r.GET("/key/show", ac.ShowPublicKey)
	// Documentation handler
	r.HandlerFunc(http.MethodGet, "/docs/*route", httpSwagger.Handler())

	return r, nil
}

// createAndParseFlags creates and parses command line flags and returns their values.
func createAndParseFlags() (vaultAddress string, vaultToken string, authName string, authPassword string, devMode bool, addr string, hostAddr string) {
	hostAddrPtr := flag.String("host-address", "http://127.0.0.1:5429", "domain name and protocol used by this service")
	addrPtr := flag.String("address", "127.0.0.1:5429", "address in the form 'host:port' for Revolori to listen at")
	vaultAddressPtr := flag.String("vault-address", "http://127.0.0.1:5430", "address of Vault")
	vaultTokenPtr := flag.String("vault-token", "default_token", "access token of Vault")
	authNamePtr := flag.String("auth-name", "user", "username for basic authentication")
	authPasswordPtr := flag.String("auth-password", "password", "password for basic authentication")
	devModePtr := flag.Bool("dev", false, "whether dev mode should be enabled")
	flag.Parse()

	return *vaultAddressPtr, *vaultTokenPtr, *authNamePtr, *authPasswordPtr, *devModePtr, *addrPtr, *hostAddrPtr
}
