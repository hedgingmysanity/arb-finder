# Real-Time Cross-Venue Arbitrage Engine

A quantitative tool designed to identify and calculate risk-free arbitrage opportunities across 20+ UK sportsbooks and exchanges using REST API integration.
Streamlit link: https://arb-finder.streamlit.app/    (API key not provided)

## 🚀 The Mission
The goal of this project was to build a robust execution dashboard that synchronizes fragmented liquidity pools to find price discrepancies in "Head-to-Head" markets.

## 🛠️ Technical Stack
* **Language:** Python 3.14.3
* **Framework:** Streamlit (Web UI)
* **Data Source:** The-Odds-API (RESTful)
* **Libraries:** Pandas (Data Wrangling), Requests (API Handling)

## 🔍 Key Technical Milestone: Deep Inspection Audit
The most significant challenge in development was identifying "Phantom Arbitrage." During initial testing, the model reported high-margin opportunities that appeared statistically improbable for efficient markets.

**The Diagnosis:** By performing a raw JSON audit, I discovered a market microstructure mismatch. The system was inadvertently comparing **Bookmaker Back Odds** (Bid) against **Exchange Back Odds** (Bid) instead of **Exchange Lay Odds** (Ask).

**The Solution:**
I engineered a logic gate to strictly filter for the `h2h_lay` market key within the JSON hierarchy. This ensured the engine only calculated profit based on true sell-side liquidity, accounting for the bid-ask spread and exchange commissions.



## 📈 Features
* **Dynamic Hedging:** Calculates exact Lay Stakes and total Liability required for a perfect hedge.
* **Temporal Sync:** Automatically converts UTC API timestamps to local UK time (GMT/BST).
* **Credit Optimization:** Refined regional request parameters to reduce API overhead by 50% without data loss.
* **Risk Management:** Includes a "Minimum Profit" threshold to filter out low-liquidity or high-noise trades.

## ⚠️ Risk Disclaimer
This tool is for educational and quantitative analysis purposes. In live markets, users must account for **execution latency** and **slippage**.
