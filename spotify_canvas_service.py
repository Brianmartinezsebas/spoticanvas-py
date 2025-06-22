import requests
from spotify_auth_service import get_token
from proto import _canvas_pb2

def get_canvases(track_uri):
    access_token = get_token()
    canvas_request = _canvas_pb2.CanvasRequest()
    track = canvas_request.tracks.add()
    track.track_uri = track_uri
    request_bytes = canvas_request.SerializeToString()

    resp = requests.post(
        "https://spclient.wg.spotify.com/canvaz-cache/v0/canvases",
        data=request_bytes,
        headers={
            "Accept": "application/protobuf",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Language": "en",
            "User-Agent": "Spotify/9.0.34.593 iOS/18.4 (iPhone15,3)",
            "Accept-Encoding": "gzip, deflate, br",
            "Authorization": f"Bearer {access_token}",
        },
        timeout=10,
    )
    resp.raise_for_status()
    canvas_response = _canvas_pb2.CanvasResponse()
    canvas_response.ParseFromString(resp.content)
    return canvas_response