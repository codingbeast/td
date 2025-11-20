# GoldBEES Strategy – Buy & Sell Logic (Release Notes)

## 🚀 What’s New

### ✅ Revised Buy Logic (0.30% Dip with Tick Precision)
The strategy buys only when GoldBEES price dips by **0.30%** from the previous close, with Zerodha-compatible tick size correction (₹0.05 multiples).

### Example:
| Last Price | Raw 0.30% Dip | Raw Buy Price | Final Adjusted Buy Price |
|-----------|----------------|----------------|---------------------------|
| 101.66    | 0.30498        | 101.355        | **101.35**                |
| 101.66    | 0.312          | 101.348        | **101.35**                |
| 101.66    | 0.36           | 101.30         | **101.30**                |

---

## 🟢 Buy Logic Summary (manually set this in config)
- Calculate 0.30% reduction from previous close  
- Convert to a valid Zerodha price (nearest ₹0.05 lower)  
- Place BUY only if time/day rules allow  

---

## 🔴 Sell Logic – 2% Profit Target
- After buying, target profit = **2%** on buy price  
- Price is again adjusted to nearest valid ₹0.05 tick  
- SELL triggers automatically when conditions match  

---

## ⏱ Time Filters
- Strategy only runs inside configured time window  
- Example fields: `run_before_time`, `run_after_time`, `is_time_between`

---

## ⚠️ Disclaimer
Trading involves risk.  
This strategy does **NOT** guarantee profits.  
Always test before using on real money.

---

## 📌 Summary Table

| Step | Condition | Action |
|------|-----------|--------|
| BUY | Price dips 0.30% (adjusted) | Buy |
| SELL | Price hits 2% profit | Sell |
| TIME FILTER | Must be in allowed time window | Execute |

---

Generated automatically for GitHub Release Notes.
