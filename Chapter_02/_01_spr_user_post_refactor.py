class User:
    def __init__(self, user_id: str, username: str, email: str):
        self.user_id = user_id
        self.username = username
        self.email = email


class PostManager:
    def create_post(self, user: User, content: str):
        post = {
            "id": self.generate_post_id(),
            "user_id": user.user_id,
            "content": content,
            "likes": 0,
        }
        return post

    def generate_post_id(self):
        pass


class TimelineService:
    def get_timeline(self, user: User) -> list:
        pass


class ProfileManager:
    def update_profile(
        self, user: User, new_username: str = None, new_email: str = None
    ):
        if new_username:
            user.username = new_username
        if new_email:
            user.email = new_email