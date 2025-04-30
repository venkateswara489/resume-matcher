from flask import Flask, render_template, request, jsonify
import os
from matcher import ResumeMatcher
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

matcher = ResumeMatcher()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/match', methods=['POST'])
def match_resume():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        resume_text = data.get('resume_text')
        job_description = data.get('job_description')
        
        if not resume_text:
            return jsonify({'error': 'No resume text provided'}), 400
            
        if not job_description:
            return jsonify({'error': 'No job description provided'}), 400
        
        result = matcher.calculate_match(resume_text, job_description)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
