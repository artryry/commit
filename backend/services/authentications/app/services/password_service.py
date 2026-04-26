import bcrypt

from config import cfg


class PasswordService:
    @staticmethod
    def check_password_strength(password: str) -> bool:
        return (
                len(password) >= cfg.MIN_PASSWORD_LENGTH and
                any(c.isupper() for c in password) and 
                any(c.islower() for c in password) and 
                any(c.isdigit() for c in password)
            )


    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
        
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        