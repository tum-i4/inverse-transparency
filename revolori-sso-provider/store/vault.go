// Package store implements functionality to store secrets and user credentials.
// It uses HashiCorp Vault to encrypt and securely store sensitive data.
package store

import (
	"errors"
	"revolori/user"

	"github.com/hashicorp/vault/api"
)

// Client represents a store client that allows to manipulate the underlying vault.
type Client struct {
	vaultClient *api.Client
}

// ErrNoSecrets is thrown in case there are no keys in a secrets engine.
var ErrNoSecrets = errors.New("no secrets found in given engine")

// New creates a new Client to store, read and delete data from a vault.
func New(token string, address string) (*Client, error) {
	client, err := initVaultClient(token, address)
	if err != nil {
		return nil, err
	}
	return &Client{client}, nil
}

// initVaultClient initializes and authenticates to a vault client that enables data access.
func initVaultClient(token string, address string) (*api.Client, error) {
	config := &api.Config{
		Address: address,
	}
	vaultClient, err := api.NewClient(config)
	if err != nil {
		return nil, err
	}
	vaultClient.SetToken(token)
	return vaultClient, nil
}

// read returns the data of the secret with specified name and secret engine.
func (c Client) read(engine string, name string) (map[string]interface{}, error) {
	path := engine + "/" + name
	secret, err := c.vaultClient.Logical().Read(path)
	if err != nil {
		return nil, err
	}
	if secret == nil {
		return nil, user.ErrUserNotFound
	}
	return secret.Data, nil
}

// getKeys returns all keys from a specified secrets engine.
func (c Client) getKeys(engine string) (map[string]interface{}, error) {
	secret, err := c.vaultClient.Logical().List(engine)
	if err != nil {
		return nil, err
	}
	if secret == nil {
		return nil, ErrNoSecrets
	}
	return secret.Data, nil
}

// write adds a new secret to the specified secret engine of the vault client.
func (c Client) write(engine string, name string, data map[string]interface{}) error {
	path := engine + "/" + name
	_, err := c.vaultClient.Logical().Write(path, data)
	if err != nil {
		return err
	}
	return nil
}

// delete deletes the data of the secret with specified name and secret engine.
func (c Client) delete(engine string, name string) error {
	path := engine + "/" + name
	_, err := c.vaultClient.Logical().Delete(path)
	return err
}
