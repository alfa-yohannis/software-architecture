package routes

import (
	"chapter05_demo/api/controller"
	"chapter05_demo/api/middleware"
	"chapter05_demo/api/repository"
	"chapter05_demo/api/service"

	"gorm.io/gorm"

	cors "github.com/rs/cors/wrapper/gin"

	"github.com/gin-gonic/gin"
)

func NewUserRoutes(db *gorm.DB, route *gin.Engine) {
	userRepository := repository.NewUserRepository(db)
	userService := service.NewUserService(userRepository)
	userController := controller.NewUserController(userService)

	userRoute := route.Group("/api/v1")
	userRoute.Use(middleware.ErrorHandler)
	userRoute.Use(cors.Default())
	userRoute.POST("/login/", userController.Login)
	userRoute.POST("/register/", userController.Register)
}
