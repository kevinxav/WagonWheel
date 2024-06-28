import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import zipfile

def filter_data_by_bowling_type(data, bowling_type, pace_subtype=None, spin_subtype=None):
    if bowling_type == "Pace":
        if pace_subtype == "Right Arm Fast (RAP)":
            return data[data['BowlerType'] == 1]
        elif pace_subtype == "Left Arm Fast (LAP)":
            return data[data['BowlerType'] == 2]
        else:
            return data
    elif bowling_type == "Spin":
        if spin_subtype == "Right Arm Off Spin (RAO)":
            return data[data['BowlerType'] == 3]
        elif spin_subtype == "Left Arm Orthodox (SLAO)":
            return data[data['BowlerType'] == 4]
        elif spin_subtype == "Right Arm Leg Break (RALB)":
            return data[data['BowlerType'] == 5]
        elif spin_subtype == "Left Arm Chinaman (LAC)":
            return data[data['BowlerType'] == 6]
        else:
            return data
    elif bowling_type == "Both":
        return data
    else:
        return data

def filter_data_by_phase(data, phase):
    if phase == "Power Play (1-6)":
        return data[(data['overs'] >= 0.1) & (data['overs'] <= 5.6)]
    elif phase == "Middle Overs (7-15)":
        return data[(data['overs'] >= 6.1) & (data['overs'] <= 14.6)]
    elif phase == "Death Overs (16-20)":
        return data[(data['overs'] >= 15.1) & (data['overs'] <= 19.6)]
    else:  # "All"
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

    if batting_type == '1':
        regions = regions_rhb
    elif batting_type == '2':
        regions = regions_lhb
    else:
        st.error("Invalid batting type! Please check the data.")
        return

    region_runs = {region: 0 for region in regions}
    for index, row in data[data['StrikerName'] == batsman_name].iterrows():
        wagon_wheel_position = row['WWregion63']
        runs_scored = row['batruns']
        if batting_type == '1':
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
        elif batting_type == '2':
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

    if batting_type == '1':
        regions = regions_rhb
    elif batting_type == '2':
        regions = regions_lhb
    else:
        st.error("Invalid batting type! Please check the data.")
        return

    region_runs = {region: 0 for region in regions}
    for index, row in data[data['StrikerName'] == batsman_name].iterrows():
        wagon_wheel_position = row['WWregion63']
        runs_scored = row['batruns']
        if batting_type == '1':
            if wagon_wheel_position in [23, 15, 7, 24, 16, 8, 18, 10, 2, 17, 9, 1]:
                region_runs['Region 1'] += runs_scored
            elif wagon_wheel_position in [19, 11, 3, 20, 12, 4]:
                region_runs['Region 2'] += runs_scored
            elif wagon_wheel_position in [21, 13, 5, 22, 14, 6]:
                region_runs['Region 3'] += runs_scored
            elif wagon_wheel_position in [25, 15, 7, 26, 16, 8]:
                region_runs['Region 4'] += runs_scored
        elif batting_type == '2':
            if wagon_wheel_position in [18, 10, 2, 17, 9, 1, 24, 16, 8, 23, 15, 7]:
                region_runs['Region 1'] += runs_scored
            elif wagon_wheel_position in [22, 14, 6, 21, 13, 5]:
                region_runs['Region 2'] += runs_scored
            elif wagon_wheel_position in [20, 12, 4, 19, 11, 3]:
                region_runs['Region 3'] += runs_scored
            elif wagon_wheel_position in [25, 15, 7, 26, 16, 8]:
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
    st.image(buf, caption=f"Wagon Wheel for {batsman_name} in All Phases", use_column_width=True)

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
    st.title("Wagon Wheel Analysis")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)

        st.sidebar.title("Filter Options")
        phase_option = st.sidebar.selectbox("Select Phase", ["All", "Power Play (1-6)", "Middle Overs (7-15)", "Death Overs (16-20)"])
        bowling_option = st.sidebar.selectbox("Select Bowling Type", ["Both", "Pace", "Spin"])
        pace_subtype = None
        spin_subtype = None
        if bowling_option == "Pace":
            pace_subtype = st.sidebar.selectbox("Select Pace Type", ["All", "Right Arm Fast (RAP)", "Left Arm Fast (LAP)"])
        elif bowling_option == "Spin":
            spin_subtype = st.sidebar.selectbox("Select Spin Type", ["All", "Right Arm Off Spin (RAO)", "Left Arm Orthodox (SLAO)", "Right Arm Leg Break (RALB)", "Left Arm Chinaman (LAC)"])

        batsman_name = st.sidebar.selectbox("Select Batsman", data['StrikerName'].unique())
        total_runs_all = data.groupby('StrikerName')['batruns'].sum().to_dict()

        filtered_data = filter_data_by_bowling_type(data, bowling_option, pace_subtype, spin_subtype)
        filtered_data = filter_data_by_phase(filtered_data, phase_option)

        plots = []
        six_region(filtered_data, batsman_name, total_runs_all, plots, phase_option)
        four_region(filtered_data, batsman_name, total_runs_all, plots)

        if plots:
            # Save all plots to a zip file
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for i, plot in enumerate(plots):
                    plot_filename = f"plot_{i + 1}.png"
                    zip_file.writestr(plot_filename, plot.getvalue())

            # Provide a download link for the zip file
            st.sidebar.download_button(
                label="Download All Plots as ZIP",
                data=zip_buffer.getvalue(),
                file_name="wagon_wheel_plots.zip",
                mime="application/zip"
            )

if __name__ == "__main__":
    main()
