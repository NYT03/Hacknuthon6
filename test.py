import os
import subprocess

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Directory to save uploaded test files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    # More detailed debugging
    # print("Request received at /upload")
    print(request.files)
    # print(f"Form data: {request.form}")
    # print(f"Files: {request.files}")
    # print(f"Content-Type: {request.headers.get('Content-Type', 'No Content-Type header')}")
    
    if 'file' not in request.files:
        print("No 'file' found in request.files")
        return jsonify({'error': 'No file part', 'available_keys': list(request.files.keys())}), 400

    file = request.files['file']
    if file.filename == '':
        print("Filename is empty")
        return jsonify({'error': 'No selected file'}), 400

    print(f"Received file: {file.filename}")
    
    # Save the uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    print(f"File saved to {file_path}")

    # Run the Selenium test
    try:
        print(f"Running command: node {file_path}")
        result = subprocess.run(['node', file_path], capture_output=True, text=True)
        output = result.stdout
        error = result.stderr
        print(f"Command return code: {result.returncode}")
        print(f"Command output: {output}")
        print(f"Command error: {error}")

        if result.returncode == 0:
            return jsonify({'message': 'Test executed successfully', 'output': output, 'file_path': file_path}), 200
        else:
            return jsonify({'error': 'Test execution failed', 'details': error}), 500
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Simple test endpoint
@app.route('/test', methods=['GET'])
def test_cors():
    return jsonify({'message': 'CORS is enabled'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)