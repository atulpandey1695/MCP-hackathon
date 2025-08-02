from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/api/githistory', methods=['POST'])
def write_json_to_file():
    """Write JSON POST body to a file"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if data is None:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include milliseconds
        filename = f'data/githistory.json'
        
        # Read existing data if file exists
        existing_data = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_content = f.read().strip()
                    if existing_content:
                        existing_data = json.loads(existing_content)
                        # If existing data is not a list, convert it to a list
                        if not isinstance(existing_data, list):
                            existing_data = [existing_data]
            except (json.JSONDecodeError, FileNotFoundError):
                existing_data = []
        
        # Add timestamp to new data
        data_with_timestamp = {
            "timestamp": timestamp,
            "data": data
        }
        
        # Append new data to existing data
        existing_data.append(data_with_timestamp)
        
        # Write updated data to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'status': 'success',
            'message': 'JSON data appended to file',
            'filename': filename,
            'timestamp': timestamp,
            'data_size': len(json.dumps(data)),
            'total_entries': len(existing_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting JSON Writer API on http://localhost:5000")
    print("POST endpoint: http://localhost:5000/api/githistory")
    app.run(host='localhost', port=5000, debug=True)
