"""
Receipt Processor Module - REVISED

Based on analysis showing receipts are NOT fully covered.
Key insights from interviews:
- Kevin: Different spending thresholds for different trip lengths
- Lisa: Diminishing returns on high receipts
- Dave: Small receipts get penalized
- The system gives NEGATIVE returns for receipts in many cases

New hypothesis: Receipts have partial coverage with complex rules
"""


class ReceiptProcessor:
    """
    Processes receipt amounts with complex coverage rules.
    
    Key finding: Receipts are not fully reimbursed!
    The system has coverage rates and penalties that can make
    high receipts actually REDUCE total reimbursement.
    """

    def __init__(self):
        # Base receipt coverage rates (not 100%!)
        self.base_coverage_rate = 0.5  # Only 50% of receipts covered by default
        
        # Trip-length dependent thresholds (from Kevin)
        self.short_trip_days = (1, 3)
        self.medium_trip_days = (4, 7)
        self.long_trip_days = 8
        
        # Daily spending thresholds
        self.short_trip_threshold = 75.0
        self.medium_trip_threshold = 120.0
        self.long_trip_threshold = 90.0
        
        # Coverage rates for different scenarios
        self.below_threshold_coverage = 0.75  # Better coverage if under threshold
        self.above_threshold_coverage = 0.25  # Poor coverage if over threshold
        
        # Small receipt penalty
        self.small_receipt_threshold = 20.0
        self.small_receipt_penalty = 50.0
        
    def process(self, days: float, receipts: float) -> float:
        """
        Process receipt amount with coverage rates and penalties.
        
        Key insight: This can return NEGATIVE values!
        High receipts can actually reduce total reimbursement.
        """
        if days <= 0 or receipts <= 0:
            return 0.0
            
        receipts_per_day = receipts / days
        
        # Determine coverage rate based on trip length and spending
        if self.short_trip_days[0] <= days <= self.short_trip_days[1]:
            threshold = self.short_trip_threshold
        elif self.medium_trip_days[0] <= days <= self.medium_trip_days[1]:
            threshold = self.medium_trip_threshold
        else:
            threshold = self.long_trip_threshold
            
        # Apply coverage rate
        if receipts_per_day <= threshold:
            coverage_rate = self.below_threshold_coverage
        else:
            # Over threshold - poor coverage
            coverage_rate = self.above_threshold_coverage
            
        # Calculate base receipt coverage
        receipt_pay = receipts * coverage_rate
        
        # Apply small receipt penalty
        if 0 < receipts and receipts_per_day < self.small_receipt_threshold:
            receipt_pay -= self.small_receipt_penalty
            
        # For very high spending, apply additional penalty
        if receipts_per_day > threshold * 2:
            excess = receipts_per_day - (threshold * 2)
            penalty = excess * days * 0.5
            receipt_pay -= penalty
            
        # Receipt pay can go negative!
        # This explains why high-receipt cases get lower total reimbursement
        return receipt_pay
        
    def get_parameters(self) -> dict:
        """Return current parameters for optimization."""
        return {
            "base_coverage_rate": self.base_coverage_rate,
            "short_trip_threshold": self.short_trip_threshold,
            "medium_trip_threshold": self.medium_trip_threshold,
            "long_trip_threshold": self.long_trip_threshold,
            "below_threshold_coverage": self.below_threshold_coverage,
            "above_threshold_coverage": self.above_threshold_coverage,
            "small_receipt_threshold": self.small_receipt_threshold,
            "small_receipt_penalty": self.small_receipt_penalty,
        }
        
    def set_parameters(self, params: dict) -> None:
        """Set parameters from optimization process."""
        for param_name, param_value in params.items():
            if hasattr(self, param_name):
                setattr(self, param_name, param_value)