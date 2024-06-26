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

    csv_path = "NewData.csv"
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
                filtered_data = filtered_data[filtered_data['BowlingTypeGroup'].isin(selected_bowling_types)]
        
        # Filtered batsmen
        if 'All' not in selected_batsman_name:
            filtered_data = filtered_data[filtered_data['StrikerName'].isin(selected_batsman_name)]
    
        st.dataframe(filtered_data[['StrikerName', 'matchid', 'battingclubid', 'PaceorSpin', 'BowlingTypeGroup']])

        # Region Type
        region_type = st.selectbox("Select Region Type:", ["4 Region", "6 Region", "8 Region"])

        # Batting Hand
        batting_hand = st.selectbox("Select Batting Hand:", ["RHB", "LHB"])

        # Region Configuration
        regions = get_regions(region_type, batting_hand)
        
        # Plot Configuration
        runs_columns = st.columns(len(regions))
        regions_data = {}
        for i, (region_name, region_info) in enumerate(regions.items()):
            with runs_columns[i]:
                regions_data[region_name] = st.number_input(f"Runs in {region_name}", min_value=0, max_value=1000, value=0)

        if st.button("Plot"):
            fig, ax = plt.subplots()

            # Plot setup
            ax.set_xlim([0, 600])
            ax.set_ylim([0, 600])
            ax.imshow(Image.open("Pitch_Map1.png"))

            for region_name, region_info in regions.items():
                runs = regions_data[region_name]
                if runs > 0:
                    polygon = plt.Polygon(region_info['boundary'], closed=True, fill=None, edgecolor='r')
                    ax.add_patch(polygon)
                    plt.text(region_info['text_position'][0], region_info['text_position'][1], str(runs), fontsize=12, ha='center')

            st.pyplot(fig)

            # Create download link for the plot
            img_buffer = BytesIO()
            fig.savefig(img_buffer, format='png')
            img_buffer.seek(0)
            img_data = img_buffer.getvalue()
            download_link = get_binary_file_downloader_html(img_data, "wagon_wheel_plot.png", "Download Wagon Wheel Plot")
            st.markdown(download_link, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

