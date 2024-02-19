import json
from flask import Flask, request, jsonify, send_file
import csv
import os
from flask_cors import CORS  # Import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import fetch_channels
import parameters
import requests
import shutil
import jellyfin

# Load the configuration file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)


VIDEO_OUTPUT_DIRECTORY = config['VIDEO_OUTPUT_DIRECTORY']

# Load the configuration file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

csv_file_path = 'channels.csv'
csv_catalog_path = 'catalog.csv'


app = Flask(__name__)
#CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://jellyfin.home:3000"]}})
CORS(app)


@app.route('/channels', methods=['GET'])
def get_channels():
    if not os.path.exists(csv_file_path):
        return jsonify({'error': 'CSV file does not exist'}), 404
    channels = []
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        channels = [{'channelName': row[0], 'channelUrl': f"https://www.youtube.com/@{row[0]}/videos", 'channelOutputDirectory': f"{VIDEO_OUTPUT_DIRECTORY}/{row[0]}/"} for row in reader]

    # Sort the channels list by 'channelName' key in alphabetical order
    sorted_channels = sorted(channels, key=lambda x: x['channelName'].lower())

    return jsonify(sorted_channels)

@app.route('/catalog', methods=['GET'])
def get_catalog():
    if not os.path.exists(csv_catalog_path):
        return jsonify({'error': 'CSV file does not exist'}), 404

    # Attempt to get the 'videoUrl' parameter from the query string
    filter_video_url = request.args.get('videoUrl', None)
    
    
    catalog = []
    with open(csv_catalog_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            # If 'videoUrl' query parameter is specified and matches the current row, add it to the channels list
            if filter_video_url:
                if filter_video_url == row[0]:
                    catalog.append({'videoUrl': row[0]})
            else:
                # If no 'videoUrl' query parameter is specified, add all rows to the channels list
                catalog.append({'videoUrl': row[0]})

    # Check if the catalog is empty after filtering (or if the file had no content)
    if not catalog:
        return jsonify({'error': 'No items found in the catalog'}), 404

    # Sort the catalog list by 'videoUrl' key in alphabetical order
    sorted_catalog = sorted(catalog, key=lambda x: x['videoUrl'].lower())

    return jsonify(sorted_catalog)


@app.route('/channels', methods=['POST'])
def add_channel():
    channel_data = request.json
    channel_name = channel_data['channelName']
    
    # Check if the CSV exists
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([channel_name])
        return jsonify({'message': 'Channel created successfully'}), 201

    # If the CSV exists, check if the channel already exists
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == channel_name:
                # Channel already exists
                return jsonify({'error': 'Channel already exists'}), 409

    # If channel name not found, append the new channel
    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([channel_name])
        jellyfin.add_library(channel_name, f"{VIDEO_OUTPUT_DIRECTORY}/{channel_name}/", "Movies")
    
    return jsonify({'message': 'Channel added successfully'}), 201

@app.route('/catalog', methods=['POST'])
def add_catalog():
    video_data = request.json
    channel_name = video_data['channelName']
    video_url = video_data['videoUrl']
    
    # Check if the CSV exists
    if not os.path.exists(csv_catalog_path):
        with open(csv_catalog_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([video_url, channel_name])
        return jsonify({'message': 'video created successfully'}), 201

    # If the CSV exists, check if the channel already exists
    with open(csv_catalog_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == video_url:
                # Channel already exists
                return jsonify({'error': 'Channel already exists'}), 409

    # If channel name not found, append the new channel
    with open(csv_catalog_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([video_url, channel_name])
    
    return jsonify({'message': 'Channel added successfully'}), 201

@app.route('/channels', methods=['DELETE'])
def remove_channel():
    channel_name = request.args.get('channelName')
    if not channel_name:
        return jsonify({'error': 'Channel name is required'}), 400
    rows = []
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = [row for row in reader if row[0] != channel_name]
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)
    jellyfin.delete_library(channel_name)
    delete_channel_from_catalog(channel_name)
    force_delete_folder(f"{VIDEO_OUTPUT_DIRECTORY}/{channel_name}/")
    return jsonify({'message': 'Channel removed successfully'}), 200


def refresh_library():
    added_new_content = fetch_channels.run()
    if (added_new_content):
        jellyfin.refresh_library()

def start_background_service():
    print("[backend] **Configuring background service...")
    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_library, 'interval', minutes=1, max_instances=1)
    print("[backend] **Starting background service...")
    scheduler.start()
    print("[backend] **Background service started!")

start_background_service()

import csv

def delete_channel_from_catalog(channel_name):
    """
    Removes all lines from the CSV file at file_path where the second column matches channel_name.

    Parameters:
    - file_path: str, the path to the CSV file.
    - channel_name: str, the name of the channel to remove from the catalog.

    Returns:
    - None, but modifies the CSV file by removing matching rows.
    """
    # Read the original data, skipping rows that match the condition
    with open(csv_catalog_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = [row for row in reader if row[1] != channel_name]
    
    # Write the filtered data back to the file
    with open(csv_catalog_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

def force_delete_folder(folder_path):
    try:
        # Check if the folder exists
        if not os.path.exists(folder_path):
            return "The specified folder does not exist."

        # Remove the folder and all its contents
        shutil.rmtree(folder_path)
        return "Folder deleted successfully."
    except Exception as e:
        # Return the error message if an exception occurs
        return f"An error occurred: {e}"


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
