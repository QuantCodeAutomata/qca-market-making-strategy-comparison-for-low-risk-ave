"""Visualization utilities for experiment results."""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any
import os


def plot_profit_distributions(results: Dict[str, Any], save_path: str | None = None) -> None:
    """
    Plot profit distributions for both strategies.
    
    Parameters
    ----------
    results : dict
        Experiment results
    save_path : str, optional
        Path to save figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    gamma = results["gamma"]
    
    inv_profits = results["inventory_strategy"]["profits"]
    sym_profits = results["symmetric_strategy"]["profits"]
    
    axes[0].hist(inv_profits, bins=50, alpha=0.7, color='blue', edgecolor='black')
    axes[0].axvline(np.mean(inv_profits), color='red', linestyle='--', 
                    label=f'Mean: {np.mean(inv_profits):.2f}')
    axes[0].set_xlabel('Terminal Profit')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title(f'Inventory Strategy (γ={gamma})')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    axes[1].hist(sym_profits, bins=50, alpha=0.7, color='green', edgecolor='black')
    axes[1].axvline(np.mean(sym_profits), color='red', linestyle='--',
                    label=f'Mean: {np.mean(sym_profits):.2f}')
    axes[1].set_xlabel('Terminal Profit')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title(f'Symmetric Strategy (γ={gamma})')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved profit distribution plot to {save_path}")
    
    plt.close()


def plot_inventory_distributions(results: Dict[str, Any], save_path: str | None = None) -> None:
    """
    Plot inventory distributions for both strategies.
    
    Parameters
    ----------
    results : dict
        Experiment results
    save_path : str, optional
        Path to save figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    gamma = results["gamma"]
    
    inv_inventories = results["inventory_strategy"]["inventories"]
    sym_inventories = results["symmetric_strategy"]["inventories"]
    
    axes[0].hist(inv_inventories, bins=50, alpha=0.7, color='blue', edgecolor='black')
    axes[0].axvline(np.mean(inv_inventories), color='red', linestyle='--',
                    label=f'Mean: {np.mean(inv_inventories):.2f}')
    axes[0].set_xlabel('Terminal Inventory')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title(f'Inventory Strategy (γ={gamma})')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    axes[1].hist(sym_inventories, bins=50, alpha=0.7, color='green', edgecolor='black')
    axes[1].axvline(np.mean(sym_inventories), color='red', linestyle='--',
                    label=f'Mean: {np.mean(sym_inventories):.2f}')
    axes[1].set_xlabel('Terminal Inventory')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title(f'Symmetric Strategy (γ={gamma})')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved inventory distribution plot to {save_path}")
    
    plt.close()


def plot_variance_comparison(all_results: Dict[str, Dict[str, Any]], save_path: str | None = None) -> None:
    """
    Plot variance comparison across all gamma values.
    
    Parameters
    ----------
    all_results : dict
        Results from all experiments
    save_path : str, optional
        Path to save figure
    """
    gammas = []
    inv_profit_stds = []
    sym_profit_stds = []
    inv_inventory_stds = []
    sym_inventory_stds = []
    
    for exp_id in sorted(all_results.keys()):
        results = all_results[exp_id]
        gammas.append(results["gamma"])
        inv_profit_stds.append(results["inventory_strategy"]["profit_std"])
        sym_profit_stds.append(results["symmetric_strategy"]["profit_std"])
        inv_inventory_stds.append(results["inventory_strategy"]["inventory_std"])
        sym_inventory_stds.append(results["symmetric_strategy"]["inventory_std"])
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    x = np.arange(len(gammas))
    width = 0.35
    
    axes[0].bar(x - width/2, inv_profit_stds, width, label='Inventory', color='blue', alpha=0.7)
    axes[0].bar(x + width/2, sym_profit_stds, width, label='Symmetric', color='green', alpha=0.7)
    axes[0].set_xlabel('Risk Aversion (γ)')
    axes[0].set_ylabel('Standard Deviation')
    axes[0].set_title('Profit Standard Deviation Comparison')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([f'{g}' for g in gammas])
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    axes[1].bar(x - width/2, inv_inventory_stds, width, label='Inventory', color='blue', alpha=0.7)
    axes[1].bar(x + width/2, sym_inventory_stds, width, label='Symmetric', color='green', alpha=0.7)
    axes[1].set_xlabel('Risk Aversion (γ)')
    axes[1].set_ylabel('Standard Deviation')
    axes[1].set_title('Terminal Inventory Standard Deviation Comparison')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([f'{g}' for g in gammas])
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved variance comparison plot to {save_path}")
    
    plt.close()


def generate_all_plots(all_results: Dict[str, Dict[str, Any]], output_dir: str = "results") -> None:
    """
    Generate all plots for the experiments.
    
    Parameters
    ----------
    all_results : dict
        Results from all experiments
    output_dir : str
        Directory to save plots
    """
    for exp_id, results in all_results.items():
        gamma = results["gamma"]
        
        plot_profit_distributions(
            results,
            save_path=f"{output_dir}/{exp_id}_profit_distributions.png"
        )
        
        plot_inventory_distributions(
            results,
            save_path=f"{output_dir}/{exp_id}_inventory_distributions.png"
        )
    
    plot_variance_comparison(
        all_results,
        save_path=f"{output_dir}/variance_comparison.png"
    )
    
    print(f"\nAll plots saved to {output_dir}/")
