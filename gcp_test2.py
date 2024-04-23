import praw
import pandas as pd
import datetime
import pytz
from google.cloud import storage
import os
import credsam

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

def upload_to_gcs(bucket_name, data, file_name):
    """
    Uploads data to Google Cloud Storage.

    :param bucket_name: The name of the GCS bucket
    :param data: The DataFrame to upload
    :param file_name: The name of the file to create in GCS
    """
    # Initialize GCS client
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)

    # Convert DataFrame to CSV
    csv_data = data.to_csv(index=False)

    # Create a new blob and upload the file's content
    blob = bucket.blob(file_name)
    blob.upload_from_string(csv_data, content_type='text/csv')
    
    print(f"Uploaded {file_name} to {bucket_name}.")

def scrape_subreddit(subreddits, start_date, end_date, limit=1000, bucket_name='your-bucket-name'):
    # Initialize praw Reddit instance with your credentials
    reddit = praw.Reddit(client_id=credsam.CLIENT_ID,
                         client_secret=credsam.CLIENT_SECRET,
                         user_agent=credsam.USER_AGENT)
    
    # Convert start and end dates to Unix timestamps
    start_timestamp = to_unix_timestamp(start_date)
    end_timestamp = to_unix_timestamp(end_date)
    
    for subreddit_name in subreddits:
        posts_data = []
        subreddit = reddit.subreddit(subreddit_name)
        # Loop through the hot posts of the subreddit up to the specified limit
        for post in subreddit.hot(limit=limit):
            created_utc = post.created_utc
            if start_timestamp <= created_utc <= end_timestamp:
                post_data = {
                    'title': post.title,
                    'score': post.score,
                    'subreddit': str(post.subreddit),
                    'selftext': post.selftext,
                    'url': post.url,
                    'created_utc': created_utc,
                    'num_comments': post.num_comments
                }
                posts_data.append(post_data)

        posts_df = pd.DataFrame(posts_data)
        posts_df['created_utc'] = pd.to_datetime(posts_df['created_utc'], unit='s')
        
        if not posts_df.empty:
            current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
            file_name = f"{subreddit_name}_{current_time}.csv"
            upload_to_gcs(bucket_name, posts_df, file_name)

# Example start and end dates
start_date = "2024-01-01 00:00:00"  # YYYY-MM-DD HH:MM:SS
end_date = "2024-09-03 23:59:59"    # Adjust this as needed

# Define a list of subreddits you want to scrape
subreddits = ['republican']

# Set the number of posts (limit) you want to fetch
limit = 1000

# Set the name of your GCS bucket
bucket_name = 'bucket-2-republican'

# Ensure your Google Cloud credentials are set
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:/Users/017409561/Documents/intricate-aria-420404-fb4f614bce51.json"

# Fetch the data and upload to GCS
scrape_subreddit(subreddits, start_date, end_date, limit, bucket_name)

# Print completion message
print(f"Data scraped for the period: {start_date} to {end_date} and uploaded to GCS.")
