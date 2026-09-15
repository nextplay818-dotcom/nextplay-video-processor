from flask import Flask, request, jsonify, send_file
import os
import tempfile
import subprocess
import gdown

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "NextPlay Video Processor",
        "status": "ok"
    })


@app.route("/process", methods=["POST"])
def process_video():
    data = request.get_json(silent=True) or {}
    video_url = data.get("video_url")

    if not video_url:
        return jsonify({"error": "Falta video_url"}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.mp4")
        output_path = os.path.join(temp_dir, "output.mp4")

        try:
            gdown.download(
                url=video_url,
                output=input_path,
                quiet=False,
            )

            command = [
                "ffmpeg",
                "-y",
                "-i", input_path,
                "-t", "30",
                "-c:v", "libx264",
                "-preset", "fast",
                "-c:a", "aac",
                output_path
            ]

            subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            return send_file(
                output_path,
                mimetype="video/mp4",
                as_attachment=True,
                download_name="nextplay-short.mp4"
            )

        except Exception as e:
            return jsonify({
                "error": str(e)
            }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
