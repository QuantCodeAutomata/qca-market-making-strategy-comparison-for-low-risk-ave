"""Market Making Simulation Engine."""

import numpy as np
from typing import Tuple, Protocol


class QuotingStrategy(Protocol):
    """Protocol for quoting strategies."""
    
    def get_quotes(
        self, 
        mid_price: float, 
        inventory: int, 
        time_remaining: float
    ) -> Tuple[float, float]:
        """Return (bid_price, ask_price) for current state."""
        ...


class MarketMakingSimulation:
    """
    Monte Carlo simulation of market making with Arithmetic Brownian Motion.
    
    Parameters
    ----------
    s0 : float
        Initial mid-price
    T : float
        Time horizon
    dt : float
        Time step size
    sigma : float
        Volatility parameter
    A : float
        Intensity amplitude parameter
    k : float
        Intensity decay parameter
    q0 : int
        Initial inventory
    X0 : float
        Initial cash position
    seed : int, optional
        Random seed for reproducibility
    """
    
    def __init__(
        self,
        s0: float = 100.0,
        T: float = 1.0,
        dt: float = 0.005,
        sigma: float = 2.0,
        A: float = 140.0,
        k: float = 1.5,
        q0: int = 0,
        X0: float = 0.0,
        seed: int | None = None
    ):
        self.s0 = s0
        self.T = T
        self.dt = dt
        self.sigma = sigma
        self.A = A
        self.k = k
        self.q0 = q0
        self.X0 = X0
        self.n_steps = int(T / dt)
        
        self.rng = np.random.default_rng(seed)
        
    def _compute_intensity(self, delta: float) -> float:
        """Compute execution intensity λ(δ) = A * exp(-k * δ)."""
        return self.A * np.exp(-self.k * delta)
    
    def _simulate_price_path(self) -> np.ndarray:
        """
        Simulate mid-price as arithmetic Brownian motion.
        
        Returns
        -------
        prices : np.ndarray
            Array of mid-prices at each time step
        """
        prices = np.zeros(self.n_steps + 1)
        prices[0] = self.s0
        
        for i in range(self.n_steps):
            shock = self.rng.choice([-1, 1]) * self.sigma * np.sqrt(self.dt)
            prices[i + 1] = prices[i] + shock
            
        return prices
    
    def run_single_path(self, strategy: QuotingStrategy) -> Tuple[float, int, np.ndarray, np.ndarray]:
        """
        Run a single simulation path.
        
        Parameters
        ----------
        strategy : QuotingStrategy
            The quoting strategy to use
            
        Returns
        -------
        terminal_profit : float
            Final profit (cash + inventory * final_price)
        terminal_inventory : int
            Final inventory position
        inventory_path : np.ndarray
            Inventory at each time step
        cash_path : np.ndarray
            Cash position at each time step
        """
        prices = self._simulate_price_path()
        
        inventory = self.q0
        cash = self.X0
        
        inventory_path = np.zeros(self.n_steps + 1)
        cash_path = np.zeros(self.n_steps + 1)
        inventory_path[0] = inventory
        cash_path[0] = cash
        
        for i in range(self.n_steps):
            t = i * self.dt
            time_remaining = self.T - t
            mid_price = prices[i]
            
            bid_price, ask_price = strategy.get_quotes(mid_price, inventory, time_remaining)
            
            delta_bid = mid_price - bid_price
            delta_ask = ask_price - mid_price
            
            delta_bid = max(0, delta_bid)
            delta_ask = max(0, delta_ask)
            
            lambda_bid = self._compute_intensity(delta_bid)
            lambda_ask = self._compute_intensity(delta_ask)
            
            prob_bid = min(lambda_bid * self.dt, 1.0)
            prob_ask = min(lambda_ask * self.dt, 1.0)
            
            bid_executed = self.rng.random() < prob_bid
            ask_executed = self.rng.random() < prob_ask
            
            if bid_executed:
                inventory += 1
                cash -= bid_price
                
            if ask_executed:
                inventory -= 1
                cash += ask_price
                
            inventory_path[i + 1] = inventory
            cash_path[i + 1] = cash
        
        final_price = prices[-1]
        terminal_profit = cash + inventory * final_price
        
        return terminal_profit, inventory, inventory_path, cash_path
    
    def run_multiple_paths(
        self, 
        strategy: QuotingStrategy, 
        n_paths: int = 1000
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Run multiple simulation paths.
        
        Parameters
        ----------
        strategy : QuotingStrategy
            The quoting strategy to use
        n_paths : int
            Number of simulation paths
            
        Returns
        -------
        profits : np.ndarray
            Terminal profits for each path
        inventories : np.ndarray
            Terminal inventories for each path
        """
        profits = np.zeros(n_paths)
        inventories = np.zeros(n_paths)
        
        for i in range(n_paths):
            profit, inventory, _, _ = self.run_single_path(strategy)
            profits[i] = profit
            inventories[i] = inventory
            
        return profits, inventories
