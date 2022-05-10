package utils

import (
	"crypto/rand"
	"io"
)

func NewUUIDVer4() ([]byte, error) {
	u := new([16]byte)
	if _, err := io.ReadFull(rand.Reader, u[:]); err != nil {
		return u[:], err
	}
	// u.SetVersion(V4)
	// u.SetVariant(VariantRFC4122)

	return u[:], nil
}
