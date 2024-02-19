import os
import parameters
import requests
import re
import subprocess
import json


# Load the configuration file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)


BACKEND_BASE_URL = config['BACKEND_BASE_URL']

def extract_watch_urls(text):
    # Regular expression to find patterns that match "/watch?v=" followed by any character except for spaces or quotes
    pattern = r'\"/watch\?v=[^\"\s]+\"'
    
    # Find all occurrences of the pattern in the text
    matches = re.findall(pattern, text)

    # Extract and clean the URLs from the matches
    urls = [match.strip("\"") for match in matches]

    return urls


def get_last_videos(channel_url, how_many_videos):
    # YouTube's server-side rendering might not include all video details in the HTML response,
    # making it hard to scrape video information directly from the channel's main page.
    # This is a placeholder to show the approach.

    # Send a request to the channel URL
    response = requests.get(channel_url)
    response.raise_for_status()  # Raise an error for bad responses

    # Extract URLs
    extracted_urls = extract_watch_urls(response.text)

    i = 0
    lastXVideos = []
    for url in extracted_urls:
        lastXVideos.append(f"https://www.youtube.com{url}")
        i=i+1
        if(i==how_many_videos):
            break
    return lastXVideos

def download_videos(channel_name, url, outputDirectory):
    print(f"[backgroundservice] **calling backend to check if the video already exists, {channel_name}, {url}")
    # Make a GET request to the endpoint with the query parameter
    response = requests.get(f'{BACKEND_BASE_URL}/catalog?videoUrl={url}')
    # Check if the request was successful
    exists = response.status_code == 200
    

    if exists:
        print(f"[backgroundservice] **download_videos - skiping download video {url} because has already been downloaded before")
    else:
        # Check if the output directory exists, create it if not
        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)
            print(f"[backgroundservice] **Created directory: {outputDirectory}")
        subprocess.run(["yt-dlp", url, 
                '--write-description', 
                '--write-thumbnail',
                "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                "-o", f"{outputDirectory}%(upload_date)s-%(title)s.%(ext)s"])
    
        print(f"[backgroundservice] **download_videos - adding video {url} to the catalog")
        response = requests.post(f"{BACKEND_BASE_URL}/catalog", json={"channelName":channel_name, "videoUrl": url})
        if response.status_code == 201:
            print(f"[backgroundservice] **download_videos - video {url} has been successiful added to the catalog")
            return True

def run():
    print("[backgroundservice] **This task update videos every 1 minute.")
    url = 'http://localhost:5000/channels'  # Change this URL to your Flask backend URL if it's different
    response = requests.get(url)
    newContent = False
    
    if response.status_code == 200:
        channels = response.json()
        for channel in channels:
            print(f"[backgroundservice] **CHANNEL************************************" )
            print(f"[backgroundservice] **run() - searching last 3 videos of {channel['channelName']}" )
            urls = get_last_videos(channel['channelUrl'], 3)
            for url in urls:
                print(f"[backgroundservice] **VIDEO {url} ***************")
                newContent = newContent or download_videos(channel['channelName'], url, channel['channelOutputDirectory'])
                print(f"[backgroundservice] **newContent {newContent}")
    else:
        print(f"[backgroundservice] **run() - Failed to fetch channels. Status code: {response.status_code}")
    
    return newContent

