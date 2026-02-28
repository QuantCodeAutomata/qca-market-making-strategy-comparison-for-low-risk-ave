#!/usr/bin/env python3
"""Run all market making strategy comparison experiments."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from market_making.experiment import run_all_experiments
from market_making.visualization import generate_all_plots
import pandas as pd


def main() -> None:
    """Run all experiments and generate visualizations."""
    print("="*70)
    print("Market Making Strategy Comparison Experiments")
    print("="*70)
    print("\nComparing Inventory-Based vs Symmetric Quoting Strategies")
    print("Across different risk aversion levels (γ = 0.01, 0.1, 0.5)\n")
    
    all_results = run_all_experiments()
    
    generate_all_plots(all_results, output_dir="results")
    
    print("\n" + "="*70)
    print("Summary Comparison Across All Experiments")
    print("="*70 + "\n")
    
    summary_rows = []
    for exp_id in sorted(all_results.keys()):
        results = all_results[exp_id]
        gamma = results["gamma"]
        
        inv = results["inventory_strategy"]
        sym = results["symmetric_strategy"]
        
        profit_var_reduction = (1 - inv["profit_std"]**2 / sym["profit_std"]**2) * 100
        inv_var_reduction = (1 - inv["inventory_std"]**2 / sym["inventory_std"]**2) * 100
        
        summary_rows.append({
            "Experiment": exp_id,
            "γ": gamma,
            "Inv Profit Mean": f"{inv['profit_mean']:.2f}",
            "Inv Profit Std": f"{inv['profit_std']:.2f}",
            "Sym Profit Mean": f"{sym['profit_mean']:.2f}",
            "Sym Profit Std": f"{sym['profit_std']:.2f}",
            "Profit Var Reduction %": f"{profit_var_reduction:.2f}",
            "Inventory Var Reduction %": f"{inv_var_reduction:.2f}"
        })
    
    summary_df = pd.DataFrame(summary_rows)
    print(summary_df.to_string(index=False))
    print("\n" + "="*70)
    
    summary_df.to_csv("results/summary_statistics.csv", index=False)
    print("\nSummary statistics saved to results/summary_statistics.csv")
    
    print("\n" + "="*70)
    print("All experiments completed successfully!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
