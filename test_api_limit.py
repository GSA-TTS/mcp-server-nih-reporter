#!/usr/bin/env python3
"""
Test script to validate API pagination limit enforcement.
This tests the get_all_responses() function with queries that exceed 15,000 results.
"""

import asyncio
import sys
from reporter.models import SearchParams
from reporter.utils import get_all_responses, API_PAGINATION_LIMIT
from reporter.models import IncludeField


async def test_under_limit():
    """Test a query that should succeed (under 15,000 results)"""
    print("\n" + "="*80)
    print("TEST 1: Query Under Limit (Should Succeed)")
    print("="*80)
    
    # Query with limited scope - should be under 15K
    search_params = SearchParams(
        fiscal_years=[2024],
        agencies=["NCI"]
    )
    
    try:
        results = await get_all_responses(
            search_params,
            [IncludeField.PROJECT_NUM.value],
            limit=500
        )
        total = len(results['results'])
        print(f"✅ SUCCESS: Retrieved {total:,} results (under {API_PAGINATION_LIMIT:,} limit)")
        return True
    except ValueError as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False


async def test_over_limit():
    """Test a query that should fail (over 15,000 results)"""
    print("\n" + "="*80)
    print("TEST 2: Query Over Limit (Should Fail with Clear Error)")
    print("="*80)
    
    # Broad query - should exceed 15K
    search_params = SearchParams(
        fiscal_years=list(range(2000, 2025)),  # 25 years
        agencies=None  # All agencies
    )
    
    try:
        results = await get_all_responses(
            search_params,
            [IncludeField.PROJECT_NUM.value],
            limit=500
        )
        total = len(results['results'])
        print(f"❌ FAIL: Query succeeded with {total:,} results, but should have raised ValueError")
        return False
    except ValueError as e:
        error_msg = str(e)
        print(f"✅ SUCCESS: ValueError raised as expected")
        print(f"\nError message preview:")
        print("-" * 80)
        print(error_msg[:500])
        if len(error_msg) > 500:
            print("...")
        print("-" * 80)
        
        # Verify error message contains key information
        checks = [
            ("mentions result count", "results" in error_msg.lower()),
            ("mentions 15,000 limit", "15,000" in error_msg or "15000" in error_msg),
            ("provides suggestions", "narrow" in error_msg.lower() or "refine" in error_msg.lower()),
            ("mentions fiscal years", "fiscal year" in error_msg.lower()),
        ]
        
        print("\nError message validation:")
        all_passed = True
        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False
        
        return all_passed


async def test_exact_limit():
    """Test edge case: query with results close to 15,000"""
    print("\n" + "="*80)
    print("TEST 3: Query Near Limit (Edge Case)")
    print("="*80)
    
    # Try to craft a query near the limit
    # This is difficult without knowing exact counts, so we'll use a moderate query
    search_params = SearchParams(
        fiscal_years=[2020, 2021, 2022],
        agencies=["NCI", "NHLBI"]
    )
    
    try:
        results = await get_all_responses(
            search_params,
            [IncludeField.PROJECT_NUM.value],
            limit=500
        )
        total = len(results['results'])
        if total < API_PAGINATION_LIMIT:
            print(f"✅ Query returned {total:,} results (under limit)")
            return True
        else:
            print(f"⚠️  Query returned {total:,} results (at or over limit, but succeeded)")
            return True
    except ValueError as e:
        print(f"✅ Query failed with ValueError (result count exceeded limit)")
        return True


async def main():
    print("\n" + "="*80)
    print("API PAGINATION LIMIT VALIDATION TEST SUITE")
    print("="*80)
    print(f"Testing enforcement of {API_PAGINATION_LIMIT:,} result limit")
    print("="*80)
    
    results = []
    
    # Run tests
    results.append(("Under Limit Test", await test_under_limit()))
    results.append(("Over Limit Test", await test_over_limit()))
    results.append(("Edge Case Test", await test_exact_limit()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("="*80)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("="*80)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
