# YouTube Metrics Tracker

A Python script to track YouTube video metrics such as likes, views, and comments over time. The script uses web scraping techniques to fetch the data directly from YouTube and saves the results to a CSV file for further analysis.

## Features
- Fetches the number of likes, views, and comments for a given YouTube video.
- Tracks metrics over time with periodic checks.
- Saves metrics to a CSV file named after the YouTube video ID.
- Debug-friendly: Saves raw HTML for inspection if parsing fails.

## License
This project is licensed under the MIT License.

## Requirements
The script requires the following Python packages:
- `requests`
- `beautifulsoup4`

## Installation
To install the required packages, run:
```bash
pip install -r requirements.txt
```

## Usage
1. Clone this repository:
```bash
git clone https://github.com/<your-username>/youtube-metrics-tracker.git
cd youtube-metrics-tracker
```

2. Run the script:
```bash
python track_video.py <video_id> [--interval <interval_in_seconds>]
```

   - Replace `<video_id>` with the unique YouTube video ID (e.g., `wDchsz8nmbo`).
   - Optional: Set the interval in seconds between checks (default is 3600 seconds, i.e., 1 hour).

Example:
```bash
python track_video.py wDchsz8nmbo --interval 1800
```

3. Metrics are saved in `<video_id>.csv` in the following format:
```csv
timestamp,title,publishedAt,views,likes,comments
2024-11-14T12:00:00,Sample Video,2024-11-11T17:30:28,72940,2100,227
```

## Debugging
If likes or comments are missing:
1. Inspect the raw HTML saved as `<video_id>.html`.
2. Adjust the parsing logic in `track_video.py` if the YouTube structure changes.

## Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request.

## License
This project is licensed under the [MIT License](LICENSE).