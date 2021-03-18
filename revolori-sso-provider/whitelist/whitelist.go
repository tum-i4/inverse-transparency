// Package whitelist defines the type for token whitelist entries and provides utility functions to manipulate entries.
package whitelist

import "time"

// Entry represents an entry in the token whitelist.
type Entry struct {
	Token      string
	UserID     string
	Expiration time.Time
}

// IsExpired returns if an entry is expired.
func (e Entry) IsExpired() bool {
	return e.Expiration.Before(time.Now())
}

// BelongsToUser returns if an entry belongs to the specified userID.
func (e Entry) BelongsToUser(userID string) bool {
	return e.UserID == userID
}
