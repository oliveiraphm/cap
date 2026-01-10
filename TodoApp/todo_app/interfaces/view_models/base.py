from typing import Generic, TypeVar, Optional
from dataclasses import dataclass

T = TypeVar("T")

@dataclass(frozen=True)
class ErrorViewModel:
    
    message: str
    code: Optional[str] = None

@dataclass
class OperationResult(Generic[T]):
    
    _success: Optional[T] = None
    _error: Optional[ErrorViewModel] = None

    def __init__(self, success: Optional[T] = None, error: Optional[ErrorViewModel] = None):
        
        if(success is None and error is None) or (success is not None and error is not None):
            raise ValueError("Either success or error must be provided, but not both")
        
        self._success = success
        self._error = error
    
    @property
    def is_success(self) -> bool:
        return self._success is not None
    
    @property
    def success(self) -> T:

        if self._success is None:
            raise ValueError("Cannot access success value on error result")
        return self._success
    
    @property
    def error(self) -> ErrorViewModel:
        
        if self._error is None:
            raise ValueError("Cannot access error value on success result")
        return self._error
    
    @classmethod
    def succeed(cls, value: T) -> "OperationResult[T]":
        
        return cls(success=value)

    @classmethod
    def fail(cls, message: str, code: Optional[str] = None) -> "OperationResult[T]":
        
        return cls(error=ErrorViewModel(message, code))