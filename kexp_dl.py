#!/usr/bin/env python3
"""
Download a show's mp3 from the KEXP archive.

Built with Claude Code, simple script to download KEXP shows by date via their public API.

Usage: kexp_dl.py <date> <show_name>
Author: @dencold
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API_URL = "https://api.kexp.org/get_streaming_url/?bitrate=256&timestamp={date}T15:01:46Z"
DOWNLOAD_DIR = os.path.join(os.environ["HOME"], "Downloads", "media-mgmt", "kexp")
USER_AGENT = "Mozilla/5.0 (compatible; kexp-dl/1.0)"


def fetch_streaming_info(date):
    url = API_URL.format(date=date)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def extract_show_name(sg_url):
    filename = sg_url.rsplit("/", 1)[-1]
    stem = filename[: -len(".mp3")] if filename.endswith(".mp3") else filename
    # filename format: {timestamp}-{n}-{n}-{show-name}
    parts = stem.split("-", 3)
    return parts[3] if len(parts) == 4 else stem, filename


def download_file(url, dest_path):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request) as response, open(dest_path, "wb") as out_file:
        out_file.write(response.read())


def main():
    parser = argparse.ArgumentParser(description="Download a show's mp3 from the KEXP archive.")
    parser.add_argument("date", help="Date of the show in ISO 8601 format (e.g. 2024-11-08)")
    parser.add_argument("show_name", help="Show name in kebab case (e.g. the-morning-show)")
    args = parser.parse_args()

    try:
        info = fetch_streaming_info(args.date)
    except urllib.error.URLError as e:
        print(f"Error fetching streaming URL: {e}", file=sys.stderr)
        sys.exit(1)

    sg_url = info.get("sg-url")
    if not sg_url:
        print("Error: no sg-url in server response", file=sys.stderr)
        sys.exit(1)

    show_name, filename = extract_show_name(sg_url)
    if show_name != args.show_name:
        print(f"Show name does not match KEXP mp3: {filename}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    dest_path = os.path.join(DOWNLOAD_DIR, f"{args.date}-{args.show_name}.mp3")

    print(f"Downloading {sg_url} -> {dest_path}")
    try:
        download_file(sg_url, dest_path)
    except urllib.error.URLError as e:
        print(f"Error downloading mp3: {e}", file=sys.stderr)
        sys.exit(1)

    print("Done.")


if __name__ == "__main__":
    main()
