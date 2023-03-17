package middleware

import (
	"chapter05_demo/api/helper"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
)

type ValidationError struct {
	Key     string `json:"key,omitempty"`
	Message string `json:"message"`
}

func (e ValidationError) Error(splitedError []string) []ValidationError {
	var errors []ValidationError
	for _, error := range splitedError {
		splittedError := strings.Split(error, "'")
		errors = append(errors, ValidationError{
			Key:     splittedError[3],
			Message: "Error :" + splittedError[4] + splittedError[5] + splittedError[6],
		})
	}
	return errors
}

func ErrorHandler(c *gin.Context) {
	c.Next()
	if c.Errors != nil {
		err := c.Errors.Last()
		if err.Meta == "VALIDATION_ERROR" {
			validationErrors(c, err)
			return
		} else if err.Meta == "NOT_FOUND" {
			notFoundError(c, err)
			return
		}
		if err.Meta == "UNAUTHORIZED" {
			authenticationError(c, err)
			return
		}
		internalServerError(c, err)
	}
}

func validationErrors(c *gin.Context, err *gin.Error) {
	splittedError := strings.Split(err.Error(), "\n")
	errors := ValidationError{}.Error(splittedError)
	webResponse := helper.BuildErrorResponse(http.StatusBadRequest, "BAD REQUEST", errors)
	c.JSON(http.StatusBadRequest, webResponse)
}

func authenticationError(c *gin.Context, err *gin.Error) {
	webResponse := helper.BuildErrorResponse(http.StatusUnauthorized, "UNAUTHORIZED", err)
	c.JSON(http.StatusUnauthorized, webResponse)
}

func notFoundError(c *gin.Context, err *gin.Error) {
	webResponse := helper.BuildErrorResponse(http.StatusNotFound, "Not Found", err)
	c.JSON(http.StatusNotFound, webResponse)
}

func internalServerError(c *gin.Context, err *gin.Error) {
	webResponse := helper.BuildErrorResponse(http.StatusInternalServerError, "INTERNAL SERVER ERROR", err)
	c.JSON(http.StatusInternalServerError, webResponse)
}
