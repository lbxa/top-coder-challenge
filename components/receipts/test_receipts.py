"""
Test suite for the ReceiptProcessor component.

Tests the various hypotheses about receipt processing including:
- Trip-length dependent spending thresholds
- Overspending penalties
- Small receipt penalties
"""

from receipts import ReceiptProcessor


def test_basic_functionality():
    """Test basic receipt processing functionality."""
    processor = ReceiptProcessor()
    
    print("Testing basic receipt processing...")
    
    # Test zero days
    assert processor.process(0, 100) == 0.0
    print("✓ Zero days returns 0")
    
    # Test negative days (edge case)
    assert processor.process(-1, 100) == 0.0
    print("✓ Negative days returns 0")
    
    # Test zero receipts
    assert processor.process(5, 0) == 0.0
    print("✓ Zero receipts returns 0")
    
    # Test normal case within threshold
    result = processor.process(3, 200)  # 3 days, $200 total = $66.67/day (under $75)
    assert result == 200.0  # No penalty
    print(f"✓ Normal case (3 days, $200): ${result:.2f}")


def test_overspending_penalties():
    """Test overspending penalties for different trip lengths."""
    processor = ReceiptProcessor()
    
    print("\nTesting overspending penalties...")
    
    # Short trip (1-3 days) overspending
    # 2 days, $200 = $100/day, threshold is $75/day
    # Overage: $25/day * 2 days = $50 overage
    # Penalty: $50 * 0.5 = $25
    result = processor.process(2, 200)
    expected = 200 - 25
    print(f"Short trip overspending (2 days, $200): ${result:.2f} (expected ${expected:.2f})")
    
    # Medium trip (4-7 days) overspending  
    # 5 days, $700 = $140/day, threshold is $120/day
    # Overage: $20/day * 5 days = $100 overage
    # Penalty: $100 * 0.75 = $75
    result = processor.process(5, 700)
    expected = 700 - 75
    print(f"Medium trip overspending (5 days, $700): ${result:.2f} (expected ${expected:.2f})")
    
    # Long trip (8+ days) overspending
    # 10 days, $1200 = $120/day, threshold is $90/day
    # Overage: $30/day * 10 days = $300 overage
    # Penalty: $300 * 1.0 = $300
    result = processor.process(10, 1200)
    expected = 1200 - 300
    print(f"Long trip overspending (10 days, $1200): ${result:.2f} (expected ${expected:.2f})")


def test_small_receipt_penalty():
    """Test small receipt penalty."""
    processor = ReceiptProcessor()
    
    print("\nTesting small receipt penalty...")
    
    # Small receipts (under $20/day)
    # 5 days, $50 = $10/day < $20/day threshold
    # Penalty: $50 flat
    result = processor.process(5, 50)
    expected = 50 - 50  # Should be 0 (capped at 0)
    print(f"Small receipts (5 days, $50): ${result:.2f} (expected ${expected:.2f})")
    
    # Just under threshold
    # 3 days, $59 = $19.67/day < $20/day
    # Penalty: $50 flat
    result = processor.process(3, 59)
    expected = 59 - 50
    print(f"Just under threshold (3 days, $59): ${result:.2f} (expected ${expected:.2f})")
    
    # Just over threshold
    # 3 days, $61 = $20.33/day > $20/day
    # No small receipt penalty
    result = processor.process(3, 61)
    expected = 61  # No penalty
    print(f"Just over threshold (3 days, $61): ${result:.2f} (expected ${expected:.2f})")


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    processor = ReceiptProcessor()
    
    print("\nTesting edge cases...")
    
    # Boundary between short and medium trips
    result_3 = processor.process(3, 300)  # Short trip rules
    result_4 = processor.process(4, 480)  # Medium trip rules
    print(f"3 days at $100/day: ${result_3:.2f}")
    print(f"4 days at $120/day: ${result_4:.2f}")
    
    # Boundary between medium and long trips
    result_7 = processor.process(7, 840)  # Medium trip rules
    result_8 = processor.process(8, 960)  # Long trip rules  
    print(f"7 days at $120/day: ${result_7:.2f}")
    print(f"8 days at $120/day: ${result_8:.2f}")
    
    # Combined penalties (overspending + small receipts)
    # This should not happen in practice since small receipts can't also be overspending
    # But let's test the edge case
    result = processor.process(1, 10)  # $10/day is small
    print(f"1 day, $10 (small receipt): ${result:.2f}")
    
    # Very large receipts
    result = processor.process(5, 10000)  # $2000/day
    print(f"5 days, $10000 (very high): ${result:.2f}")


def test_parameter_management():
    """Test parameter get/set functionality."""
    processor = ReceiptProcessor()
    
    print("\nTesting parameter management...")
    
    # Get current parameters
    params = processor.get_parameters()
    print("Current parameters:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    
    # Modify parameters
    new_params = {
        "short_trip_threshold": 80.0,
        "medium_trip_threshold": 125.0,
        "small_receipt_penalty_factor": 0.90
    }
    processor.set_parameters(new_params)
    
    # Verify changes
    updated_params = processor.get_parameters()
    for key, value in new_params.items():
        assert updated_params[key] == value
    print("✓ Parameters updated successfully")


def test_negative_receipt_protection():
    """Test that receipt pay cannot go negative."""
    processor = ReceiptProcessor()
    
    print("\nTesting negative receipt protection...")
    
    # Case where penalties exceed receipt amount
    # 1 day, $10 = $10/day < $20/day, penalty = $50
    # Receipt pay would be $10 - $50 = -$40, but should be capped at 0
    result = processor.process(1, 10)
    assert result == 0.0
    print(f"✓ Negative protection works (1 day, $10): ${result:.2f}")
    
    # Large overspending that could go negative
    # 1 day, $200 = $200/day, threshold $75/day
    # Overage: $125 * 1 = $125, penalty = $125 * 0.5 = $62.50
    # Result: $200 - $62.50 = $137.50 (stays positive)
    result = processor.process(1, 200)
    assert result > 0
    print(f"✓ Large penalty stays positive (1 day, $200): ${result:.2f}")


if __name__ == "__main__":
    print("Receipt Processor Test Suite")
    print("=" * 50)
    
    test_basic_functionality()
    test_overspending_penalties()
    test_small_receipt_penalty()
    test_edge_cases()
    test_parameter_management()
    test_negative_receipt_protection()
    
    print("\n✅ All tests completed!")