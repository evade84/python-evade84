class APIException(Exception):
    def __init__(self, error_id: str, error_message: str, error_details: str | None):
        self.error_id = error_id
        self.error_message = error_message
        self.error_details = error_details
        self.message = f"(#{error_id}) {error_message} Details: {error_details}."
        super(APIException, self).__init__(self.message)


class IncorrectInputException(APIException):  # code: 400
    pass


class AccessDeniedException(APIException):  # code: 403
    pass


class NotFoundException(APIException):  # code: 404
    pass


class ConflictException(APIException):  # code: 409
    pass


class UnprocessableEntityException(APIException):  # code 422
    pass


class InternalServerErrorException(APIException):  # code: 500
    pass
