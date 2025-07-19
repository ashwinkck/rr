import praw
from datetime import datetime

# Replace these with your actual credentials
client_id = "D4dA47GQcl-on4gNMn1HSg"
client_secret = "nU0nwRVM_-HfOS7n3WdtQ6h7WYkHkw"
user_agent = "RiskRoboApp/0.1 by ashhigh"

# Initialize Reddit instance
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

def fetch_reddit_posts(subreddit_name, limit=10):
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    for post in subreddit.hot(limit=limit):
        posts.append({
            "title": post.title,
            "score": post.score,
            "url": post.url,
            "comments": post.num_comments,
            "created": datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            "author": str(post.author)
        })
    return posts

# Example usage
if __name__ == "__main__":
    posts = fetch_reddit_posts("ethereum", limit=5)
    for post in posts:
        print(post)
