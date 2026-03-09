import streamlit as st
import requests
import pandas as pd

# 1. PAGE AND CONFIGURATION
st.set_page_config(page_title="Sports Arb Finder", layout="wide")
st.title("🌎 Multi-League Arbitrage Finder")

SPORT_MAP = {
    "EPL (UK)": "soccer_epl",
    "Serie A (Italy)": "soccer_italy_serie_a",
    "Champions League": "soccer_uefa_champs_league",
    "Bundesliga (Germany)": "soccer_germany_bundesliga",
    "La Liga (Spain)": "soccer_spain_la_liga"
}

# 2. SIDEBAR SETTINGS
st.sidebar.header("Settings")
API_KEY = st.sidebar.text_input("Enter API Key", type="password")
selected_sports = st.sidebar.multiselect("Leagues", list(SPORT_MAP.keys()), default=["Serie A (Italy)"])
STAKE = st.sidebar.number_input("Back Stake (£)", value=10.0)
COMMISSION = st.sidebar.slider("Exchange Commission (%)", 0.0, 5.0, 2.0) / 100
MIN_PROFIT = st.sidebar.slider("Min Profit Filter (£)", -10.0, 5.0, 0.01)

# Placeholder for the credit counter
credit_placeholder = st.sidebar.empty()

# 3. SCANNING LOGIC
if st.sidebar.button("Scan for Arbs"):
    if not API_KEY:
        st.error("Please enter your API Key.")
    else:
        all_results = []
        
        for sport_display in selected_sports:
            sport_key = SPORT_MAP[sport_display]
            # Use 'uk' region for Smarkets/Betfair to save credits
            url = f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds/'
            params = {
                'api_key': API_KEY, 
                'regions': 'uk', 
                'markets': 'h2h,h2h_lay', 
                'oddsFormat': 'decimal'
            }
            
            with st.spinner(f'Scanning {sport_display}...'):
                response = requests.get(url, params=params)
                
                # CREDIT TRACKER: Extract from headers
                remaining = response.headers.get('x-requests-remaining', 'N/A')
                credit_placeholder.metric("Credits Remaining", remaining)
                
                data = response.json()

            if isinstance(data, list):
                for event in data:
                    # TIME CONVERSION: Convert UTC to Local UK Time
                    commence_utc = pd.to_datetime(event.get('commence_time'))
                    local_time = commence_utc.tz_convert('Europe/London').strftime('%d %b, %H:%M')
                    
                    lays_by_outcome = {}
                    exchange_by_outcome = {}
                    
                    # STEP A: Identify TRUE Lay odds from Exchanges
                    for bookie in event.get('bookmakers', []):
                        name, key = bookie['title'].lower(), bookie['key'].lower()
                        if any(x in name or x in key for x in ['lay', 'smarkets', 'exchange', 'matchbook']):
                            for market in bookie.get('markets', []):
                                # The Gatekeeper: Only grab prices from the 'lay' market key
                                if 'lay' in market['key'].lower():
                                    for outcome in market['outcomes']:
                                        lays_by_outcome[outcome['name']] = outcome['price']
                                        exchange_by_outcome[outcome['name']] = bookie['title']
                    
                    if not lays_by_outcome: continue

                    # STEP B: Compare Bookie Back odds against the TRUE Lay odds
                    for bookie in event.get('bookmakers', []):
                        # Ensure we are only looking at standard bookmakers for 'Back' prices
                        is_ex = any(x in bookie['title'].lower() for x in ['smarkets', 'exchange', 'matchbook'])
                        if not is_ex:
                            for market in bookie.get('markets', []):
                                for outcome in market['outcomes']:
                                    selection = outcome['name']
                                    back_odds = outcome['price']
                                    
                                    if selection in lays_by_outcome:
                                        best_lay = lays_by_outcome[selection]
                                        
                                        # ARB CALCULATIONS
                                        lay_stake = (back_odds * STAKE) / (best_lay - COMMISSION)
                                        profit = (lay_stake * (1 - COMMISSION)) - STAKE
                                        liability = lay_stake * (best_lay - 1)
                                        
                                        if profit >= MIN_PROFIT:
                                            all_results.append({
                                                "Status": "💰 ARB" if profit > 0 else "❌ No Arb",
                                                "Kickoff": local_time,
                                                "Event": f"{event['home_team']} vs {event['away_team']}",
                                                "Bet On": selection,
                                                "Bookie": bookie['title'],
                                                "Back": back_odds,
                                                "Lay": best_lay,
                                                "Exchange": exchange_by_outcome[selection],
                                                "Liability": f"£{liability:.2f}",
                                                "Profit_Raw": profit, # Numeric for sorting
                                                "Profit/Loss": f"£{profit:.2f}"
                                            })

        # 4. DISPLAY RESULTS (Sorted Descending)
        if all_results:
            st.success(f"Scanning complete! Found {len(all_results)} total outcomes.")
            df = pd.DataFrame(all_results)
            # Sorting so highest profit is at the top
            df = df.sort_values(by="Profit_Raw", ascending=False)
            display_df = df.drop(columns=["Profit_Raw"])
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No matches found. Try lowering the profit filter.")