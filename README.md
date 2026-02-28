# Market Making Strategy Comparison

This repository implements Monte Carlo simulations to compare **inventory-based** and **symmetric** market making strategies under different risk aversion levels.

## Overview

Market makers face the challenge of balancing profit maximization with inventory risk management. This project tests the hypothesis that inventory-based quoting strategies, which dynamically adjust quotes based on current position, can reduce both profit variance and inventory variance compared to symmetric strategies that ignore inventory.

### Key Research Questions

1. Does inventory-based quoting reduce P&L variance compared to symmetric quoting?
2. How does the variance reduction effect scale with risk aversion (γ)?
3. What is the impact on terminal inventory risk?

## Experiments

The project includes three experiments testing different risk aversion levels:

- **Experiment 1**: Low risk aversion (γ = 0.01, spread = 1.33)
- **Experiment 2**: Medium risk aversion (γ = 0.1, spread = 1.29)
- **Experiment 3**: High risk aversion (γ = 0.5, spread = 1.15)

Each experiment runs 1,000 independent simulation paths for both strategies.

## Methodology

### Market Model

- **Mid-price dynamics**: Arithmetic Brownian Motion
  - dS = σdW
  - Discrete approximation: S_{t+dt} = S_t ± σ√dt
- **Parameters**:
  - Initial mid-price: s₀ = 100
  - Volatility: σ = 2
  - Time horizon: T = 1
  - Time step: dt = 0.005 (200 steps)

### Strategies

#### Inventory Strategy

Quotes centered around reservation price:
```
r_t = s - q·γ·σ²·(T-t)
bid = r_t - spread/2
ask = r_t + spread/2
```

Where:
- `q` is current inventory
- `γ` is risk aversion parameter
- `σ` is volatility
- `T-t` is time remaining

#### Symmetric Strategy

Quotes centered at mid-price:
```
bid = s - spread/2
ask = s + spread/2
```

### Execution Model

Order arrival intensities follow exponential decay:
```
λ(δ) = A·exp(-k·δ)
```

Where:
- `δ` is distance from mid-price
- `A = 140` (intensity amplitude)
- `k = 1.5` (decay parameter)

Execution probabilities per time step:
```
P(execution) = min(λ·dt, 1)
```

### Performance Metrics

- **Terminal Profit**: X_T + q_T·S_T
- **Terminal Inventory**: q_T
- **Standard Deviations**: Measures of risk
- **Variance Reduction**: Percentage decrease in variance

## Installation

### Requirements

- Python 3.8+
- NumPy
- Pandas
- Matplotlib
- SciPy
- pytest (for testing)

### Setup

```bash
git clone https://github.com/QuantCodeAutomata/qca-market-making-strategy-comparison-for-low-risk-ave.git
cd qca-market-making-strategy-comparison-for-low-risk-ave
pip install -r requirements.txt
```

## Usage

### Run All Experiments

```bash
python run_experiments.py
```

This will:
1. Execute all three experiments
2. Generate visualizations in `results/`
3. Save summary statistics to `results/summary_statistics.csv`

### Run Individual Experiment

```python
import sys
sys.path.insert(0, 'src')

from market_making.experiment import ExperimentConfig, ExperimentRunner

config = ExperimentConfig(
    gamma=0.1,
    spread=1.29,
    n_paths=1000,
    seed=42
)

runner = ExperimentRunner(config)
results = runner.run_experiment()
runner.print_summary(results)
```

### Run Custom Simulation

```python
import sys
sys.path.insert(0, 'src')

from market_making.simulation import MarketMakingSimulation
from market_making.strategies import InventoryStrategy

sim = MarketMakingSimulation(
    s0=100.0,
    T=1.0,
    dt=0.005,
    sigma=2.0,
    seed=42
)

strategy = InventoryStrategy(gamma=0.1, sigma=2.0, spread=1.0)
profit, inventory, inv_path, cash_path = sim.run_single_path(strategy)

print(f"Terminal Profit: {profit:.2f}")
print(f"Terminal Inventory: {inventory}")
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=src/market_making --cov-report=html
```

## Project Structure

```
.
├── src/
│   └── market_making/
│       ├── __init__.py
│       ├── simulation.py      # Core simulation engine
│       ├── strategies.py      # Quoting strategies
│       ├── experiment.py      # Experiment runner
│       └── visualization.py   # Plotting utilities
├── tests/
│   ├── test_simulation.py
│   ├── test_strategies.py
│   └── test_experiment.py
├── results/                   # Generated plots and statistics
├── run_experiments.py         # Main execution script
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Expected Results

### Experiment 1: γ = 0.01

| Strategy   | Profit Mean | Profit Std | Inventory Mean | Inventory Std |
|------------|-------------|------------|----------------|---------------|
| Inventory  | ~66.78      | ~8.76      | ~-0.02         | ~4.70         |
| Symmetric  | ~67.36      | ~13.40     | ~-0.31         | ~8.65         |

### Experiment 2: γ = 0.1

| Strategy   | Profit Mean | Profit Std | Inventory Mean | Inventory Std |
|------------|-------------|------------|----------------|---------------|
| Inventory  | ~62.94      | ~5.89      | ~0.10          | ~2.80         |
| Symmetric  | ~67.21      | ~13.43     | ~-0.018        | ~8.66         |

### Experiment 3: γ = 0.5

| Strategy   | Profit Mean | Profit Std | Inventory Mean | Inventory Std |
|------------|-------------|------------|----------------|---------------|
| Inventory  | ~33.92      | ~4.72      | ~-0.02         | ~1.88         |
| Symmetric  | ~66.20      | ~14.53     | ~0.25          | ~9.06         |

## Key Findings

1. **Variance Reduction**: Inventory-based strategies consistently show lower variance in both profit and terminal inventory
2. **Scaling with Risk Aversion**: The variance reduction effect strengthens as γ increases
3. **Trade-offs**: Higher risk aversion reduces mean profit but provides more stable outcomes

## Implementation Details

### Numerical Stability

- Execution probabilities are capped at 1.0 to ensure valid probability model
- RNG seeding ensures reproducibility across runs
- Sample standard deviation uses Bessel's correction (ddof=1)

### Performance Considerations

- Vectorized NumPy operations where possible
- Single-threaded execution for reproducibility
- ~10-20 seconds per experiment (1,000 paths × 200 steps)

## References

This implementation is based on the Avellaneda-Stoikov market making framework:

- Avellaneda, M., & Stoikov, S. (2008). "High-frequency trading in a limit order book." Quantitative Finance, 8(3), 217-224.

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

For questions or issues, please open an issue on GitHub.

---

**Note**: Results may vary slightly due to Monte Carlo randomness. Use consistent seeds for reproducible results.
