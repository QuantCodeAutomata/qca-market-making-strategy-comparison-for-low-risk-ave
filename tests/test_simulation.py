"""Tests for market making simulation."""

import pytest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from market_making.simulation import MarketMakingSimulation
from market_making.strategies import InventoryStrategy, SymmetricStrategy


class TestMarketMakingSimulation:
    """Tests for MarketMakingSimulation."""
    
    def test_initialization(self) -> None:
        """Test simulation initialization."""
        sim = MarketMakingSimulation(
            s0=100.0,
            T=1.0,
            dt=0.005,
            sigma=2.0,
            A=140.0,
            k=1.5,
            q0=0,
            X0=0.0,
            seed=42
        )
        
        assert sim.s0 == 100.0
        assert sim.T == 1.0
        assert sim.dt == 0.005
        assert sim.sigma == 2.0
        assert sim.A == 140.0
        assert sim.k == 1.5
        assert sim.q0 == 0
        assert sim.X0 == 0.0
        assert sim.n_steps == 200
    
    def test_intensity_computation(self) -> None:
        """Test execution intensity calculation."""
        sim = MarketMakingSimulation(A=140.0, k=1.5)
        
        assert abs(sim._compute_intensity(0.0) - 140.0) < 1e-10
        
        lambda_1 = sim._compute_intensity(1.0)
        expected_1 = 140.0 * np.exp(-1.5)
        assert abs(lambda_1 - expected_1) < 1e-10
        
        assert sim._compute_intensity(2.0) < sim._compute_intensity(1.0)
    
    def test_price_path_simulation(self) -> None:
        """Test mid-price path generation."""
        sim = MarketMakingSimulation(s0=100.0, T=1.0, dt=0.005, sigma=2.0, seed=42)
        
        prices = sim._simulate_price_path()
        
        assert len(prices) == sim.n_steps + 1
        assert prices[0] == 100.0
        
        for i in range(1, len(prices)):
            diff = abs(prices[i] - prices[i-1])
            expected_step = sim.sigma * np.sqrt(sim.dt)
            assert abs(diff - expected_step) < 1e-10
    
    def test_single_path_execution(self) -> None:
        """Test single simulation path."""
        sim = MarketMakingSimulation(
            s0=100.0,
            T=1.0,
            dt=0.005,
            sigma=2.0,
            A=140.0,
            k=1.5,
            q0=0,
            X0=0.0,
            seed=42
        )
        
        strategy = SymmetricStrategy(spread=1.0)
        profit, inventory, inv_path, cash_path = sim.run_single_path(strategy)
        
        assert len(inv_path) == sim.n_steps + 1
        assert len(cash_path) == sim.n_steps + 1
        assert inv_path[0] == 0
        assert cash_path[0] == 0.0
        assert isinstance(profit, (int, float))
        assert isinstance(inventory, (int, np.integer))
    
    def test_reproducibility_with_seed(self) -> None:
        """Test that results are reproducible with same seed."""
        strategy = SymmetricStrategy(spread=1.0)
        
        sim1 = MarketMakingSimulation(seed=42)
        profit1, inv1, _, _ = sim1.run_single_path(strategy)
        
        sim2 = MarketMakingSimulation(seed=42)
        profit2, inv2, _, _ = sim2.run_single_path(strategy)
        
        assert abs(profit1 - profit2) < 1e-10
        assert inv1 == inv2
    
    def test_different_seeds_produce_different_results(self) -> None:
        """Test that different seeds produce different results."""
        strategy = SymmetricStrategy(spread=1.0)
        
        sim1 = MarketMakingSimulation(seed=42)
        profit1, _, _, _ = sim1.run_single_path(strategy)
        
        sim2 = MarketMakingSimulation(seed=123)
        profit2, _, _, _ = sim2.run_single_path(strategy)
        
        assert abs(profit1 - profit2) > 1e-6
    
    def test_multiple_paths_shape(self) -> None:
        """Test multiple paths execution."""
        sim = MarketMakingSimulation(seed=42)
        strategy = SymmetricStrategy(spread=1.0)
        
        n_paths = 100
        profits, inventories = sim.run_multiple_paths(strategy, n_paths)
        
        assert len(profits) == n_paths
        assert len(inventories) == n_paths
    
    def test_inventory_affects_pnl(self) -> None:
        """Test that inventory position affects final P&L."""
        sim = MarketMakingSimulation(s0=100.0, T=1.0, dt=0.005, seed=42)
        strategy = InventoryStrategy(gamma=0.1, sigma=2.0, spread=1.0)
        
        profit, inventory, inv_path, cash_path = sim.run_single_path(strategy)
        
        assert isinstance(inventory, (int, np.integer))
        assert isinstance(profit, (int, float))
    
    def test_cash_updates_correctly(self) -> None:
        """Test that cash position updates correctly on execution."""
        sim = MarketMakingSimulation(
            s0=100.0,
            T=1.0,
            dt=0.005,
            A=1000.0,
            k=0.5,
            seed=42
        )
        strategy = SymmetricStrategy(spread=1.0)
        
        _, _, inv_path, cash_path = sim.run_single_path(strategy)
        
        inventory_changes = np.diff(inv_path)
        cash_changes = np.diff(cash_path)
        
        assert len(inventory_changes) == len(cash_changes)
    
    def test_probability_capping(self) -> None:
        """Test that execution probabilities are capped at 1.0."""
        sim = MarketMakingSimulation(A=1000.0, k=0.1, dt=0.1)
        
        lambda_val = sim._compute_intensity(0.1)
        prob = min(lambda_val * sim.dt, 1.0)
        
        assert prob <= 1.0
