// Package p3 defines functionality needed for the P3 PoC
package p3

import "crypto/rsa"

type IdentityCard struct {
	SSOID     string        `json:"ssoid"`
	PublicKey rsa.PublicKey `json:"public_key"`
}
