import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.colors as mcolors
import matplotlib.patches as patches
import pandas as pd
import numpy as np

# Constants for pitch map coordinates calculations
old_reg_start_y = 0
old_reg_stump_y = 101
old_reg_2m_y = 263
old_reg_4m_y = 439
old_reg_6m_y = 620
old_reg_8m_y = 808
old_reg_10m_y = 1005
old_reg_end_y = 1788
old_reg_xlen = 364

pitch_map_height = 600
pitch_map_weight = 1080
pitch_map_start_y = 153
pitch_map_stump_y = 178
pitch_map_2m_y = 208
pitch_map_4m_y = 253
pitch_map_6m_y = 298
pitch_map_8m_y = 352
pitch_map_10m_y = 408
pitch_map_end_y = 489

pitch_map_start_x1p = 344
pitch_map_start_x2p = 704
pitch_map_stump_x1p = 339
pitch_map_stump_x2p = 709
pitch_map_2m_x1p = 332
pitch_map_2m_x2p = 714
pitch_map_4m_x1p = 323
pitch_map_4m_x2p = 722
pitch_map_6m_x1p = 316 
pitch_map_6m_x2p = 729
pitch_map_8m_x1p = 306
pitch_map_8m_x2p = 742
pitch_map_10m_x1p = 294
pitch_map_10m_x2p = 752
pitch_map_end_x1p = 277
pitch_map_end_x2p = 769

# Function to read data from a default CSV file
def read_data():
    file_path = 'NewData.csv'
    try:
        data = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Data file not found: {file_path}")
        st.stop()  # Stop execution if file is not found
    return data

# Mapping of MatchtypeId to match types
match_type_dict = {
    1: "Test Match", 2: "One-Day International", 3: "Twenty20 International", 
    4: "First Class Match", 5: "List A Match", 6: "Twenty20 Match", 7: "Others", 
    8: "Women's Tests", 9: "Women's One-Day Internationals", 10: "Women's Twenty20 Internationals", 
    11: "Other First Class", 12: "Other List A", 13: "Other Twenty20", 
    14: "Women's First Class Matches", 15: "Women's List A Matches", 16: "Women's Twenty20", 
    17: "Others Women's First Class", 18: "Others Women's List A", 19: "Others Women's Twenty20", 
    20: "Youth Tests", 21: "Youth One-Day Internationals", 22: "Youth Twenty20 Internationals", 
    26: "Youth First Class", 27: "Youth List A", 28: "Youth Twenty20", 
    29: "Women's Youth Tests", 30: "Women's Youth One-Day Internationals", 
    31: "Women's Youth Twenty20 Internationals", 32: "Women's Youth First Class", 
    33: "Women's Youth List A", 34: "Women's Youth Twenty20", 35: "Other Youth First Class Matches", 
    36: "Other Youth List A Matches", 37: "Dual Collection Fast Test Format", 
    38: "Dual Collection Fast ODI Format", 39: "Dual Collection Fast T20 Format", 
    40: "Other Youth Twenty20 Matches", 41: "International The Hundred", 
    42: "Domestic The Hundred", 43: "Women's International The Hundred", 
    44: "Women's Domestic The Hundred", 45: "Youth Women's T20", 50: "T10", 51: "W T10", 
    53: "Others U19 Women T20", 54: "Other Women's Youth Twenty20", 91: "The 6ixty"
}

# Reverse the dictionary for easy lookup by match type name
reverse_match_type_dict = {v: k for k, v in match_type_dict.items()}

# Functions for Beehive transformations
def ShortZoneXaxis(HeightX, OldRegStartSS_X, OldRegEndSS_X, RegStartSS_X, RegEndSS_X):
    if OldRegStartSS_X <= HeightX <= OldRegEndSS_X:
        return (((RegEndSS_X - RegStartSS_X) / (OldRegEndSS_X - OldRegStartSS_X)) * (HeightX - OldRegStartSS_X)) + RegStartSS_X
    else:
        return None

def ShortZoneYaxis(HeightY, OldRegStartSS_Y, OldRegStumpHeightSS_Y, OldRegStumpLineSS_Y, OldRegEndSS_Y, RegStartSS_Y, RegStumpHeightSS_Y, RegStumpLineSS_Y, RegEndSS_Y):
    if OldRegStartSS_Y <= HeightY <= OldRegStumpHeightSS_Y:
        return (((RegStumpHeightSS_Y - RegStartSS_Y) / (OldRegStumpHeightSS_Y - OldRegStartSS_Y)) * (HeightY - OldRegStartSS_Y)) + RegStartSS_Y
    elif OldRegStumpHeightSS_Y < HeightY <= OldRegStumpLineSS_Y:
        return (((RegStumpLineSS_Y - RegStumpHeightSS_Y) / (OldRegStumpLineSS_Y - OldRegStumpHeightSS_Y)) * (HeightY - OldRegStumpHeightSS_Y)) + RegStumpHeightSS_Y
    elif OldRegStumpLineSS_Y < HeightY <= OldRegEndSS_Y:
        return (((RegEndSS_Y - RegStumpLineSS_Y) / (OldRegEndSS_Y - OldRegStumpLineSS_Y)) * (HeightY - OldRegStumpLineSS_Y)) + RegStumpLineSS_Y
    else:
        return None

def calculate_runs_and_balls(row):
    if row['0s'] == 1:
        return 0, 1
    elif row['1s'] == 1:
        return 1, 1
    elif row['2s'] == 1:
        return 2, 1
    elif row['3s'] == 1:
        return 3, 1
    elif row['4s'] == 1:
        return 4, 1
    elif row['6s'] == 1:
        return 6, 1
    else:
        return 0, 0

# Function for PitchMap coordinates
def calculate_pitch_map_coordinates(length_x, length_y, origin_x, origin_y):
    x_axis = calculate_pitch_map_xaxis(length_x, length_y, origin_x)
    y_axis = calculate_pitch_map_yaxis(length_y, origin_y)
    return x_axis, y_axis

def calculate_pitch_map_xaxis(length_x, length_y, origin_x):
    return ((pitch_map_start_x2p - pitch_map_start_x1p) / old_reg_xlen) * length_x + pitch_map_start_x1p

def calculate_pitch_map_yaxis(length_y, origin_y):
    return pitch_map_height - (((pitch_map_stump_y - pitch_map_start_y) / (old_reg_stump_y - old_reg_start_y)) * (length_y - old_reg_start_y) + pitch_map_start_y)

# Function for WagonWheel regions and percentage calculation
def get_batting_type(df, batsman_name):
    df_batsman = df[df['StrikerName'] == batsman_name]
    if not df_batsman.empty:
        batting_type = df_batsman.iloc[0]['StrikerBattingType']
        return 'RHB' if batting_type == 1 else 'LHB'
    return None

def calculate_runs_by_region(df, batsman_name):
    batting_type = get_batting_type(df, batsman_name)
    
    if not batting_type:
        raise ValueError(f"Batsman {batsman_name} not found or invalid StrikerBattingType")
    
    df_batsman = df[df['StrikerName'] == batsman_name]
    
    region_runs = {f'Region {i}': 0 for i in range(1, 9)}
    total_runs = 0
    
    for _, row in df_batsman.iterrows():
        wagon_wheel_position = row['WWregion63']
        runs_scored = row['batruns']
        
        if batting_type == 'RHB':
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
        elif batting_type == 'LHB':
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
        
        total_runs += runs_scored
    
    return region_runs, total_runs, batting_type

def calculate_percentage(runs_data, total_runs):
    percentage_data = {}
    for region, runs in runs_data.items():
        percentage = round((runs / total_runs) * 100) if total_runs != 0 else 0
        percentage_data[region] = percentage
    return percentage_data

def create_circle_with_regions(title, region_labels, percentage_data, cmap_name='Purples', width=4, height=4):
    fig, ax = plt.subplots(figsize=(6, 6))  # Adjust the figure size here

    norm = plt.Normalize(min(percentage_data.values()), max(percentage_data.values()))
    
    colormaps = {
        'Blues': plt.cm.Blues,
        'Reds': plt.cm.Reds,
        'Greens': plt.cm.Greens,
        'Purples': plt.cm.Purples,
        'Oranges': plt.cm.Oranges
    }
    cmap = colormaps.get(cmap_name, plt.cm.Purples)

    angles = np.linspace(0, 2 * np.pi, 9)  # 9 points to ensure the circle closes
    for i in range(len(angles) - 1):
        theta1, theta2 = np.degrees(angles[i]), np.degrees(angles[i+1])
        wedge = patches.Wedge((300, 300), 300, theta1, theta2, facecolor=cmap(norm(percentage_data[region_labels[i]])), edgecolor='black', alpha=0.6)
        ax.add_patch(wedge)
        
        mid_angle = (angles[i] + angles[i + 1]) / 2
        text_x = 300 + 150 * np.cos(mid_angle)
        text_y = 300 + 150 * np.sin(mid_angle)
        ax.text(text_x, text_y, f"{percentage_data[region_labels[i]]}%", ha='center', va='center', fontsize=10)

    rectangle = plt.Rectangle((275, 220), 50, 100, edgecolor='black', facecolor='none', alpha=0.5)
    ax.add_patch(rectangle)
    
    ax.plot(300, 300, marker='*', color='black')

    ax.set_xlim(0, 600)
    ax.set_ylim(0, 600)
    ax.set_aspect('equal')
    ax.set_xlabel('X-axis (pixels)')
    ax.set_ylabel('Y-axis (pixels)')
    ax.set_title(title)
    ax.axis('off')
    
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.036, pad=0.1, label='Percentage of Runs')
    
    return fig, ax

# Filtering functions
def filter_data_by_pace_or_spin(data, pace_or_spin):
    if "All" in pace_or_spin:
        return data
    pace_or_spin_values = []
    if "Pace" in pace_or_spin:
        pace_or_spin_values.append(1)
    if "Spin" in pace_or_spin:
        pace_or_spin_values.append(2)
    return data[data['PaceorSpin'].isin(pace_or_spin_values)]

def filter_data_by_bowling_type_group(data, bowling_types, is_pace=True):
    if "All" in bowling_types:
        return data
    bowling_type_values = []
    if is_pace:
        if "RAP" in bowling_types:
            bowling_type_values.append(1)
        if "LAP" in bowling_types:
            bowling_type_values.append(2)
    else:
        if "RAO" in bowling_types:
            bowling_type_values.append(3)
        if "SLAO" in bowling_types:
            bowling_type_values.append(4)
        if "RALB" in bowling_types:
            bowling_type_values.append(5)
        if "LAC" in bowling_types:
            bowling_type_values.append(6)
    return data[data['BowlingTypeGroup'].isin(bowling_type_values)]

def filter_data_by_phase(data, phase_column, phases):
    if "All" in phases:
        return data
    phase_mapping = {
        "1 to 6": 1,
        "7 to 15": 2,
        "16 to 20": 3,
        "7 to 10": 2,
        "11-15": 3,
        "16 to 20": 4,
    }
    phase_values = [phase_mapping.get(phase) for phase in phases if phase in phase_mapping]
    return data[data[phase_column].isin(phase_values)]

def filter_data_by_run_type(data, run_types):
    if "All" in run_types:
        return data
    run_columns = {
        '0s': '0s', '1s': '1s', '2s': '2s', '3s': '3s',
        '4s': '4s', '6s': '6s', 'wickets': 'Batwkts'
    }
    for run_type in run_types:
        if run_type in run_columns:
            data = data[data[run_columns[run_type]] == 1]
    return data

# Main function
def main():
    st.title('Cricket Dashboard - kevin_xaviour')

    # Load data from default file
    data = read_data()
    data_filtered=data
    # 6. Select multiple batsmen
    available_player_names = data['StrikerName'].unique()
    selected_batsmen = st.multiselect("Select players' names", available_player_names, key="batsmen")

    # 7. Select bowler type (Pace/Spin)
    pace_or_spin = st.multiselect("Select bowler type", ["All", "Pace", "Spin"], default=["All"], key="pace_or_spin")
    data_filtered = filter_data_by_pace_or_spin(data_filtered, pace_or_spin)

    # Select Bowling Type Group
    if "Pace" in pace_or_spin:
        selected_bowling_types = st.multiselect("Select Bowling Type Group (Pace)", ["All", "RAP", "LAP"], default=["All"], key="bowling_type_pace")
        data_filtered = filter_data_by_bowling_type_group(data_filtered, selected_bowling_types, is_pace=True)

    if "Spin" in pace_or_spin:
        selected_bowling_types = st.multiselect("Select Bowling Type Group (Spin)", ["All", "RAO", "SLAO", "RALB", "LAC"], default=["All"], key="bowling_type_spin")
        data_filtered = filter_data_by_bowling_type_group(data_filtered, selected_bowling_types, is_pace=False)

    # 8. Select phase type (3Phase/4Phase)
    phase_type = st.selectbox("Select phase type", ["3Phase", "4Phase"], key="phase_type")
    if phase_type == "3Phase":
        selected_phases = st.multiselect("Select Phase (3Phase)", ["All", "1 to 6", "7 to 15", "16 to 20"], default=["All"], key="phase_3")
        data_filtered = filter_data_by_phase(data_filtered, 'Phase3idStar', selected_phases)
    elif phase_type == "4Phase":
        selected_phases = st.multiselect("Select Phase (4Phase)", ["All", "1 to 6", "7 to 10", "11-15", "16 to 20"], default=["All"], key="phase_4")
        data_filtered = filter_data_by_phase(data_filtered, 'Phase4id', selected_phases)

    # 9. Select run types
    run_types = st.multiselect("Select run types", ["0s", "1s", "2s", "3s", "4s", "6s", "wickets", "All"], default=["All"], key="run_types")
    data_filtered = filter_data_by_run_type(data_filtered, run_types)

    if data_filtered.empty:
        st.write(f"No data available after filtering with the selected options.")
        return

    # Generate output for each selected batsman
    for player_name in selected_batsmen:
        st.subheader(f'Visualizations for {player_name}')
        
        player_data_filtered = data_filtered[data_filtered['StrikerName'] == player_name]

        # Beehive Visualization
        OldRegStartSS_Y = 189
        OldRegStumpHeightSS_Y = 312
        OldRegStumpLineSS_Y = 406
        OldRegEndSS_Y = 446
        OldRegStartSS_X = 144
        OldRegEndSS_X = 462

        RegStartSS_Y = 90
        RegEndSS_Y = 467
        RegStartSS_X = 300
        RegEndSS_X = 781
        RegStumpHeightSS_Y = 335
        RegStumpLineSS_Y = 439

        width = 1080
        height = 600

        player_data_filtered['TransformedX'] = player_data_filtered['HeightX'].apply(lambda x: ShortZoneXaxis(x, OldRegStartSS_X, OldRegEndSS_X, RegStartSS_X, RegEndSS_X))
        player_data_filtered['TransformedY'] = player_data_filtered['HeightY'].apply(lambda y: ShortZoneYaxis(y, OldRegStartSS_Y, OldRegStumpHeightSS_Y, OldRegStumpLineSS_Y, OldRegEndSS_Y, RegStartSS_Y, RegStumpHeightSS_Y, RegStumpLineSS_Y, RegEndSS_Y))

        runs_balls = player_data_filtered.apply(calculate_runs_and_balls, axis=1, result_type='expand')
        player_data_filtered['Runs'] = runs_balls[0]
        player_data_filtered['Balls'] = runs_balls[1]

        player_data_filtered = player_data_filtered.dropna(subset=['TransformedX', 'TransformedY'])

        fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
        ax.set_title(f'Beehive for {player_name}')

        heatmap_startdown = 300
        heatmap_startup = 0
        heatmap_enddown = 780
        heatmap_endup = 466

        xedges = np.linspace(heatmap_startdown, heatmap_enddown, 5)
        yedges = np.linspace(heatmap_startup, heatmap_endup, 5)

        ax.set_xlim(0, width)
        ax.set_ylim(height, 0)

        ax.plot([522, 522], [437, 336], color='black', linewidth=3, alpha=0.5)
        ax.plot([540, 540], [437, 336], color='black', linewidth=3, alpha=0.5)
        ax.plot([559, 559], [437, 336], color='black', linewidth=3, alpha=0.5)

        ax.plot([522, 540], [336, 336], color='black', linewidth=3, alpha=0.5)
        ax.plot([540, 559], [336, 336], color='black', linewidth=3, alpha=0.5)
        ax.axis('off')

        for index, row in player_data_filtered.iterrows():
            X = (row['TransformedX'] / 1080 * width) - 7
            Y = (row['TransformedY'] / 600 * height) - 13
            size = 2
            if row['0s'] == 1:
                size = 15
            if row['1s'] == 1 or row['2s'] == 1 or row['3s'] == 1:
                size = 5
            if row['4s'] == 1:
                size = 30
            if row['6s'] == 1:
                size = 45
            if row['Batwkts'] == 1:
                size = 80
            ax.scatter(X, Y, marker='o', edgecolors='black', facecolors='none', s=size, alpha=0.15)

        runs_in_box = np.zeros((4, 4), dtype=int)
        balls_in_box = np.zeros((4, 4), dtype=int)
        x_bin_indices = np.digitize(player_data_filtered['TransformedX'], xedges) - 1
        y_bin_indices = np.digitize(player_data_filtered['TransformedY'], yedges) - 1

        valid_indices = (x_bin_indices >= 0) & (x_bin_indices < 4) & (y_bin_indices >= 0) & (y_bin_indices < 4)

        filtered_x_bin_indices = x_bin_indices[valid_indices]
        filtered_y_bin_indices = y_bin_indices[valid_indices]
        filtered_data = player_data_filtered[valid_indices]

        for idx in range(len(filtered_data)):
            runs_in_box[filtered_y_bin_indices[idx], filtered_x_bin_indices[idx]] += filtered_data.iloc[idx]['Runs']
            balls_in_box[filtered_y_bin_indices[idx], filtered_x_bin_indices[idx]] += filtered_data.iloc[idx]['Balls']

        norm = mcolors.Normalize(vmin=runs_in_box.min(), vmax=runs_in_box.max())
        cmap = plt.cm.Reds

        for i in range(4):
            for j in range(4):
                x_center = (xedges[j] + xedges[j + 1]) / 2
                y_center = (yedges[i] + yedges[i + 1]) / 2
                color = cmap(norm(runs_in_box[i, j]))
                rect = plt.Rectangle((xedges[j], yedges[i]), xedges[j + 1] - xedges[j], yedges[i + 1] - yedges[i], color=color, alpha=0.5)
                ax.add_patch(rect)

                if balls_in_box[i, j] > 0:
                    strike_rate = int((runs_in_box[i, j] / balls_in_box[i, j]) * 100)
                else:
                    strike_rate = 0
                ax.text(x_center, y_center, f"{runs_in_box[i, j]} ({balls_in_box[i, j]})\nSR: {strike_rate}", color='black', ha='center', va='center', fontsize=10, weight='bold')

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        fig.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.036, pad=0.1, label='Number of Runs')

        st.pyplot(fig)

        # PitchMap Visualization
        img_path = 'Pacer_PM.png'
        try:
            img = mpimg.imread(img_path)
        except FileNotFoundError:
            st.error(f"Image file not found: {img_path}")
            return

        height, width = 600, 1080
        print(f'Pitch Map for {player_name}')
        fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
        ax = fig.add_subplot(111)

        ax.set_xlim(0, width)
        ax.set_ylim(height, 0)

        stump1_start = (519, 95)
        stump1_end = (519, 181)
        stump2_start = (534, 95)
        stump2_end = (534, 181)
        stump3_start = (549, 95)
        stump3_end = (549, 181)

        ax.plot([519, 519], [95, 181], color='black', linewidth=3, alpha=0.3)
        ax.plot([534, 534], [95, 181], color='black', linewidth=3, alpha=0.3)
        ax.plot([549, 549], [95, 181], color='black', linewidth=3, alpha=0.3)

        ax.plot([519, 534], [95, 95], color='black', linewidth=3, alpha=0.3)
        ax.plot([534, 549], [95, 95], color='black', linewidth=3, alpha=0.3)

        lines_and_labels = [
            ((340, 215), (520, 215), "2m"),
            ((330, 257), (520, 257), "4m"),
            ((321, 304), (520, 304), "6m"),
            ((312, 357), (520, 357), "8m"),
            ((300, 415), (520, 415), "Halfway")
        ]

        for start, end, label in lines_and_labels:
            ax.text(start[0], start[1] - 5, label, verticalalignment='bottom', horizontalalignment='left', color='black', fontsize=6, alpha=1.0)
            ax.plot([start[0], end[0]], [start[1], end[1]], linestyle='dotted', color='black', alpha=0.5)

        ax.plot([stump1_end[0], 519], [stump1_end[1], 600], linestyle='dotted', color='red', alpha=0.6)
        ax.plot([stump3_end[0], 549], [stump3_end[1], 600], linestyle='dotted', color='red', alpha=0.6)

        heatmap_startdown = 345
        heatmap_startup = 160
        heatmap_enddown = 727
        heatmap_endup = 600

        xedges = np.linspace(heatmap_startdown, heatmap_enddown, 6)
        yedges = np.linspace(heatmap_startup, heatmap_endup, 10)

        for x in xedges:
            ax.plot([x, x], [heatmap_startup, heatmap_endup], color='black', linewidth=1, alpha=0)
        for y in yedges:
            ax.plot([heatmap_startdown, heatmap_enddown], [y, y], color='black', linewidth=1, alpha=0)

        ax.set_xlim(0, width)
        ax.set_ylim(height, 0)

        batting_outcomes = player_data_filtered[['LengthX', 'LengthY', '1s', '2s', '3s', '4s', '6s', '0s', 'Batwkts']].values

        grid_runs_balls = np.zeros((len(xedges) - 1, len(yedges) - 1), dtype=object)

        for i in range(len(xedges) - 1):
            for j in range(len(yedges) - 1):
                grid_runs_balls[i, j] = {'runs': 0, 'balls': 0}

        for outcome in batting_outcomes:
            x, y, is_1s, is_2s, is_3s, is_4s, is_6s, is_0s, is_batwkts = outcome
            x_mapped, y_mapped = calculate_pitch_map_coordinates(x, y, 0, 0)

            size = 2
            if is_0s == 1:
                size = 15
            elif is_1s == 1 or is_2s == 1 or is_3s == 1:
                size = 5
            elif is_4s == 1:
                size = 30
            elif is_6s == 1:
                size = 45
            elif is_batwkts == 1:
                size = 80

            ax.scatter(x_mapped, y_mapped, marker='o', edgecolors='black', facecolors='none', s=size, alpha=0.1)
            ax.axis('off')

            x_idx = np.digitize(x_mapped, xedges) - 1
            y_idx = np.digitize(y_mapped, yedges) - 1

            if 0 <= x_idx < len(xedges) - 1 and 0 <= y_idx < len(yedges) - 1:
                runs = int(is_1s + is_2s * 2 + is_3s * 3 + is_4s * 4 + is_6s * 6)
                grid_runs_balls[x_idx, y_idx]['runs'] += runs
                grid_runs_balls[x_idx, y_idx]['balls'] += 1

        runs_in_box = np.array([[grid_runs_balls[i, j]['runs'] for j in range(len(yedges) - 1)] for i in range(len(xedges) - 1)])
        norm = mcolors.Normalize(vmin=runs_in_box.min(), vmax=runs_in_box.max())
        cmap = plt.cm.Reds

        for i in range(len(xedges) - 1):
            for j in range(len(yedges) - 1):
                runs_balls = grid_runs_balls[i, j]
                runs, balls = int(runs_balls['runs']), runs_balls['balls']
                if balls > 0:
                    color = cmap(norm(runs))
                    rect = plt.Rectangle((xedges[i], yedges[j]), xedges[i+1] - xedges[i], yedges[j+1] - yedges[j], color=color, alpha=0.3)
                    ax.add_patch(rect)
                    strike_rate = (runs / balls) * 100
                    ax.text((xedges[i] + xedges[i+1]) / 2, (yedges[j] + yedges[j+1]) / 2 - 5, f'{runs}({balls})', 
                            color='black', fontsize=8, ha='center', va='center')
                    ax.text((xedges[i] + xedges[i+1]) / 2, (yedges[j] + yedges[j+1]) / 2 + 10, f'{strike_rate:.1f}', 
                            color='black', fontsize=6, ha='center', va='center')

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        fig.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.036, pad=0.1, label='Number of Runs')

        ax.plot([352, 264], [160, 599], color='black', linewidth=1, alpha=0.2)
        ax.plot([718, 806], [160, 599], color='black', linewidth=1, alpha=0.2)
        ax.plot([352, 718], [160, 160], color='black', linewidth=1, alpha=0.2)

        additional_lines = [
            ((342, 206), (727, 206)),
            ((394, 184), (674, 184)),
            ((674, 205), (674, 166)),
            ((391, 205), (394, 166)),
            ((435, 205), (435, 185)),
            ((630, 205), (630, 185))
        ]
        for start, end in additional_lines:
            ax.plot([start[0], end[0]], [start[1], end[1]], color='black',alpha=0.3)

        st.pyplot(fig)

        # WagonWheel Visualization
        region_labels_rhb = ['Region 4', 'Region 3', 'Region 2', 'Region 1', 'Region 8', 'Region 7', 'Region 6', 'Region 5']
        region_labels_lhb = ['Region 1', 'Region 2', 'Region 3', 'Region 4', 'Region 5', 'Region 6', 'Region 7', 'Region 8']

        region_runs, total_runs, batting_type = calculate_runs_by_region(player_data_filtered, player_name)
        percentage_data = calculate_percentage(region_runs, total_runs)

        fig, ax = create_circle_with_regions(f'Wagon Region for {player_name}', 
                                             region_labels_rhb if batting_type == 'RHB' else region_labels_lhb, 
                                             percentage_data, 
                                             cmap_name='Reds',
                                             width=6,  # Set smaller width
                                             height=4)  # Set smaller height

        st.pyplot(fig, use_container_width=True)  # Display the plot in Streamlit

if __name__ == '__main__':
    main()
