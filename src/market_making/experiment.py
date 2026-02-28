"""Experiment Runner for Market Making Strategy Comparison."""

import numpy as np
import pandas as pd
from typing import Dict, Any
from dataclasses import dataclass

from .simulation import MarketMakingSimulation
from .strategies import InventoryStrategy, SymmetricStrategy


@dataclass
class ExperimentConfig:
    """Configuration for a single experiment."""
    gamma: float
    spread: float
    s0: float = 100.0
    T: float = 1.0
    dt: float = 0.005
    sigma: float = 2.0
    A: float = 140.0
    k: float = 1.5
    q0: int = 0
    X0: float = 0.0
    n_paths: int = 1000
    seed: int = 42


class ExperimentRunner:
    """
    Runner for market making strategy comparison experiments.
    
    Parameters
    ----------
    config : ExperimentConfig
        Experiment configuration
    """
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        
    def run_experiment(self) -> Dict[str, Any]:
        """
        Run comparison experiment between inventory and symmetric strategies.
        
        Returns
        -------
        results : dict
            Dictionary containing results for both strategies
        """
        sim = MarketMakingSimulation(
            s0=self.config.s0,
            T=self.config.T,
            dt=self.config.dt,
            sigma=self.config.sigma,
            A=self.config.A,
            k=self.config.k,
            q0=self.config.q0,
            X0=self.config.X0,
            seed=self.config.seed
        )
        
        inventory_strategy = InventoryStrategy(
            gamma=self.config.gamma,
            sigma=self.config.sigma,
            spread=self.config.spread
        )
        
        symmetric_strategy = SymmetricStrategy(
            spread=self.config.spread
        )
        
        print(f"Running {self.config.n_paths} simulations for Inventory Strategy (γ={self.config.gamma})...")
        inv_profits, inv_inventories = sim.run_multiple_paths(
            inventory_strategy, 
            self.config.n_paths
        )
        
        sim_symmetric = MarketMakingSimulation(
            s0=self.config.s0,
            T=self.config.T,
            dt=self.config.dt,
            sigma=self.config.sigma,
            A=self.config.A,
            k=self.config.k,
            q0=self.config.q0,
            X0=self.config.X0,
            seed=self.config.seed
        )
        
        print(f"Running {self.config.n_paths} simulations for Symmetric Strategy (γ={self.config.gamma})...")
        sym_profits, sym_inventories = sim_symmetric.run_multiple_paths(
            symmetric_strategy,
            self.config.n_paths
        )
        
        results = {
            "gamma": self.config.gamma,
            "spread": self.config.spread,
            "n_paths": self.config.n_paths,
            "inventory_strategy": {
                "profits": inv_profits,
                "inventories": inv_inventories,
                "profit_mean": np.mean(inv_profits),
                "profit_std": np.std(inv_profits, ddof=1),
                "inventory_mean": np.mean(inv_inventories),
                "inventory_std": np.std(inv_inventories, ddof=1)
            },
            "symmetric_strategy": {
                "profits": sym_profits,
                "inventories": sym_inventories,
                "profit_mean": np.mean(sym_profits),
                "profit_std": np.std(sym_profits, ddof=1),
                "inventory_mean": np.mean(sym_inventories),
                "inventory_std": np.std(sym_inventories, ddof=1)
            }
        }
        
        return results
    
    def generate_summary(self, results: Dict[str, Any]) -> pd.DataFrame:
        """
        Generate summary statistics DataFrame.
        
        Parameters
        ----------
        results : dict
            Results from run_experiment
            
        Returns
        -------
        summary : pd.DataFrame
            Summary statistics for both strategies
        """
        summary_data = {
            "Strategy": ["Inventory", "Symmetric"],
            "Profit Mean": [
                results["inventory_strategy"]["profit_mean"],
                results["symmetric_strategy"]["profit_mean"]
            ],
            "Profit Std": [
                results["inventory_strategy"]["profit_std"],
                results["symmetric_strategy"]["profit_std"]
            ],
            "Inventory Mean": [
                results["inventory_strategy"]["inventory_mean"],
                results["symmetric_strategy"]["inventory_mean"]
            ],
            "Inventory Std": [
                results["inventory_strategy"]["inventory_std"],
                results["symmetric_strategy"]["inventory_std"]
            ]
        }
        
        return pd.DataFrame(summary_data)
    
    def print_summary(self, results: Dict[str, Any]) -> None:
        """Print formatted summary of results."""
        print(f"\n{'='*70}")
        print(f"Experiment Results: γ = {results['gamma']}, spread = {results['spread']}")
        print(f"{'='*70}\n")
        
        summary_df = self.generate_summary(results)
        print(summary_df.to_string(index=False))
        
        print(f"\n{'='*70}")
        print("Variance Reduction Analysis:")
        print(f"{'='*70}")
        
        profit_var_reduction = (
            1 - results["inventory_strategy"]["profit_std"]**2 / 
            results["symmetric_strategy"]["profit_std"]**2
        ) * 100
        
        inv_var_reduction = (
            1 - results["inventory_strategy"]["inventory_std"]**2 / 
            results["symmetric_strategy"]["inventory_std"]**2
        ) * 100
        
        print(f"Profit Variance Reduction: {profit_var_reduction:.2f}%")
        print(f"Inventory Variance Reduction: {inv_var_reduction:.2f}%")
        print(f"{'='*70}\n")


def run_all_experiments() -> Dict[str, Dict[str, Any]]:
    """
    Run all three experiments with different gamma values.
    
    Returns
    -------
    all_results : dict
        Results for all experiments
    """
    experiments = {
        "exp_1": ExperimentConfig(gamma=0.01, spread=1.33, seed=42),
        "exp_2": ExperimentConfig(gamma=0.1, spread=1.29, seed=42),
        "exp_3": ExperimentConfig(gamma=0.5, spread=1.15, seed=42)
    }
    
    all_results = {}
    
    for exp_id, config in experiments.items():
        print(f"\n{'#'*70}")
        print(f"Running {exp_id}: γ = {config.gamma}")
        print(f"{'#'*70}")
        
        runner = ExperimentRunner(config)
        results = runner.run_experiment()
        runner.print_summary(results)
        
        all_results[exp_id] = results
    
    return all_results
