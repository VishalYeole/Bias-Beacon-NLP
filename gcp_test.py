import praw
import creds
import pandas as pd
from google.cloud import storage
from google.cloud import bigquery

# Reddit Scraping Function
def scrape_keyword(subreddits, keyword, limit=50):
    reddit = praw.Reddit(client_id = creds.CLIENT_ID,          # your client id
                      client_secret = creds.CLIENT_SECRET,        # your client secret
                      user_agent = creds.USER_AGENT,)
    posts_data = []
    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.search(keyword, limit=limit):
            post_data = {
                'title': post.title,
                'author': str(post.author),
                'score': post.score,
                'id': post.id,
                'subreddit': str(post.subreddit),
                'url': post.url,
                'created_utc': post.created_utc,
                'selftext': post.selftext,
                'num_comments': post.num_comments
            }
            posts_data.append(post_data)
    posts_df = pd.DataFrame(posts_data)
    posts_df.sort_values(by='created_utc', ascending=False, inplace=True)
    return posts_df

# Google Cloud Storage Upload Function
def upload_to_gcs(bucket_name, dataframe, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(dataframe.to_csv(index=False), 'text/csv')
    print(f"Data uploaded to {destination_blob_name} in bucket {bucket_name}.")

# Google BigQuery Upload Function
def upload_to_bigquery(dataframe, project_id, dataset_id, table_id):
    client = bigquery.Client(project=project_id)
    table_ref = client.dataset(dataset_id).table(table_id)
    job = client.load_table_from_dataframe(dataframe, table_ref, location="US")  # Change location if needed
    job.result()  # Wait for the job to complete
    print(f"Loaded {job.output_rows} rows into {dataset_id}:{table_id}.")

# Example usage
subreddits = ['politics', 'worldnews']
keyword = "global warming"
limit = 50
bucket_name = 'your_bucket_name'
gcs_file_name = 'subreddit_data.csv'
project_id = 'your_project_id'
dataset_id = 'your_dataset_id'
table_id = 'your_table_id'

# Scrape data
dataframe = scrape_keyword(subreddits, keyword, limit)

# Upload to Google Cloud Storage
upload_to_gcs(bucket_name, dataframe, gcs_file_name)

# Upload to Google BigQuery
upload_to_bigquery(dataframe, project_id, dataset_id, table_id)