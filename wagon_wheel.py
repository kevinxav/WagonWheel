import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Read CSV file
default_file_path = "C:/Users/sabarish jayakumar/OneDrive/Desktop/KAD/WagonWheel/batruns.csv"
data = pd.read_csv(default_file_path)

regions = {
    'Region 1': {'boundary': [(64, 261), (134, 96)], 'text_position': (143, 205)},
    'Region 2': {'boundary': [(134, 96), (294, 25)], 'text_position': (234, 115)},
    'Region 3': {'boundary': [(294, 25), (467, 95)], 'text_position': (364, 115)},
    'Region 4': {'boundary': [(467, 95), (536, 263)], 'text_position': (445, 205)},
    'Region 5': {'boundary': [(536, 263), (464, 429)], 'text_position': (450, 329)},
    'Region 6': {'boundary': [(464, 429), (300, 495)], 'text_position': (359, 411)},
    'Region 7': {'boundary': [(300, 495), (130, 425)], 'text_position': (225, 411)},
    'Region 8': {'boundary': [(130, 425), (64, 261)], 'text_position': (131, 329)}
}

def calculate_runs(batsman_name):
    # Step 2: Calculate total runs scored by the batsman
    total_runs = data[data['StrikerName'] == batsman_name]['BatRuns'].sum()

    # Step 3: Calculate runs scored in each region by the batsman
    region_runs = {region: 0 for region in regions}
    for index, row in data[data['StrikerName'] == batsman_name].iterrows():
        wagon_wheel_position = row['WagonWheel']
        runs_scored = row['BatRuns']
        # Map wagon wheel position to region and accumulate runs
        if wagon_wheel_position == 'Point':
            region_runs['Region 1'] += runs_scored
        elif wagon_wheel_position == 'Third Man':
            region_runs['Region 2'] += runs_scored
        elif wagon_wheel_position == 'Fine Leg':
            region_runs['Region 3'] += runs_scored
        elif wagon_wheel_position == 'Square Leg':
            region_runs['Region 4'] += runs_scored
        elif wagon_wheel_position == 'Mid Wicket':
            region_runs['Region 5'] += runs_scored
        elif wagon_wheel_position == 'Long On':
            region_runs['Region 6'] += runs_scored
        elif wagon_wheel_position == 'Long Off':
            region_runs['Region 7'] += runs_scored
        elif wagon_wheel_position == 'Covers':
            region_runs['Region 8'] += runs_scored

    # Step 4: Calculate percentage of runs in each region
    region_percentages = {region: round((runs / total_runs) * 100) for region, runs in region_runs.items()}

    return region_percentages

def main():
    st.title("Cricket Wagon Wheel Analysis")

    # Step 1: Ask for batsman name
    batsman_name = st.text_input("Enter the batsman's name:")

    if batsman_name:
        region_percentages = calculate_runs(batsman_name)

        # Step 5: Display wagon wheel with percentages
        fig, ax = plt.subplots()  # Creating a new figure
        img = plt.imread("C:/Users/sabarish jayakumar/OneDrive/Desktop/KAD/WagonWheel/wagon.jpg")
        ax.imshow(img)

        for region, info in regions.items():
            text_position = info['text_position']
            ax.text(text_position[0], text_position[1], f"{region_percentages[region]}%", ha='center', va='center', fontsize=10, color='White', bbox=dict(facecolor='blue', edgecolor='black', boxstyle='round,pad=0.5'))

        ax.axis('off')
        st.pyplot(fig)  # Passing the figure object to st.pyplot()

if __name__ == "__main__":
    main()
