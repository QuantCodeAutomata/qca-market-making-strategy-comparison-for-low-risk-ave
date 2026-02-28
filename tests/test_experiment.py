"""Tests for experiment runner."""

import pytest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from market_making.experiment import ExperimentConfig, ExperimentRunner


class TestExperimentConfig:
    """Tests for ExperimentConfig."""
    
    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = ExperimentConfig(gamma=0.1, spread=1.0)
        
        assert config.gamma == 0.1
        assert config.spread == 1.0
        assert config.s0 == 100.0
        assert config.T == 1.0
        assert config.dt == 0.005
        assert config.sigma == 2.0
        assert config.A == 140.0
        assert config.k == 1.5
        assert config.q0 == 0
        assert config.X0 == 0.0
        assert config.n_paths == 1000
        assert config.seed == 42


class TestExperimentRunner:
    """Tests for ExperimentRunner."""
    
    def test_initialization(self) -> None:
        """Test experiment runner initialization."""
        config = ExperimentConfig(gamma=0.1, spread=1.0, n_paths=10)
        runner = ExperimentRunner(config)
        
        assert runner.config == config
    
    def test_run_experiment_structure(self) -> None:
        """Test that experiment returns correct structure."""
        config = ExperimentConfig(gamma=0.1, spread=1.0, n_paths=10, seed=42)
        runner = ExperimentRunner(config)
        
        results = runner.run_experiment()
        
        assert "gamma" in results
        assert "spread" in results
        assert "n_paths" in results
        assert "inventory_strategy" in results
        assert "symmetric_strategy" in results
        
        inv_results = results["inventory_strategy"]
        assert "profits" in inv_results
        assert "inventories" in inv_results
        assert "profit_mean" in inv_results
        assert "profit_std" in inv_results
        assert "inventory_mean" in inv_results
        assert "inventory_std" in inv_results
        
        sym_results = results["symmetric_strategy"]
        assert "profits" in sym_results
        assert "inventories" in sym_results
        assert "profit_mean" in sym_results
        assert "profit_std" in sym_results
        assert "inventory_mean" in sym_results
        assert "inventory_std" in sym_results
    
    def test_correct_number_of_paths(self) -> None:
        """Test that correct number of paths are simulated."""
        n_paths = 50
        config = ExperimentConfig(gamma=0.1, spread=1.0, n_paths=n_paths, seed=42)
        runner = ExperimentRunner(config)
        
        results = runner.run_experiment()
        
        assert len(results["inventory_strategy"]["profits"]) == n_paths
        assert len(results["inventory_strategy"]["inventories"]) == n_paths
        assert len(results["symmetric_strategy"]["profits"]) == n_paths
        assert len(results["symmetric_strategy"]["inventories"]) == n_paths
    
    def test_statistics_consistency(self) -> None:
        """Test that computed statistics match raw data."""
        config = ExperimentConfig(gamma=0.1, spread=1.0, n_paths=100, seed=42)
        runner = ExperimentRunner(config)
        
        results = runner.run_experiment()
        
        inv_profits = results["inventory_strategy"]["profits"]
        computed_mean = results["inventory_strategy"]["profit_mean"]
        computed_std = results["inventory_strategy"]["profit_std"]
        
        assert abs(np.mean(inv_profits) - computed_mean) < 1e-10
        assert abs(np.std(inv_profits, ddof=1) - computed_std) < 1e-10
    
    def test_generate_summary(self) -> None:
        """Test summary DataFrame generation."""
        config = ExperimentConfig(gamma=0.1, spread=1.0, n_paths=10, seed=42)
        runner = ExperimentRunner(config)
        
        results = runner.run_experiment()
        summary = runner.generate_summary(results)
        
        assert len(summary) == 2
        assert list(summary["Strategy"]) == ["Inventory", "Symmetric"]
        assert "Profit Mean" in summary.columns
        assert "Profit Std" in summary.columns
        assert "Inventory Mean" in summary.columns
        assert "Inventory Std" in summary.columns
    
    def test_inventory_strategy_reduces_variance(self) -> None:
        """Test that inventory strategy typically reduces variance."""
        config = ExperimentConfig(gamma=0.5, spread=1.15, n_paths=500, seed=42)
        runner = ExperimentRunner(config)
        
        results = runner.run_experiment()
        
        inv_profit_std = results["inventory_strategy"]["profit_std"]
        sym_profit_std = results["symmetric_strategy"]["profit_std"]
        
        inv_inventory_std = results["inventory_strategy"]["inventory_std"]
        sym_inventory_std = results["symmetric_strategy"]["inventory_std"]
        
        assert inv_profit_std < sym_profit_std
        assert inv_inventory_std < sym_inventory_std
    
    def test_reproducibility(self) -> None:
        """Test that experiments are reproducible with same seed."""
        config1 = ExperimentConfig(gamma=0.1, spread=1.0, n_paths=50, seed=42)
        runner1 = ExperimentRunner(config1)
        results1 = runner1.run_experiment()
        
        config2 = ExperimentConfig(gamma=0.1, spread=1.0, n_paths=50, seed=42)
        runner2 = ExperimentRunner(config2)
        results2 = runner2.run_experiment()
        
        assert abs(results1["inventory_strategy"]["profit_mean"] - 
                   results2["inventory_strategy"]["profit_mean"]) < 1e-10
        assert abs(results1["symmetric_strategy"]["profit_mean"] - 
                   results2["symmetric_strategy"]["profit_mean"]) < 1e-10
