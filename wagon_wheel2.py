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

def six_region(data, batsman_name, total_runs_all, plots, phase_option):
    batting_type_data = data[data['StrikerName'] == batsman_name]['BattingType']
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
        elif batting_type == 'LHB':
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
    batting_type_data = data[data['StrikerName'] == batsman_name]['BattingType']
    if batting_type_data.empty:
        st.error(f"No data available for {batsman_name} with the selected filter.")
        return

    batting_type = batting_type_data.iloc[0]

    regions_rhb = {
        'Region 1': {'boundary': [(64, 262), (296, 28)], 'text_position': (136, 96)},
        'Region 2': {'boundary': [(296, 28), (533, 259)], 'text_position': (465, 96)},
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

# Add this line to specify the file path
csv_file_path = "Ausvsnz_new.csv"

# Replace this line
# file = st.file_uploader("Upload CSV", type="csv")

# Add this line to read the CSV directly
data = pd.read_csv(csv_file_path)

# Select filtering options
bowling_type = st.selectbox("Select Bowling Type", ["Both", "Pace", "Spin"])
pace_subtype = st.selectbox("Select Pace Subtype", ["All", "RAP", "LAP"]) if bowling_type == "Pace" else None
spin_subtype = st.selectbox("Select Spin Subtype", ["All", "RAO", "SLAO", "RALB", "LAC"]) if bowling_type == "Spin" else None

phase_option = st.selectbox("Select Phase", ["All", "Power Play (1-6)", "Middle Overs (7-15)", "Death Overs (16-20)"])

# Filter data based on selections
filtered_data = filter_data_by_bowling_type(data, bowling_type, pace_subtype, spin_subtype)
filtered_data = filter_data_by_phase(filtered_data, phase_option)

# Display the filtered data
st.write("Filtered Data", filtered_data)

# Prepare the data for plotting
batsmen = filtered_data['StrikerName'].unique()
total_runs_all = filtered_data.groupby('StrikerName')['BatRuns'].sum().to_dict()

plots = []
for batsman in batsmen:
    six_region(filtered_data, batsman, total_runs_all, plots, phase_option)
    four_region(filtered_data, batsman, total_runs_all, plots)

# Create a zip file of all the plots
zip_buffer = BytesIO()
with zipfile.ZipFile(zip_buffer, "w") as zf:
    for i, plot in enumerate(plots):
        zf.writestr(f"plot_{i+1}.png", plot.getvalue())

# Provide a download link for the zip file
st.markdown(get_binary_file_downloader_html(zip_buffer.getvalue(), file_label="plots.zip", button_text="Download All Plots"), unsafe_allow_html=True)
