import urllib.request
import urllib.error
import time

urls = [
    ("http://127.0.0.1:5000/api/report/college-toppers", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    ("http://127.0.0.1:5000/api/report/ledger-csv", "text/csv"),
    ("http://127.0.0.1:5000/api/report/failed-students?format=pdf", "application/pdf"),
    ("http://127.0.0.1:5000/api/report/subject-toppers", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
]

all_passed = True
for url, expected_type in urls:
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            print(f"[{response.status}] {url}")
            print(f"  Content-Type: {response.headers.get('Content-Type')}")
            if response.status != 200:
                print(f"  FAIL: Expected 200, got {response.status}")
                all_passed = False
                continue
            
            if not response.headers.get('Content-Type').startswith(expected_type):
                print(f"  FAIL: Expected {expected_type}, got {response.headers.get('Content-Type')}")
                all_passed = False
                continue
                
            data = response.read(100)
            if len(data) == 0:
                print("  FAIL: Response content is empty")
                all_passed = False
                continue
                
            print("  OK")
    except urllib.error.HTTPError as e:
        print(f"HTTP ERROR on {url}: {e.code} {e.reason}")
        print(e.read().decode('utf-8'))
        all_passed = False
    except Exception as e:
        print(f"ERROR on {url}: {e}")
        all_passed = False

if all_passed:
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED")
