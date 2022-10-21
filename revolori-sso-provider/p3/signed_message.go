package p3

import (
	"crypto"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"encoding/json"
)

type SignedMessage struct {
	// Content has to be []byte otherwise the unmarshal fails
	Content   []byte `json:"content"`
	Signature []byte `json:"signature"`
}

func CreateSignedIdentityCard(card IdentityCard, revoloriPrivateKey *rsa.PrivateKey) (SignedMessage, error) {
	cardJSON, err := json.Marshal(card)
	if err != nil {
		return SignedMessage{}, err
	}

	signature, err := calculateSignature(cardJSON, revoloriPrivateKey)
	if err != nil {
		return SignedMessage{}, err
	}

	return SignedMessage{
		Content:   cardJSON,
		Signature: signature,
	}, nil
}

func calculateSignature(message []byte, privateKey *rsa.PrivateKey) ([]byte, error) {
	hashed := sha256.Sum256(message)
	return rsa.SignPKCS1v15(rand.Reader, privateKey, crypto.SHA256, hashed[:])
}
