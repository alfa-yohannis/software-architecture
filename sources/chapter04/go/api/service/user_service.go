package service

import (
	"chapter05_demo/api/model/domain"
	"chapter05_demo/api/model/web"
	"chapter05_demo/api/repository"

	"github.com/mashingan/smapping"
)

type UserService interface {
	VerifyCredential(b web.UserLoginRequest) (interface{}, error)
	Create(b web.UserRegisterRequest) (domain.User, error)
}

type userService struct {
	userRepository repository.UserRepository
}

func NewUserService(userRepository repository.UserRepository) UserService {
	return &userService{
		userRepository: userRepository,
	}
}

func (s *userService) VerifyCredential(u web.UserLoginRequest) (interface{}, error) {
	user, err := s.userRepository.VerifyCredential(u.Username, u.Password)
	if err != nil {
		return user, err
	}
	return user, nil
}

func (s *userService) Create(request web.UserRegisterRequest) (domain.User, error) {
	user := domain.User{}
	err := smapping.FillStruct(&user, smapping.MapFields(&request))

	if err != nil {
		return user, err
	}

	return s.userRepository.Create(user), nil
}
