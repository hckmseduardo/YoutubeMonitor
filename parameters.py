import argparse
def fetch_parameters():
    parser = argparse.ArgumentParser(description='Flask app with dynamic video_output_directory for channel outputs.')
    parser.add_argument('--video_output_directory', type=str, help='video_output_directory for channel output', required=False, default="/mnt/media/Videos")
    parser.add_argument('--enable-download', action='store_true', help='Enable the download feature')
    args = parser.parse_args()
    return args
