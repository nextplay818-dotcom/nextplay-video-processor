from flask import Flask, request, jsonify, send_file
import os
import tempfile
import subprocess

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "NextPlay Video Processor",
        "status": "ok"
    })


@app.route("/process", methods=["POST"])
def process_video():
    if "video" not in request.files:
        return jsonify({
            "error": "No se recibió ningún video"
        }), 400

    video = request.files["video"]

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.mp4")
        output_path = os.path.join(temp_dir, "output.mp4")

        video.save(input_path)

        command = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-t", "60",
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            output_path
        ]

        try:
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

        except subprocess.CalledProcessError as e:
            return jsonify({
                "error": "FFmpeg no pudo procesar el video",
                "details": e.stderr.decode(
                    "utf-8",
                    errors="ignore"
                )
            }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
