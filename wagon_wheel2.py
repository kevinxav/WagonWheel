import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
import zipfile
import os
from io import BytesIO

# Define regions for right-hand batsmen
regions_4_rhb = {
    'Region 1': {'boundary': [(296, 28), (533, 259)], 'text_position': (465, 96)},
    'Region 2': {'boundary': [(64, 262), (296, 28)], 'text_position': (136, 96)},
    'Region 3': {'boundary': [(533, 259), (299, 493)], 'text_position': (383, 478)},
    'Region 4': {'boundary': [(299, 493), (64, 262)], 'text_position': (202, 478)},
}

regions_6_rhb = {
    'Region 1': {'boundary': [(296, 28), (422, 134)], 'text_position': (365, 81)},
    'Region 2': {'boundary': [(422, 134), (533, 259)], 'text_position': (485, 196)},
    'Region 3': {'boundary': [(533, 259), (366, 375)], 'text_position': (465, 333)},
    'Region 4': {'boundary': [(366, 375), (299, 493)], 'text_position': (333, 434)},
    'Region 5': {'boundary': [(299, 493), (198, 385)], 'text_position': (239, 431)},
    'Region 6': {'boundary': [(198, 385), (64, 262)], 'text_position': (113, 334)},
}

regions_8_rhb = {
    'Region 1': {'boundary': [(296, 28), (399, 111)], 'text_position': (365, 81)},
    'Region 2': {'boundary': [(399, 111), (486, 189)], 'text_position': (455, 143)},
    'Region 3': {'boundary': [(486, 189), (533, 259)], 'text_position': (505, 230)},
    'Region 4': {'boundary': [(533, 259), (436, 347)], 'text_position': (465, 333)},
    'Region 5': {'boundary': [(436, 347), (366, 375)], 'text_position': (401, 361)},
    'Region 6': {'boundary': [(366, 375), (299, 493)], 'text_position': (333, 434)},
    'Region 7': {'boundary': [(299, 493), (211, 404)], 'text_position': (239, 431)},
    'Region 8': {'boundary': [(211, 404), (64, 262)], 'text_position': (153, 321)},
}

# Define regions for left-hand batsmen
regions_4_lhb = {
    'Region 1': {'boundary': [(533, 28), (296, 259)], 'text_position': (136, 96)},
    'Region 2': {'boundary': [(64, 28), (533, 28)], 'text_position': (465, 96)},
    'Region 3': {'boundary': [(533, 259), (299, 493)], 'text_position': (202, 478)},
    'Region 4': {'boundary': [(299, 493), (64, 259)], 'text_position': (383, 478)},
}

regions_6_lhb = {
    'Region 1': {'boundary': [(533, 28), (399, 134)], 'text_position': (465, 81)},
    'Region 2': {'boundary': [(399, 134), (296, 259)], 'text_position': (365, 196)},
    'Region 3': {'boundary': [(296, 259), (436, 375)], 'text_position': (485, 333)},
    'Region 4': {'boundary': [(436, 375), (299, 493)], 'text_position': (465, 434)},
    'Region 5': {'boundary': [(299, 493), (198, 385)], 'text_position': (333, 431)},
    'Region 6': {'boundary': [(198, 385), (64, 259)], 'text_position': (239, 334)},
}

regions_8_lhb = {
    'Region 1': {'boundary': [(533, 28), (399, 111)], 'text_position': (465, 81)},
    'Region 2': {'boundary': [(399, 111), (296, 189)], 'text_position': (455, 143)},
    'Region 3': {'boundary': [(296, 189), (133, 259)], 'text_position': (505, 230)},
    'Region 4': {'boundary': [(133, 259), (236, 347)], 'text_position': (465, 333)},
    'Region 5': {'boundary': [(236, 347), (366, 375)], 'text_position': (401, 361)},
    'Region 6': {'boundary': [(366, 375), (299, 493)], 'text_position': (333, 434)},
    'Region 7': {'boundary': [(299, 493), (211, 404)], 'text_position': (239, 431)},
    'Region 8': {'boundary': [(211, 404), (64, 259)], 'text_position': (153, 321)},
}

def get_regions(region_type, batting_hand):
    if batting_hand == "RHB":
        if region_type == "4 Region":
            return regions_4_rhb
        elif region_type == "6 Region":
            return regions_6_rhb
        elif region_type == "8 Region":
            return regions_8_rhb
    elif batting_hand == "LHB":
        if region_type == "4 Region":
            return regions_4_lhb
        elif region_type == "6 Region":
            return regions_6_lhb
        elif region_type == "8 Region":
            return regions_8_lhb

def main():
    st.title("Cricket Wagon Wheel Visualization")

    csv_path ="NewData.csv"
    data = pd.read_csv(csv_path)
    data = data.dropna(subset=['overs'])
    data['Date'] = pd.to_datetime(data['date'])

    # Date range filter
    start_date, end_date = st.date_input("Select date range:", [data['Date'].min(), data['Date'].max()])
    filtered_data = data[(data['Date'] >= pd.to_datetime(start_date)) & (data['Date'] <= pd.to_datetime(end_date))]

    # Filter competitions based on date range
    competitions = list(filtered_data['CompName'].unique())
    selected_competition = st.multiselect("Select competition:", competitions)

    if selected_competition:
        filtered_data = filtered_data[filtered_data['CompName'].isin(selected_competition)]

    # Filter batsman club names based on competition
    bat_club_names = list(filtered_data['battingclubid'].unique())
    selected_bat_club_name = st.multiselect("Select the batsman's club id:", bat_club_names)

    if selected_bat_club_name:
        filtered_data = filtered_data[filtered_data['battingclubid'].isin(selected_bat_club_name)]

    match_ids = ['All'] + list(filtered_data['matchid'].unique())
    selected_match_id = st.multiselect("Select Match:", match_ids, default=['All'])

    if 'All' not in selected_match_id:
        filtered_data = filtered_data[filtered_data['matchid'].isin(selected_match_id)]

    # Filter batsman names based on match id
    batsman_names = ['All'] + list(filtered_data['StrikerName'].unique())
    selected_batsman_name = st.multiselect("Select the batsman's name:", batsman_names, default=['All'])

    if selected_batsman_name:
        # Pace or Spin filter
        pace_or_spin = st.multiselect("Select bowler type (Pace/Spin):", ["All", "Pace", "Spin"], default=["All"])

        if "All" not in pace_or_spin:
            pace_or_spin_values = []
            if "Pace" in pace_or_spin:
                pace_or_spin_values.append(1)
            if "Spin" in pace_or_spin:
                pace_or_spin_values.append(2)
            filtered_data = filtered_data[filtered_data['PaceorSpin'].isin(pace_or_spin_values)]

        # Bowling Type Group filter
        if "Pace" in pace_or_spin:
            bowling_type_options = ["All", "RAP", "LAP"]
            selected_bowling_types = st.multiselect("Select Bowling Type Group:", bowling_type_options, default=["All"])
            if "All" not in selected_bowling_types:
                bowling_type_values = []
                if "RAP" in selected_bowling_types:
                    bowling_type_values.append(1)
                if "LAP" in selected_bowling_types:
                    bowling_type_values.append(2)
                filtered_data = filtered_data[filtered_data['BowlingTypeGroup'].isin(bowling_type_values)]

        # Batsman's Hand filter
        batting_hand_options = ["RHB", "LHB"]
        batting_hand = st.selectbox("Select the batsman's hand:", batting_hand_options)

        # Region Type filter
        region_types = ["4 Region", "6 Region", "8 Region"]
        selected_region_type = st.selectbox("Select the region type:", region_types)

        total_runs_all = filtered_data.groupby(['StrikerName']).sum()['batsmantotalruns']
        batsman_groups = filtered_data.groupby(['StrikerName', 'batsmanballposition', 'wagonregion'])

        if "All" not in selected_batsman_name:
            filtered_data = filtered_data[filtered_data['StrikerName'].isin(selected_batsman_name)]

        for batsman_name in selected_batsman_name:
            total_runs = total_runs_all.get(batsman_name, 0)
            batsman_data = batsman_groups.get_group((batsman_name, 'R', '3'))

            # Plotting code using the selected region type and batting hand
            regions = get_regions(selected_region_type, batting_hand)
            for region_name, region_info in regions.items():
                # Perform plotting based on regions
                plt.plot(region_info['boundary'], label=region_name)

            plt.title(f"Wagon Wheel for {batsman_name}")
            plt.legend()
            plt.show()

if __name__ == "__main__":
    main()
