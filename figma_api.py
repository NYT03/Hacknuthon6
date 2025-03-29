import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Get Figma token from .env
FIGMA_ACCESS_TOKEN = os.getenv("FIGMA_ACCESS_TOKEN")

def fetch_figma_data(endpoint_type, param):
    """Fetch data from the Figma API."""
    
    # Define base URL
    base_url = "https://api.figma.com/v1"

    # Map endpoint types to actual Figma API endpoints
    endpoint_map = {
        "files": f"/files/{param}",
        "images": f"/images/{param}",
        "projects": f"/projects/{param}",
        "team_projects": f"/teams/{param}/projects",
        "components": f"/components/{param}",
        "component_sets": f"/component_sets/{param}",
        "styles": f"/styles/{param}",
        "comments": f"/files/{param}/comments",
        "user_me": "/me",
        "file_nodes": f"/files/{param}/nodes",
        "team_components": f"/teams/{param}/components",
        "team_styles": f"/teams/{param}/styles"
    }

    # Get the specific endpoint
    endpoint = endpoint_map.get(endpoint_type)

    if not endpoint:
        return None, "Invalid endpoint type"

    url = f"{base_url}{endpoint}"
    
    # Set headers
    headers = {
        "Authorization": f"Bearer {FIGMA_ACCESS_TOKEN}"
    }

    # Make API request
    response = requests.get(url, headers=headers)

    # Return response or error
    if response.status_code == 200:
        return response.json(), None
    else:
        return None, f"Error: {response.status_code} - {response.text}"
