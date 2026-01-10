"""
Script to update the scoring system weights based on training feedback.
It can be executed periodically to automatically adjust the weights.
"""
import asyncio
import logging
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.settings import DB_CONFIG
from services.scoring import get_adjusted_weights

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    """
    Calculate and display the adjusted weights based on training feedback.
    """
    logging.info("Calculating adjusted weights based on training feedback...")
    
    weights = get_adjusted_weights(DB_CONFIG)
    
    print("\n=== Current Scoring System Weights ===")
    print(f"Sensitive Terms: {weights['sensitive_terms']:.2f} points per term")
    print(f"Suspicious Links: {weights['suspicious_links']:.2f} points per link")
    print(f"Repeated Sharing: {weights['repeated_sharing']:.2f} points")
    print(f"High-Risk User: {weights['high_risk_user']:.2f} points")
    print("\n=== Default Weights (for comparison) ===")
    print("Sensitive Terms: 3.00 points per term")
    print("Suspicious Links: 4.00 points per link")
    print("Repeated Sharing: 2.00 points")
    print("High-Risk User: 5.00 points")
    print("\nThe adjusted weights are used automatically in the score calculation of new messages.")

if __name__ == "__main__":
    asyncio.run(main())
