class User:
    def __init__(self, item):
        self.username = item.get('username').get('S')
        self.password = item.get('password').get('S')
        self.posts = item.get('posts').get('N')
        
class Post:
    def __init__(self, item):
        self.username = item.get('username').get('S')
        # datetime.datetime.now().isoformat()
        self.timestamp = item.get('timestamp').get('S')
        self.image = item.get('image').get('S')
        self.title = item.get('title').get('S')
        self.body = item.get('body').get('S')

