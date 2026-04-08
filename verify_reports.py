import sys
import os
import io

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

    print("--- Testing Reports Endpoints ---")
    
    client = app.test_client()
    
    all_passed = True
    for endpoint, expected_content_type in endpoints:
        print(f"Testing {endpoint}...")
        response = client.get(endpoint, headers=headers)
        
        if response.status_code != 200:
            print(f"  [FAIL] Expected status 200, got {response.status_code}")
            if response.status_code == 404:
                 print("  Note: 404 might indicate 'No data available'. Do we have data in generated/latest_report.xlsx?")
            elif response.status_code == 500:
                 print(f"  [Error] {response.get_data().decode('utf-8')}")
            all_passed = False
            continue
            
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith(expected_content_type):
            print(f"  [FAIL] Expected Content-Type {expected_content_type}, got {content_type}")
            all_passed = False
            continue
            
        data = response.data
        if len(data) == 0:
            print("  [FAIL] Response body is empty")
            all_passed = False
            continue
            
        print("  [OK] Endpoint works and returns expected data format.")

    if all_passed:
        print("\nSUCCESS: All endpoints return 200 and expected formats.")
    else:
        print("\nWARNING: Some endpoints failed.")

if __name__ == '__main__':
    test_endpoints()
