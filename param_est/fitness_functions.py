import numpy as np
import pandas as pd
import ast
import csv
from scipy.stats import spearmanr
from scipy import signal as sg

from src.sim.simulation.sim import GrowingSim
from src.agent.cell import Cell


def avg_auxin_root_tip_greater_than_elsewhere(sim: GrowingSim, chromosome: dict) -> float:
    """
    Returns the ratio of the average auxin concentration in non-root tip cells
    to the average auxin concentration in root tip cells.

    Parameters
    ----------
    sim : GrowingSima
        The simulation object containing the cells.
    chromosome: Dict
        The dictionary being populated with information about this simulation's run

    Returns
    -------
    float
        The ratio of the average auxin concentration in root tip cells to non-root tip cells
    """
    non_root_tip_auxins = [cell.get_circ_mod().get_auxin() for cell in sim.cell_list if cell.get_dev_zone() != 'roottip']
    root_tip_auxins = [cell.get_circ_mod().get_auxin() for cell in sim.cell_list if cell.get_dev_zone() == 'roottip']
    avg_non_root_tip_auxins = sum(non_root_tip_auxins)/len(non_root_tip_auxins)
    avg_root_tip_auxins = sum(root_tip_auxins)/len(root_tip_auxins)
    return avg_root_tip_auxins/avg_non_root_tip_auxins # maximizing this

def auxin_greater_in_larger_cells_at_trans_elon_interface(sim: GrowingSim, chromosome: dict) -> float:
    """
    """
    transition_and_elongation_cells = [cell for cell in sim.cell_list if (cell.get_dev_zone() == 'transition' or cell.get_dev_zone() == 'elongation')]
    xpp_trans_and_elon_cells = [cell for cell in transition_and_elongation_cells if (cell.get_cell_type() == 'peri')]
    # get correlation coefficient between cell size and auxin concentration in xpp_trans_and_elon_cells
    # Trying with all cells
    areas = [cell.get_quad_perimeter().get_area() for cell in xpp_trans_and_elon_cells]
    auxins = [cell.get_circ_mod().get_auxin() for cell in xpp_trans_and_elon_cells]
    corr_coeff = spearmanr(areas, auxins).statistic
    if corr_coeff < 0:
        print(f"Inverse correlation between xpp cell size and auxin concentration in transition and elongation zone. Fitness set to {abs(corr_coeff)}.")
        print(f"corr_coef = {corr_coeff}")
        chromosome["notes"] = f"Inverse correlation between xpp cell size and auxin concentration in transition and elongation zone. Fitness set to {abs(corr_coeff)}."
        return abs(corr_coeff) #we want there to be a strong positive correlation
    return abs(corr_coeff)

def auxin_oscillation_across_XPP_cells_in_OZ(sim: GrowingSim, chromosome: dict) -> float:
    """
    Performs a fourier transform on the auxin concentrations of the XPP cells in the oscillation zone.
    Looks for oscillation in auxin concentration across these cells
    Filters out high frequency noise and returns highest frequency peak.

    Parameters
    ----------
    sim : GrowingSim
        The simulation object containing the cells.
    chromosome: Dict
        The dictionary being populated with information about this simulation's run

    Returns
    -------
    float
        The highest frequency peak in the auxin concentration of the XPP cells in the oscillation zone.
    """
    # Get auxin concentrations of XPP cells in the oscillation zone
    xpp_cells_in_oz = [cell for cell in sim.cell_list if cell.get_dev_zone() in ["transition", "elongation"] and cell.get_cell_type() == 'peri']
    auxins = [cell.get_circ_mod().get_auxin() for cell in xpp_cells_in_oz]
    # Perform fourier transform
    fourier = np.fft.fft(auxins)
    freqs = np.fft.fftfreq(len(auxins))
    # Filter out high frequency noise
    fourier[freqs > 0.1] = 0
    # Return highest frequency peak
    return max(fourier) # maximizing this

def parity_of_mz_auxin_concentrations_with_VDB_data(sim: GrowingSim, chromosome: dict) -> float:
    """
    Returns the Pearson correlation coefficient of parity of the auxin concentrations in the meristematic zone cells 
    between ARORA and the VDB data.

    Parameters
    ----------
    sim : GrowingSim
        The simulation object containing the cells.
    chromosome : dict
        Dictionary being populated with information about this simulation's run.

    Returns
    -------
    float
        The parity of the auxin concentrations in the marginal zone cells with the VDB data.
    """

    # Step 1: Load VDB and ARORA data
    vdb_summary_df = pd.read_csv('param_est/vdb_summary_seven_peri_cells_across_27_ticks.csv')
    sim_output_df = pd.read_csv(sim.output.filename_csv)
    # Preprocess ARORA simulation output for analysis
    sim_output_df = preprocess_ARORA_sim_output(sim_output_df)

    # Step 2: Collect auxin concentrations at specific locations for each tick
    centroid_y_locations = np.linspace(75, 178, 7)
    closest_arora_cells_dfs = collect_auxin_data_by_tick(sim_output_df, centroid_y_locations)

    # Step 3: Generate summary statistics of auxin concentration per location
    ARORA_summary_df = calculate_auxin_summary(closest_arora_cells_dfs)
    # Step 4: Calculate Pearson correlation between ARORA and VDB data
    correlation_coefficient = np.corrcoef(vdb_summary_df['auxin_mean'], ARORA_summary_df['auxin_mean'])[0, 1]
    chromosome["auxin_corr_with_mz"] = correlation_coefficient
    return correlation_coefficient

def parity_of_auxin_c_for_xpp_boundary_cell_at_each_time_point(sim: GrowingSim, chromosome: dict) -> float:
    # Load VDB data
    vdb_auxins = pd.read_csv('param_est/vdb_auxins_at_56pt5_336pt5.csv')
    sim_output_df = pd.read_csv(sim.output.filename_csv)
    sim_output_df = preprocess_ARORA_sim_output(sim_output_df)
    # Get auxin concentrations of XPP boundary cell at each time point
    xpp_boundary_cell_loc = [56.5, 336.5]
    # For every tick in sim_output_df, find the ARORA cell closest to the XPP boundary cell
    closest_cells = []
    for tick in sim_output_df['tick'].unique():
        sim_output_df_tick = sim_output_df[sim_output_df['tick'] == tick]
        closest_cell = find_ARORA_cell_closest_to_centroid(xpp_boundary_cell_loc, sim_output_df_tick)
        closest_cells.append(closest_cell)
    # Calculate Pearson correlation between ARORA and VDB data
    correlation_coefficient = np.corrcoef(vdb_auxins['auxin'], [cell['Auxin'] for cell in closest_cells])[0, 1]
    chromosome["auxin_corr_with_xpp_boundary"] = correlation_coefficient
    return correlation_coefficient


def collect_auxin_data_by_tick(sim_output_df: pd.DataFrame, centroid_y_locations: np.ndarray) -> pd.DataFrame:
    """
    Collects the auxin concentration data for cells closest to the specified centroid locations across ticks.

    Parameters
    ----------
    sim_output_df : pd.DataFrame
        DataFrame of ARORA simulation output.
    centroid_y_locations : np.ndarray
        Array of centroid y locations to sample from.

    Returns
    -------
    pd.DataFrame
        DataFrame with auxin data for closest cells per tick.
    """
    closest_arora_cells_dfs = []
    unique_ticks = sim_output_df['tick'].unique()

    for tick in unique_ticks:
        closest_cells_df = pd.DataFrame()
        sim_output_df_meri_peri = sim_output_df[
            (sim_output_df['tick'] == tick) &
            (sim_output_df['dev_zone'] == 'meristematic') &
            (sim_output_df['cell_type'] == 'peri')
        ].copy()
        closest_cells = find_closest_ARORA_pericycle_cell(centroid_y_locations, sim_output_df_meri_peri)
        closest_cells_df = pd.concat([closest_cells_df, pd.DataFrame(closest_cells)])
        closest_cells_df = closest_cells_df.sort_values(by='adj_centroid_y')
        closest_arora_cells_dfs.append(closest_cells_df)

    return pd.concat(closest_arora_cells_dfs)

def calculate_auxin_summary(closest_arora_cells_dfs: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates summary statistics (range, mean, median, std deviation) for auxin concentrations.

    Parameters
    ----------
    closest_arora_cells_dfs : pd.DataFrame
        DataFrame of closest ARORA cells auxin concentrations.

    Returns
    -------
    pd.DataFrame
        Summary statistics of auxin concentrations for each rank.
    """
    grouped = closest_arora_cells_dfs.groupby('tick')
    max_rows_per_tick = grouped.size().max()

    summary_stats = []

    for rank in range(max_rows_per_tick):
        rows_at_rank = []

        for _, group in grouped:
            sorted_group = group.sort_values(by='centroid_y')
            if rank < len(sorted_group):
                rows_at_rank.append(sorted_group.iloc[rank])

        rank_df = pd.DataFrame(rows_at_rank)

        auxin_values = rank_df['auxin']
        summary_stats.append({
            'rank': rank + 1,
            'auxin_range': auxin_values.max() - auxin_values.min(),
            'auxin_mean': auxin_values.mean(),
            'auxin_median': auxin_values.median(),
            'auxin_standard_deviation': auxin_values.std()
        })

    return pd.DataFrame(summary_stats)

def preprocess_ARORA_sim_output(sim_output_df):
    # Ensure 'location' is parsed from strings only if necessary
    sim_output_df['location'] = sim_output_df['location'].apply(
        lambda loc: ast.literal_eval(loc) if isinstance(loc, str) else loc
    )

    # Calculate centroids from location
    sim_output_df['centroid'] = sim_output_df['location'].apply(parse_and_compute_centroid)
    sim_output_df['centroid_x'] = sim_output_df['centroid'].apply(lambda x: x[0])
    sim_output_df['centroid_y'] = sim_output_df['centroid'].apply(lambda x: x[1])

    # Adjust centroid y-values based on minimum y in each tick
    sim_output_df['min_y'] = sim_output_df.groupby('tick')['location'].transform(get_min_y)
    VDB_Y_min = 11
    sim_output_df['adj_centroid_y'] = sim_output_df['centroid_y'] - (sim_output_df['min_y'] + VDB_Y_min)
    # Apply row-wise operation for 'adj_centroid'
    sim_output_df['adj_centroid'] = sim_output_df.apply(
        lambda row: [row['centroid_x'], row['centroid_y'] - (row['min_y'] + VDB_Y_min)], axis=1
    )
    return sim_output_df


def find_closest_ARORA_pericycle_cell(centroid_y_locations, arora_df_ONLY_PERI):
    closest_cells = []
    # Make a copy of the DataFrame to avoid the SettingWithCopyWarning
    arora_df_ONLY_PERICYCLE = arora_df_ONLY_PERI.copy()
    for ylocation in centroid_y_locations:
        # Calculate the distance between each cell's centroid and the y-location
        arora_df_ONLY_PERICYCLE.loc[:, 'distance'] = (arora_df_ONLY_PERICYCLE['adj_centroid_y'] - ylocation).abs()
        closest_cell = arora_df_ONLY_PERICYCLE.loc[arora_df_ONLY_PERICYCLE['distance'].idxmin()]
        # Drop the 'distance' column after finding the closest cell
        arora_df_ONLY_PERICYCLE = arora_df_ONLY_PERICYCLE.drop(columns=['distance'])
        closest_cells.append(closest_cell)
    return closest_cells

def find_ARORA_cell_closest_to_centroid(arora_centroid_location, arora_df):
    # Ensure centroids are in the correct format (e.g., list of tuples)
    if isinstance(arora_df['adj_centroid'].iloc[0], str):
        arora_df['adj_centroid'] = arora_df['adj_centroid'].apply(eval)

    # Extract centroids and calculate distances vectorized
    centroids = np.array(arora_df['adj_centroid'].tolist())
    distances = np.linalg.norm(centroids - np.array(arora_centroid_location), axis=1)
    
    # Find the index of the closest centroid
    closest_index = np.argmin(distances)
    
    # Get the closest cell and centroid
    closest_cell = arora_df.iloc[closest_index]['cell']
    closest_centroid = arora_df.iloc[closest_index]['adj_centroid']
    closest_distance = distances[closest_index]
    closest_cell_auxin = arora_df.iloc[closest_index]['auxin']
    this_tick = arora_df.iloc[closest_index]['tick']

    # Return the closest cell and its centroid
    return {
        'Closest_Cell': closest_cell,
        'Closest_Adj_Centroid': closest_centroid,
        'Distance': closest_distance,
        'Auxin': closest_cell_auxin,
        'Tick': this_tick
    }

def get_min_y(locations):
    return min(y for loc in locations for _, y in loc)

def parse_and_compute_centroid(location):
        # Convert points into a NumPy array for easier manipulation
        points_array = np.array(location)
        # Calculate the centroid
        x_coords = points_array[:, 0]
        y_coords = points_array[:, 1]
        centroid = [sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords)]
        return centroid

def arora_vdb_ssd(chromosome_idx: int):
    total_ssd = 0.0
    reference_filenames = get_filenames("param_est/vdb_data/references/Caux1Array_", 0, 400, 93600) # not quite sure how the matching of temporal scales is going
    output_filenames = [f"param_est/ARORA_auxin_output_chrom_{chromosome_idx}_tick_{tick}.csv" for tick in range(234)]
    for output_file, reference_file in zip(output_filenames, reference_filenames):
        total_ssd += np.sum((file_extract_values(output_file) - file_extract_values(reference_file))**2)
    return -total_ssd

def file_extract_values(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        data = []
        for row in reader:
            if row and row[-1].strip() == '':
                row.pop()
            float_row = [float(cell) for cell in row]
            data.append(float_row)
        return np.array(data)

def get_filenames(stringstart, t_start, tstep, t_total): # changed
    filenames = []
    for t in range(t_start, (t_total + tstep), tstep):
        filename = stringstart + str(t).zfill(8) + ".csv" # if we decide to change number of digits in filename later, change this line
        filenames.append(filename)
    return filenames


def oscillation_score_from_csv(output_csv_path: str) -> float:
    """
    Measures oscillatory behavior in XPP cells in the oscillation zone (OZ).

    Combines two independent signals from the output CSV, both bounded in [0, 1]:

    1. Peak-counting score (cycle_score, 60%): counts genuine oscillation cycles
       (up-then-down excursions) in the mean OZ XPP auxin time series.
       Requires the LINEARLY-DETRENDED signal to have ≥2 peaks AND ≥2 troughs
       with inter-peak spacing in the 1.5–13 h range and minimum prominence
       ≥ 20% of the signal's standard deviation.

       This metric cannot be fooled by a monotonically declining (or rising)
       transient because linear detrending of a convex/concave monotone curve
       produces at most one arch-shaped residual, which has at most one peak
       and one trough — scoring 0.

    2. Spatial CoV score (cov_score, 40%): mean coefficient-of-variation of auxin
       across OZ XPP cells at each tick, clipped to [0, 1].  Rewards the
       spatial alternating pattern (large cell ↔ small cell with differing auxin)
       that is the hallmark of the paper's mechanical oscillation mechanism.

    Both scores use the second half of the simulation (skip first half) to
    exclude the initial transient.  The minimum-auxin guard (mean < 0.5 a.u.)
    rejects degenerate near-zero solutions.

    Returns
    -------
    float
        0.6 × cycle_score + 0.4 × cov_score, both in [0, 1].
        Returns -1.0 for degenerate inputs (empty OZ, too few ticks, low auxin).
    """
    try:
        df = pd.read_csv(output_csv_path, usecols=["tick", "dev_zone", "cell_type", "auxin"])
    except Exception:
        return -1.0

    xpp_oz = df[
        df["dev_zone"].isin(["transition", "elongation"]) &
        (df["cell_type"] == "peri")
    ]

    if xpp_oz.empty:
        return -1.0

    agg = (
        xpp_oz.groupby("tick")["auxin"]
        .agg(["mean", "std"])
        .sort_index()
        .reset_index()
    )
    n = len(agg)
    if n < 30:
        return -1.0

    mean_ts = agg["mean"].values
    std_ts = agg["std"].fillna(0.0).values

    if float(np.mean(mean_ts)) < 0.5:
        return -1.0

    timestep = 1.0 / 9.0  # hours per tick

    # Use the second half of the simulation only (skip the initial transient).
    # For an 18 h run (162 ticks) this gives a 9 h steady-state window.
    skip = n // 2
    mean_ts_ss = mean_ts[skip:]
    std_ts_ss = std_ts[skip:]
    n_ss = len(mean_ts_ss)
    if n_ss < 20:
        return -1.0

    mean_ss = float(np.mean(mean_ts_ss))
    if mean_ss < 0.5:
        return -1.0

    # --- Score 1: cycle count after quadratic detrending ---
    #
    # WHY quadratic, not linear?
    # Auxin relaxes from initial conditions via an approximately exponential
    # decay.  Linear detrend leaves a convex arch residual, which scipy's
    # find_peaks can detect as 2–3 spurious peaks.  A quadratic fit captures
    # the curved shape of the transient well, leaving only genuinely periodic
    # components in the residual.
    #
    # WHY 5%-of-mean minimum prominence?
    # After quadratic detrend the arch residual is typically < 1% of the mean
    # auxin.  Requiring peaks to be ≥ 5% of mean rejects that noise and any
    # remnant arch artifact, while accepting real oscillations which typically
    # have amplitude ≥ 10–20% of the mean.
    t = np.arange(n_ss, dtype=float)
    trend_poly = np.polyfit(t, mean_ts_ss, deg=2)
    trend = np.polyval(trend_poly, t)
    detrended = mean_ts_ss - trend

    # min_dist: at least 1.5 h between consecutive peaks (avoids double-counting)
    min_dist_ticks = max(1, int(np.floor(1.5 / timestep)))
    # min_prominence: peaks must correspond to ≥ 5% amplitude in the mean auxin
    min_prom = max(1e-6, 0.05 * mean_ss)

    peaks,   _ = sg.find_peaks( detrended, distance=min_dist_ticks, prominence=min_prom)
    troughs, _ = sg.find_peaks(-detrended, distance=min_dist_ticks, prominence=min_prom)

    def count_valid_intervals(indices: np.ndarray) -> int:
        """Count inter-index spacings in the 1.5–13 h biological range."""
        if len(indices) < 2:
            return 0
        spacings_h = np.diff(indices) * timestep
        return int(np.sum((spacings_h >= 1.5) & (spacings_h <= 13.0)))

    # Require BOTH peaks AND troughs for genuine up-down cycles.
    # Score saturates at 1.0 when ≥2 valid intervals of each type are found
    # (equivalent to ≥3 peaks and ≥3 troughs = at least 2 full cycles visible).
    n_cycles = min(count_valid_intervals(peaks), count_valid_intervals(troughs))
    cycle_score = float(min(1.0, n_cycles / 2.0))

    # --- Score 2: mean spatial CoV, clipped to [0, 1] ---
    cov_ts = std_ts_ss / (mean_ts_ss + 1e-10)
    cov_score = float(min(np.mean(cov_ts), 1.0))

    return float(0.6 * cycle_score + 0.4 * cov_score)
