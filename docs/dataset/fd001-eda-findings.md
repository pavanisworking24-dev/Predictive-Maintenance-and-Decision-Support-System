# Detailed NASA C-MAPSS FD001 Exploratory Data Analysis Findings Summary

## 1. Objective
This document presents the exploratory data analysis (EDA) results for the NASA C-MAPSS FD001 dataset. The goal is to investigate dataset characteristics, establish operational behaviors, analyze Remaining Useful Life (RUL) targets, verify data quality, and document concrete insights to assist future predictive maintenance modeling steps without applying machine learning yet.

## 2. Dataset Structure and Dimensions
- **Training Dataset**: Contains 20631 rows and 26 base columns (excluding calculated RUL targets). It records full operational runs up to the exact point of system failure.
- **Test Dataset**: Contains 13096 rows and 26 columns. Test runs are truncated before failure occurs, which forms the core of the evaluation task.
- **RUL Dataset**: Contains 100 rows, representing a single true target RUL value for each test engine at its last recorded cycle.
- **Feature Space**: Standard layout including engine unit number, cycle count, three operational settings, and 21 distinct sensor measurements.

## 3. Engine and Cycle Observations
- **Unique Engines**: Both training and test subsets contains exactly 100 engines.
- **Operational Durations**: Training engine run lengths vary significantly. The minimum lifetime is 128 cycles, while the longest-lived engine survives for 362 cycles. On average, a training engine runs for 206.31 cycles before failure. This highlights substantial variation in degradation rates under identical single-regime operational conditions.

## 4. Sensor and Operating-Setting Observations
- **Constant Features (No Predictive Value)**: ['op_setting_3', 'sensor_18', 'sensor_19']. These features have a standard deviation of exactly zero and do not change across any recorded cycles. They should be dropped from feature sets during modeling.
- **Near-Constant Features (Very Low Variance)**: ['op_setting_1', 'op_setting_2', 'sensor_1', 'sensor_5', 'sensor_6', 'sensor_10', 'sensor_16']. These display negligible fluctuation and provide minimal helpful signal for RUL estimation.
- **Highly Active Features**: ['sensor_2', 'sensor_3', 'sensor_4', 'sensor_7', 'sensor_8', 'sensor_9', 'sensor_11', 'sensor_12', 'sensor_13', 'sensor_14', 'sensor_15', 'sensor_17', 'sensor_20', 'sensor_21']. These dynamic sensors show notable variation and respond directly to the mechanical degradation of the engine.

## 5. Sensor Trend Visualization Findings
- **Monotonic Trends**: Dynamic sensors show strong trend characteristics. Sensors like `sensor_2`, `sensor_3`, `sensor_4`, `sensor_11`, and `sensor_15` progressively increase over cycles, while sensors like `sensor_7`, `sensor_12`, and `sensor_21` decrease over cycles.
- **Shared Degradation Signatures**: Engines with varying operational lifespans converge to consistent critical values just before failure. This indicates that despite different lifespans, the boundary degradation values are relatively uniform across engines.
- **Stable Environment**: Plotting operational settings reveals that the FD001 dataset behaves under a stable, single operational regime with minor noise variations.

## 6. Training and Test RUL Distribution Findings
- **Uncapped Training RUL**: RUL drops linearly to zero at failure. The uncapped distribution is highly uniform during mid-life but presents high variance in initial states due to variable lifespans.
- **Capped Training RUL**: Capping RUL at a standard limit of 125 cycles is recommended because engine degradation remains near-zero during early cycles. Capping prevents models from attempting to predict high RUL when an engine is still completely healthy, creating a prominent spike in the target distribution at 125.
- **Test RUL**: The ground truth test RUL represents the remaining lifetime at the final observed test cycle. It spans from a minimum of 7 cycles (high urgency) to a maximum of 145 cycles (low urgency), with an average of 75.52 cycles.

## 7. Data-Quality Observations
- **Missing Values**: None (0 missing records).
- **Duplicate Rows**: None.
- **Key Consistency**: The key combination of `['unit_number', 'time_in_cycles']` has zero duplicate entries, verifying its suitability as a unique composite index.
- **Anomalies**: Only the constant features identified in Section 4 are present; otherwise, the dataset is exceptionally clean.

## 8. Brief Observations Relevant to Future Feature Engineering
- **Feature Removal**: Drop all constant columns (`sensor_18`, `sensor_19`, `op_setting_3`) and consider removing near-constant sensors to simplify input space.
- **Temporal Smoothing**: Implement rolling window calculations (such as rolling mean and rolling standard deviation) to smooth out high-frequency sensor noise and isolate the underlying degradation trend.
- **Trend Ratios**: Calculate ratios between opposing trends (e.g., dividing an increasing sensor by a decreasing sensor) to build highly responsive, monotonic indicators of wear.
- **Time-Since-Start**: Maintain current cycle count directly, as it acts as a primary index of cumulative operational stress.

## 9. Conclusion
The NASA C-MAPSS FD001 dataset provides clear, structured trends that are highly suitable for predictive maintenance RUL modeling. The high-quality signal and monotonic trends in active sensors allow for robust wear modeling once constant attributes are removed.
