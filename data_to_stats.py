import pandas as pd
from dataclasses import dataclass 
import math
import numpy as np

SAMPLES_PER_BUFFER = 50 
WINDOW_SIZE = 20
STRIDE = 10
NUM_STATS = 14

ALPHA = 0.2
overall_ema_x = 0.0
overall_ema_y = 0.0
overall_ema_z = 0.0
is_initalized = False

@dataclass
class Sample:
    x: float
    y: float
    z: float

def ema(raw_x, raw_y, raw_z):
    global is_initalized, overall_ema_x, overall_ema_y, overall_ema_z
    if not is_initalized:
        overall_ema_x = float(raw_x)
        overall_ema_y = float(raw_y)
        overall_ema_z = float(raw_z)
        is_initalized = True
    else:
        overall_ema_x = (ALPHA * raw_x) + ((1.0 - ALPHA) * overall_ema_x)
        overall_ema_y = (ALPHA * raw_y) + ((1.0 - ALPHA) * overall_ema_y)
        overall_ema_z = (ALPHA * raw_z) + ((1.0 - ALPHA) * overall_ema_z)
    
    return [overall_ema_x, overall_ema_y, overall_ema_z]

def create_windows_per_row(row):
    windows = []
    start = 0
    stop = WINDOW_SIZE
    for _ in range(4):
        new_window = []
        for i in range(start, stop):
            x_val = row[f"X_{i}"]
            y_val = row[f"Y_{i}"]
            z_val = row[f"Z_{i}"]

            sample = Sample(x_val, y_val, z_val)
            new_window.append(sample)

        start += STRIDE
        stop += STRIDE

        windows.append(new_window)

    return windows

def compute_stats_for_window(window):
    total_x: float = 0.0
    total_y: float = 0.0
    total_z: float = 0.0
    total_dvm: float = 0.0   

    x_min: float
    y_min: float
    z_min: float
    x_min, y_min, z_min = [1.0e9] * 3

    x_max: float
    y_max: float
    z_max: float
    dvm_max: float
    x_max, y_max, z_max, dvm_max = [-1.0e9] * 4

    for i in range(WINDOW_SIZE):
        s = window[i]
        x = s.x
        y = s.y
        z = s.z

        total_x += x
        total_y += y
        total_z += z

        dvm = math.sqrt(x*x + y*y + z*z)
        total_dvm += dvm

        x_min = min(x, x_min)
        x_max = max(x, x_max)

        y_min = min(y, y_min)
        y_max = max(y, y_max)

        z_min = min(z, z_min)
        z_max = max(z, z_max)

        dvm_max = max(dvm, dvm_max)
    
    x_mean: float
    y_mean: float
    z_mean: float
    dvm_mean: float
    x_mean = y_mean = z_mean = dvm_mean = 0.0

    x_mean = total_x / WINDOW_SIZE
    y_mean = total_y / WINDOW_SIZE
    z_mean = total_z / WINDOW_SIZE
    dvm_mean = total_dvm / WINDOW_SIZE

    # get the covariances
    cov_xy_sum: float
    cov_yz_sum: float
    cov_xz_sum: float 
    cov_xy_sum = cov_yz_sum = cov_xz_sum = 0.0

    for i in range(WINDOW_SIZE):
        dx: float = window[i].x - x_mean
        dy: float = window[i].y - y_mean
        dz: float = window[i].z - z_mean

        cov_xy_sum += dx * dy
        cov_yz_sum += dy * dz
        cov_xz_sum += dx * dz

    cov_xy = cov_xy_sum / WINDOW_SIZE
    cov_yz = cov_yz_sum / WINDOW_SIZE
    cov_xz = cov_xz_sum / WINDOW_SIZE

    # contruct array of stats
    stats_summary: list[float] = [x_mean, y_mean, z_mean, dvm_mean,
                    x_min, y_min, z_min,
                    x_max, y_max, z_max, dvm_max,
                    cov_xy, cov_yz, cov_xz]

    return stats_summary

def process_df_to_stats(df: pd.DataFrame):
    columns = [
        'x_mean', 'y_mean', 'z_mean', 'dvm_mean',
        'x_min', 'y_min', 'z_min',
        'x_max', 'y_max', 'z_max', 'dvm_max',
        'cov_xy', 'cov_yz', 'cov_xz',
        'gesture_id'
    ]
    n_rows = len(df)
    rows_list = []

    for row_i in range(n_rows):
        row = df.iloc[row_i]
        windows = create_windows_per_row(row)
        gesture_id = df.iloc[row_i]['gesture_id']
        for win in windows:
            stats = compute_stats_for_window(win)
            new_row = {
                'x_mean': float(stats[0]),
                'y_mean': float(stats[1]),
                'z_mean': float(stats[2]),
                'dvm_mean': float(stats[3]),
                'x_min': float(stats[4]),
                'y_min': float(stats[5]),
                'z_min': float(stats[6]),
                'x_max': float(stats[7]),
                'y_max': float(stats[8]),
                'z_max': float(stats[9]),
                'dvm_max': float(stats[10]),
                'cov_xy': float(stats[11]),
                'cov_yz': float(stats[12]),
                'cov_xz': float(stats[13]),
                'gesture_id': gesture_id
            }
            rows_list.append(new_row)
    
    if rows_list:
        new_df = pd.DataFrame(rows_list, columns=columns)
    else:
        new_df = pd.DataFrame(columns=columns)

    return new_df

# runs ema pass on the old df
def process_raw_data(df, output_filename='processed_gesture_dataset.csv'):
    features = df.iloc[:, :-1].to_numpy()
    labels = df.iloc[:,-1].values

    n_cols = (features.shape[1] // 3) * 3
    triplets = features[:, :n_cols].reshape(features.shape[0], -1, 3)

    processed_rows = []

    for row_idx in range(len(df)):
        smoothed_row = []

        global is_initalized
        is_initalized = False
        for block in triplets[row_idx]:
            x, y, z = block[0], block[1], block[2]
            smoothed_xyz = ema(x, y, z)
            smoothed_row.extend(smoothed_xyz)

        smoothed_row.append(labels[row_idx])
        processed_rows.append(smoothed_row)

    num_triplets = triplets.shape[1]
    col_names = []
    for i in range(num_triplets):
        col_names.extend([f"X_{i}", f"Y_{i}", f"Z_{i}"])
    col_names.append("gesture_id")

    # export to csv
    processed_df = pd.DataFrame(processed_rows, columns=col_names)
    processed_df.to_csv(output_filename, index=False)

    return processed_df

def debug_func(df, row_i):
    # prints out the summary stats for a singular row
    row = df.iloc[row_i]
    wins = create_windows_per_row(row)

    for win in wins:
        stats = compute_stats_for_window(win)     
        print(stats)
        print("\n")

# old_df = pd.read_csv('gesture_dataset.csv')
# df = process_raw_data(old_df)

if __name__ == "__main__":
    df = pd.read_csv('processed_gesture_dataset.csv')
    debug_func(df, 0)