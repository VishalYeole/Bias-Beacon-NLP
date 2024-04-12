import pandas as pd
import praw
import datetime
import pytz
import creds

def to_unix_timestamp(date_str, date_format='%Y-%m-%d %H:%M:%S', timezone=pytz.utc):
    """
    Convert a date string to a Unix timestamp.
    
    :param date_str: Date string
    :param date_format: Format of the date string
    :param timezone: Timezone for the date
    :return: Unix timestamp
    """
    dt = datetime.datetime.strptime(date_str, date_format)
    dt_tz = timezone.localize(dt)
    return dt_tz.timestamp()

def scrape_keyword(subreddits, keyword, start_date, end_date, limit=500):
    posts_data = []
    # Initialize praw Reddit instance with your credentials
    reddit = praw.Reddit(client_id=creds.CLIENT_ID,          # your client id
                         client_secret=creds.CLIENT_SECRET,  # your client secret
                         user_agent=creds.USER_AGENT,)       # your user agent
    
    # Convert start and end dates to Unix timestamps
    start_timestamp = to_unix_timestamp(start_date)
    end_timestamp = to_unix_timestamp(end_date)
    
    # Iterate over each subreddit in the provided list
    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.search(keyword, limit=limit):
            created_utc = post.created_utc
            # Filter posts by the specified timestamp range
            if start_timestamp <= created_utc <= end_timestamp:
                post_data = {
                    'title': post.title,
                    'author': str(post.author),
                    'score': post.score,
                    'subreddit': str(post.subreddit),
                    'url': post.url,
                    'created_utc': created_utc,
                    'num_comments': post.num_comments
                }
                posts_data.append(post_data)

    # Convert the collected data into a DataFrame
    posts_df = pd.DataFrame(posts_data)
    
    # Sort the DataFrame by 'created_utc' in descending order to get the latest posts first
    #posts_df.sort_values(by='created_utc', ascending=False, inplace=True)

    return posts_df

# Example start and end dates
start_date = "2021-04-05 00:00:00"  # YYYY-MM-DD HH:MM:SS
end_date = "2023-04-10 23:59:59"    # Adjust this as needed

# Define a list of subreddits you want to scrape
subreddits = ['politics', 'worldnews', 'news']

# Specify your keyword(s) and the number of posts (limit) you want to fetch
keyword = "modi, BJP, shah"

limit = 500

# Fetch the data
combined_df = scrape_keyword(subreddits, keyword, start_date, end_date, limit)

# Display the first few rows of the DataFrame
print(combined_df.head())

# Print the start and end dates for confirmation
print(f"Data scraped for the period: {start_date} to {end_date}")
