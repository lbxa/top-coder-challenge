"""
Optimized Per Diem Calculator Module

Based on comprehensive data analysis of historical reimbursement patterns.
Key finding: Per diem is NOT a simple $100/day rate but includes fixed costs
that create a declining per-day rate structure.
"""


class OptimizedPerDiemCalculator:
    """
    Calculates per diem payments based on discovered patterns in the data.
    
    Analysis revealed:
    - Strong economies of scale (longer trips have lower per-day rates)
    - No 5-day bonus despite interview claims
    - Fixed cost component makes short trips expensive per day
    """
    
    def __init__(self):
        # Discovered rate structure from data analysis
        # These represent TOTAL per diem for the trip, not daily rates
        self.rate_structure = {
            1: 874.0,      # 1-day trips have high fixed costs
            2: 1038.0,     # 519 * 2
            3: 1011.0,     # 337 * 3
            4: 1220.0,     # 305 * 4
            5: 1275.0,     # 255 * 5
            6: 1440.0,     # 240 * 6
            7: 1519.0,     # 217 * 7
            8: 1440.0,     # 180 * 8
            9: 1440.0,     # 160 * 9
            10: 1450.0,    # 145 * 10
        }
        
        # For trips longer than 10 days
        self.extended_daily_rate = 145.0
        
        # Alternative model: Fixed cost + declining daily rate
        self.fixed_cost = 400.0  # Covers admin, setup, etc.
        self.daily_rates_by_duration = {
            1: 474.0,   # Very high for single day
            2: 319.0,   # Still high for 2 days
            3: 204.0,   # Declining...
            4: 180.0,
            5: 175.0,
            6: 165.0,
            7: 160.0,
            8: 150.0,
            9: 145.0,
            10: 140.0,
        }
        self.extended_rate = 135.0
    
    def calculate(self, days: int) -> float:
        """
        Calculate per diem payment for given number of days.
        
        Uses discovered non-linear rate structure from data analysis.
        """
        if days <= 0:
            return 0.0
            
        # Use lookup table for common trip lengths
        if days in self.rate_structure:
            return self.rate_structure[days]
        
        # For longer trips, use extended rate
        if days > 10:
            return 1450.0 + (days - 10) * self.extended_daily_rate
        
        # Shouldn't reach here, but fallback to interpolation
        return days * self.extended_daily_rate
    
    def calculate_alternative(self, days: int) -> float:
        """
        Alternative calculation using fixed cost + daily rate model.
        
        This might be more accurate as it explicitly models the fixed
        cost component that makes short trips expensive.
        """
        if days <= 0:
            return 0.0
        
        # Get daily rate for this duration
        if days <= 10:
            daily_rate = self.daily_rates_by_duration.get(days, self.extended_rate)
        else:
            daily_rate = self.extended_rate
        
        # Fixed cost + daily rates
        return self.fixed_cost + (days * daily_rate)
    
    def get_parameters(self) -> dict:
        """Return current parameters for further optimization."""
        return {
            "rate_structure": self.rate_structure,
            "extended_daily_rate": self.extended_daily_rate,
            "fixed_cost": self.fixed_cost,
            "daily_rates": self.daily_rates_by_duration,
        }
    
    def explain_calculation(self, days: int) -> str:
        """
        Provide explanation for the calculation.
        """
        if days <= 0:
            return "No per diem for zero or negative days"
        
        per_diem = self.calculate(days)
        avg_daily = per_diem / days
        
        explanation = f"Per diem calculation for {days}-day trip:\n"
        explanation += f"Total per diem: ${per_diem:.2f}\n"
        explanation += f"Average per day: ${avg_daily:.2f}\n"
        
        if days == 1:
            explanation += "Note: Single-day trips include high fixed costs\n"
        elif days <= 3:
            explanation += "Note: Short trips have higher per-day rates due to fixed costs\n"
        elif days >= 10:
            explanation += "Note: Extended trips use a flat daily rate\n"
        
        return explanation


# Example usage and validation
if __name__ == "__main__":
    calculator = OptimizedPerDiemCalculator()
    
    print("Per Diem Analysis Results:")
    print("-" * 50)
    
    for days in range(1, 15):
        per_diem = calculator.calculate(days)
        daily_avg = per_diem / days
        print(f"{days:2d} days: ${per_diem:7.2f} total (${daily_avg:6.2f}/day)")
    
    print("\nAlternative Model (Fixed + Daily):")
    print("-" * 50)
    
    for days in range(1, 15):
        per_diem = calculator.calculate_alternative(days)
        daily_avg = per_diem / days
        print(f"{days:2d} days: ${per_diem:7.2f} total (${daily_avg:6.2f}/day)")