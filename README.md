# Spotify Canvas API (Python Version)

This is a Python reimplementation of the [Spotify-Canvas-API](https://github.com/Paxsenix0/Spotify-Canvas-API) originally created by [Paxsenix0](https://github.com/Paxsenix0). It allows you to fetch the animated canvas videos used by Spotify for specific tracks, using a valid `sp_dc` cookie.

## 📁 Project Structure

```
spoticanvas-py/
│
├── main.py                     # Flask server entry point
├── canvas_controller.py        # Flask blueprint with canvas route
├── spotify_auth_service.py     # Handles authentication and sp_dc token logic
├── spotify_canvas_service.py   # Logic to fetch Spotify canvas videos
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (e.g., SP_DC)
├── README.md                   # You're reading it!
└── proto/
    └── _canvas_pb2.py          # Generated by protoc from your .proto file
```

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Brianmartinezsebas/spoticanvas-py.git
cd spoticanvas-py
```

### 2. Install Dependencies

Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory with the following:

```
SP_DC=your_sp_dc_cookie_here
```

> 🔒 Your `sp_dc` cookie can be extracted from your Spotify web session (used for authentication).

### 4. Run the Server

```bash
python main.py
```

The server should start on:

```
http://localhost:3000
```

## 📡 API Usage

### GET `/api/canvas/?trackId=`

**Response:**

A JSON object containing canvas URLs or an error message.

```json
{
  "data": {
    "canvases": [
      {
        "artist": {
          "artistImgUrl": "https://i.scdn.co/image/ab6761610000f1788bde168596b92de17fdfcc6d",
          "artistName": "ACRU",
          "artistUri": "spotify:artist:0bYQe0JDIjxkSHQoXlfngl"
        },
        "canvasUri": "spotify:canvas:3CWsGNVKham58Yqf1ofUu8",
        "canvasUrl": "https://canvaz.scdn.co/upload/artist/0bYQe0JDIjxkSHQoXlfngl/video/773556b29e1f4827ba11cfcd741ac8d4.cnvs.mp4",
        "id": "773556b29e1f4827ba11cfcd741ac8d4",
        "trackUri": "spotify:track:2RsQG67mE9to2O6BS9QRbY"
      }
    ]
  }
}
```

## 🛠 Requirements

- Python 3.8+
- `protoc` (Protocol Buffers Compiler) if you need to regenerate `_canvas_pb2.py`

To regenerate protobuf:

```bash
protoc --proto_path=proto --python_out=proto proto/_canvas.proto
```

## 📄 License

This project is for educational purposes and follows the same guidelines as the original [Spotify-Canvas-API](https://github.com/Paxsenix0/Spotify-Canvas-API). Be aware of Spotify's [Terms of Service](https://www.spotify.com/legal/end-user-agreement/) when using internal APIs.

---

**Author:** Xer0  
Forked from [Paxsenix0](https://github.com/Paxsenix0)
