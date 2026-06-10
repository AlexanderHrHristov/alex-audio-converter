BASIC_PROFILES = {
    "Car Standard": {"format": "mp3", "bitrate": "320"},
    "Car Premium": {"format": "m4a", "bitrate": "256"},
    #"Car Premium Max": {"format": "m4a", "bitrate": "320"},
    "Fast Original": {"format": "original", "bitrate": "copy"},
    "Hi-Fi": {"format": "flac", "bitrate": "lossless"},
    "Archive": {"format": "wav", "bitrate": "lossless"},
}

FORMATS = ["mp3", "m4a", "flac", "wav", "ogg", "opus", "original"]
BITRATES = ["96", "128", "192", "256", "320", "lossless", "copy"]
SPLIT_MODES = ["No split", "By chapters", "By silence", "From timestamps file"]