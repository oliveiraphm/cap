from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Generic, TypeVar, Self

T = TypeVar('T')

class ErrorCode(Enum):

    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    UNAUTHORIZED = "UNAUTHORIZED"
    CONFLICT = "CONFLICT"

@dataclass(frozen=True)
class Error:

    code: ErrorCode
    message: str
    details: Optional[dict[str, Any]] = None

    @classmethod
    def not_found(cls, entity: str, entity_id: str) -> Self:
        
        return cls(
            code=ErrorCode.NOT_FOUND,
            message=f"{entity} with id {entity_id} not found",
        )
    
    @classmethod
    def validation_error(cls, message: str) -> Self:

        return cls(code=ErrorCode.VALIDATION_ERROR, message=message)
    
    @classmethod
    def business_rule_violation(cls, message: str) -> Self:
        return cls(code=ErrorCode.BUSINESS_RULE_VIOLATION, message=message)
    
@dataclass(frozen=True)
class Result(Generic[T]):

    _value: Optional[T] = None
    _error: Optional[Error] = None

    def __post_init__(self):
        if (self._value is None and self._error is None) or \
        (self._value is not None and self._error is not None):
            raise ValueError("Either value or error must be provided, but not both")
        
    @property
    def is_success(self) -> bool:

        return self._value is not None
    
    @property
    def value(self) -> T:
        if self._value is None:
            raise ValueError("Cannot access value on error result")
        return self._value
    
    @property
    def error(self) -> Error:
        if self._error is None:
            raise ValueError("Cannot access error on success result")
        return self._error
    
    @classmethod
    def success(cls, value: T) -> 'Result[T]':
        return cls(_value=value)
    
    @classmethod
    def failure(cls, error: Error) -> 'Result[T]':
        return cls(_error=error)