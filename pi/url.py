import re
from urllib.parse import urlsplit

SPOTIFY_REGEX = "^(https://open\\.spotify\\.com)/(album|track|playlist|episode|show)/([0-9a-zA-Z]{22})(\\?.*)?$"

def is_spotify_url(url):
    '''
    Check if a url is a valid spotify url
    '''
    if re.match(SPOTIFY_REGEX, url):
        return True
    else:
        return False

def spotify_get_type(url):
    '''
    Given a valid spotify url return the type
    of content (album, playlist, etc.)
    '''
    match= re.match(SPOTIFY_REGEX, url)
    if not match:
        raise ValueError("Incorrect spotify uri encoding.")
    else:
        return match.group(2)

def spotify_get_id(url):
    '''
    Given a valid spotify url return the spotify
    id
    '''
    match= re.match(SPOTIFY_REGEX, url)
    if not match:
        raise ValueError("Incorrect spotify uri encoding.")
    else:
        return match.group(3)

def is_youtube_url(url):
    '''
    Check if a url is a valid youtube url
    '''
    host = urlsplit(url).netloc
    return host == "youtu.be" or "youtube" in host
