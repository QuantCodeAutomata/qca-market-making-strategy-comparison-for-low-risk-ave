"""Market Making Quoting Strategies."""

from typing import Tuple


class InventoryStrategy:
    """
    Inventory-based quoting strategy using reservation price.
    
    Quotes are centered around reservation price:
    r_t = s - q * γ * σ² * (T - t)
    
    Parameters
    ----------
    gamma : float
        Risk aversion parameter
    sigma : float
        Volatility parameter
    spread : float
        Bid-ask spread
    """
    
    def __init__(self, gamma: float, sigma: float, spread: float):
        self.gamma = gamma
        self.sigma = sigma
        self.spread = spread
        
    def get_quotes(
        self, 
        mid_price: float, 
        inventory: int, 
        time_remaining: float
    ) -> Tuple[float, float]:
        """
        Compute bid and ask prices based on reservation price.
        
        Parameters
        ----------
        mid_price : float
            Current mid-price
        inventory : int
            Current inventory position
        time_remaining : float
            Time remaining until horizon
            
        Returns
        -------
        bid_price : float
            Bid quote
        ask_price : float
            Ask quote
        """
        reservation_price = mid_price - inventory * self.gamma * self.sigma**2 * time_remaining
        
        half_spread = self.spread / 2
        bid_price = reservation_price - half_spread
        ask_price = reservation_price + half_spread
        
        return bid_price, ask_price


class SymmetricStrategy:
    """
    Symmetric quoting strategy centered at mid-price.
    
    Quotes are symmetric around mid-price:
    bid = s - spread/2
    ask = s + spread/2
    
    Parameters
    ----------
    spread : float
        Bid-ask spread
    """
    
    def __init__(self, spread: float):
        self.spread = spread
        
    def get_quotes(
        self, 
        mid_price: float, 
        inventory: int, 
        time_remaining: float
    ) -> Tuple[float, float]:
        """
        Compute symmetric bid and ask prices.
        
        Parameters
        ----------
        mid_price : float
            Current mid-price
        inventory : int
            Current inventory position (unused)
        time_remaining : float
            Time remaining until horizon (unused)
            
        Returns
        -------
        bid_price : float
            Bid quote
        ask_price : float
            Ask quote
        """
        half_spread = self.spread / 2
        bid_price = mid_price - half_spread
        ask_price = mid_price + half_spread
        
        return bid_price, ask_price
