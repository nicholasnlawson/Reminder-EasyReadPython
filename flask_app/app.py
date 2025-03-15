from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, url_for
import os
import re
import io
import PyPDF2
import tempfile
import glob
from datetime import datetime, timedelta

app = Flask(__name__)

# Path to the original HTML file
# The original HTML file is in the parent directory
ORIGINAL_HTML_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'chartgenerator.html')

@app.route('/')
def index():
    # Clean up old temp files on startup
    cleanup_temp_files(hours=24)
    # Render the Flask UI template
    return render_template('flask_ui_updated.html')

@app.route('/cleanup_temp', methods=['POST'])
def cleanup_temp():
    """Clean up temporary PDF files"""
    try:
        # Get the file to clean up from the request
        data = request.json
        filename = data.get('filename', None)
        
        if filename:
            # Clean up a specific file
            file_path = os.path.join(app.static_folder, 'temp', filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return jsonify({'status': 'success', 'message': f'File {filename} deleted'})
            else:
                return jsonify({'status': 'error', 'message': f'File {filename} not found'})
        else:
            # Clean up all files older than 1 hour
            num_deleted = cleanup_temp_files(hours=1)
            return jsonify({'status': 'success', 'message': f'Deleted {num_deleted} temporary files'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def cleanup_temp_files(hours=1):
    """Delete temporary files older than the specified number of hours"""
    temp_dir = os.path.join(app.static_folder, 'temp')
    if not os.path.exists(temp_dir):
        return 0
        
    # Get current time
    now = datetime.now()
    count = 0
    
    # Check all files in the temp directory
    for file_path in glob.glob(os.path.join(temp_dir, '*')):
        # Skip directories
        if os.path.isdir(file_path):
            continue
            
        # Get file modification time
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        # If file is older than specified hours, delete it
        if now - file_mod_time > timedelta(hours=hours):
            try:
                os.remove(file_path)
                count += 1
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
                
    return count

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



# Define medication keyword mappings
def find_matching_pdf(medication_name, pdf_type):
    """
    Find the most appropriate PDF based on medication name and keywords.
    pdf_type should be either 'leaflets' or 'pictorials'
    """
    # Convert medication name to lowercase for case-insensitive matching
    med_name_lower = medication_name.lower()
    
    # Define keyword mappings for medications
    keyword_mappings = {
        'paracetamol': {
            'tablet': {
                'leaflet': 'paracetamoltabletsleaflet.pdf',
                'pictorial': 'Paracetamoltabletspictorial.pdf'
            }
        },
        'salbutamol': {
            'inhaler': {
                'leaflet': 'Salbutamolinhalerleaflet.pdf',
                'pictorial': 'Salbutamolinhalerpictorial.pdf'
            }
        },
        'peptac': {
            'suspension': {
                'leaflet': 'peptacliquidleaflet.pdf',
                'pictorial': 'peptacliquidpictorial.pdf'
            },
            'liquid': {
                'leaflet': 'peptacliquidleaflet.pdf',
                'pictorial': 'peptacliquidpictorial.pdf'
            }
        },
        'amlodipine': {
            'tablet': {
                'leaflet': 'amlodipinetabletleaflet.pdf',
                'pictorial': 'amlodipinetabletpictorial.pdf'
            }
        },
        'atorvastatin': {
            'tablet': {
                'leaflet': 'atorvastatintabletleaflet.pdf',
                'pictorial': 'atorvastatintabletpictrorial.pdf'
            }
        },
        'carbomer': {
            'gel': {
                'leaflet': 'carbomerleaflet.pdf',
                'pictorial': 'carbomerpictorial.pdf'
            }
        },
        'doxycycline': {
            'capsule': {
                'leaflet': 'doxycyclinecapsuleleaflet.pdf',
                'pictorial': 'doxycyclinecapsulepictorial.pdf'
            }
        },
        'esomeprazole': {
            'tablet': {
                'leaflet': 'esomeprazoletabletleaflet.pdf',
                'pictorial': 'esomeprazoletabletpictorial.pdf'
            }
        },
        'furosemide': {
            'tablet': {
                'leaflet': 'furosemidetabletleaflet.pdf',
                'pictorial': 'furosemidetabletpictorial.pdf'
            }
        },
        'lisinopril': {
            'tablet': {
                'leaflet': 'lisinopriltabletleaflet.pdf',
                'pictorial': 'lisinopriltabletpictorial.pdf'
            }
        },
        'metformin': {
            'm/r tablet': {
                'leaflet': 'metforminmrtabletleaflet.pdf',
                'pictorial': 'metforminmrtabletpictorial.pdf'
            }
        },
        'mirtazapine': {
            'tablets': {
                'leaflet': 'mirtazapinetabletleaflet.pdf',
                'pictorial': 'mirtazapinetabletpictorial.pdf'
            }
        },
        'prednisolone': {
            'tablet': {
                'leaflet': 'prednisolonetabletleaflet.pdf',
                'pictorial': 'prednisolonetabletpictorial.pdf'
            }
        },
        'trimbow': {
            'mdi': {
                'leaflet': 'trimbowpMDIleaflet.pdf',
                'pictorial': 'trimbowpMDIpictorial.pdf'
            }
        }
    }
    
    # Track the best match and its score
    best_match = None
    best_score = 0
    
    # Determine which type of PDF we're looking for
    pdf_key = 'leaflet' if pdf_type == 'leaflets' else 'pictorial'
    
    # Check each medication keyword
    for med_key, formulations in keyword_mappings.items():
        if med_key in med_name_lower:
            # Found a medication match, now check formulations
            for form_key, pdf_info in formulations.items():
                if form_key in med_name_lower:
                    # Both medication and formulation match - this is a perfect match
                    return pdf_info[pdf_key]
                else:
                    # Only medication matches, keep track of it as a potential match
                    # Score of 1 for medication match
                    if 1 > best_score:
                        best_score = 1
                        best_match = list(formulations.values())[0][pdf_key]
    
    # If we found any match, return it
    if best_match:
        return best_match
    
    # No match found, return None
    return None

def get_formatted_medication_name(med_name):
    """
    Get a properly formatted medication name with formulation details.
    """
    med_name_lower = med_name.lower()
    
    # Define medication mappings with their proper names and formulations
    medication_mappings = {
        'salbutamol': {
            'mdi': 'Salbutamol pMDI inhaler',
            'inhaler': 'Salbutamol pMDI inhaler',
        },
        'trimbow': {
            'pMDI': 'Trimbow pMDI inhaler',
            'inhaler': 'Trimbow pMDI inhaler'
        },
        'doxycycline': {
            'capsule': 'Doxycycline capsules',
        },
        'esomeprazole': {
            'tablet': 'Esomeprazole tablets',
        },
        'furosemide': {
            'tablet': 'Furosemide tablets',
        },
        'lisinopril': {
            'tablet': 'Lisinopril tablets'
        },
        'metformin': {
            'm/r tablet': 'Metformin modified-release tablets',
        },
        'mirtazapine': {
            'tablet': 'Mirtazapine tablets',
        },
        'prednisolone': {
            'tablet': 'Prednisolone tablets',
        },
        'paracetamol': {
            'tablet': 'Paracetamol tablets',
        },
        'peptac': {
            'suspension': 'Peptac liquid',
            'liquid': 'Peptac liquid'
        },
        'amlodipine': {
            'tablet': 'Amlodipine tablets'
        },
        'atorvastatin': {
            'tablet': 'Atorvastatin tablets'
        },
        'carbomer': {
            'gel': 'Carbomer eye gel'
        }
    }
    
    # Find the medication in our mappings
    for med_key, formulations in medication_mappings.items():
        if med_key in med_name_lower:
            # Found a medication match, now check formulations
            for form_key, formatted_name in formulations.items():
                if form_key in med_name_lower:
                    # Both medication and formulation match
                    return formatted_name
            
            # If no formulation match but medication matches, return the first formulation
            if formulations:
                return list(formulations.values())[0]
    
    # If no match found, return the original name
    return med_name

def get_all_medications():
    """
    Get a list of all available medications with their formulations.
    """
    medications = [
        {'name': 'Salbutamol', 'formulation': 'pMDI inhaler'},
        {'name': 'Trimbow', 'formulation': 'pMDI inhaler'},
        {'name': 'Doxycycline', 'formulation': 'capsules'},
        {'name': 'Esomeprazole', 'formulation': 'tablets'},
        {'name': 'Furosemide', 'formulation': 'tablets'},
        {'name': 'Lisinopril', 'formulation': 'tablets'},
        {'name': 'Metformin', 'formulation': 'M/R tablets'},
        {'name': 'Mirtazapine', 'formulation': 'tablets'},
        {'name': 'Prednisolone', 'formulation': 'tablets'},
        {'name': 'Paracetamol', 'formulation': 'tablets'},
        {'name': 'Peptac', 'formulation': 'liquid'},
        {'name': 'Amlodipine', 'formulation': 'tablets'},
        {'name': 'Atorvastatin', 'formulation': 'tablets'},
        {'name': 'Carbomer', 'formulation': 'eye gel'}
    ]
    
    # Add PDF availability information
    for med in medications:
        med_name = f"{med['name']} {med['formulation']}"
        pdf_leaflet = find_matching_pdf(med_name, 'leaflets')
        pdf_pictorial = find_matching_pdf(med_name, 'pictorials')
        
        med['pdfAvailable'] = (pdf_leaflet is not None) or (pdf_pictorial is not None)
        med['pdfLeafletAvailable'] = pdf_leaflet is not None
        med['pdfPictorialAvailable'] = pdf_pictorial is not None
        
        if pdf_leaflet:
            med['pdfLeafletFilename'] = pdf_leaflet
        if pdf_pictorial:
            med['pdfPictorialFilename'] = pdf_pictorial
    
    return medications

@app.route('/generate_leaflet', methods=['POST'])
def generate_leaflet():
    """
    Generate patient information leaflets based on the provided medication names.
    This will find and serve the appropriate PDF leaflets based on keyword matching.
    """
    data = request.json
    medication_names = data.get('medicationNames', [])
    
    # If no medications were provided, return an error
    if not medications_list_check(medication_names):
        return jsonify({
            'status': 'error',
            'message': 'No medication names provided'
        })
    
    # Find matching PDF leaflets for all medications
    pdf_files = []
    not_found_medications = []
    
    for medication_name in medication_names:
        pdf_filename = find_matching_pdf(medication_name, 'leaflets')
        if pdf_filename:
            # Store the full file path
            pdf_files.append(os.path.join(app.root_path, 'static', 'pdfs', 'leaflets', pdf_filename))
        else:
            not_found_medications.append(medication_name)
    
    # If we found at least one PDF, merge them and return the merged PDF
    if pdf_files:
        # Create a unique filename for the merged PDF
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        merged_filename = f'merged_leaflets_{timestamp}.pdf'
        merged_filepath = os.path.join(app.root_path, 'static', 'temp', merged_filename)
        
        # Create the temp directory if it doesn't exist
        os.makedirs(os.path.join(app.root_path, 'static', 'temp'), exist_ok=True)
        
        # Merge the PDFs
        merge_pdfs(pdf_files, merged_filepath)
        
        # Return the path to the merged PDF
        return jsonify({
            'status': 'success',
            'type': 'pdf',
            'pdf_path': f'/static/temp/{merged_filename}',
            'not_found_medications': not_found_medications
        })
    
    # If no matching PDFs were found, generate a fallback HTML response
    # Create a list of medications that weren't found
    not_found_list = '\n'.join([f'<li>{med}</li>' for med in not_found_medications])
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Patient Information Leaflet - Not Found</title>
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
            <h2>Medications Not Found</h2>
        </div>
        
        <div class="warning">
            <strong>Important:</strong> No matching leaflets found for the following medications:
        </div>
        
        <div class="section">
            <h3>Medications Without Leaflets</h3>
            <ul>
                {not_found_list}
            </ul>
            <p>Please consult your healthcare provider for information about these medications.</p>
        </div>
        
        <div class="footer">
            <p>This notice was generated on {datetime.now().strftime('%Y-%m-%d')}.</p>
            <p>For medical emergencies, contact your healthcare provider or local emergency services.</p>
            <button class="no-print" onclick="window.print()">Print this Notice</button>
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
    Generate easy read pictorials based on the provided medication names.
    This will find and serve the appropriate PDF pictorials based on keyword matching.
    """
    data = request.json
    medication_names = data.get('medicationNames', [])
    
    # If no medications were provided, return an error
    if not medications_list_check(medication_names):
        return jsonify({
            'status': 'error',
            'message': 'No medication names provided'
        })
    
    # Find matching PDF pictorials for all medications
    pdf_files = []
    not_found_medications = []
    
    for medication_name in medication_names:
        pdf_filename = find_matching_pdf(medication_name, 'pictorials')
        if pdf_filename:
            # Store the full file path
            pdf_files.append(os.path.join(app.root_path, 'static', 'pdfs', 'pictorials', pdf_filename))
        else:
            not_found_medications.append(medication_name)
    
    # If we found at least one PDF, merge them and return the merged PDF
    if pdf_files:
        # Create a unique filename for the merged PDF
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        merged_filename = f'merged_pictorials_{timestamp}.pdf'
        merged_filepath = os.path.join(app.root_path, 'static', 'temp', merged_filename)
        
        # Create the temp directory if it doesn't exist
        os.makedirs(os.path.join(app.root_path, 'static', 'temp'), exist_ok=True)
        
        # Merge the PDFs
        merge_pdfs(pdf_files, merged_filepath)
        
        # Return the path to the merged PDF
        return jsonify({
            'status': 'success',
            'type': 'pdf',
            'pdf_path': f'/static/temp/{merged_filename}',
            'not_found_medications': not_found_medications
        })
    
    # If no matching PDFs were found, generate a fallback HTML response
    # Create a list of medications that weren't found
    not_found_list = '\n'.join([f'<li>{med}</li>' for med in not_found_medications])
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Easy Read Pictorial - Not Found</title>
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
            ul {{
                text-align: left;
                padding-left: 20px;
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
                <div class="medication">Medications Not Found</div>
            </div>
            
            <div class="card">
                <p>No matching pictorials found for the following medications:</p>
                <ul>
                    {not_found_list}
                </ul>
                <p>Please consult your healthcare provider for information about these medications.</p>
            </div>
        </div>
        
        <div class="footer">
            <p>This notice was generated on {datetime.now().strftime('%Y-%m-%d')}.</p>
            <p>If you have questions, talk to your doctor or pharmacist.</p>
            <button class="no-print" onclick="window.print()">Print this Notice</button>
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

def medications_list_check(medication_names):
    """
    Check if the medication_names list is valid
    """
    return medication_names and isinstance(medication_names, list) and len(medication_names) > 0


def merge_pdfs(pdf_files, output_path):
    """
    Merge multiple PDF files into a single PDF file
    """
    merger = PyPDF2.PdfMerger()
    
    for pdf_file in pdf_files:
        merger.append(pdf_file)
    
    merger.write(output_path)
    merger.close()
    
    return output_path


@app.route('/search_medications', methods=['POST'])
def search_medications():
    """
    Search for medications based on a search term.
    Returns a list of matching medications with their formulations.
    """
    data = request.json
    search_term = data.get('searchTerm', '').lower()
    
    if not search_term or len(search_term) < 2:
        return jsonify({
            'status': 'error',
            'message': 'Search term must be at least 2 characters long'
        })
    
    # Get all medications
    all_medications = get_all_medications()
    
    # Filter medications based on search term
    matching_medications = []
    for med in all_medications:
        if search_term in med['name'].lower() or search_term in med['formulation'].lower():
            matching_medications.append(med)
    
    return jsonify({
        'status': 'success',
        'medications': matching_medications
    })

@app.route('/get_medication_details', methods=['POST'])
def get_medication_details():
    """
    Get details for a specific medication, including its formatted name and PDF availability.
    """
    data = request.json
    medication_name = data.get('medicationName', '')
    
    if not medication_name:
        return jsonify({
            'status': 'error',
            'message': 'No medication name provided'
        })
    
    # Get formatted medication name
    formatted_name = get_formatted_medication_name(medication_name)
    
    # Check if PDF is available
    pdf_leaflet = find_matching_pdf(medication_name, 'leaflets')
    pdf_pictorial = find_matching_pdf(medication_name, 'pictorials')
    
    return jsonify({
        'status': 'success',
        'formattedName': formatted_name,
        'pdfAvailable': (pdf_leaflet is not None) or (pdf_pictorial is not None),
        'pdfLeafletAvailable': pdf_leaflet is not None,
        'pdfPictorialAvailable': pdf_pictorial is not None,
        'pdfLeafletFilename': pdf_leaflet if pdf_leaflet else None,
        'pdfPictorialFilename': pdf_pictorial if pdf_pictorial else None
    })



if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
