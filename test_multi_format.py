import urllib.request
import time

endpoints = [
    "/api/report/college-toppers",
    "/api/report/failed-students",
    "/api/report/subject-toppers"
]

formats = {
    "pdf": "application/pdf",
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}

all_passed = True
for ep in endpoints:
    for fmt, expected_type in formats.items():
        url = f"http://127.0.0.1:5000{ep}?format={fmt}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                ctype = response.headers.get('Content-Type')
                if response.status != 200:
                    print(f"FAIL [{response.status}] {url}")
                    all_passed = False
                elif not ctype.startswith(expected_type):
                    print(f"FAIL Type mismatch {url} (expected {expected_type}, got {ctype})")
                    all_passed = False
                else:
                    print(f"OK [200] {url} -> {ctype}")
        except Exception as e:
            print(f"ERROR on {url}: {e}")
            all_passed = False

if all_passed:
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED")
