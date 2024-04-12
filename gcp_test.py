import pandas as pd
import praw
import datetime
import pytz
from google.cloud import storage
import os
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

def scrape_keyword(subreddits, keyword, start_date, end_date, limit=500, bucket_name='your-bucket-name'):
    # Initialize praw Reddit instance with your credentials
    reddit = praw.Reddit(client_id=creds.CLIENT_ID,          # your client id
                         client_secret=creds.CLIENT_SECRET,  # your client secret
                         user_agent=creds.USER_AGENT,)       # your user agent
    
    # Convert start and end dates to Unix timestamps
    start_timestamp = to_unix_timestamp(start_date)
    end_timestamp = to_unix_timestamp(end_date)
    
    for subreddit_name in subreddits:
        posts_data = []
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
        
        if not posts_df.empty:
            # Upload data to GCS for each subreddit
            current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
            file_name = f"{subreddit_name}_{current_time}.csv"
            upload_to_gcs(bucket_name, posts_df, file_name)

# Example start and end dates
start_date = "2021-04-05 00:00:00"  # YYYY-MM-DD HH:MM:SS
end_date = "2023-04-10 23:59:59"    # Adjust this as needed

# Define a list of subreddits you want to scrape
subreddits = ['politics', 'worldnews', 'news']

# Specify your keyword(s) and the number of posts (limit) you want to fetch
keyword = "modi, BJP, shah"

limit = 500

# Set the name of your GCS bucket
bucket_name = 'subreddit_bucket_1'

# Ensure your Google Cloud credentials are set
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/credentials-file.json"

# Fetch the data and upload to GCS
scrape_keyword(subreddits, keyword, start_date, end_date, limit, bucket_name)

# Print completion message
print(f"Data scraped for the period: {start_date} to {end_date} and uploaded to GCS.")
