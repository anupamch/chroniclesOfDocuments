#!/usr/bin/env python3
"""
Test OCR functionality with image files
"""

import requests
import json
import time
import os
from datetime import datetime

BASE_URL = "http://localhost:8000/api"
TEST_DOCS_DIR = os.path.join(os.path.dirname(__file__), 'test_documents')
RESULTS = []

def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    RESULTS.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def create_case(case_number, title):
    response = requests.post(f"{BASE_URL}/cases", json={"case_number": case_number, "title": title})
    if response.status_code == 201:
        data = response.json()
        log(f"Created case: {case_number} -> {data.get('case_id')}")
        return data
    else:
        log(f"Failed to create case: {response.text}")
        return None

def upload_documents(case_id, files):
    files_to_upload = []
    for f in files:
        file_path = os.path.join(TEST_DOCS_DIR, f)
        if os.path.exists(file_path):
            ext = os.path.splitext(f)[1].lower()
            mime_type = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg'
            }.get(ext, 'application/octet-stream')
            files_to_upload.append(('files', (f, open(file_path, 'rb'), mime_type)))
        else:
            log(f"File not found: {file_path}")

    if not files_to_upload:
        return None

    response = requests.post(f"{BASE_URL}/cases/{case_id}/documents", files=files_to_upload)
    for _, f in files_to_upload:
        f[1].close()

    if response.status_code == 200:
        data = response.json()
        log(f"Uploaded {data.get('total_uploaded', 0)} documents")
        return data
    else:
        log(f"Failed to upload: {response.text}")
        return None

def start_scan(case_id):
    response = requests.post(f"{BASE_URL}/cases/{case_id}/scan")
    if response.status_code == 200:
        data = response.json()
        log(f"Started scan: {data.get('total_documents')} documents")
        return data
    else:
        log(f"Failed to start scan: {response.text}")
        return None

def get_scan_status(case_id, max_wait=180, poll_interval=5):
    start_time = time.time()
    while time.time() - start_time < max_wait:
        response = requests.get(f"{BASE_URL}/cases/{case_id}/scan/status")
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            log(f"Status: {status} - {data.get('processed_documents')}/{data.get('total_documents')} processed")
            if status in ['completed', 'not_started']:
                return data
        time.sleep(poll_interval)
    return None

def run_image_test(name, case_number, files):
    import uuid
    timestamp = uuid.uuid4().hex[:8]
    unique_case_number = f"{case_number}-{timestamp}"

    log(f"\n{'='*60}")
    log(f"IMAGE OCR TEST: {name}")
    log(f"{'='*60}")

    case = create_case(unique_case_number, f"Image OCR: {name}")
    if not case:
        return None

    case_id = case.get('case_id')

    upload_result = upload_documents(case_id, files)
    if not upload_result:
        return None

    scan_result = start_scan(case_id)
    if not scan_result:
        return None

    log("Waiting for OCR processing...")
    status = get_scan_status(case_id, max_wait=300)

    return {
        'test_name': name,
        'case_id': case_id,
        'files': files,
        'status': status
    }

def main():
    log("Starting Image OCR Tests")
    log(f"Test images directory: {TEST_DOCS_DIR}")

    # Test 1: Invoice PNG Image
    result1 = run_image_test(
        "Invoice PNG Image OCR",
        "TEST-IMG-INV",
        ["invoice_image.png"]
    )

    # Test 2: WhatsApp Chat Image
    result2 = run_image_test(
        "WhatsApp Chat OCR",
        "TEST-IMG-WHATSAPP",
        ["whatsapp_chat.png"]
    )

    # Test 3: Invoice JPG Image
    result3 = run_image_test(
        "Invoice JPG OCR",
        "TEST-IMG-JPG",
        ["invoice_jpg.jpg"]
    )

    # Test 4: Multiple Images
    result4 = run_image_test(
        "Multiple Images OCR",
        "TEST-IMG-MULTI",
        ["invoice_image.png", "whatsapp_chat.png"]
    )

    # Test 5: Notes/Handwritten
    result5 = run_image_test(
        "Notes Image OCR",
        "TEST-IMG-NOTES",
        ["notes_image.png"]
    )

    results = {
        'test_run_timestamp': datetime.now().isoformat(),
        'tests': [result1, result2, result3, result4, result5],
        'logs': RESULTS
    }

    output_file = os.path.join(os.path.dirname(__file__), 'image_test_results.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    log(f"\n{'='*60}")
    log("IMAGE OCR TEST RUN COMPLETE")
    log(f"{'='*60}")
    log(f"Results saved to: {output_file}")

    return results

if __name__ == "__main__":
    results = main()
    print(f"\nTotal image tests: {len([r for r in results['tests'] if r])}")