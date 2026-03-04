---

# 📺 YouTube Playlist Downloader

A powerful, "polite," and versatile YouTube metadata extractor and media downloader. Whether you need to sync a channel's playlists to your **cliamp** player, export a library to **CSV**, or download high-quality **MP3s**, this script handles it with built-in anti-abuse delays to keep your IP safe.

## ✨ Features

* **Dual Scan Modes**:
* **Quick Scan**: Extracts playlist containers from a channel.
* **Deep Scan (`-f`)**: Recursively dives into every playlist to extract individual tracks.


* **Multi-Format Exporter**: Support for `cliamp` (TOML), `M3U`, `JSON`, and `CSV`.
* **Media Downloader**: Download Audio (MP3) or Video (MP4/WebM) directly.
* **Smart Filtering**: Automatically skips "Upcoming" events, live stream premieres, and deleted/private videos.
* **Anti-Abuse System**: Implements randomized cooldown delays between requests to prevent YouTube rate-limiting.
* **Safety First**: Includes an execution plan summary and confirmation prompt before starting heavy tasks.

---

## 🚀 Installation

### 1. Prerequisites

Ensure you have [Python 3.x](https://www.python.org/) installed and the following dependencies:

```bash
# Install yt-dlp (the core engine)
pip install yt-dlp

# or with curl to get the latest version directly
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
chmod a+rx /usr/local/bin/yt-dlp  # Make executable

# Ensure ffmpeg is installed on your system (Required for MP3 conversion and merging video)
# Linux: sudo apt install ffmpeg
# macOS: brew install ffmpeg
# Windows: winget install ffmpeg

```

### 2. Setup

Clone this repository or save `yt_pls_downloader.py` to your local machine.

---

## 📖 Usage Guide

### Basic Explorer (Preview Only)

See what's on a channel without saving anything:

```bash
python yt_pls_downloader.py https://www.youtube.com/@ChannelName/playlists

```

### Exporting Playlists

```bash
# Export to cliamp (TOML)
python yt_pls_downloader.py [URL] --to-pls cliamp -f

# Export to CSV for Excel/Google Sheets
python yt_pls_downloader.py [URL] --to-pls csv -n my_export

```

### Downloading Media

```bash
# Download all tracks as high-quality MP3s
python yt_pls_downloader.py [URL] --download mp3 -o ~/Music/YouTube -f

```

---

## 🛠 Command Line Arguments

| Argument | Description |
| --- | --- |
| `url` | The YouTube channel playlists URL (Required). |
| `--to-pls` | Export format: `cliamp`, `m3u`, `json`, `csv`. |
| `--download` | Media format: `mp3`, `mp4`, `webm`. |
| `-o`, `--output` | Output directory (for downloads) or file path (for playlist). |
| `-n`, `--name` | Custom filename for the playlist export. |
| `-f`, `--flatten` | **Deep Scan**: Extract every video inside every playlist. |
| `-y`, `--yes` | Skip the execution plan confirmation and start immediately. |

---

## 🔍 Troubleshooting

### 1. `ffmpeg` not found

**Error:** `Postprocessing: ffmpeg not found. Please install it.`

* **Solution:** The script requires `ffmpeg` to convert YouTube's native audio to MP3 or to merge high-quality video and audio streams.
* **Check:** Run `ffmpeg -version` in your terminal. If it's not recognized, follow the installation steps in the Prerequisites section.

### 2. `yt-dlp` is out of date

**Error:** `Sign in to confirm you are not a bot` or `Unable to extract video data`.

* **Solution:** YouTube frequently updates its site, which can break older versions of `yt-dlp`. Update it using:
```bash
pip install -U yt-dlp

```



### 3. Rate Limiting (HTTP Error 429)

**Error:** `HTTP Error 429: Too Many Requests`.

* **Solution:** Even with our built-in delays, scanning massive channels (100+ playlists) can trigger blocks.
* **Fix:** Avoid using a VPN (as many VPN IPs are flagged) or wait 24 hours. The script's randomized 3–6s delay is designed to minimize this risk.

### 4. Empty Playlists

**Problem:** The script finishes but 0 items are found.

* **Solution:** Ensure the URL you provide ends in `/playlists`. If the channel has hidden their playlists or made them private, `yt-dlp` cannot "see" them.

---

## 🛡 Anti-Abuse Logic

To protect your IP from being flagged, the script implements:

1. **Metadata Delay**: 1s delay between playlist extractions.
2. **Download Cooldown**: Randomized 3–6s delay between every file download.

---

## ⚖️ License

This project is for personal use and educational purposes. Please respect YouTube's Terms of Service and the copyrights of content creators.

---