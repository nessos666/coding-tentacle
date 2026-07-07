"""
Bug: SECURITY — Hardcoded API Key (CWE-798)
"""
import os
# BUG: API Key im Code
# API_KEY = "sk-abc123def456"
API_KEY = os.getenv('API_KEY', '')  # Fix: aus Environment

def get_api_key():
    return API_KEY

def test_get_api_key():
    assert get_api_key() == ''

if __name__ == '__main__':
    test_get_api_key()
    print("OK — API Key aus Env")
