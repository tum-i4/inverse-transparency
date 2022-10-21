package store

import (
	"fmt"
	"revolori/whitelist"
	"time"
)

const storagePath = "whitelist"

// CreateWhitelistEntry writes a given whitelist entry to the secrets engine 'whitelist'.
func (c Client) CreateWhitelistEntry(entry whitelist.Entry) error {
	return c.write(storagePath, entry.Token, map[string]interface{}{
		"token":      entry.Token,
		"userID":     entry.UserID,
		"expiration": entry.Expiration.Format(time.RFC3339),
	})
}

// GetWhitelistEntry reads a given whitelist entry from the secrets engine 'whitelist'.
func (c Client) GetWhitelistEntry(token string) (whitelist.Entry, error) {
	data, err := c.read(storagePath, token)
	if err != nil {
		fmt.Printf("[!] Could not read storage path '%s' because: %s\n", storagePath, err.Error())
		return whitelist.Entry{}, err
	}

	expiration, err := time.Parse(time.RFC3339, data["expiration"].(string))
	if err != nil {
		fmt.Printf("[!] Expired? Error: %s\n", err.Error())
		return whitelist.Entry{}, err
	}

	entry := whitelist.Entry{
		Token:      data["token"].(string),
		UserID:     data["userID"].(string),
		Expiration: expiration,
	}
	return entry, nil
}

// DeleteWhitelistEntry deletes a given whitelist entry from the secrets engine 'whitelist'.
func (c Client) DeleteWhitelistEntry(token string) error {
	return c.delete(storagePath, token)
}

// DeleteUsersWhitelistEntries deletes all whitelist entries of a given user from the secrets engine 'whitelist'.
func (c Client) DeleteUsersWhitelistEntries(userID string) error {
	return c.deleteWhitelistEntries(func(entry whitelist.Entry) bool {
		return entry.BelongsToUser(userID)
	})
}

// DeleteExpiredWhitelistEntries deletes all expired whitelist entries from the secrets engine 'whitelist'.
func (c Client) DeleteExpiredWhitelistEntries() error {
	return c.deleteWhitelistEntries(func(entry whitelist.Entry) bool {
		return entry.IsExpired()
	})
}

// deleteWhitelistEntries deletes all entries for which the passed function evaluates to true from the secrets engine 'whitelist'.
func (c Client) deleteWhitelistEntries(cond func(entry whitelist.Entry) bool) error {
	data, err := c.getKeys(storagePath)
	if err != nil {
		return err
	}
	keys := data["keys"].([]interface{})
	for _, key := range keys {
		entry, err := c.GetWhitelistEntry(key.(string))
		if err != nil {
			return err
		}
		if cond(entry) {
			if err = c.DeleteWhitelistEntry(entry.Token); err != nil {
				return err
			}
		}
	}
	return nil
}
