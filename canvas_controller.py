from flask import Blueprint, request, jsonify
from spotify_canvas_service import get_canvases

canvas_bp = Blueprint("canvas", __name__)

@canvas_bp.route("/", methods=["GET"])
def fetch_canvas():
    track_id = request.args.get("trackId")
    if not track_id:
        return jsonify({"error": "Missing trackId parameter"}), 400
    try:
        canvas_data = get_canvases(f"spotify:track:{track_id}")
        from google.protobuf.json_format import MessageToDict
        return jsonify({"data": MessageToDict(canvas_data)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500