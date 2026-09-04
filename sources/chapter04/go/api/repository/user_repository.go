package repository

import (
	"chapter05_demo/api/helper"
	"chapter05_demo/api/model/domain"
	"errors"

	"gorm.io/gorm"
)

type UserRepository interface {
	Create(u domain.User) domain.User
	VerifyCredential(userName, password string) (domain.User, error)
}

type UserConnection struct {
	connection *gorm.DB
}

func NewUserRepository(connection *gorm.DB) UserRepository {
	return &UserConnection{connection: connection}
}

func (c *UserConnection) Create(u domain.User) domain.User {
	u.Password = helper.HashAndSalt([]byte(u.Password))
	c.connection.Save(&u)
	return u
}

func (c *UserConnection) VerifyCredential(userName, password string) (domain.User, error) {
	var user domain.User
	c.connection.Find(&user, "username = ?", userName)

	res := helper.ComparedPassword(user.Password, []byte(password))
	if !res {
		return user, errors.New("invalid credential")
	}
	if user.Id == 0 {
		return user, errors.New("wrong credential")
	}
	return user, nil
}
