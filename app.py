import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from src.main import analyze_video

app = Flask(__name__, static_folder='frontend', static_url_path='/static')

# Configuration
UPLOAD_FOLDER = 'data/input_videos'
ALLOWED_EXTENSIONS = {'mp4', 'mkv', 'avi', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the sleek professional frontend HTML."""
    return send_from_directory('frontend', 'index.html')

@app.route('/api/analyze', methods=['POST'])
def handle_analysis():
    """
    Accepts a video upload from the frontend, saves it locally,
    and runs the LogiCheck AI Analysis Pipeline on it.
    """
    if 'video' not in request.files:
        return jsonify({'error': 'No video file part in the request'}), 400
        
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            # Save the file temporarily
            file.save(filepath)
            
            # Run the LogiCheck Pipeline!
            print(f"Starting analysis for uploaded video: {filename}")
            results = analyze_video(filepath)
            
            # Clean up (Optional, commented out to keep the file for the video player if served locally)
            # os.remove(filepath) 
            
            return jsonify(results)
            
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            return jsonify({'error': f"Pipeline failed: {str(e)}"}), 500
            
    return jsonify({'error': 'File type not allowed. Please upload MP4/MKV/AVI/MOV'}), 400


if __name__ == '__main__':
    # Run the server. In production, use a WSGI server like gunicorn.
    app.run(host='0.0.0.0', port=5000, debug=True)
