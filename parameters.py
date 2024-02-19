import argparse
def fetch_parameters():
    parser = argparse.ArgumentParser(description='Flask app with dynamic video_output_directory for channel outputs.')
    parser.add_argument('--base-url', type=str, help='base_url to the backend', required=False, default="")
    args = parser.parse_args()
    return args
