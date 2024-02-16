import requests
import re
from bs4 import BeautifulSoup
import subprocess

def extract_watch_urls(text):
    """
    Extracts URLs containing '/watch?v=' from a given text.

    Parameters:
    - text (str): The input text from which URLs will be extracted.

    Returns:
    - list: A list of extracted URLs containing '/watch?v='.
    """

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

def download_videos(urls, outputDirectory):
    for url in urls:
        print(url)
        subprocess.run(["yt-dlp", url, 
                        '--write-description', 
                        '--write-comments', 
                        '--write-thumbnail',
                        "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                        "-o", f"{outputDirectory}%(upload_date)s-%(title)s.%(ext)s"])


if __name__ == '__main__':
    urls = get_last_three_videos('https://www.youtube.com/@wrevolving/videos')
    download_videos(urls, "/mnt/media/Videos/wrevolving/")
    urls = get_last_three_videos('https://www.youtube.com/@Visao_Libertaria/videos') 
    download_videos(urls, "/mnt/media/Videos/ancapsu/")
    urls = get_last_three_videos('https://www.youtube.com/@FernandoUlrichCanal/videos')
    download_videos(urls, "/mnt/media/Videos/ulrich/")
    urls = get_last_three_videos('https://www.youtube.com/@oloopinfinito/videos')
    download_videos(urls, "/mnt/media/Videos/loop/")
    urls = get_last_three_videos('https://www.youtube.com/@Diolinux/videos')
    download_videos(urls, "/mnt/media/Videos/diolinux/")
    urls = get_last_three_videos('https://www.youtube.com/@Diolinuxlabs/videos')
    download_videos(urls, "/mnt/media/Videos/diolinux/")



# Print the extracted URLs
