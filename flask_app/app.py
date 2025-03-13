from flask import Flask, render_template, request, jsonify, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    """
    Main route that renders the Flask UI directly
    """
    return render_template('flask_ui.html')

@app.route('/original')
def original():
    """
    Route to serve the original HTML file directly
    """
    return send_from_directory(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              'chartgenerator.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
