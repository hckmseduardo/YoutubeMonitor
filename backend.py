from flask import Flask, request, jsonify, send_file
import csv
import os
from flask_cors import CORS  # Import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import fetch_channels
import parameters
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
csv_file_path = 'channels.csv'

def configure_parameters():
    args = parameters.fetch_parameters()
    video_output_directory = args.video_output_directory
    enable_download = args.enable_download
    print(f" * The video output directory is configured to {video_output_directory}")
    print(f" * Download videos is configured to {enable_download}")




@app.route('/channels', methods=['GET'])
def get_channels():
    if not os.path.exists(csv_file_path):
        return jsonify({'error': 'CSV file does not exist'}), 404
    channels = []
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        channels = [{'channelName': row[0], 'channelUrl': f"https://www.youtube.com/@{row[0]}/videos", 'channelOutputDirectory': f"{parameters.fetch_parameters().video_output_directory}/{row[0]}/"} for row in reader]

    # Sort the channels list by 'channelName' key in alphabetical order
    sorted_channels = sorted(channels, key=lambda x: x['channelName'].lower())

    return jsonify(sorted_channels)


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
    return jsonify({'message': 'Channel removed successfully'}), 200

def start_background_service():
    print(" * Configuring background service...")
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_channels.run, 'interval', minutes=1, max_instances=1)
    print(" * Starting background service...")
    scheduler.start()
    print(" * Background service started!")

  
if __name__ == '__main__':
    configure_parameters()
    start_background_service()
    app.run(debug=True)
