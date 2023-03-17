package domain

type User struct {
	Id       uint64 `json:"id" gorm:"primary_key:auto_increment"`
	Username string `json:"username" gorm:"type:varchar(255);not null, unique"`
	Password string `json:"-" gorm:"type:varchar(255);not null"`
}
