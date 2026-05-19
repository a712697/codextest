from __future__ import annotations


class AppError(Exception):
    code = 50000

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    code = 40000


class NotFoundError(AppError):
    code = 40400


class ConflictError(AppError):
    code = 40900


class BusinessRuleError(AppError):
    code = 42200
