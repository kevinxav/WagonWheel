import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
import zipfile
import os
from io import BytesIO

# Define regions for right-hand batsmen
regions_4_rhb = {
    'Region 1': {'boundary': [(64, 262), (296, 28)], 'text_position': (136, 96)},
    'Region 2': {'boundary': [(296, 28), (533, 259)], 'text_position': (465, 96)},
    'Region 3': {'boundary': [(533, 259), (299, 493)], 'text_position': (456, 432)},
    'Region 4': {'boundary': [(299, 493), (64, 262)], 'text_position': (133, 432)},
}

regions_6_rhb = {
    'Region 1': {'boundary': [(64, 261), (294, 25)], 'text_position': (136, 95)},
    'Region 2': {'boundary': [(294, 25), (536, 263)], 'text_position': (465, 95)},
    'Region 3': {'boundary': [(536, 263), (461,263)], 'text_position': (516, 343)},
    'Region 4': {'boundary': [(461, 263), (298, 492)], 'text_position': (383, 477)},
    'Region 5': {'boundary': [(298, 492), (130, 425)], 'text_position': (202, 477)},
    'Region 6': {'boundary': [(130, 425), (64, 261)], 'text_position': (77, 343)},
}

regions_8_rhb = {
    'Region 1': {'boundary': [(64, 260), (131, 96)], 'text_position': (84, 169)},
    'Region 2': {'boundary': [(131, 96), (298, 25)], 'text_position': (211, 44)},
    'Region 3': {'boundary': [(298, 25), (466, 97)], 'text_position': (385, 44)},
    'Region 4': {'boundary': [(466, 97), (533, 260)], 'text_position': (513, 169)},
    'Region 5': {'boundary': [(533, 260), (465, 425)], 'text_position': (512, 358)},
    'Region 6': {'boundary': [(465, 260), (299, 498)], 'text_position': (392, 473)},
    'Region 7': {'boundary': [(299, 498), (136, 426)], 'text_position': (215, 473)},
    'Region 8': {'boundary': [(136, 426), (64, 260)], 'text_position': (84, 358)},
}

# Define regions for left-hand batsmen
regions_4_lhb = {
    'Region 1': {'boundary': [(296, 28), (533, 259)], 'text_position': (465, 96)},
    'Region 2': {'boundary': [(64, 262), (296, 28)], 'text_position': (136, 96)},
    'Region 3': {'boundary': [(533, 259), (299, 493)], 'text_position': (133, 432)},
    'Region 4': {'boundary': [(299, 493), (64, 262)], 'text_position': (456, 432)},
}

regions_6_lhb = {
    'Region 1': {'boundary': [(294, 25), (536, 263)], 'text_position': (465, 95)},
    'Region 2': {'boundary': [(64, 261), (294, 25)], 'text_position': (136, 95)},
    'Region 3': {'boundary': [(536, 263), (461,263)], 'text_position': (77, 343)},
    'Region 4': {'boundary': [(298, 492), (130, 425)], 'text_position': (202, 477)},
    'Region 5': {'boundary': [(461, 263), (298, 492)], 'text_position': (383, 477)},
    'Region 6': {'boundary': [(536, 263), (461,263)], 'text_position': (516, 343)},
}

regions_8_lhb = {
    'Region 1': {'boundary': [(533, 260), (466, 97)], 'text_position': (513, 169)},
    'Region 2': {'boundary': [(466, 97), (298, 25)], 'text_position': (385, 44)},
    'Region 3': {'boundary': [(298, 25), (131, 96)], 'text_position': (211, 44)},
    'Region 4': {'boundary': [(131, 96), (64, 260)], 'text_position': (84, 169)},
    'Region 5': {'boundary': [(64, 260), (136, 426)], 'text_position': (84, 358)},
    'Region 6': {'boundary': [(136, 426), (299, 498)], 'text_position': (215, 473)},
    'Region 7': {'boundary': [(299, 498), (465, 260)], 'text_position': (392, 473)},
    'Region 8': {'boundary': [(465, 260), (533, 260)], 'text_position': (512, 358)},
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

        total_runs_all = filtered_data.groupby(['StrikerName']).sum()['batruns']
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
