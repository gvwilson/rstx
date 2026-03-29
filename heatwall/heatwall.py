import numpy as np
import polars as pl
import altair as alt

# mccole: constants
# Three-layer composite wall: brick | mineral wool insulation | concrete
LAYER_WIDTHS = [0.10, 0.05, 0.15]  # layer thicknesses (m)
LAYER_K = [0.72, 0.04, 1.20]  # thermal conductivities (W m⁻¹ K⁻¹)
LAYER_NAMES = ["brick", "insulation", "concrete"]
T_LEFT = 20.0  # inner-surface temperature (°C)
T_RIGHT = -10.0  # outer-surface temperature (°C)

# N_PER_LAYER cells per layer.  More cells → smaller discretisation error.
# 20 cells per layer is sufficient to recover the exact piecewise-linear solution
# of the steady-state heat equation to numerical-precision.
N_PER_LAYER = 20

# Convergence tolerance for Jacobi iteration: iteration stops when the maximum
# change in any nodal temperature between successive sweeps falls below this value.
# 1e-6 °C is well below measurement precision for building physics calculations.
TOLERANCE = 1e-6
# mccole: /constants


# mccole: grid
def build_grid(widths=LAYER_WIDTHS, conductivities=LAYER_K, n_per_layer=N_PER_LAYER):
    """Return (x, k_seg) for a node-centred composite-wall grid.

    x      : positions of all nodes (m); length n_layers * n_per_layer + 1
    k_seg  : conductivity of the segment to the RIGHT of each node (W m⁻¹ K⁻¹);
             length n_layers * n_per_layer (one per inter-node gap)

    Each layer is divided into n_per_layer equal cells.  The rightmost node of
    one layer is shared with the leftmost node of the next, so interface nodes
    appear exactly once.  Every segment between adjacent nodes lies entirely
    inside one material, so no harmonic-mean formula is needed.
    """
    x_parts, k_seg = [], []
    x_start = 0.0
    for i, (width, kval) in enumerate(zip(widths, conductivities)):
        xs = np.linspace(x_start, x_start + width, n_per_layer + 1)
        # Skip the first node for all but the first layer to avoid duplication.
        x_parts.append(xs if i == 0 else xs[1:])
        # Each of the n_per_layer segments inside this layer has conductivity kval.
        k_seg.extend([kval] * n_per_layer)
        x_start += width
    return np.concatenate(x_parts), np.array(k_seg)
# mccole: /grid


# mccole: jacobi
def jacobi_solve(x, k_seg, t_left=T_LEFT, t_right=T_RIGHT, tolerance=TOLERANCE):
    """Solve for steady-state temperatures using Jacobi (relaxation) iteration.

    Starting from a linear temperature profile as an initial guess, each interior
    node i is updated to the value that balances the heat fluxes on both sides.
    The steady-state heat balance at node i is:

        k[i-1] * (T[i-1] - T[i]) / dx_left + k[i] * (T[i+1] - T[i]) / dx_right = 0

    Solving for T[i] gives a weighted average of the two neighbours:

        a = k[i-1] / dx_left    (weight for left neighbour)
        b = k[i]   / dx_right   (weight for right neighbour)
        T_new[i] = (a * T[i-1] + b * T[i+1]) / (a + b)

    The weights combine both the conductivity and the node spacing so that the
    update is correct even when segments in different layers have different lengths.

    Iteration continues until max(|T_new - T_old|) < tolerance.
    Boundary nodes are fixed throughout (Dirichlet conditions).

    Returns (T, n_iters) — the converged temperature array and the number of
    iterations taken.
    """
    n = len(x)
    # Linear profile as starting guess: physically reasonable and reduces
    # the number of iterations needed compared with a flat (uniform) guess.
    T = np.linspace(t_left, t_right, n)

    n_iters = 0
    while True:
        T_new = T.copy()
        for i in range(1, n - 1):
            dx_left = x[i] - x[i - 1]
            dx_right = x[i + 1] - x[i]
            a = k_seg[i - 1] / dx_left   # conductivity of segment [i-1, i]
            b = k_seg[i] / dx_right      # conductivity of segment [i, i+1]
            T_new[i] = (a * T[i - 1] + b * T[i + 1]) / (a + b)
        n_iters += 1
        if np.max(np.abs(T_new - T)) < tolerance:
            return T_new, n_iters
        T = T_new
# mccole: /jacobi


# mccole: solve
def solve_temperatures(
    widths=LAYER_WIDTHS,
    conductivities=LAYER_K,
    t_left=T_LEFT,
    t_right=T_RIGHT,
    n_per_layer=N_PER_LAYER,
):
    """Return (x, T) — grid positions and steady-state temperatures (°C)."""
    x, k_seg = build_grid(widths, conductivities, n_per_layer)
    T, _ = jacobi_solve(x, k_seg, t_left, t_right)
    return x, T
# mccole: /solve


# mccole: snapshots
def convergence_snapshots(
    x, k_seg, t_left=T_LEFT, t_right=T_RIGHT, snap_iters=(0, 10, 100)
):
    """Return a list of (iteration_label, T_array) pairs at selected iterations.

    The last entry is always the converged solution, labelled "converged".
    snap_iters lists the intermediate iteration counts to capture.
    """
    n = len(x)
    T = np.linspace(t_left, t_right, n)
    records = []
    snap_set = set(snap_iters)
    if 0 in snap_set:
        records.append(("0", T.copy()))

    n_iters = 0
    while True:
        T_new = T.copy()
        for i in range(1, n - 1):
            dx_left = x[i] - x[i - 1]
            dx_right = x[i + 1] - x[i]
            a = k_seg[i - 1] / dx_left
            b = k_seg[i] / dx_right
            T_new[i] = (a * T[i - 1] + b * T[i + 1]) / (a + b)
        n_iters += 1
        converged = np.max(np.abs(T_new - T)) < TOLERANCE
        T = T_new
        if n_iters in snap_set:
            records.append((str(n_iters), T.copy()))
        if converged:
            records.append(("converged", T.copy()))
            return records
# mccole: /snapshots


# mccole: flux
def layer_heat_flux(x, T, k_seg, widths=LAYER_WIDTHS):
    """Return the heat flux (W m⁻²) in each layer.

    Flux in segment j: q_j = -k_seg[j] * (T[j+1] - T[j]) / (x[j+1] - x[j]).
    In steady state q is constant everywhere; averaging over each layer's
    segments reduces discretisation noise near boundaries.
    """
    fluxes = []
    x_start = 0.0
    seg = 0  # running segment index
    for width, kval in zip(widths, LAYER_K):
        x_end = x_start + width
        layer_q = []
        while seg < len(k_seg) and x[seg + 1] <= x_end + 1e-12:
            q = -k_seg[seg] * (T[seg + 1] - T[seg]) / (x[seg + 1] - x[seg])
            layer_q.append(q)
            seg += 1
        fluxes.append(float(np.mean(layer_q)))
        x_start = x_end
    return np.array(fluxes)
# mccole: /flux


# mccole: analytic
def analytic_solution(
    widths=LAYER_WIDTHS, conductivities=LAYER_K, t_left=T_LEFT, t_right=T_RIGHT
):
    """Exact steady-state solution via thermal resistance.

    For a composite wall the total thermal resistance is:

        R_total = sum_i ( L_i / k_i )   (m² K W⁻¹)

    and the uniform heat flux is:

        q = (T_left - T_right) / R_total   (W m⁻²)

    The temperature at each layer interface follows from subtracting q * R_i
    in sequence from T_left.
    """
    resistances = [w / k for w, k in zip(widths, conductivities)]
    r_total = sum(resistances)
    q = (t_left - t_right) / r_total
    interface_temps = [t_left]
    for r in resistances:
        interface_temps.append(interface_temps[-1] - q * r)
    return q, resistances, interface_temps
# mccole: /analytic


# mccole: plot
def plot_profile(
    x, T, widths=LAYER_WIDTHS, layer_names=LAYER_NAMES, filename="heatwall.svg"
):
    """Save an Altair line chart of the temperature profile."""
    df = pl.DataFrame({"x": x, "T": T})

    profile = (
        alt.Chart(df)
        .mark_line(color="firebrick", strokeWidth=2)
        .encode(
            x=alt.X("x:Q", title="Position (m)"),
            y=alt.Y("T:Q", title="Temperature (°C)"),
        )
    )

    boundaries = np.cumsum([0.0] + list(widths[:-1]))
    bound_df = pl.DataFrame({"x": boundaries.tolist()})
    rules = (
        alt.Chart(bound_df)
        .mark_rule(color="grey", strokeDash=[4, 2], strokeWidth=1)
        .encode(x="x:Q")
    )

    (rules + profile).properties(width=480, height=280).save(filename)
# mccole: /plot


# mccole: plot_convergence
def plot_convergence(
    x, records, widths=LAYER_WIDTHS, filename="heatwall_convergence.svg"
):
    """Save an Altair chart showing temperature profiles at selected iterations.

    records is a list of (label, T_array) pairs as returned by convergence_snapshots.
    """
    rows = []
    for label, T in records:
        for xi, Ti in zip(x, T):
            rows.append({"x": xi, "T": Ti, "iteration": label})
    df = pl.DataFrame(rows)

    profiles = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("x:Q", title="Position (m)"),
            y=alt.Y("T:Q", title="Temperature (°C)"),
            color=alt.Color("iteration:N", title="Iteration"),
        )
    )

    boundaries = np.cumsum([0.0] + list(widths[:-1]))
    bound_df = pl.DataFrame({"x": boundaries.tolist()})
    rules = (
        alt.Chart(bound_df)
        .mark_rule(color="grey", strokeDash=[4, 2], strokeWidth=1)
        .encode(x="x:Q")
    )

    (rules + profiles).properties(width=480, height=280).save(filename)
# mccole: /plot_convergence


if __name__ == "__main__":
    x, k_seg = build_grid()
    T, n_iters = jacobi_solve(x, k_seg)
    print(f"Grid nodes: {len(x)}")
    print(f"Converged in {n_iters} iterations")
    print(f"T at left wall:  {T[0]:.4f}°C  (expected {T_LEFT})")
    print(f"T at right wall: {T[-1]:.4f}°C  (expected {T_RIGHT})")

    fluxes = layer_heat_flux(x, T, k_seg)
    q_analytic, resistances, interface_temps = analytic_solution()
    print(f"\nAnalytic heat flux: {q_analytic:.4f} W/m²")
    for name, q in zip(LAYER_NAMES, fluxes):
        print(f"  {name}: {q:.4f} W/m²")
    print("Interface temperatures (analytic):", [f"{t:.4f}°C" for t in interface_temps])

    plot_profile(x, T, filename="heatwall.svg")
    print("\nSaved heatwall.svg")

    records = convergence_snapshots(x, k_seg)
    plot_convergence(x, records, filename="heatwall_convergence.svg")
    print("Saved heatwall_convergence.svg")
