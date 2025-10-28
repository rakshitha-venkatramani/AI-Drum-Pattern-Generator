from flask import Flask, render_template, request, send_from_directory
import subprocess
import os
import shutil
import glob

app = Flask(__name__)
OUTPUT_DIR = "../output"
MIDI_DEST = "static/midi"

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    genre = request.form.get("genre")
    
    # Run the original BBN script with input via subprocess
    process = subprocess.run(
        ["python", "../scripts/drum_bbn_main.py"],
        input=f"{genre}\n",
        text=True,
        capture_output=True
    )

    # Look for the latest generated MIDI file
    files = glob.glob(os.path.join(OUTPUT_DIR, "generated_loop_*.mid"))
    latest_file = max(files, key=os.path.getctime)
    
    # Copy to static folder
    if not os.path.exists(MIDI_DEST):
        os.makedirs(MIDI_DEST)
    shutil.copy(latest_file, MIDI_DEST)
    
    filename = os.path.basename(latest_file)
    return render_template("result.html", midi_file=filename)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(MIDI_DEST, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
