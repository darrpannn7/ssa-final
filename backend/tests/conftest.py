"""
conftest.py — shared pytest fixtures for all test files
"""
import sys, os
# Ensure backend app is importable from any test file
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call":
        if rep.passed:
            print(f"\n[✅ PASS] {item.name}")
        elif rep.failed:
            print(f"\n[❌ FAIL] {item.name}")
    elif rep.when == "setup" and rep.skipped:
        print(f"\n[⏭️ SKIP] {item.name} - {rep.longrepr[-1] if hasattr(rep, 'longrepr') and hasattr(rep.longrepr, '__len__') else ''}")
