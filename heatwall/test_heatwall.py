import numpy as np
import pytest
from heatwall import (
    build_grid,
    jacobi_solve,
    solve_temperatures,
    layer_heat_flux,
    analytic_solution,
    LAYER_WIDTHS,
    T_LEFT,
    T_RIGHT,
    N_PER_LAYER,
    TOLERANCE,
)


def test_grid_node_count():
    # Each layer contributes N_PER_LAYER cells and shares boundary nodes,
    # giving n_layers * N_PER_LAYER + 1 nodes total.
    x, k_seg = build_grid()
    n_layers = len(LAYER_WIDTHS)
    assert len(x) == n_layers * N_PER_LAYER + 1
    assert len(k_seg) == n_layers * N_PER_LAYER


def test_grid_covers_full_wall():
    # First node must be at x=0; last at the total wall thickness.
    x, _ = build_grid()
    assert x[0] == pytest.approx(0.0)
    assert x[-1] == pytest.approx(sum(LAYER_WIDTHS), rel=1e-10)


def test_boundary_temperatures_enforced():
    # The solver must return exactly T_LEFT and T_RIGHT at the two wall surfaces.
    x, T = solve_temperatures()
    assert T[0] == pytest.approx(T_LEFT, abs=1e-10)
    assert T[-1] == pytest.approx(T_RIGHT, abs=1e-10)


def test_single_layer_is_linear():
    # For a single uniform layer the steady-state profile is exactly linear.
    # Jacobi iteration on a uniform grid with equal conductivities converges to
    # the linear profile because each node settles at the mean of its two neighbours,
    # which is the discrete condition for linearity.
    x, T = solve_temperatures(widths=[0.10], conductivities=[0.72])
    T_exact = np.linspace(T_LEFT, T_RIGHT, len(x))
    # Jacobi converges to within TOLERANCE per node; max error across all nodes
    # is bounded by a small multiple of TOLERANCE for a linear profile.
    assert np.allclose(T, T_exact, atol=100 * TOLERANCE)


def test_convergence_is_reached():
    # After jacobi_solve returns, the maximum change between one more sweep and
    # the returned solution must be below TOLERANCE, confirming convergence.
    x, k_seg = build_grid()
    T, _ = jacobi_solve(x, k_seg)
    n = len(x)
    T_check = T.copy()
    for i in range(1, n - 1):
        dx_left = x[i] - x[i - 1]
        dx_right = x[i + 1] - x[i]
        a = k_seg[i - 1] / dx_left
        b = k_seg[i] / dx_right
        T_check[i] = (a * T[i - 1] + b * T[i + 1]) / (a + b)
    assert np.max(np.abs(T_check - T)) < TOLERANCE


def test_flux_constant_across_layers():
    # In steady state q = -k dT/dx is uniform throughout the wall.
    # All per-layer flux averages must match the analytic value within 1%.
    x, T = solve_temperatures()
    _, k_seg = build_grid()
    fluxes = layer_heat_flux(x, T, k_seg)
    q_analytic, _, _ = analytic_solution()
    assert np.allclose(fluxes, q_analytic, rtol=0.01), (
        f"Layer fluxes {np.round(fluxes, 4)} not all close to analytic {q_analytic:.4f} W/m²"
    )


def test_numeric_matches_analytic_flux():
    # Mean numerical flux must match the analytic value to within 0.1%.
    x, T = solve_temperatures()
    _, k_seg = build_grid()
    fluxes = layer_heat_flux(x, T, k_seg)
    q_analytic, _, _ = analytic_solution()
    assert abs(fluxes.mean() - q_analytic) / abs(q_analytic) < 0.001


def test_numeric_matches_analytic_interface_temps():
    # Numerically solved temperatures at layer interfaces must match the
    # analytic values.  The tolerance of 1e-3 °C is conservative: Jacobi
    # iteration converges to within TOLERANCE (1e-6) per node, and the small
    # remaining error at interface nodes is dominated by the finite node spacing
    # rather than iteration error.  Any deviation larger than 1e-3 °C indicates
    # a conductivity-assignment or grid-construction bug.
    x, T_numeric = solve_temperatures()
    _, _, interface_temps = analytic_solution()
    x_interfaces = np.cumsum([0.0] + LAYER_WIDTHS)
    for x_iface, T_analytic in zip(x_interfaces, interface_temps):
        j = np.argmin(np.abs(x - x_iface))
        assert abs(T_numeric[j] - T_analytic) < 1e-3, (
            f"At x={x_iface:.3f} m: numeric {T_numeric[j]:.6f}°C, "
            f"analytic {T_analytic:.6f}°C"
        )


def test_higher_flux_for_larger_delta_T():
    # Doubling the temperature difference must double the heat flux (linearity).
    q1, _, _ = analytic_solution(t_left=20.0, t_right=-10.0)
    q2, _, _ = analytic_solution(t_left=40.0, t_right=-20.0)
    assert q2 == pytest.approx(2.0 * q1, rel=1e-6)


def test_flux_continuity_at_interfaces():
    # At every layer interface, heat flux continuity requires:
    #   k_left * dT/dx_left = k_right * dT/dx_right
    # We check this for the brick-insulation and insulation-concrete interfaces
    # by computing the flux in the last segment of the left layer and the first
    # segment of the right layer; they must agree within 1% of the analytic flux.
    x, T = solve_temperatures()
    _, k_seg = build_grid()
    q_analytic, _, _ = analytic_solution()

    # Segment indices at each interface: the last segment of layer l ends at
    # the interface node; segment index = cumulative N_PER_LAYER across layers.
    layer_seg_counts = [N_PER_LAYER] * len(LAYER_WIDTHS)
    cumulative = np.cumsum(layer_seg_counts)

    for iface in range(len(LAYER_WIDTHS) - 1):
        # Last segment of left layer
        seg_l = cumulative[iface] - 1
        q_l = -k_seg[seg_l] * (T[seg_l + 1] - T[seg_l]) / (x[seg_l + 1] - x[seg_l])
        # First segment of right layer
        seg_r = cumulative[iface]
        q_r = -k_seg[seg_r] * (T[seg_r + 1] - T[seg_r]) / (x[seg_r + 1] - x[seg_r])
        # Both fluxes must equal the analytic value to within 1%
        assert abs(q_l - q_analytic) / abs(q_analytic) < 0.01, (
            f"Interface {iface}: left flux {q_l:.4f} deviates from analytic {q_analytic:.4f}"
        )
        assert abs(q_r - q_analytic) / abs(q_analytic) < 0.01, (
            f"Interface {iface}: right flux {q_r:.4f} deviates from analytic {q_analytic:.4f}"
        )
        # And the two sides must agree with each other to within 0.1%
        assert abs(q_l - q_r) / abs(q_analytic) < 0.001, (
            f"Interface {iface}: flux discontinuity q_l={q_l:.4f}, q_r={q_r:.4f}"
        )
