import jwt
from datetime import datetime, timedelta

class TokenManager:
    """Minimal JWT token manager (scaffold, spec-compliant)"""
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.algorithm = 'HS256'
    def generate_token(self, client_id, user_id, permissions, expires_hours=24):
        payload = {
            'client_id': client_id,
            'user_id': user_id,
            'permissions': permissions,
            'exp': datetime.utcnow() + timedelta(hours=expires_hours),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    def validate_token(self, token):
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except Exception:
            return None 