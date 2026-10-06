from fastapi import HTTPException, status


class DomainException(HTTPException):
    pass

class NotAuthenticatedException(DomainException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

class PermissionDeniedException(DomainException):
    def __init__(self, detail: str = "You dont have permission to perform this action") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class ResourceNotFoundException(DomainException):
    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")

class ConflictException(DomainException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)