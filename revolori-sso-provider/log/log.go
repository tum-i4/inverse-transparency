// Package log contains ready loggers for easy use throughout the program
package log

import (
	"log"
	"os"
)

var InfoLogger = *log.New(os.Stdout, "", log.Ldate|log.Ltime|log.LUTC|log.Lshortfile)
var ErrorLogger = *log.New(os.Stderr, "", log.Ldate|log.Ltime|log.LUTC|log.Lshortfile)
