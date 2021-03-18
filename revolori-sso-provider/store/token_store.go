package store

// CreateKey writes a given key to the secrets engine 'keys'.
func (c Client) CreateKey(name string, key []byte) error {
	return c.write("keys", name, map[string]interface{}{
		"key": string(key),
	})
}

// GetKey reads a crypto key with specified name from the secrets engine 'keys'.
func (c Client) GetKey(name string) ([]byte, error) {
	data, err := c.read("keys", name)
	if err != nil {
		return nil, err
	}
	keyString := data["key"].(string)
	return []byte(keyString), nil
}
