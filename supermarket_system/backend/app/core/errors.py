class AppError(Exception):
    code = 50000
    http_status = 500

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class BadRequest(AppError):
    code = 40000
    http_status = 400


class Unauthorized(AppError):
    code = 40100
    http_status = 401


class Forbidden(AppError):
    code = 40300
    http_status = 403


class NotFound(AppError):
    code = 40400
    http_status = 404


class Conflict(AppError):
    code = 40900
    http_status = 409


class BusinessError(AppError):
    code = 42200
    http_status = 422
