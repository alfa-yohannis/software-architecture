package helper

type SuccessWebResponse struct {
	Code   int         `json:"code"`
	Status string      `json:"status"`
	Data   interface{} `json:"data"`
}

type ErrorWebResponse struct {
	Code   int         `json:"code"`
	Status string      `json:"status"`
	Errors interface{} `json:"errors"`
}

func BuildResponse(code int, status string, data interface{}) SuccessWebResponse {
	return SuccessWebResponse{
		Code:   code,
		Status: status,
		Data:   data,
	}
}

func BuildErrorResponse(code int, status string, errors interface{}) ErrorWebResponse {
	return ErrorWebResponse{
		Code:   code,
		Status: status,
		Errors: errors,
	}
}
