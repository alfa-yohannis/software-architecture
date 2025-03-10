package controller

import (
	"net/http"

	"chapter05_demo/api/helper"
	"chapter05_demo/api/model/web"
	"chapter05_demo/api/service"

	"github.com/gin-gonic/gin"
)

type UserController interface {
	Login(ctx *gin.Context)
	Register(ctx *gin.Context)
}

type userController struct {
	userService service.UserService
}

func NewUserController(userService service.UserService) UserController {
	return &userController{
		userService: userService,
	}
}

func (c *userController) Login(ctx *gin.Context) {
	var u web.UserLoginRequest
	err := ctx.BindJSON(&u)
	ok := helper.ValidationError(ctx, err)
	if ok {
		return
	}
	user, err := c.userService.VerifyCredential(u)
	ok = helper.ValidationError(ctx, err)
	if ok {
		return
	}
	webResponse := helper.BuildResponse(http.StatusOK, "Success", user)
	ctx.JSON(http.StatusOK, webResponse)
}

func (c *userController) Register(ctx *gin.Context) {
	var u web.UserRegisterRequest
	err := ctx.BindJSON(&u)
	ok := helper.ValidationError(ctx, err)
	if ok {
		return
	}
	user, err := c.userService.Create(u)
	ok = helper.ValidationError(ctx, err)
	if ok {
		return
	}
	ok = helper.InternalServerError(ctx, err)
	if ok {
		return
	}
	webResponse := helper.BuildResponse(http.StatusOK, "Success", user)
	ctx.JSON(http.StatusCreated, webResponse)
}
