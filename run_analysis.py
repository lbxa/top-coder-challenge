#!/usr/bin/env python3
"""
Script to run the analysis notebook and generate insights for the reimbursement system.
"""

import subprocess
import sys
import os


def main():
    """Run the analysis notebook."""
    print("🔍 Starting ACME Corp Reimbursement System Analysis...")
    print("=" * 60)

    # Check if we're in a uv environment
    if not os.path.exists(".venv"):
        print("❌ Virtual environment not found. Please run 'uv sync' first.")
        sys.exit(1)

    # Start Jupyter Lab
    print("🚀 Starting Jupyter Lab...")
    print("📝 Open analysis.ipynb to run the analysis")
    print("🌐 Jupyter Lab will open in your browser")
    print("=" * 60)

    try:
        # Run jupyter lab with uv
        subprocess.run(
            [
                "uv",
                "run",
                "jupyter",
                "lab",
                "--notebook-dir=.",
                "--ip=127.0.0.1",
                "--port=8888",
            ],
            check=True,
        )
    except KeyboardInterrupt:
        print("\n👋 Jupyter Lab stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Jupyter Lab: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
