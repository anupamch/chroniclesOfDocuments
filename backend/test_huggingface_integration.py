#!/usr/bin/env python
"""
HuggingFace Integration Test Script

Tests the HuggingFace API integration without making actual API calls
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env
from dotenv import load_dotenv
load_dotenv()

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_configuration():
    """Test 1: Configuration loading"""
    logger.info("\n" + "="*70)
    logger.info("TEST 1: Configuration Loading")
    logger.info("="*70)
    
    try:
        from app.core.config import settings
        
        logger.info("✓ Config module imported successfully")
        logger.info(f"  • model_provider: {settings.model_provider}")
        logger.info(f"  • hf_model_name: {settings.hf_model_name}")
        logger.info(f"  • hf_access_token exists: {bool(settings.hf_access_token)}")
        
        if settings.model_provider == "api":
            logger.info("✓ Provider is set to 'api' (HuggingFace)")
        else:
            logger.info(f"⚠ Provider is set to '{settings.model_provider}' (not api)")
            
        return True
    except Exception as e:
        logger.error(f"✗ Configuration loading failed: {e}")
        return False


def test_provider_detection():
    """Test 2: Provider detection"""
    logger.info("\n" + "="*70)
    logger.info("TEST 2: Provider Detection")
    logger.info("="*70)
    
    try:
        from app.core.huggingface_client import (
            should_use_huggingface,
            get_active_provider
        )
        
        is_hf = should_use_huggingface()
        provider = get_active_provider()
        
        logger.info(f"✓ Provider detection working")
        logger.info(f"  • should_use_huggingface(): {is_hf}")
        logger.info(f"  • get_active_provider(): {provider}")
        
        if provider == "huggingface":
            logger.info("✓ Correctly detected HuggingFace as active provider")
        
        return True
    except Exception as e:
        logger.error(f"✗ Provider detection failed: {e}")
        return False


def test_unified_llm_init():
    """Test 3: Unified LLM initialization"""
    logger.info("\n" + "="*70)
    logger.info("TEST 3: Unified LLM Initialization")
    logger.info("="*70)
    
    try:
        from app.core.llm_client import get_llm
        
        llm = get_llm(temperature=0.3)
        logger.info("✓ Unified LLM created successfully")
        logger.info(f"  • Temperature: 0.3")
        
        provider = llm.provider
        logger.info(f"  • Detected provider: {provider}")
        
        if provider == "huggingface":
            logger.info("✓ LLM is configured to use HuggingFace")
        
        return True
    except Exception as e:
        logger.error(f"✗ Unified LLM initialization failed: {e}")
        return False


def test_huggingface_client():
    """Test 4: HuggingFace client initialization"""
    logger.info("\n" + "="*70)
    logger.info("TEST 4: HuggingFace Client Initialization")
    logger.info("="*70)
    
    try:
        from app.core.huggingface_client import get_huggingface_client
        from app.core.config import settings
        
        if not settings.hf_access_token:
            logger.warning("✗ HuggingFace token not configured - skipping client test")
            return False
        
        logger.info("Initializing HuggingFace client...")
        client = get_huggingface_client(temperature=0.3)
        
        logger.info("✓ HuggingFace client initialized successfully")
        logger.info(f"  • Model: {settings.hf_model_name}")
        logger.info(f"  • Client class: {client.__class__.__name__}")
        
        return True
    except ValueError as e:
        logger.warning(f"⚠ HuggingFace client initialization warning: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ HuggingFace client initialization failed: {e}")
        return False


def test_startup_check():
    """Test 5: Startup configuration check"""
    logger.info("\n" + "="*70)
    logger.info("TEST 5: Startup Configuration Check")
    logger.info("="*70)
    
    try:
        from app.core.startup_check import get_provider_info
        
        info = get_provider_info()
        logger.info("✓ Startup check functions working")
        logger.info(f"  • Provider info: {info}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Startup check failed: {e}")
        return False


def test_imports():
    """Test 6: All necessary imports"""
    logger.info("\n" + "="*70)
    logger.info("TEST 6: Module Imports")
    logger.info("="*70)
    
    imports_to_test = [
        ("app.core.config", "Settings"),
        ("app.core.llm_client", "get_llm"),
        ("app.core.huggingface_client", "HuggingFaceClient"),
        ("app.core.huggingface_client", "get_huggingface_client"),
        ("app.core.startup_check", "check_configuration_on_startup"),
    ]
    
    all_passed = True
    for module, name in imports_to_test:
        try:
            exec(f"from {module} import {name}")
            logger.info(f"✓ {module}.{name}")
        except ImportError as e:
            logger.error(f"✗ {module}.{name}: {e}")
            all_passed = False
    
    return all_passed


def run_all_tests():
    """Run all tests"""
    logger.info("\n" + "="*70)
    logger.info("HuggingFace Integration Test Suite")
    logger.info("="*70)
    
    tests = [
        ("Configuration Loading", test_configuration),
        ("Provider Detection", test_provider_detection),
        ("Unified LLM Initialization", test_unified_llm_init),
        ("HuggingFace Client", test_huggingface_client),
        ("Startup Check", test_startup_check),
        ("Module Imports", test_imports),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    logger.info("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
