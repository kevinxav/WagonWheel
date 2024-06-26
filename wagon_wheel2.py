import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
import zipfile
import os
from io import BytesIO

def six_region(data, batsman_name, total_runs_all, plots, phase_option):
    regions_rhb = {
        'Region 1': {'boundary': [(296, 28), (533, 259)], 'text_position': (465, 96)},
        'Region 2': {'boundary': [(64, 262), (296, 28)], 'text_position': (136, 96)},
        'Region 3': {'boundary': [(533, 259), (299, 493)], 'text_position': (383, 478)},
        'Region 4': {'boundary': [(299, 493), (64, 262)], 'text_position': (202, 478)},
    }

    regions_lhb = {
        'Region 1': {'boundary': [(296, 28), (533, 259)], 'text_position': (465, 96)},
        'Region 2': {'boundary': [(64, 262), (296, 28)], 'text_position': (136, 96)},
        'Region 3': {'boundary': [(533, 259), (299, 493)], 'text_position': (202, 478)},
        'Region 4': {'boundary': [(299, 493), (64, 262)], 'text_position': (383, 478)},
    }

    total_runs = total_runs_all[batsman_name]

    if batting_type == 'RHB':
        regions = regions_rhb
    elif batting_type == 'LHB':
        regions = regions_lhb
    else:
        st.error("Invalid batting type! Please check the data.")
        return

    region_runs = {region: 0 for region in regions}
    for index, row in data[data['StrikerName'] == batsman_name].iterrows():
        wagon_wheel_position = row['WagonWheel']
        runs_scored = row['BatRuns']
        if batting_type == 'RHB':
            if wagon_wheel_position in [18, 10, 2, 24, 16, 8, 23, 15, 7, 17, 9, 1]:
                region_runs['Region 1'] += runs_scored
            elif wagon_wheel_position in [22, 14, 6, 19, 11, 3, 20, 12, 4, 21, 13, 5]:
                region_runs['Region 2'] += runs_scored
            elif wagon_wheel_position in [25, 26, 27, 28]:
                region_runs['Region 3'] += runs_scored
            elif wagon_wheel_position in [29, 30, 31, 32]:
                region_runs['Region 4'] += runs_scored
        elif batting_type == 'LHB':
            if wagon_wheel_position in [22, 14, 6, 19, 11, 3, 20, 12, 4, 21, 13, 5]:
                region_runs['Region 1'] += runs_scored
            elif wagon_wheel_position in [18, 10, 2, 24, 16, 8, 23, 15, 7, 17, 9, 1]:
                region_runs['Region 2'] += runs_scored
            elif wagon_wheel_position in [25, 26, 27, 28]:
                region_runs['Region 3'] += runs_scored
            elif wagon_wheel_position in [29, 30, 31, 32]:
                region_runs['Region 4'] += runs_scored
        else:
            st.error("Invalid batting type! Please check the data.")
            return

    region_percentages = {region: round((runs / total_runs) * 100) for region, runs in region_runs.items()}

    img = plt.imread('wagon.jpg')
    plt.imshow(img)

    for region, info in regions.items():
        text_position = info['text_position']
        plt.text(text_position[0], text_position[1], f"{region_percentages[region]}%", ha='center', va='center', fontsize=10, color='White', bbox=dict(facecolor='blue', edgecolor='black', boxstyle='round,pad=0.5'))

    plt.axis('off')

    # Save the plot as an image and append it to the list
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    plots.append(buf)

    # Display the image on the page
    st.image(buf, caption=f"Wagon Wheel for {batsman_name}", use_column_width=True)

    # Save the plot as a detailed image
    plt.figure()
    plt.imshow(img)
    for region, info in regions.items():
        text_position = info['text_position']
        plt.text(text_position[0], text_position[1], f"{region_percentages[region]}%", ha='center', va='center', fontsize=10, color='White', bbox=dict(facecolor='blue', edgecolor='black', boxstyle='round,pad=0.5'))
    plt.axis('off')
    plt.savefig(f"{batsman_name}_wagon_wheel.png")
    plt.close()

def main():
    st.title("Cricket Wagon Wheel Visualization")

    csv_path = "NewData.csv"
    data = pd.read_csv(csv_path)
    data = data.dropna(subset=['overs'])
    data['LengthX'] = data['LengthX'] + 17
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

        if "Spin" in pace_or_spin:
            bowling_type_options = ["All", "RAO", "SLAO", "RALB", "LAC"]
            selected_bowling_types = st.multiselect("Select Bowling Type Group:", bowling_type_options, default=["All"])
            if "All" not in selected_bowling_types:
                bowling_type_values = []
                if "RAO" in selected_bowling_types:
                    bowling_type_values.append(3)
                if "SLAO" in selected_bowling_types:
                    bowling_type_values.append(4)
                if "RALB" in selected_bowling_types:
                    bowling_type_values.append(5)
                if "LAC" in selected_bowling_types:
                    bowling_type_values.append(6)
                filtered_data = filtered_data[filtered_data['BowlingTypeGroup'].isin(bowling_type_values)]

        # Phase selection
        phase_type = st.selectbox("Select phase type (3Phase/4Phase):", ["3Phase", "4Phase"])
        if phase_type == "3Phase":
            phase_options = ["All", "1 to 6", "7 to 15", "16 to 20"]
            selected_phases = st.multiselect("Select Phase:", phase_options, default=["All"])
            filtered_data = filter_data_by_phase(filtered_data, 'Phase3idStarPhrase', selected_phases)
        elif phase_type == "4Phase":
            phase_options = ["All", "1 to 6", "7 to 10", "11-15", "16 to 20"]
            selected_phases = st.multiselect("Select Phase:", phase_options, default=["All"])
            filtered_data = filter_data_by_phase(filtered_data, 'Phase4idPhrase', selected_phases)

        run_types = st.multiselect("Select run types:", ['0s', '1s', '2s', '3s', '4s', '6s', 'wickets', 'All'], default=['All'])

        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            if 'All' in selected_batsman_name:
                batsmen_to_plot = filtered_data['StrikerName'].unique()
            else:
                batsmen_to_plot = selected_batsman_name

            for batsman in batsmen_to_plot:
                filtered_data_batsman = filtered_data[filtered_data['StrikerName'] == batsman]

                if not filtered_data_batsman.empty:
                    six_region(filtered_data_batsman, batsman, run_types, zip_file, output_dir)

        st.download_button(
            label="Download ZIP",
            data=zip_buffer.getvalue(),
            file_name="batsman_wagon_wheel.zip",
            mime="application/zip"
        )

if __name__ == "__main__":
    main()
