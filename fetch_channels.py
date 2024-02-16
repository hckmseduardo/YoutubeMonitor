import requests
import re
import subprocess

def extract_watch_urls(text):
    # Regular expression to find patterns that match "/watch?v=" followed by any character except for spaces or quotes
    pattern = r'\"/watch\?v=[^\"\s]+\"'
    
    # Find all occurrences of the pattern in the text
    matches = re.findall(pattern, text)

    # Extract and clean the URLs from the matches
    urls = [match.strip("\"") for match in matches]

    return urls


def get_last_three_videos(channel_url):
    # YouTube's server-side rendering might not include all video details in the HTML response,
    # making it hard to scrape video information directly from the channel's main page.
    # This is a placeholder to show the approach.

    # Send a request to the channel URL
    response = requests.get(channel_url)
    response.raise_for_status()  # Raise an error for bad responses

    # Extract URLs
    extracted_urls = extract_watch_urls(response.text)

    i = 0
    urls = []
    for url in extracted_urls:
        urls.append(f"https://www.youtube.com{url}")
        i=i+1
        if(i==3):
            break
    return urls

def download_videos(url, outputDirectory):
    subprocess.run(["yt-dlp", url, 
                    '--write-description', 
                    '--write-comments', 
                    '--write-thumbnail',
                    "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                    "-o", f"{outputDirectory}%(upload_date)s-%(title)s.%(ext)s"])



def run():
    print("This task update videos every 1 minute.")
    url = 'http://localhost:5000/channels'  # Change this URL to your Flask backend URL if it's different
    response = requests.get(url)
    
    if response.status_code == 200:
        channels = response.json()
        for channel in channels:
            print(f"last 3 videos of {channel['channelName']}" )
            urls = get_last_three_videos(channel['channelUrl'])
            for url in urls:
                print(url)
                if (download_videos):
                    download_videos(urls, channel['channelOutputDirectory'])
            
    else:
        print(f"Failed to fetch channels. Status code: {response.status_code}")

