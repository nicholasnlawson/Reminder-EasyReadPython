from flask import Flask, render_template, send_from_directory, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# Path to the original HTML file
# The original HTML file is in the parent directory
ORIGINAL_HTML_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'chartgenerator.html')

@app.route('/')
def index():
    # Render the Flask UI template
    return render_template('flask_ui_updated.html')

@app.route('/original')
def original():
    # Serve the original HTML file directly
    try:
        with open(ORIGINAL_HTML_PATH, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        # If the file is not found, return a simple message
        return f"Original HTML file not found at: {ORIGINAL_HTML_PATH}"

@app.route('/extract_medications', methods=['POST'])
def extract_medications():
    """
    This route is used to extract medication information from a discharge letter.
    The actual extraction is done client-side using JavaScript.
    """
    # Get the discharge letter text from the request
    data = request.json
    discharge_text = data.get('discharge_text', '')
    
    # We'll just return a success response, as the actual extraction
    # will be handled by the JavaScript function
    return jsonify({
        'status': 'success',
        'message': 'Use the extractMedicationsFromDischargeLetter function in the client-side JavaScript'
    })

@app.route('/generate_leaflet', methods=['POST'])
def generate_leaflet():
    """
    Generate a patient information leaflet based on the provided medication name.
    In a production environment, this would retrieve a pre-made leaflet from a database.
    """
    data = request.json
    medication_name = data.get('medicationName', '')
    
    # Generate a placeholder HTML leaflet
    # In a real application, you would look up the medication in a database
    # and retrieve the corresponding pre-made leaflet
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Patient Information Leaflet - {medication_name}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
            }}
            h1, h2 {{
                color: #2c3e50;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 10px;
                border-bottom: 2px solid #3498db;
            }}
            .section {{
                margin-bottom: 20px;
                padding: 15px;
                background-color: #f9f9f9;
                border-radius: 5px;
            }}
            .warning {{
                background-color: #ffe6e6;
                border-left: 4px solid #ff4d4d;
                padding: 10px 15px;
                margin-bottom: 20px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 10px;
                border-top: 1px solid #ddd;
                font-size: 0.9em;
                color: #7f8c8d;
            }}
            @media print {{
                body {{
                    padding: 0;
                }}
                .no-print {{
                    display: none;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Patient Information Leaflet</h1>
            <h2>{medication_name}</h2>
        </div>
        
        <div class="warning">
            <strong>Important:</strong> This is a placeholder for a pre-made patient information leaflet.
        </div>
        
        <div class="section">
            <h3>About This Leaflet</h3>
            <p>This is a placeholder for the pre-made patient information leaflet for {medication_name}.</p>
            <p>In a production environment, this would be replaced with the actual leaflet content from a database.</p>
        </div>
        
        <div class="section">
            <h3>Medication Information</h3>
            <p><strong>Name:</strong> {medication_name}</p>
            <p>Complete information about dosage, administration, and other details would be included here.</p>
        </div>
        
        <div class="footer">
            <p>This leaflet was generated on {datetime.now().strftime('%Y-%m-%d')}.</p>
            <p>For medical emergencies, contact your healthcare provider or local emergency services.</p>
            <button class="no-print" onclick="window.print()">Print this Leaflet</button>
        </div>
    </body>
    </html>
    """
    
    return jsonify({
        'status': 'success',
        'html': html
    })

@app.route('/generate_pictorial', methods=['POST'])
def generate_pictorial():
    """
    Generate an easy read pictorial based on the provided medication name.
    In a production environment, this would retrieve a pre-made pictorial from a database.
    """
    data = request.json
    medication_name = data.get('medicationName', '')
    
    # Generate a placeholder HTML pictorial
    # In a real application, you would look up the medication in a database
    # and retrieve the corresponding pre-made pictorial
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Easy Read Pictorial - {medication_name}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
                text-align: center;
            }}
            h1 {{
                color: #2c3e50;
                margin-bottom: 30px;
            }}
            .pictorial {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 20px;
                margin: 30px 0;
            }}
            .card {{
                background-color: #f9f9f9;
                border-radius: 10px;
                padding: 20px;
                width: 100%;
                max-width: 400px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
            .emoji {{
                font-size: 5em;
                margin: 10px 0;
            }}
            .instruction {{
                font-size: 1.5em;
                margin: 10px 0;
            }}
            .medication {{
                font-size: 2em;
                font-weight: bold;
                color: #3498db;
                margin: 15px 0;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 0.9em;
                color: #7f8c8d;
            }}
            @media print {{
                body {{
                    padding: 0;
                }}
                .no-print {{
                    display: none;
                }}
            }}
        </style>
    </head>
    <body>
        <h1>Easy Read Pictorial</h1>
        
        <div class="pictorial">
            <div class="card">
                <div class="emoji">💊</div>
                <div class="medication">{medication_name}</div>
            </div>
            
            <div class="card">
                <p>This is a placeholder for the pre-made easy read pictorial for {medication_name}.</p>
                <p>In a production environment, this would be replaced with the actual pictorial content from a database.</p>
            </div>
        </div>
        
        <div class="footer">
            <p>This pictorial was generated on {datetime.now().strftime('%Y-%m-%d')}.</p>
            <p>If you have questions, talk to your doctor or pharmacist.</p>
            <button class="no-print" onclick="window.print()">Print this Pictorial</button>
        </div>
    </body>
    </html>
    """
    
    return jsonify({
        'status': 'success',
        'html': html
    })

@app.route('/test')
def test_page():
    """
    Serve a test page with a sample discharge letter for testing the medication extraction.
    """
    return send_from_directory('static', 'test_discharge_letter.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
