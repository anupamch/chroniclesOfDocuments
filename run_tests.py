#!/usr/bin/env python3
"""
Test Runner for Chronicles of Documents API
Tests various scenarios and collects results
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
    """Print and log message"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    RESULTS.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def create_case(case_number, title, description=""):
    """Create a new case"""
    response = requests.post(
        f"{BASE_URL}/cases",
        json={
            "case_number": case_number,
            "title": title,
            "description": description
        }
    )
    if response.status_code == 201:
        data = response.json()
        log(f"Created case: {case_number} -> {data.get('case_id')}")
        return data
    else:
        log(f"Failed to create case {case_number}: {response.text}")
        return None

def upload_documents(case_id, files):
    """Upload documents to a case"""
    files_to_upload = []
    for f in files:
        file_path = os.path.join(TEST_DOCS_DIR, f)
        if os.path.exists(file_path):
            files_to_upload.append(('files', (f, open(file_path, 'rb'), 'application/octet-stream')))
        else:
            log(f"File not found: {file_path}")

    if not files_to_upload:
        log(f"No files to upload for case {case_id}")
        return None

    response = requests.post(
        f"{BASE_URL}/cases/{case_id}/documents",
        files=files_to_upload
    )

    # Close file handles
    for _, f in files_to_upload:
        f[1].close()

    if response.status_code == 200:
        data = response.json()
        log(f"Uploaded {data.get('total_uploaded', 0)} documents to case {case_id}")
        return data
    else:
        log(f"Failed to upload documents: {response.text}")
        return None

def start_scan(case_id):
    """Start scanning a case"""
    response = requests.post(f"{BASE_URL}/cases/{case_id}/scan")
    if response.status_code == 200:
        data = response.json()
        log(f"Started scan for case {case_id}: {data.get('total_documents')} documents")
        return data
    else:
        log(f"Failed to start scan: {response.text}")
        return None

def get_scan_status(case_id, max_wait=180, poll_interval=5):
    """Get scan status and wait for completion"""
    start_time = time.time()
    last_status = None

    while time.time() - start_time < max_wait:
        response = requests.get(f"{BASE_URL}/cases/{case_id}/scan/status")
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            processed = data.get('processed_documents', 0)
            total = data.get('total_documents', 0)
            failed = data.get('failed_documents', 0)

            log(f"Case {case_id}: {status} - {processed}/{total} processed, {failed} failed")

            if status == 'completed' or status == 'not_started':
                last_status = data
                break
        else:
            log(f"Failed to get status: {response.text}")
            break

        time.sleep(poll_interval)

    return last_status

def run_scenario(name, case_number, files):
    """Run a test scenario"""
    # Add timestamp to ensure unique case numbers
    import uuid
    timestamp = uuid.uuid4().hex[:8]
    unique_case_number = f"{case_number}-{timestamp}"

    log(f"\n{'='*60}")
    log(f"SCENARIO: {name}")
    log(f"{'='*60}")

    # Create case
    case = create_case(unique_case_number, f"Test: {name}")
    if not case:
        return None

    case_id = case.get('case_id')

    # Upload documents
    upload_result = upload_documents(case_id, files)
    if not upload_result:
        return None

    # Start scan
    scan_result = start_scan(case_id)
    if not scan_result:
        return None

    # Wait for completion
    log(f"Waiting for scan to complete...")
    status = get_scan_status(case_id)

    return {
        'scenario': name,
        'case_id': case_id,
        'case_number': case_number,
        'files': files,
        'status': status
    }

def main():
    log("Starting Chronicles of Documents API Tests")
    log(f"Test documents directory: {TEST_DOCS_DIR}")

    # Test 1: PDF Documents Only
    result1 = run_scenario(
        "PDF Documents",
        "TEST-PDF-001",
        ["invoice_sample.pdf", "contract_sample.pdf", "letter_sample.pdf"]
    )

    # Test 2: DOCX Documents Only
    result2 = run_scenario(
        "DOCX Documents",
        "TEST-DOCX-001",
        ["invoice_docx.docx", "contract_docx.docx"]
    )

    # Test 3: Text Documents
    result3 = run_scenario(
        "Text Documents",
        "TEST-TXT-001",
        ["invoice_text.txt", "contract_text.txt", "letter_text.txt"]
    )

    # Test 4: Mixed Document Types
    result4 = run_scenario(
        "Mixed Document Types",
        "TEST-MIXED-001",
        ["invoice_sample.pdf", "invoice_docx.docx", "contract_sample.pdf"]
    )

    # Test 5: Invoice Focus
    result5 = run_scenario(
        "Invoice Processing",
        "TEST-INVOICE-001",
        ["invoice_sample.pdf", "invoice_docx.docx", "invoice_text.txt"]
    )

    # Test 6: Contract Focus
    result6 = run_scenario(
        "Contract Processing",
        "TEST-CONTRACT-001",
        ["contract_sample.pdf", "contract_docx.docx", "contract_text.txt"]
    )

    # Save results
    results = {
        'test_run_timestamp': datetime.now().isoformat(),
        'scenarios': [result1, result2, result3, result4, result5, result6],
        'logs': RESULTS
    }

    output_file = os.path.join(os.path.dirname(__file__), 'test_results.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    log(f"\n{'='*60}")
    log("TEST RUN COMPLETE")
    log(f"{'='*60}")
    log(f"Results saved to: {output_file}")

    return results

if __name__ == "__main__":
    results = main()
    print(f"\nTotal scenarios run: {len(results['scenarios'])}")