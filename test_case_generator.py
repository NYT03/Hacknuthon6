from flask import Flask, render_template, request, jsonify, send_file, Response
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List
import io
from groq import Groq

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class TestCaseGenerator:
    """Generates test cases using Groq API"""
    def __init__(self):
        # API key should ideally be stored as an environment variable
        api_key = os.environ.get("GROQ_API_KEY", "your_api_key_here")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    def _generate_with_groq(self, prompt: str) -> str:
        """Generate test cases using Groq API with better error handling"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a test automation expert. Always respond with valid JSON following the specified structure."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=4000
            )
            
            # Debug logging
            logger.info("Raw API Response received")
            response_content = completion.choices[0].message.content
            logger.info(f"Response content type: {type(response_content)}")
            
            # Try to clean the response if it's not pure JSON
            cleaned_response = self._clean_response(response_content)
            return cleaned_response

        except Exception as e:
            logger.error(f"Error in Groq API call: {str(e)}")
            raise

    def _clean_response(self, response: str) -> str:
        """Clean the API response to ensure valid JSON"""
        try:
            # If response is already valid JSON, return it
            json.loads(response)
            return response
        except json.JSONDecodeError:
            logger.info("Cleaning malformed JSON response")
            
            # Try to extract JSON content between curly braces
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    cleaned = response[start_idx:end_idx]
                    # Validate the cleaned JSON
                    json.loads(cleaned)
                    return cleaned
            except:
                pass

            # If extraction failed, return a minimal valid structure
            logger.warning("Falling back to minimal structure")
            return '''
            {
              "components": [
                {
                  "parent_component": "error-fallback",
                  "sub_components": [
                    {
                      "summary": "Error in test case generation",
                      "priority": "P1",
                      "tags": ["Error"],
                      "test_cases": [
                        {
                          "action": "Check system response",
                          "expected_result": "System should handle errors gracefully"
                        }
                      ]
                    }
                  ]
                }
              ]
            }
            '''

    def generate_test_cases(self, ui_description: str, srs_description: str) -> Dict[str, Any]:
        """Generate test cases with enhanced error handling"""
        try:
            combined_prompt = self._create_prompt(ui_description, srs_description)
            response = self._generate_with_groq(combined_prompt)
            
            # Log the response for debugging
            logger.info("Attempting to parse response")
            
            structured_test_cases = self._structure_response(response)
            return structured_test_cases
        except Exception as e:
            logger.error(f"Error generating test cases: {str(e)}")
            raise

    def _create_prompt(self, ui_description: str, srs_description: str) -> str:
        return f"""Generate test cases in valid JSON format for the following UI and SRS descriptions.
The response must be a valid JSON object and nothing else.

UI Description:
{ui_description}

SRS Description:
{srs_description}

The response must strictly follow this JSON structure:
{{
  "components": [
    {{
      "parent_component": "component-name",
      "sub_components": [
        {{
          "summary": "test-objective",
          "priority": "P1",
          "tags": ["tag1", "tag2"],
          "test_cases": [
            {{
              "action": "test-step",
              "expected_result": "expected-outcome"
            }}
          ]
        }}
      ]
    }}
  ]
}}

Generate comprehensive test cases for each component mentioned in the UI description, following the requirements in the SRS."""

    def _structure_response(self, response: str) -> Dict[str, Any]:
        """Structure the API response into required format"""
        try:
            test_cases = json.loads(response)
            self._validate_structure(test_cases)
            return test_cases
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error structuring response: {str(e)}")
            raise

    def _validate_structure(self, test_cases: Dict[str, Any]):
        """Validate the test case structure"""
        required_keys = {"components"}
        if not all(key in test_cases for key in required_keys):
            raise ValueError("Invalid test case structure: missing required keys")

        for component in test_cases["components"]:
            if "parent_component" not in component or "sub_components" not in component:
                raise ValueError("Invalid component structure")

            for sub_component in component["sub_components"]:
                required_sub_keys = {"summary", "priority", "tags", "test_cases"}
                if not all(key in sub_component for key in required_sub_keys):
                    raise ValueError("Invalid sub-component structure")

    def generate_detailed_summary(self, test_cases: Dict[str, Any]) -> str:
        """Generate a detailed summary of test cases"""
        summary = "\n=== Test Case Generation Summary ===\n"
        
        # Overall statistics
        total_components = len(test_cases['components'])
        total_test_cases = sum(
            len(sub['test_cases']) 
            for component in test_cases['components'] 
            for sub in component['sub_components']
        )
        
        summary += f"\n📊 Overall Statistics:"
        summary += f"\n- Total Components: {total_components}"
        summary += f"\n- Total Test Cases: {total_test_cases}"
        
        # Priority distribution
        priority_count = {"P1": 0, "P2": 0, "P3": 0}
        for component in test_cases['components']:
            for sub in component['sub_components']:
                priority_count[sub['priority']] += len(sub['test_cases'])
        
        summary += f"\n\n🎯 Priority Distribution:"
        summary += f"\n- Critical (P1): {priority_count['P1']} test cases"
        summary += f"\n- Important (P2): {priority_count['P2']} test cases"
        summary += f"\n- Nice-to-have (P3): {priority_count['P3']} test cases"
        
        # Tag analysis
        all_tags = set()
        tag_count = {}
        for component in test_cases['components']:
            for sub in component['sub_components']:
                for tag in sub['tags']:
                    all_tags.add(tag)
                    tag_count[tag] = tag_count.get(tag, 0) + len(sub['test_cases'])
        
        summary += f"\n\n🏷 Tag Coverage:"
        for tag in sorted(all_tags):
            summary += f"\n- {tag}: {tag_count[tag]} test cases"
        
        # Component breakdown
        summary += f"\n\n📝 Component Breakdown:"
        for component in test_cases['components']:
            sub_case_count = sum(len(sub['test_cases']) for sub in component['sub_components'])
            summary += f"\n\n🔹 {component['parent_component'].upper()}"
            summary += f"\n  - Sub-components: {len(component['sub_components'])}"
            summary += f"\n  - Total test cases: {sub_case_count}"
            for sub in component['sub_components']:
                summary += f"\n  - {sub['summary'][:50]}... ({len(sub['test_cases'])} tests, {sub['priority']})"
        
        return summary


# Initialize test case generator
generator = TestCaseGenerator()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        ui_description = data.get('ui_description', '')
        srs_description = data.get('srs_description', '')
        
        if not ui_description or not srs_description:
            return jsonify({'error': 'Both UI and SRS descriptions are required'}), 400
        
        # Generate test cases
        logger.info("Generating test cases...")
        test_cases = generator.generate_test_cases(ui_description, srs_description)
        
        # Generate summary
        detailed_summary = generator.generate_detailed_summary(test_cases)
        
        # Store generated data in session for download
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result = {
            'timestamp': timestamp,
            'test_cases': test_cases,
            'summary': detailed_summary
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/json/<timestamp>')
def download_json(timestamp):
    try:
        # Get data from session
        test_cases = request.args.get('test_cases')
        if not test_cases:
            return "No test cases found", 404
            
        # Create an in-memory file
        test_cases_json = json.loads(test_cases)
        file_data = json.dumps(test_cases_json, indent=2)
        file_stream = io.BytesIO(file_data.encode('utf-8'))
        
        filename = f'test_cases_{timestamp}.json'
        
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error downloading JSON: {str(e)}")
        return str(e), 500

@app.route('/download/summary/<timestamp>')
def download_summary(timestamp):
    try:
        # Get data from session
        summary = request.args.get('summary')
        if not summary:
            return "No summary found", 404
            
        # Create an in-memory file
        file_stream = io.BytesIO(summary.encode('utf-8'))
        
        filename = f'test_cases_summary_{timestamp}.txt'
        
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
        
    except Exception as e:
        logger.error(f"Error downloading summary: {str(e)}")
        return str(e), 500

if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create index.html template
    with open('templates/index.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Case Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        #results {
            display: none;
            margin-top: 30px;
        }
        .code-block {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            white-space: pre-wrap;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4 text-center">Test Case Generator</h1>
        
        <div class="card mb-4">
            <div class="card-header">
                <h5>Input Details</h5>
            </div>
            <div class="card-body">
                <form id="generatorForm">
                    <div class="mb-3">
                        <label for="uiDescription" class="form-label">UI Description</label>
                        <textarea class="form-control" id="uiDescription" rows="5" required placeholder="Describe the UI components..."></textarea>
                    </div>
                    <div class="mb-3">
                        <label for="srsDescription" class="form-label">SRS Description</label>
                        <textarea class="form-control" id="srsDescription" rows="5" required placeholder="Describe the requirements..."></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Generate Test Cases</button>
                </form>
            </div>
        </div>
        
        <div id="loading" class="loading">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p>Generating test cases, please wait...</p>
        </div>
        
        <div id="results">
            <div class="card mb-4">
                <div class="card-header">
                    <h5>Test Case Summary</h5>
                </div>
                <div class="card-body">
                    <pre id="summaryDisplay" class="code-block"></pre>
                    <button id="downloadSummary" class="btn btn-sm btn-outline-secondary mt-2">Download Summary</button>
                </div>
            </div>
            
            <div class="card mb-4">
                <div class="card-header">
                    <h5>Test Cases (JSON)</h5>
                </div>
                <div class="card-body">
                    <pre id="jsonDisplay" class="code-block"></pre>
                    <button id="downloadJson" class="btn btn-sm btn-outline-secondary mt-2">Download JSON</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('generatorForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const uiDescription = document.getElementById('uiDescription').value;
            const srsDescription = document.getElementById('srsDescription').value;
            
            // Show loading indicator
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        ui_description: uiDescription,
                        srs_description: srsDescription
                    }),
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                // Hide loading, show results
                document.getElementById('loading').style.display = 'none';
                document.getElementById('results').style.display = 'block';
                
                // Display results
                document.getElementById('summaryDisplay').textContent = data.summary;
                document.getElementById('jsonDisplay').textContent = JSON.stringify(data.test_cases, null, 2);
                
                // Set up download buttons
                const timestamp = data.timestamp;
                
                document.getElementById('downloadSummary').onclick = function() {
                    window.location.href = `/download/summary/${timestamp}?summary=${encodeURIComponent(data.summary)}`;
                };
                
                document.getElementById('downloadJson').onclick = function() {
                    window.location.href = `/download/json/${timestamp}?test_cases=${encodeURIComponent(JSON.stringify(data.test_cases))}`;
                };
                
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('loading').style.display = 'none';
                alert('Error generating test cases: ' + error.message);
            }
        });
    </script>
</body>
</html>''')

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))