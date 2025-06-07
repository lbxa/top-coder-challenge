import sys
from components.per_diem.per_diem import PerDiemCalculator
from components.mileage.mileage import MileageCalculator
from components.receipts.receipts import ReceiptProcessor
from components.bonuses.bonuses import BonusCalculator
from components.bugs.bugs import BugProcessor
from components.duration.duration import DurationCalculator


from claude_solution.reimbursement_calculator_v2 import (
    calculate_reimbursement as claude_calculate_reimbursement,
)


def calculate_reimbursement(days: float, miles: float, receipts: float) -> float:
    """
    Main reimbursement calculation function that orchestrates all components.

    Architecture follows the master plan:
    1. Calculate base per diem
    2. Calculate tiered mileage pay
    3. Process receipts (with penalties/caps)
    4. Apply duration-specific adjustments
    5. Apply global bonuses and quirks
    6. Return final formatted amount
    """

    # Initialize all component calculators
    per_diem_calc = PerDiemCalculator()
    mileage_calc = MileageCalculator()
    receipt_processor = ReceiptProcessor()
    bonus_calc = BonusCalculator()
    bug_processor = BugProcessor()
    duration_calc = DurationCalculator()

    # 1. Calculate base components
    per_diem_pay = per_diem_calc.calculate(days)
    mileage_pay = mileage_calc.calculate(miles)

    # 2. Process receipts (most complex component)
    receipt_pay = receipt_processor.process(days, receipts)

    # 3. Combine base total
    base_total = per_diem_pay + mileage_pay + receipt_pay

    # 4. Apply duration-specific adjustments
    duration_adjustment = duration_calc.calculate(days)

    # 5. Apply bonuses and quirks
    bonus_amount = bonus_calc.calculate_all_bonuses(days, miles, receipts)
    bug_adjustment = bug_processor.apply_bugs(receipts)

    # 6. Final calculation
    total = base_total + duration_adjustment + bonus_amount + bug_adjustment

    return round(total, 2)


if __name__ == "__main__":
    # Get command line arguments
    days = float(sys.argv[1])
    miles = float(sys.argv[2])
    receipts = float(sys.argv[3])

    # Calculate and print reimbursement
    print(claude_calculate_reimbursement(days, miles, receipts))
