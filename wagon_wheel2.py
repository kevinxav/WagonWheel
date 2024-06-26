import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import zipfile

# Function to create a download link
def get_binary_file_downloader_html(data, file_label='File', button_text='Download'):
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_label}">{button_text}</a>'
    return href

def filter_data_by_bowling_type(data, bowling_type, pace_subtype=None, spin_subtype=None):
    if bowling_type == "Pace":
        if pace_subtype == "RAP":
            return data[data['BowlerType'] == 1]
        elif pace_subtype == "LAP":
            return data[data['BowlerType'] == 2]
        else:
            return data
    elif bowling_type == "Spin":
        if spin_subtype == "RAO":
            return data[data['BowlerType'] == 3]
        elif spin_subtype == "SLAO":
            return data[data['BowlerType'] == 4]
        elif spin_subtype == "RALB":
            return data[data['BowlerType'] == 5]
        elif spin_subtype == "LAC":
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

def generate_wagon_wheel_plot(batsman_name, batting_type, region_runs, total_runs, regions, phase_option, plots):
    region_percentages = {region: round((runs / total_runs) * 100) for region, runs in region_runs.items()}
    img = plt.imread('wagon.jpg')
    plt.imshow(img)

    for region, info in regions.items():
        text_position = info['text_position']
        plt.text(text_position[0], text_position[1], f"{region_percentages[region]}%", ha='center', va='center', fontsize=10, color='White', bbox=dict(facecolor='blue', edgecolor='black', boxstyle='round,pad=0.5'))

    plt.axis('off')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    plots.append(buf)

    st.image(buf, caption=f"Wagon Wheel for {batsman_name} in {phase_option}", use_column_width=True)

    plt.figure()
    plt.imshow(img)
    for region, info in regions.items():
        text_position = info['text_position']
        plt.text(text_position[0], text_position[1], f"{region_percentages[region]}%", ha='center', va='center', fontsize=10, color='White', bbox=dict(facecolor='blue', edgecolor='black', boxstyle='round,pad=0.5'))
    plt.axis('off')
    plt.savefig(f"{batsman_name}_wagon_wheel.png")
    plt.close()

def eight_region(data, batsman_name, total_runs_all, plots, phase_option):
    batting_type_data = data[data['StrikerName'] == batsman_name]['BattingType']
    if batting_type_data.empty:
        st.error(f"No data available for {batsman_name} with the selected filter.")
        return

    batting_type = batting_type_data.iloc[0]

    regions_rhb = {
        'Region 1': {'boundary': [(64, 262), (296, 28)], 'text_position': (136, 96)},
        'Region 2': {'boundary': [(296, 28), (533, 259)], 'text_position': (465, 96)},
        'Region 3': {'boundary': [(533, 259), (466,259)], 'text_position': (500, 150)},
        'Region 4': {'boundary': [(466, 259), (399,259)], 'text_position': (450, 240)},
        'Region 5': {'boundary': [(399, 259), (299, 493)], 'text_position': (300, 400)},
        'Region 6': {'boundary': [(299, 493), (130, 425)], 'text_position': (100, 400)},
        'Region 7': {'boundary': [(130, 425), (64, 262)], 'text_position': (60, 240)},
        'Region 8': {'boundary': [(64, 262), (131,259)], 'text_position': (80, 150)},
    }

    regions_lhb = {
        'Region 1': {'boundary': [(296, 28), (533, 259)], 'text_position': (465, 96)},
        'Region 2': {'boundary': [(64, 262), (296, 28)], 'text_position': (136, 96)},
        'Region 3': {'boundary': [(533, 259), (466,259)], 'text_position': (500, 150)},
        'Region 4': {'boundary': [(466, 259), (399,259)], 'text_position': (450, 240)},
        'Region 5': {'boundary': [(399, 259), (299, 493)], 'text_position': (300, 400)},
        'Region 6': {'boundary': [(299, 493), (130, 425)], 'text_position': (100, 400)},
        'Region 7': {'boundary': [(130, 425), (64, 262)], 'text_position': (60, 240)},
        'Region 8': {'boundary': [(64, 262), (131,259)], 'text_position': (80, 150)},
    }

    total_runs = total_runs_all[batsman_name]

    regions = regions_rhb if batting_type == 'RHB' else regions_lhb

    region_runs = {region: 0 for region in regions}
    for _, row in data[data['StrikerName'] == batsman_name].iterrows():
        wagon_wheel_position = row['WagonWheel']
        runs_scored = row['BatRuns']
        if batting_type == 'RHB':
            if wagon_wheel_position in [23, 15, 7, 24, 16, 8]:
                region_runs['Region 1'] += runs_scored
            elif wagon_wheel_position in [17, 9, 1, 18, 10, 2]:
                region_runs['Region 2'] += runs_scored
            elif wagon_wheel_position in [25, 26, 27]:
                region_runs['Region 3'] += runs_scored
            elif wagon_wheel_position in [21, 13, 5, 22, 14, 6]:
                region_runs['Region 4'] += runs_scored
            elif wagon_wheel_position in [19, 11, 3, 20, 12, 4]:
                region_runs['Region 5'] += runs_scored
            elif wagon_wheel_position in [29, 30, 31]:
                region_runs['Region 6'] += runs_scored
            elif wagon_wheel_position in [35, 36, 37]:
                region_runs['Region 7'] += runs_scored
            elif wagon_wheel_position in [41, 42, 43]:
                region_runs['Region 8'] += runs_scored
        else:
            if wagon_wheel_position in [18, 10, 2, 17, 9, 1]:
                region_runs['Region 1'] += runs_scored
            elif wagon_wheel_position in [24, 16, 8, 23, 15, 7]:
                region_runs['Region 2'] += runs_scored
            elif wagon_wheel_position in [29, 30, 31]:
                region_runs['Region 3'] += runs_scored
            elif wagon_wheel_position in [20, 12, 4, 19, 11, 3]:
                region_runs['Region 4'] += runs_scored
            elif wagon_wheel_position in [22, 14, 6, 21, 13, 5]:
                region_runs['Region 5'] += runs_scored
            elif wagon_wheel_position in [25, 26, 27]:
                region_runs['Region 6'] += runs_scored
            elif wagon_wheel_position in [35, 36, 37]:
                region_runs['Region 7'] += runs_scored
            elif wagon_wheel_position in [41, 42, 43]:
                region_runs['Region 8'] += runs_scored

    generate_wagon_wheel_plot(batsman_name, batting_type, region_runs, total_runs, regions, phase_option, plots)

def main():
    st.title("Cricket Wagon Wheel Plotter")

    data_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if data_file is not None:
        data = pd.read_csv(data_file)
        batsman_name = st.text_input("Enter Batsman Name")
        bowling_type = st.selectbox("Select Bowling Type", ["Pace", "Spin", "Both"])
        pace_subtype = st.selectbox("Select Pace Subtype", ["All", "RAP", "LAP"]) if bowling_type == "Pace" else None
        spin_subtype = st.selectbox("Select Spin Subtype", ["All", "RAO", "SLAO", "RALB", "LAC"]) if bowling_type == "Spin" else None
        phase_option = st.selectbox("Select Phase", ["All", "Power Play (1-6)", "Middle Overs (7-15)", "Death Overs (16-20)"])
        num_regions = st.selectbox("Select Number of Regions", [4, 6, 8])

        filtered_data = filter_data_by_bowling_type(data, bowling_type, pace_subtype, spin_subtype)
        filtered_data = filter_data_by_phase(filtered_data, phase_option)
        total_runs_all = filtered_data.groupby('StrikerName')['batruns'].sum().to_dict()

        if batsman_name:
            plots = []
            if num_regions == 4:
                four_region(filtered_data, batsman_name, total_runs_all, plots)
            elif num_regions == 6:
                six_region(filtered_data, batsman_name, total_runs_all, plots, phase_option)
            elif num_regions == 8:
                eight_region(filtered_data, batsman_name, total_runs_all, plots, phase_option)

            if plots:
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
                    for i, plot in enumerate(plots):
                        zip_file.writestr(f'plot_{i+1}.png', plot.getvalue())
                zip_buffer.seek(0)
                st.markdown(get_binary_file_downloader_html(zip_buffer.getvalue(), 'plots.zip', 'Download All Plots'), unsafe_allow_html=True)
        else:
            st.warning("Please enter the batsman's name.")
    else:
        st.warning("Please upload a CSV file.")

if __name__ == "__main__":
    main()
