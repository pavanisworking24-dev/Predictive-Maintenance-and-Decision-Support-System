# Risk Bands, Alert Logic and Decision Rules v0

**Status:** Proposed defaults for team sign-off. The numbers below are starting values that must be tuned on validation data, never on the official test set.  
**Related files:** `docs/database/database-schema-v0.sql` (`risk_threshold_configs`), `docs/api/openapi.yaml` (`/thresholds`, `/alerts`), scope sections 3.9, 3.11 and 5.4.

All outputs are research-oriented decision support based on simulated C-MAPSS data. They are not maintenance procedures.

## 1. Inputs

| Input | Meaning |
|---|---|
| ŷ | Predicted RUL in cycles for the latest cycle of a machine |
| P | Estimated probability that RUL ≤ N, where N is `horizon_cycles` (scope 3.9) |
| `at_cap` | The prediction is at the 125-cycle training cap and is shown as "≥ 125" |
| interval | Conformal interval `[lower_bound, upper_bound]` |

## 2. Risk bands

The thresholds live in the active row of `risk_threshold_configs`. The rule is evaluated in this order and stops at the first match:

1. **HIGH** if ŷ ≤ `high_rul_max` **or** P ≥ `high_probability_min`.
2. **MEDIUM** if ŷ ≤ `medium_rul_max` **or** P ≥ `medium_probability_min`.
3. **LOW** otherwise.

A capped prediction (ŷ = 125) can never match an RUL condition. It can only reach MEDIUM or HIGH through P, and P will normally be close to 0.

### Default configuration `cfg-1`

| Parameter | Value | Reason |
|---|---|---|
| `horizon_cycles` (N) | 30 | Matches the existing example and the HIGH limit |
| `high_rul_max` | 30 | A machine within 30 cycles of failure needs attention |
| `medium_rul_max` | 60 | Gives roughly twice the HIGH lead time |
| `high_probability_min` | 0.50 | More likely than not to be within N cycles |
| `medium_probability_min` | 0.20 | A noticeable chance of being within N cycles |
| `alert_rul_threshold` | 20 | Separate "imminent" alert inside the HIGH band |

### Worked examples (cfg-1)

| ŷ | P(RUL ≤ 30) | Result | Why |
|---|---|---|---|
| 18 | 0.98 | HIGH | ŷ ≤ 30 |
| 45 | 0.10 | MEDIUM | ŷ ≤ 60 |
| 70 | 0.25 | MEDIUM | P ≥ 0.20 although ŷ > 60 |
| 80 | 0.02 | LOW | no condition met |
| 125 (at cap) | 0.00 | LOW | capped value carries no remaining-life information |

### How the thresholds are evaluated and tuned

- Reference labels for evaluation come from the **true** RUL: HIGH if RUL ≤ 30, MEDIUM if 30 < RUL ≤ 60, LOW above 60.
- Report the confusion matrix, recall of HIGH, the false-alarm rate (HIGH predicted when true RUL > 60), and the lead time (cycles between the first HIGH and failure).
- Tune thresholds on validation or calibration engines only. Record each tuned set as a new configuration version; never edit an existing version.
- A new version is created through `POST /thresholds` (Admin). Stored risk scores keep the version that produced them.

## 3. Alert logic

An alert check runs every time a new prediction and risk score are stored for a machine (batch run or `POST /predictions`). The previous state is the latest earlier risk score and prediction of the same machine.

| Alert type | Fires when | Severity |
|---|---|---|
| `RISK_HIGH` | new risk level is HIGH **and** the previous level was not HIGH (or there was none) | HIGH |
| `RUL_BELOW_THRESHOLD` | ŷ ≤ `alert_rul_threshold` **and** the previous ŷ was above it (or there was none) | HIGH |

Rules:

1. **No duplicates:** do not create an alert of the same type for a machine while an alert of that type is OPEN or ACKNOWLEDGED.
2. **Lifecycle:** OPEN → ACKNOWLEDGED (Admin or Maintenance Manager; records `acknowledged_by` and `acknowledged_at`) → RESOLVED. There is no automatic resolution. A machine that drops back below HIGH and later returns to HIGH creates a new alert once the earlier one is RESOLVED.
3. **Traceability:** each alert stores the `prediction_id` that triggered it. The message contains the machine code, the cycle, ŷ, the interval and the thresholds version.
4. **First batch run:** the initial fleet load has no previous state, so every machine that is HIGH creates an alert. Provide a switch to skip alert creation for the initial load if that is too noisy.
5. **Out of scope:** notification channels (e-mail, SMS, push). Alerts are stored, listed and acknowledged only.

### Tests the alert logic needs

| Case | Expected |
|---|---|
| MEDIUM → HIGH | one `RISK_HIGH` alert |
| HIGH → HIGH | no new alert |
| HIGH with an OPEN `RISK_HIGH` alert, then LOW, then HIGH | no second alert until the first is RESOLVED |
| ŷ 25 → 18 with `alert_rul_threshold` 20 | one `RUL_BELOW_THRESHOLD` alert |
| ŷ 18 → 15 | no new `RUL_BELOW_THRESHOLD` alert |
| No previous state, HIGH | alert created |

## 4. Decision rule table (decision engine)

Input: risk level, uncertainty class, the component group of the top SHAP sensor. Output: priority, investigation guidance, rationale and evidence (scope 3.11).

- **Uncertainty class:** `wide` if `upper_bound - lower_bound` is larger than `max(10, 0.5 × ŷ)` cycles, otherwise `narrow`. These two numbers are starting values to review.
- **Component group:** taken from the sensor → component → degradation-mechanism table (scope 6.2), which still has to be written and sourced to the C-MAPSS publications. Use `unmapped` when the top sensor is not in the table.

| Rule id | Condition | Priority | Guidance (template) |
|---|---|---|---|
| R-CAP-01 | `at_cap` | P3 | RUL estimate is at the cap, so no remaining-life estimate is available. Continue routine monitoring. |
| R-HIGH-01 | HIGH, narrow | P1 | Review the trends of the top contributing sensors and investigate the {component_group} subsystem at the next opportunity. |
| R-HIGH-02 | HIGH, wide | P1 | As R-HIGH-01. The interval is wide, so confirm the estimate with additional cycles before acting. |
| R-MED-01 | MEDIUM, narrow | P2 | Schedule a review of the {component_group} sensor trends. |
| R-MED-02 | MEDIUM, wide | P2 | Monitor closely and re-run the prediction after the next cycles. |
| R-LOW-01 | LOW | P3 | Routine monitoring. |

Rules are evaluated top to bottom; the first match wins. Every output carries `rule_id`, which appears in the Health Summary as `recommendation.rule_id`. The wording describes what to investigate, never a repair instruction, and the disclaimer is always attached.

## 5. Open items

- Team review of the cfg-1 values and the uncertainty-class limits.
- Sensor → component → degradation-mechanism table (needed by the {component_group} placeholder).
- Storing the rule table as a versioned file (for example `config/decision_rules.v1.yaml`) once the decision engine is implemented, with a version recorded in each recommendation.