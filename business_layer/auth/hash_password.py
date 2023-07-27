from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HashPassword:
    """Класс содержит методы создания хэша пароля и верификации пароля"""

    def create_hash(self, password: str):
        """Метод создает хэш пароля, используя алгоритм bcrypt"""
        return pwd_context.hash(password)

    def verify_hash(self, plain_password: str, hashed_password: str):
        """Метод принимает на вход пароль и его хэш и возвращает
        результат сверки пароля с хэшем"""
        return pwd_context.verify(plain_password, hashed_password)
