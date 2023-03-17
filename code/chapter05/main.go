package main

import (
	"log"
	"os"

	"chapter05_demo/api/helper"
	"chapter05_demo/app/config"
	"chapter05_demo/app/routes"

	"github.com/joho/godotenv"
	cors "github.com/rs/cors/wrapper/gin"

	"gorm.io/gorm"

	"github.com/gin-gonic/gin"
)

var (
	db *gorm.DB = config.SetupDatabaseConnection()
)

func main() {
	defer config.CloseDatabaseConnection(db)
	err := godotenv.Load()
	helper.PanicIfError(err)
	router := setupRouter()
	log.Fatal(router.Run(":" + os.Getenv("GO_PORT")))
}

func setupRouter() *gin.Engine {
	/**
	@description Setup Database Connection
	*/

	/**
	@description Init Router
	*/
	router := gin.Default()
	/**
	@description Setup Mode Application
	*/
	if os.Getenv("GO_ENV") != "production" && os.Getenv("GO_ENV") != "test" {
		gin.SetMode(gin.DebugMode)
	} else if os.Getenv("GO_ENV") == "test" {
		gin.SetMode(gin.TestMode)
	} else {
		gin.SetMode(gin.ReleaseMode)
	}
	/**
	@description Setup Middleware
	*/

	/**
	@description Init All Route
	*/
	routes.NewUserRoutes(db, router)
	router.Use(cors.Default())

	return router
}
