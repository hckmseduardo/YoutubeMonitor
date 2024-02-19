import json
import os
import requests

# Load the configuration file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

JELLYFIN_API_KEY = config['JELLYFIN_API_KEY']
JELLYFIN_SERVER_URL = config['JELLYFIN_SERVER_URL']
delete_library_endpoint = f'{JELLYFIN_SERVER_URL}/Library/VirtualFolders'
refresh_library_endpoint = f'{JELLYFIN_SERVER_URL}/Library/Refresh'


def get_header():
    return {
        'X-Emby-Token': JELLYFIN_API_KEY,
        'Content-Type': 'application/json'
    }


def add_library(name, path, CollectionType):
    add_library_endpoint = f'{JELLYFIN_SERVER_URL}/Library/VirtualFolders'
    # Check if the output directory exists, create it if not
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"[backgroundservice] **Created directory: {path}")
    # Your Jellyfin server details

    # The headers for authentication
    headers = get_header()

    params= {
        "name": name,        
        "CollectionType": CollectionType
        }
    
    payload = {       
        "Locations": [
            path
        ],
        "LibraryOptions": {
            "PathInfos": [
                {
                    "path": path
                }                
            ]
        }
    }


    print(f"[backend] **add the channel {name} to jellyfin")
    # Making the POST request to add the library
    response = requests.post(add_library_endpoint, headers=headers, params=params, json=payload)

    if response.status_code == 204:
        print("[backend] **Library added successfully.")
    else:
        print("[backend] **Failed to add library. Status Code:", response.status_code)
    
def delete_library(name):
    # The headers for authentication
    headers = get_header()

    params= {
        "name": name
        }
    
    print(f"[backend] **remove channel {name} from jellyfin")
    # Making the POST request to add the library
    response = requests.delete(delete_library_endpoint, headers=headers, params=params)

    if response.status_code == 204:
        print(f"[backend] **Library removed successfully.")
    else:
        print(f"[backend] **Failed to remove library {name}. Status Code:", response.status_code)


def refresh_library():
        # The headers for authentication
        headers = get_header()
        print(f"[backend] **refresh jellyfin library")
        # Making the POST request to add the library
        response = requests.post(refresh_library_endpoint, headers=headers)

        if response.status_code == 204:
            print(f"[backend] **jellyfin library refresh started successfully.")
        else:
            print(f"[backend] **Failed to refresh jellyfin library. Status Code:", response.status_code)
