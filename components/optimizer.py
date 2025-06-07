"""
Optimizer Module

Coordinates parameter optimization across all reimbursement system components.
Implements systematic parameter tuning as outlined in the master plan Phase 4.

This module allows AI agents to:
1. Extract parameters from all components
2. Run systematic optimization (grid search, scipy.optimize, etc.)
3. Update all components with optimized parameters
4. Evaluate performance against test cases

AI Agent Focus Areas:
1. Implement different optimization algorithms
2. Define parameter bounds and constraints
3. Create objective functions for different optimization goals
4. Handle parameter interdependencies
5. Implement parallel optimization strategies
"""

import json
from typing import Dict, List, Tuple, Any, Optional

# Optional scipy import for optimization
try:
    from scipy.optimize import minimize, differential_evolution
    import numpy as np

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print(
        "Warning: scipy not available. Install with 'uv add scipy' for optimization features."
    )

from .per_diem.per_diem import PerDiemCalculator
from .mileage.mileage import MileageCalculator
from .receipts.receipts import ReceiptProcessor
from .bonuses.bonuses import BonusCalculator
from .bugs.bugs import BugProcessor


class SystemOptimizer:
    """
    Optimizes parameters across all reimbursement system components.

    This class provides a unified interface for parameter optimization,
    allowing AI agents to focus on different optimization strategies
    while maintaining component modularity.
    """

    def __init__(self, test_cases_file: str = "public_cases.json"):
        self.test_cases_file = test_cases_file
        self.test_cases = self._load_test_cases()

        # Initialize all components
        self.per_diem_calc = PerDiemCalculator()
        self.mileage_calc = MileageCalculator()
        self.receipt_processor = ReceiptProcessor()
        self.bonus_calc = BonusCalculator()
        self.bug_processor = BugProcessor()

        # Track optimization history
        self.optimization_history = []

    def _load_test_cases(self) -> List[Dict]:
        """Load test cases from JSON file."""
        try:
            with open(self.test_cases_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {self.test_cases_file} not found. Using empty test set.")
            return []

    def calculate_reimbursement(
        self, days: float, miles: float, receipts: float
    ) -> float:
        """Calculate reimbursement using current component parameters."""

        # Calculate base components
        per_diem_pay = self.per_diem_calc.calculate(days)
        mileage_pay = self.mileage_calc.calculate(miles)
        receipt_pay = self.receipt_processor.process(days, receipts)

        # Calculate bonuses and bugs
        bonus_amount = self.bonus_calc.calculate_all_bonuses(days, miles, receipts)
        bug_adjustment = self.bug_processor.apply_bugs(receipts)

        # Combine all components
        total = per_diem_pay + mileage_pay + receipt_pay + bonus_amount + bug_adjustment

        return round(total, 2)

    def evaluate_performance(self) -> Dict[str, float]:
        """Evaluate current parameters against test cases."""
        if not self.test_cases:
            return {"error": float("inf"), "exact_matches": 0, "close_matches": 0}

        total_error = 0.0
        exact_matches = 0
        close_matches = 0
        max_error = 0.0

        for case in self.test_cases:
            input_data = case["input"]
            expected = case["expected_output"]

            actual = self.calculate_reimbursement(
                input_data["trip_duration_days"],
                input_data["miles_traveled"],
                input_data["total_receipts_amount"],
            )

            error = abs(actual - expected)
            total_error += error
            max_error = max(max_error, error)

            if error < 0.01:
                exact_matches += 1
            if error < 1.0:
                close_matches += 1

        avg_error = total_error / len(self.test_cases)

        return {
            "avg_error": avg_error,
            "total_error": total_error,
            "max_error": max_error,
            "exact_matches": exact_matches,
            "close_matches": close_matches,
            "exact_match_rate": exact_matches / len(self.test_cases),
            "close_match_rate": close_matches / len(self.test_cases),
        }

    def get_all_parameters(self) -> Dict[str, Any]:
        """Get parameters from all components."""
        all_params = {}

        # Prefix parameters by component to avoid naming conflicts
        all_params.update(
            {f"per_diem_{k}": v for k, v in self.per_diem_calc.get_parameters().items()}
        )
        all_params.update(
            {f"mileage_{k}": v for k, v in self.mileage_calc.get_parameters().items()}
        )
        all_params.update(
            {
                f"receipts_{k}": v
                for k, v in self.receipt_processor.get_parameters().items()
            }
        )
        all_params.update(
            {f"bonuses_{k}": v for k, v in self.bonus_calc.get_parameters().items()}
        )
        all_params.update(
            {f"bugs_{k}": v for k, v in self.bug_processor.get_parameters().items()}
        )

        return all_params

    def set_all_parameters(self, params: Dict[str, Any]) -> None:
        """Set parameters for all components."""

        # Separate parameters by component prefix
        per_diem_params = {
            k.replace("per_diem_", ""): v
            for k, v in params.items()
            if k.startswith("per_diem_")
        }
        mileage_params = {
            k.replace("mileage_", ""): v
            for k, v in params.items()
            if k.startswith("mileage_")
        }
        receipts_params = {
            k.replace("receipts_", ""): v
            for k, v in params.items()
            if k.startswith("receipts_")
        }
        bonuses_params = {
            k.replace("bonuses_", ""): v
            for k, v in params.items()
            if k.startswith("bonuses_")
        }
        bugs_params = {
            k.replace("bugs_", ""): v
            for k, v in params.items()
            if k.startswith("bugs_")
        }

        # Update each component
        if per_diem_params:
            self.per_diem_calc.set_parameters(per_diem_params)
        if mileage_params:
            self.mileage_calc.set_parameters(mileage_params)
        if receipts_params:
            self.receipt_processor.set_parameters(receipts_params)
        if bonuses_params:
            self.bonus_calc.set_parameters(bonuses_params)
        if bugs_params:
            self.bug_processor.set_parameters(bugs_params)

    def objective_function(self, param_values, param_names: List[str]) -> float:
        """Objective function for optimization (minimize average error)."""

        # Convert array to parameter dictionary
        params = dict(zip(param_names, param_values))

        # Set parameters
        self.set_all_parameters(params)

        # Evaluate performance
        performance = self.evaluate_performance()

        # Return metric to minimize (average error + penalty for low exact matches)
        return performance["avg_error"] + (1000 - performance["exact_matches"]) * 0.01

    def optimize_parameters(
        self, method: str = "differential_evolution", max_iterations: int = 100
    ) -> Dict[str, Any]:
        """
        Optimize parameters using specified method.

        Args:
            method: Optimization method ('differential_evolution', 'minimize', 'grid_search')
            max_iterations: Maximum number of iterations

        Returns:
            Optimization results dictionary
        """

        if not SCIPY_AVAILABLE:
            raise ImportError(
                "scipy is required for optimization. Install with 'uv add scipy'"
            )

        # Get current parameters and define bounds
        current_params = self.get_all_parameters()
        param_names = list(current_params.keys())

        # Define reasonable bounds for each parameter type
        bounds = self._get_parameter_bounds(param_names, current_params)

        if method == "differential_evolution":
            result = differential_evolution(
                self.objective_function,
                bounds,
                args=(param_names,),
                maxiter=max_iterations,
                seed=42,
            )

            # Set optimized parameters
            optimized_params = dict(zip(param_names, result.x))
            self.set_all_parameters(optimized_params)

            return {
                "method": method,
                "success": result.success,
                "final_error": result.fun,
                "iterations": result.nit,
                "optimized_parameters": optimized_params,
                "performance": self.evaluate_performance(),
            }

        # TODO for AI agents: Implement other optimization methods
        # - Grid search for discrete parameters
        # - Bayesian optimization for expensive evaluations
        # - Multi-objective optimization
        # - Component-wise optimization

        else:
            raise NotImplementedError(f"Optimization method '{method}' not implemented")

    def _get_parameter_bounds(
        self, param_names: List[str], current_params: Dict[str, Any]
    ) -> List[Tuple[float, float]]:
        """Define reasonable bounds for parameters based on their names and current values."""

        bounds = []

        for name in param_names:
            current_value = current_params[name]

            # Define bounds based on parameter type and name
            if "rate" in name or "daily_rate" in name:
                # Rates should be positive, within reasonable range
                bounds.append((max(0.01, current_value * 0.5), current_value * 2.0))
            elif "threshold" in name:
                # Thresholds should be positive
                bounds.append((max(1.0, current_value * 0.5), current_value * 2.0))
            elif "bonus" in name or "penalty" in name:
                # Bonuses and penalties should be reasonable amounts
                bounds.append((0.0, max(200.0, current_value * 3.0)))
            elif "factor" in name:
                # Factors should be between 0 and 2
                bounds.append((0.0, 2.0))
            else:
                # Default bounds
                bounds.append((max(0.0, current_value * 0.1), current_value * 10.0))

        return bounds

    def save_optimization_state(self, filename: str) -> None:
        """Save current parameters and performance to file."""
        state = {
            "parameters": self.get_all_parameters(),
            "performance": self.evaluate_performance(),
            "optimization_history": self.optimization_history,
        }

        with open(filename, "w") as f:
            json.dump(state, f, indent=2)

    def load_optimization_state(self, filename: str) -> None:
        """Load parameters and state from file."""
        with open(filename, "r") as f:
            state = json.load(f)

        self.set_all_parameters(state["parameters"])
        if "optimization_history" in state:
            self.optimization_history = state["optimization_history"]
