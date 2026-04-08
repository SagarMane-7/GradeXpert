import sys
import os
import json

# Add backend dir to python path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app import app
from flask_jwt_extended import create_access_token

def test_endpoints():
    with app.test_request_context():
        # Create a mock JWT token for testing
        access_token = create_access_token(identity="1")
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    endpoints = [
        ('/api/reports/remedial?format=pdf', 'application/pdf'),
        ('/api/reports/remedial?format=xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
        ('/api/reports/subject-weak?format=pdf', 'application/pdf'),
        ('/api/reports/class-summary?format=pdf', 'application/pdf'),
        ('/api/reports/progress?format=pdf', 'application/pdf'),
        ('/api/reports/action-recommendation?format=pdf', 'application/pdf'),
    ]

    client = app.test_client()
    results = []
    
    all_passed = True
    for endpoint, expected_content_type in endpoints:
        response = client.get(endpoint, headers=headers)
        
        if response.status_code != 200:
            results.append({"endpoint": endpoint, "status": "FAIL", "reason": f"Expected 200, got {response.status_code}"})
            all_passed = False
            continue
            
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith(expected_content_type):
            results.append({"endpoint": endpoint, "status": "FAIL", "reason": f"Expected {expected_content_type}, got {content_type}"})
            all_passed = False
            continue
            
        data = response.data
        if len(data) == 0:
            results.append({"endpoint": endpoint, "status": "FAIL", "reason": "Empty response body"})
            all_passed = False
            continue
            
        results.append({"endpoint": endpoint, "status": "OK"})

    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=4)

if __name__ == '__main__':
    test_endpoints()
