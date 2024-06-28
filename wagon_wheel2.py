import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import zipfile


def filter_data_by_bowling_type(data, bowling_type, pace_subtype=None, spin_subtype=None):
    if bowling_type == "Pace":
        if pace_subtype == "RAP":
            return data[data['BowlingTypeGroup'] == 1]
        elif pace_subtype == "LAP":
            return data[data['BowlingTypeGroup'] == 2]
        else:
            return data
    elif bowling_type == "Spin":
        if spin_subtype == "RAO":
            return data[data['BowlingTypeGroup'] == 3]
        elif spin_subtype == "SLAO":
            return data[data['BowlingTypeGroup'] == 4]
        elif spin_subtype == "RALB":
            return data[data['BowlingTypeGroup'] == 5]
        elif spin_subtype == "LAC":
            return data[data['BowlingTypeGroup'] == 6]
        else:
            return data
    elif bowling_type == "Both":
        return data
    else:
        return data

def filter_data_by_phase(data, phase_type, selected_phase):
    if phase_type == "3Phase":
        if selected_phase != "All":
            data = data[data['Phase3idStarPhrase'] == selected_phase]
    elif phase_type == "4Phase":
        if selected_phase != "All":
            data = data[data['Phase4idPhrase'] == selected_phase]
    return data


def six_region(data, batsman_name, total_runs_all, plots, phase_option):
    batting_type_data = data[data['StrikerName'] == batsman_name]['StrikerBattingType']
    if batting_type_data.empty:
        st.error(f"No data available for {batsman_name} with the selected filter.")
        return

    batting_type = batting_type_data.iloc[0]

    regions_rhb = {
        'Region 1': {'boundary': [(64, 261), (294, 25)], 'text_position': (136, 95)},
        'Region 2': {'boundary': [(294, 25), (536, 263)], 'text_position': (465, 95)},
        'Region 3': {'boundary': [(536, 263), (461,263)], 'text_position': (516, 343)},
        'Region 4': {'boundary': [(461, 263), (298, 492)], 'text_position': (383, 477)},
        'Region 5': {'boundary': [(298, 492), (130, 425)], 'text_position': (202, 477)},
        'Region 6': {'boundary': [(130, 425), (64, 261)], 'text_position': (77, 343)},
    }                                                                   

    regions_lhb = {
        'Region 1': {'boundary': [(294, 25), (536, 263)], 'text_position': (465, 95)},
        'Region 2': {'boundary': [(64, 261), (294, 25)], 'text_position': (136, 95)},
        'Region 3': {'boundary': [(536, 263), (461,263)], 'text_position': (77, 343)},
        'Region 4': {'boundary': [(298, 492), (130, 425)], 'text_position': (202, 477)},
        'Region 5': {'boundary': [(461, 263), (298, 492)], 'text_position': (383, 477)},
        'Region 6': {'boundary': [(536, 263), (461,263)], 'text_position': (516, 343)},
    }

    total_runs = total_runs_all.get(batsman_name, 0)
    if total_runs == 0:
        st.error(f"No total runs available for {batsman_name}.")
        return

    if batting_type == 1:
        regions = regions_rhb
    elif batting_type == 2:
        regions = regions_lhb
    else:
        st.error("Invalid batting type! Please check the data.")
        return

    region_runs = {region: 0 for region in regions}
    for index, row in data[data['StrikerName'] == batsman_name].iterrows():
        wagon_wheel_position = row['WWregion63']
        runs_scored = row['batruns']
        if batting_type == 1:
            if wagon_wheel_position in [23, 15, 7, 24, 16, 8]:
                region_runs['Region 1'] += runs_scored
            elif wagon_wheel_position in [17, 9, 1, 18, 10, 2]:
                region_runs['Region 2'] += runs_scored
            elif wagon_wheel_position in [19, 11, 3]:
                region_runs['Region 3'] += runs_scored
            elif wagon_wheel_position in [20, 12, 4]:
                region_runs['Region 4'] += runs_scored
            elif wagon_wheel_position in [21, 13, 5]:
                region_runs['Region 5'] += runs_scored
            elif wagon_wheel_position in [22, 14, 6]:
                region_runs['Region 6'] += runs_scored
        elif batting_type == 2:
            if wagon_wheel_position in [18, 10, 2, 17, 9, 1]:
                region_runs['Region 1'] += runs_scored
            elif wagon_wheel_position in [24, 16, 8, 23, 15, 7]:
                region_runs['Region 2'] += runs_scored
            elif wagon_wheel_position in [22, 14, 6]:
                region_runs['Region 3'] += runs_scored
            elif wagon_wheel_position in [21, 13, 5]:
                region_runs['Region 4'] += runs_scored
            elif wagon_wheel_position in [20, 12, 4]:
                region_runs['Region 5'] += runs_scored
            elif wagon_wheel_position in [19, 11, 3]:
                region_runs['Region 6'] += runs_scored
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
    st.image(buf, caption=f"Wagon Wheel for {batsman_name} in {phase_option}", use_column_width=True)

    # Save the plot as a detailed image
    plt.figure()
    plt.imshow(img)
    for region, info in regions.items():
        text_position = info['text_position']
        plt.text(text_position[0], text_position[1], f"{region_percentages[region]}%", ha='center', va='center', fontsize=10, color='White', bbox=dict(facecolor='blue', edgecolor='black', boxstyle='round,pad=0.5'))
    plt.axis('off')
    plt.savefig(f"{batsman_name}_wagon_wheel.png")
    plt.close()

def four_region(data, batsman_name, total_runs_all, plots):
    batting_type_data = data[data['StrikerName'] == batsman_name]['StrikerBattingType']
    if batting_type_data.empty:
        st.error(f"No data available for {batsman_name} with the selected filter.")
        return

    batting_type = batting_type_data.iloc[0]

    regions_rhb = {
        'Region 1': {'boundary': [(64, 262), (296, 28)], 'text_position': (136, 96)},
        'Region 2': {'boundary': [(296, 28), (533, 259)], 'text_position': (465, 96)},
        'Region 3': {'boundary': [(533, 259), (299, 493)], 'text_position': (456, 432)},
        'Region 4': {'boundary': [(299, 493), (64, 262)], 'text_position': (133, 432)},
    }                                                                   

    regions_lhb = {
        'Region 1': {'boundary': [(296, 28), (533, 259)], 'text_position': (465, 96)},
        'Region 2': {'boundary': [(64, 262), (296, 28)], 'text_position': (136, 96)},
        'Region 3': {'boundary': [(533, 259), (299, 493)], 'text_position': (133, 432)},
        'Region 4': {'boundary': [(299, 493), (64, 262)], 'text_position': (456, 432)},
    }

    total_runs = total_runs_all.get(batsman_name, 0)
    if total_runs == 0:
        st.error(f"No total runs available for {batsman_name}.")
        return

    if batting_type == 1:
        regions = regions_rhb
    elif batting_type == 2:
        regions = regions_lhb
    else:
        st.error("Invalid batting type! Please check the data.")
        return

    region_runs = {region: 0 for region in regions}
    for index, row in data[data['StrikerName'] == batsman_name].iterrows():
        wagon_wheel_position = row['WWregion63']
        runs_scored = row['batruns']
        if batting_type == 1:
            if wagon_wheel_position in [23, 15, 7, 24, 16, 8]:
                region_runs['Region 1'] += runs_scored
            elif wagon_wheel_position in [17, 9, 1, 18, 10, 2]:
                region_runs['Region 2'] += runs_scored
            elif wagon_wheel_position in [19, 11, 3, 20, 12, 4]:
                region_runs['Region 3'] += runs_scored
            elif wagon_wheel_position in [21, 13, 5, 22, 14, 6]:
                region_runs['Region 4'] += runs_scored
        elif batting_type == 2:
            if wagon_wheel_position in [18, 10, 2, 17, 9, 1]:
                region_runs['Region 1'] += runs_scored
            elif wagon_wheel_position in [24, 16, 8, 23, 15, 7]:
                region_runs['Region 2'] += runs_scored
            elif wagon_wheel_position in [22, 14, 6, 21, 13, 5]:
                region_runs['Region 3'] += runs_scored
            elif wagon_wheel_position in [20, 12, 4, 19, 11, 3]:
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

def eight_region(data, batsman_name, total_runs_all, plots, phase_option):
    batting_type_data = data[data['StrikerName'] == batsman_name]['StrikerBattingType']
    if batting_type_data.empty:
        st.error(f"No data available for {batsman_name} with the selected filter.")
        return

    batting_type = batting_type_data.iloc[0]

    regions_rhb = {
        'Region 1': {'boundary': [(64, 260), (131, 96)], 'text_position': (84, 169)},
        'Region 2': {'boundary': [(131, 96), (298, 25)], 'text_position': (211, 44)},
        'Region 3': {'boundary': [(298, 25), (466, 97)], 'text_position': (385, 44)},
        'Region 4': {'boundary': [(466, 97), (533, 260)], 'text_position': (513, 169)},
        'Region 5': {'boundary': [(533, 260), (465, 425)], 'text_position': (512, 358)},
        'Region 6': {'boundary': [(465, 260), (299, 498)], 'text_position': (392, 473)},
        'Region 7': {'boundary': [(299, 498), (136, 426)], 'text_position': (215, 473)},
        'Region 8': {'boundary': [(136, 426), (64, 260)], 'text_position': (84, 358)},
    }

    regions_lhb = {
        'Region 1': {'boundary': [(533, 260), (466, 97)], 'text_position': (513, 169)},
        'Region 2': {'boundary': [(466, 97), (298, 25)], 'text_position': (385, 44)},
        'Region 3': {'boundary': [(298, 25), (131, 96)], 'text_position': (211, 44)},
        'Region 4': {'boundary': [(131, 96), (64, 260)], 'text_position': (84, 169)},
        'Region 5': {'boundary': [(64, 260), (136, 426)], 'text_position': (84, 358)},
        'Region 6': {'boundary': [(136, 426), (299, 498)], 'text_position': (215, 473)},
        'Region 7': {'boundary': [(299, 498), (465, 260)], 'text_position': (392, 473)},
        'Region 8': {'boundary': [(465, 260), (533, 260)], 'text_position': (512, 358)},
    }

    total_runs = total_runs_all.get(batsman_name, 0)
    if total_runs == 0:
        st.error(f"No total runs available for {batsman_name}.")
        return

    if batting_type == 1:
        regions = regions_rhb
    elif batting_type == 2:
        regions = regions_lhb
    else:
        st.error("Invalid batting type! Please check the data.")
        return

    region_runs = {region: 0 for region in regions}
    for index, row in data[data['StrikerName'] == batsman_name].iterrows():
        wagon_wheel_position = row['WWregion63']
        runs_scored = row['batruns']
        if batting_type == 1:
            if wagon_wheel_position in [23, 15, 7]:
                region_runs['Region 1'] += runs_scored
            elif wagon_wheel_position in [24, 16, 8]:
                region_runs['Region 2'] += runs_scored
            elif wagon_wheel_position in [17, 9, 1]:
                region_runs['Region 3'] += runs_scored
            elif wagon_wheel_position in [18, 10, 2]:
                region_runs['Region 4'] += runs_scored
            elif wagon_wheel_position in [19, 11, 3]:
                region_runs['Region 5'] += runs_scored
            elif wagon_wheel_position in [20, 12, 4]:
                region_runs['Region 6'] += runs_scored
            elif wagon_wheel_position in [21, 13, 5]:
                region_runs['Region 7'] += runs_scored
            elif wagon_wheel_position in [22, 14, 6]:
                region_runs['Region 8'] += runs_scored
        elif batting_type == 2:
            if wagon_wheel_position in [18, 10, 2]:
                region_runs['Region 1'] += runs_scored
            elif wagon_wheel_position in [17, 9, 1]:
                region_runs['Region 2'] += runs_scored
            elif wagon_wheel_position in [24, 16, 8]:
                region_runs['Region 3'] += runs_scored
            elif wagon_wheel_position in [23, 15, 7]:
                region_runs['Region 4'] += runs_scored
            elif wagon_wheel_position in [22, 14, 6]:
                region_runs['Region 5'] += runs_scored
            elif wagon_wheel_position in [21, 13, 5]:
                region_runs['Region 6'] += runs_scored
            elif wagon_wheel_position in [20, 12, 4]:
                region_runs['Region 7'] += runs_scored
            elif wagon_wheel_position in [19, 11, 3]:
                region_runs['Region 8'] += runs_scored
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
    st.title('Wagon Wheel')
    
    data = pd.read_csv('NewData.csv')
    data = data.dropna(subset=['overs'])
    data['Date'] = pd.to_datetime(data['date'])

    required_columns = ['date','matchid', 'battingclubid', 'StrikerName', 'StrikerBattingType', 'WWregion63', 'batruns']
    missing_columns = [col for col in required_columns if col not in data.columns]
        
    if missing_columns:
        st.error(f"Missing columns in the uploaded file: {', '.join(missing_columns)}")
        return
    
    start_date, end_date = st.date_input("Select date range:", [data['Date'].min(), data['Date'].max()])
    data = data[(data['Date'] >= pd.to_datetime(start_date)) & (data['Date'] <= pd.to_datetime(end_date))]

    competitions = list(data['CompName'].unique())
    selected_competition = st.multiselect("Select competition:", competitions)

    if selected_competition:
        data = data[data['CompName'].isin(selected_competition)]
        
    clubs = data['battingclubid'].unique().tolist()
    selected_club = st.selectbox("Select the club", clubs)

    data = data[data['battingclubid'] == selected_club]
        
    match_ids = ['All'] + list(data['matchid'].unique())
    selected_match_id = st.multiselect("Select Match:", match_ids, default=['All'])

    if 'All' not in selected_match_id:
        data = data[data['matchid'].isin(selected_match_id)]

    batsmen = data['StrikerName'].unique().tolist()
    selected_batsmen = st.multiselect("Select the batsmen", batsmen, default=batsmen)

    region_option = st.selectbox(
        'Select the region option',
        ('4 Region', '6 Region', '8 Region')
    )

    phase_type = st.selectbox("Select phase type (3Phase/4Phase):", ["3Phase", "4Phase"])
    if phase_type == "3Phase":
        phase_options = ["All", "1 to 6", "7 to 15", "16 to 20"]
    elif phase_type == "4Phase":
        phase_options = ["All", "1 to 6", "7 to 10", "11 to 15", "16 to 20"]

    selected_phase = st.selectbox("Select Phase:", phase_options)

    data = filter_data_by_phase(data, phase_type, selected_phase)

    bowling_type = st.selectbox("Select the bowling type", ["Both", "Pace", "Spin"])
    pace_subtype = spin_subtype = None
    if bowling_type == "Pace":
        pace_subtype = st.selectbox("Select the pace subtype", ["All", "RAP", "LAP"])
    elif bowling_type == "Spin":
        spin_subtype = st.selectbox("Select the spin subtype", ["All", "RAO", "SLAO", "RALB", "LAC"])

    data = filter_data_by_bowling_type(data, bowling_type, pace_subtype, spin_subtype)

    total_runs_all = data.groupby('StrikerName')['batruns'].sum().to_dict()

    plots = []

    for batsman in selected_batsmen:
        if region_option == '4 Region':
            four_region(data, batsman, total_runs_all, plots)
        elif region_option == '6 Region':
            six_region(data, batsman, total_runs_all, plots, phase_type)
        elif region_option == '8 Region':
            eight_region(data, batsman, total_runs_all, plots, phase_type)
        
    if plots:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for batsman, plot in zip(selected_batsmen, plots):
                zip_file.writestr(f"{batsman}_wagon_wheel_in_{phase_type.replace(' ', '_')}.png", plot.getvalue())
        zip_buffer.seek(0)
        st.download_button(
            label="Download ZIP",
            data=zip_buffer,
            file_name="wagon_wheel_plots.zip",
            mime="application/zip"
        )

if __name__ == '__main__':
    main()
