import pandas as pd
import numpy as np
import seaborn as sns
from pprint import pprint
import praw
import creds
import datetime

def scrape_keyword(subreddits, keyword, limit=500):
    posts_data = []
    # Iterate over each subreddit in the provided list
    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.search(keyword, limit=limit):
            post_data = {
                'title': post.title,
                'author': str(post.author),
                'score': post.score,
                'subreddit': str(post.subreddit),
                'url': post.url,
                'created_utc': post.created_utc,
                'num_comments': post.num_comments
            }
            posts_data.append(post_data)

    # Convert the collected data into a DataFrame
    posts_df = pd.DataFrame(posts_data)
    
    # Sort the DataFrame by 'created_utc' in descending order to get the latest posts first
    posts_df.sort_values(by='created_utc', ascending=False, inplace=True)

    return posts_df

# Initialize praw Reddit instance with your credentials
reddit = praw.Reddit(client_id = creds.CLIENT_ID,          # your client id
                      client_secret = creds.CLIENT_SECRET,        # your client secret
                      user_agent = creds.USER_AGENT,)

# Define a list of subreddits you want to scrape
subreddits = ['politics', 'worldnews', 'news']

# Specify your keyword(s) and the number of posts (limit) you want to fetch
keyword = "modi, BJP, shah"
limit = 500

# Fetch the data
combined_df = scrape_keyword(subreddits, keyword, limit)

# Display the first few rows of the DataFrame
print(combined_df.head())
