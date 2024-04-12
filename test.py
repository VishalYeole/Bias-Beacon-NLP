import pandas as pd
import numpy as np
import seaborn as sns
from pprint import pprint
import praw
import creds

def scrape_keyword(subreddit_name, keyword, limit=50):
            subreddit = reddit.subreddit(subreddit_name)
            posts_data = []

            for post in subreddit.search(keyword, limit=limit):
                post_data = {
                    'title': post.title,
                    'author': str(post.author),
                    'score': post.score,
                    'id': post.id,
                    'subreddit': post.subreddit,
                    'url': post.url,
                    'created_utc': post.created_utc,
                    'selftext': post.selftext,
                    'num_comments':post.num_comments
                }
                posts_data.append(post_data)

            return pd.DataFrame(posts_data)

reddit = praw.Reddit(client_id=creds.CLIENT_ID,
                     client_secret= creds.CLIENT_SECRET,
                     user_agent=creds.USER_AGENT)

republican_df = scrape_keyword('politics',' modi, BJP, shah')
print(republican_df.head())

# democrat_df = scrape_keyword('politics',' democrats')
# print(democrat_df.head())