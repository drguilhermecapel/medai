import pytest
from app.exceptions import ValidationError, AuthenticationError, AuthorizationError

def test_validation_error():
    with pytest.raises(ValidationError):
        raise ValidationError("Test error")

def test_auth_errors():
    with pytest.raises(AuthenticationError):
        raise AuthenticationError("Auth failed")
    
    with pytest.raises(AuthorizationError):
        raise AuthorizationError("Not authorized")
