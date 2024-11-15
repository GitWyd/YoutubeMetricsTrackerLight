import time
import datetime
import csv
import requests
import json
import re
from bs4 import BeautifulSoup


def save_html_to_file(video_id, html):
    """
    Save the fetched HTML to a file for debugging.
    """
    filename = f"{video_id}.html"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html)


def extract_yt_initial_data(html):
    """
    Extract the `ytInitialData` JSON from the HTML.
    """
    # Use regex to locate the `ytInitialData` JavaScript variable
    match = re.search(r'var ytInitialData = ({.*?});</script>', html, re.DOTALL)
    if match:
        try:
            json_data = json.loads(match.group(1))
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    print("No `ytInitialData` found in the HTML.")
    return None


def extract_likes_and_comments(yt_initial_data):
    """
    Extract likes and comments from the `ytInitialData` JSON.
    """
    likes = None
    comments = None

    # Extract likes from `videoPrimaryInfoRenderer`
    try:
        video_primary_info = yt_initial_data.get("contents", {}).get("twoColumnWatchNextResults", {}).get(
            "results", {}
        ).get("results", {}).get("contents", [])
        for item in video_primary_info:
            video_info = item.get("videoPrimaryInfoRenderer", {})
            if not video_info:
                continue

            video_actions = video_info.get("videoActions", {})
            top_buttons = video_actions.get("menuRenderer", {}).get("topLevelButtons", [])
            for button in top_buttons:
                segmented_button = button.get("segmentedLikeDislikeButtonViewModel", {})
                like_button = segmented_button.get("likeButtonViewModel", {}
                    ).get("likeButtonViewModel", {}
                    ).get("toggleButtonViewModel", {}
                    ).get("toggleButtonViewModel", {}
                    ).get("defaultButtonViewModel", {}
                    ).get("buttonViewModel", {})

                if like_button.get("iconName") == "LIKE":
                    likes_text = like_button.get("title", "")
                    if "K" in likes_text:
                        likes = int(float(likes_text.replace("K", "")) * 1000)
                    elif "M" in likes_text:
                        likes = int(float(likes_text.replace("M", "")) * 1000000)
                    else:
                        likes = int(likes_text.replace(",", ""))
                    break  # Exit once likes are found
    except Exception as e:
        print(f"Error extracting likes: {e}")

    # Extract comments from `engagementPanels`
    try:
        engagement_panels = yt_initial_data.get("engagementPanels", [])
        for panel in engagement_panels:
            if panel.get("engagementPanelSectionListRenderer", {}).get("panelIdentifier") == "engagement-panel-comments-section":
                header = panel.get("engagementPanelSectionListRenderer", {}).get("header", {})
                contextual_info = header.get("engagementPanelTitleHeaderRenderer", {}).get("contextualInfo", {})
                comments_text = contextual_info.get("runs", [{}])[0].get("text", "")
                comments = int(comments_text.replace(",", ""))
    except Exception as e:
        print(f"Error extracting comments: {e}")

    return likes, comments


def get_video_metrics(video_id):
    """
    Scrape video metrics including likes and comments from YouTube.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch video page (status code: {response.status_code})")

    # Save HTML for debugging
    save_html_to_file(video_id, response.text)

    # Extract the `ytInitialData` JSON
    yt_initial_data = extract_yt_initial_data(response.text)

    # Extract likes and comments from the JSON
    likes, comments = None, None
    if yt_initial_data:
        likes, comments = extract_likes_and_comments(yt_initial_data)

    # Extract video title and views using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("meta", {"name": "title"})["content"]
    views = int(soup.find("meta", {"itemprop": "interactionCount"})["content"])
    upload_date = soup.find("meta", {"itemprop": "uploadDate"})["content"]

    data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "title": title,
        "publishedAt": upload_date,
        "views": views,
        "likes": likes or "Unavailable",
        "comments": comments or "Unavailable",
    }
    return data


def write_metrics_to_csv(video_id, data):
    """
    Write metrics to a CSV file named after the video ID.
    """
    filename = f"{video_id}.csv"
    file_exists = False

    try:
        with open(filename, "r"):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(filename, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()  # Write headers if file does not exist
        writer.writerow(data)


def track_video(video_id, interval=3600):
    """
    Periodically fetch and save video metrics.
    """
    while True:
        try:
            data = get_video_metrics(video_id)
            write_metrics_to_csv(video_id, data)
            print(f"Recorded data: {data}")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(interval)  # Wait for the next interval


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Track YouTube video metrics.")
    parser.add_argument("video_id", type=str, help="YouTube video ID (e.g., dQw4w9WgXcQ)")
    parser.add_argument("--interval", type=int, default=3600, help="Time interval in seconds between checks (default: 1 hour)")
    args = parser.parse_args()

    try:
        track_video(args.video_id, args.interval)
    except KeyboardInterrupt:
        print("Tracking stopped by user.")
