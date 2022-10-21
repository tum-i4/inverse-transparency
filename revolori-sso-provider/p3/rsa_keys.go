package p3

import (
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"errors"
	"fmt"
	"io/ioutil"
)

// ToDo:
// 		* Remove hard coded path
// 		* Find out why .env is not loaded
const basePath = "./dev_keys"

func LoadRSAPublicKey() (rsa.PublicKey, error) {
	blockBytes, err := readPem(basePath + "/rsa_key.pub")
	if err != nil {
		return rsa.PublicKey{}, err
	}

	pub, err := x509.ParsePKCS1PublicKey(blockBytes)
	if err != nil {
		return rsa.PublicKey{}, errors.New(fmt.Sprintf("could not parse public key: %s\n", err))
	}

	return *pub, nil
}

func LoadRSAPrivateKey() (rsa.PrivateKey, error) {
	blockBytes, err := readPem(basePath + "/rsa_key")
	if err != nil {
		return rsa.PrivateKey{}, err
	}

	pub, err := x509.ParsePKCS1PrivateKey(blockBytes)
	if err != nil {
		return rsa.PrivateKey{}, errors.New(fmt.Sprintf("could not parse public key: %s\n", err))
	}

	return *pub, nil
}

func readPem(path string) ([]byte, error) {
	pemContent, err := ioutil.ReadFile(path)
	if err != nil {
		return nil, errors.New(fmt.Sprintf("could not read pem file: %s\n", err))
	}

	block, _ := pem.Decode(pemContent)
	if block == nil {
		return nil, errors.New("could not decode PEM block")
	}

	return block.Bytes, nil
}
