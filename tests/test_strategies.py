"""Tests for quoting strategies."""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from market_making.strategies import InventoryStrategy, SymmetricStrategy


class TestInventoryStrategy:
    """Tests for InventoryStrategy."""
    
    def test_initialization(self) -> None:
        """Test strategy initialization."""
        strategy = InventoryStrategy(gamma=0.1, sigma=2.0, spread=1.5)
        assert strategy.gamma == 0.1
        assert strategy.sigma == 2.0
        assert strategy.spread == 1.5
    
    def test_zero_inventory_quotes(self) -> None:
        """Test quotes with zero inventory."""
        strategy = InventoryStrategy(gamma=0.1, sigma=2.0, spread=1.0)
        bid, ask = strategy.get_quotes(mid_price=100.0, inventory=0, time_remaining=1.0)
        
        assert ask > bid
        assert abs((ask - bid) - 1.0) < 1e-10
        assert abs((ask + bid) / 2 - 100.0) < 1e-10
    
    def test_positive_inventory_skews_quotes_down(self) -> None:
        """Test that positive inventory skews quotes downward."""
        strategy = InventoryStrategy(gamma=0.1, sigma=2.0, spread=1.0)
        
        bid_zero, ask_zero = strategy.get_quotes(mid_price=100.0, inventory=0, time_remaining=1.0)
        bid_pos, ask_pos = strategy.get_quotes(mid_price=100.0, inventory=5, time_remaining=1.0)
        
        assert bid_pos < bid_zero
        assert ask_pos < ask_zero
    
    def test_negative_inventory_skews_quotes_up(self) -> None:
        """Test that negative inventory skews quotes upward."""
        strategy = InventoryStrategy(gamma=0.1, sigma=2.0, spread=1.0)
        
        bid_zero, ask_zero = strategy.get_quotes(mid_price=100.0, inventory=0, time_remaining=1.0)
        bid_neg, ask_neg = strategy.get_quotes(mid_price=100.0, inventory=-5, time_remaining=1.0)
        
        assert bid_neg > bid_zero
        assert ask_neg > ask_zero
    
    def test_time_remaining_effect(self) -> None:
        """Test that time remaining affects reservation price."""
        strategy = InventoryStrategy(gamma=0.1, sigma=2.0, spread=1.0)
        
        bid_early, ask_early = strategy.get_quotes(mid_price=100.0, inventory=5, time_remaining=1.0)
        bid_late, ask_late = strategy.get_quotes(mid_price=100.0, inventory=5, time_remaining=0.1)
        
        assert bid_late > bid_early
        assert ask_late > ask_early
    
    def test_spread_maintained(self) -> None:
        """Test that spread is maintained regardless of inventory."""
        strategy = InventoryStrategy(gamma=0.1, sigma=2.0, spread=1.5)
        
        for inventory in [-10, -5, 0, 5, 10]:
            bid, ask = strategy.get_quotes(mid_price=100.0, inventory=inventory, time_remaining=1.0)
            assert abs((ask - bid) - 1.5) < 1e-10


class TestSymmetricStrategy:
    """Tests for SymmetricStrategy."""
    
    def test_initialization(self) -> None:
        """Test strategy initialization."""
        strategy = SymmetricStrategy(spread=1.5)
        assert strategy.spread == 1.5
    
    def test_symmetric_quotes(self) -> None:
        """Test that quotes are symmetric around mid-price."""
        strategy = SymmetricStrategy(spread=1.0)
        bid, ask = strategy.get_quotes(mid_price=100.0, inventory=0, time_remaining=1.0)
        
        assert abs(bid - 99.5) < 1e-10
        assert abs(ask - 100.5) < 1e-10
    
    def test_inventory_ignored(self) -> None:
        """Test that inventory doesn't affect quotes."""
        strategy = SymmetricStrategy(spread=1.0)
        
        bid_zero, ask_zero = strategy.get_quotes(mid_price=100.0, inventory=0, time_remaining=1.0)
        bid_pos, ask_pos = strategy.get_quotes(mid_price=100.0, inventory=10, time_remaining=1.0)
        bid_neg, ask_neg = strategy.get_quotes(mid_price=100.0, inventory=-10, time_remaining=1.0)
        
        assert bid_zero == bid_pos == bid_neg
        assert ask_zero == ask_pos == ask_neg
    
    def test_time_ignored(self) -> None:
        """Test that time remaining doesn't affect quotes."""
        strategy = SymmetricStrategy(spread=1.0)
        
        bid_early, ask_early = strategy.get_quotes(mid_price=100.0, inventory=0, time_remaining=1.0)
        bid_late, ask_late = strategy.get_quotes(mid_price=100.0, inventory=0, time_remaining=0.1)
        
        assert bid_early == bid_late
        assert ask_early == ask_late
    
    def test_spread_scaling(self) -> None:
        """Test that different spreads work correctly."""
        for spread in [0.5, 1.0, 1.5, 2.0]:
            strategy = SymmetricStrategy(spread=spread)
            bid, ask = strategy.get_quotes(mid_price=100.0, inventory=0, time_remaining=1.0)
            
            assert abs((ask - bid) - spread) < 1e-10
            assert abs((ask + bid) / 2 - 100.0) < 1e-10
