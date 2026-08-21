class MockUser:
    def __init__(self, username: str, password_hash: str, role: str):
        self.username = username
        self.password_hash = password_hash
        self.role = role

class UserRepository:
    def __init__(self, db):
        self.db = db

    def get_user_by_username(self, username: str):
        # Mock user for now since the real model is missing
        # If this is hit, return a dummy user to allow the login to proceed if password matches
        # Note: In a real app, query the database.
        from app.core.security import hash_password
        if username == "admin":
            return MockUser("admin", hash_password("admin"), "admin")
        return None

    def create_user(self, user_data: dict):
        return MockUser(user_data["username"], user_data["password_hash"], user_data.get("role", "developer"))
