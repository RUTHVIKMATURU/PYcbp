from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey"  # For session management and flash messages

# File upload configuration
UPLOAD_FOLDER = "upload"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Updated justify_text function
def justify_text(input_file, output_file, width):
    try:
        # Read input file
        with open(input_file, 'r') as f:
            lines = f.readlines()

        justified_lines = []
        for line in lines:
            words = line.split()
            if not words:  # Handle blank lines
                justified_lines.append("")
                continue

            current_line = []
            line_length = 0
            for word in words:
                if line_length + len(word) + len(current_line) > width:
                    # Distribute spaces evenly
                    spaces = width - line_length
                    for i in range(spaces):
                        current_line[i % (len(current_line) - 1 or 1)] += ' '
                    justified_lines.append(''.join(current_line))
                    current_line = []
                    line_length = 0
                current_line.append(word)
                line_length += len(word)

            # Add the last line (left-aligned)
            justified_lines.append(' '.join(current_line))

        # Ensure output file is created if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write('\n'.join(justified_lines))

        return True

    except Exception as e:
        print(f"Error during justification: {e}")
        return False


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Validate line width
            line_width = request.form.get("line_width")
            if not line_width.isdigit() or int(line_width) <= 0:
                flash("Line width must be a positive integer.")
                return redirect(url_for("index"))

            width = int(line_width)

            # Validate file upload
            if "file" not in request.files:
                flash("No file part in the request.")
                return redirect(url_for("index"))

            file = request.files["file"]
            if file.filename == "":
                flash("No file selected.")
                return redirect(url_for("index"))

            # Save input file
            input_path = os.path.join(UPLOAD_FOLDER, file.filename)
            output_path = os.path.join(UPLOAD_FOLDER, f"justified_{file.filename}")
            file.save(input_path)

            # Process file for justification
            if justify_text(input_path, output_path, width):
                return redirect(url_for("download_file", filename=f"justified_{file.filename}"))
            else:
                flash("Error processing the file.")
                return redirect(url_for("index"))
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}")
            return redirect(url_for("index"))

    return render_template("index.html")


@app.route("/download/<filename>")
def download_file(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(path):
        flash("File not found.")
        return redirect(url_for("index"))
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
