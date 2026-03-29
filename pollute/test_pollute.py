from pollute import (
    NODE_NAMES,
    N_STEPS,
    SINK,
    SPILL_NODE,
    TRANSPORT_RATE,
    build_network,
    build_upstream,
)


def _run(n_steps=N_STEPS):
    """Return concentration list after n_steps using the same loop as simulate."""
    G = build_network()
    upstream = build_upstream(G)
    n = len(NODE_NAMES)
    c = [0.0] * n
    c[SPILL_NODE] = 1.0

    # Outflow rates mirror those in simulate().
    outflow = [0.0] * n
    for u in range(n):
        if u != SINK and list(G.successors(u)):
            outflow[u] = TRANSPORT_RATE

    for _ in range(n_steps):
        new_c = [0.0] * n
        for v in range(n):
            retained = c[v] * (1.0 - outflow[v])
            inflow = sum(fraction * c[u] for (u, fraction) in upstream[v])
            new_c[v] = retained + inflow
        c = new_c
    return c


def test_mass_conservation():
    # Each step, every unit of concentration either stays at its node or moves
    # to a downstream neighbour.  No mass is created or destroyed, so the total
    # must equal 1.0 throughout.  Floating-point rounding in repeated addition
    # can accumulate, but for 5 nodes and 20 steps the error stays below 1e-12.
    c = _run()
    assert abs(sum(c) - 1.0) < 1e-12


def test_all_nonnegative():
    # Every update is a weighted sum of non-negative values with non-negative
    # weights, so concentration cannot go negative at any node or step.
    G = build_network()
    upstream = build_upstream(G)
    n = len(NODE_NAMES)
    c = [0.0] * n
    c[SPILL_NODE] = 1.0

    outflow = [0.0] * n
    for u in range(n):
        if u != SINK and list(G.successors(u)):
            outflow[u] = TRANSPORT_RATE

    for step in range(N_STEPS):
        new_c = [0.0] * n
        for v in range(n):
            retained = c[v] * (1.0 - outflow[v])
            inflow = sum(fraction * c[u] for (u, fraction) in upstream[v])
            new_c[v] = retained + inflow
        c = new_c
        assert all(x >= 0.0 for x in c), f"negative concentration at step {step + 1}"


def test_spill_node_decreases():
    # upstream_a (node 0) has no upstream neighbours, so every step it loses
    # TRANSPORT_RATE of whatever concentration it holds and gains nothing back.
    # Its concentration must be strictly decreasing from its starting value of 1.
    G = build_network()
    upstream = build_upstream(G)
    n = len(NODE_NAMES)
    c = [0.0] * n
    c[SPILL_NODE] = 1.0

    outflow = [0.0] * n
    for u in range(n):
        if u != SINK and list(G.successors(u)):
            outflow[u] = TRANSPORT_RATE

    prev = c[SPILL_NODE]
    for _ in range(N_STEPS):
        new_c = [0.0] * n
        for v in range(n):
            retained = c[v] * (1.0 - outflow[v])
            inflow = sum(fraction * c[u] for (u, fraction) in upstream[v])
            new_c[v] = retained + inflow
        c = new_c
        assert c[SPILL_NODE] < prev
        prev = c[SPILL_NODE]


def test_uncontaminated_node_stays_zero():
    # upstream_b (node 1) starts at zero concentration and has no upstream
    # neighbours feeding into it.  It loses TRANSPORT_RATE each step, so its
    # concentration is 0 * (1 - TRANSPORT_RATE)^step = 0 throughout.
    c = _run()
    assert c[1] == 0.0  # upstream_b is never contaminated


def test_outlet_nondecreasing():
    # The outlet (sink) only receives mass; it never sends mass downstream.
    # Its concentration therefore cannot decrease between steps.
    G = build_network()
    upstream = build_upstream(G)
    n = len(NODE_NAMES)
    c = [0.0] * n
    c[SPILL_NODE] = 1.0

    outflow = [0.0] * n
    for u in range(n):
        if u != SINK and list(G.successors(u)):
            outflow[u] = TRANSPORT_RATE

    prev = c[SINK]
    for _ in range(N_STEPS):
        new_c = [0.0] * n
        for v in range(n):
            retained = c[v] * (1.0 - outflow[v])
            inflow = sum(fraction * c[u] for (u, fraction) in upstream[v])
            new_c[v] = retained + inflow
        c = new_c
        assert c[SINK] >= prev
        prev = c[SINK]


def test_upstream_fractions_sum():
    # For each non-sink node u that has downstream neighbours, the total
    # fraction of concentration it sends out equals TRANSPORT_RATE exactly.
    # This can be checked by summing the fractions stored in build_upstream.
    G = build_network()
    upstream = build_upstream(G)
    # Collect total outflow fraction assigned to each source node.
    sent = {u: 0.0 for u in range(len(NODE_NAMES))}
    for v in range(len(NODE_NAMES)):
        for (u, fraction) in upstream[v]:
            sent[u] += fraction
    for u, total in sent.items():
        if total > 0.0:
            assert abs(total - TRANSPORT_RATE) < 1e-12, (
                f"node {NODE_NAMES[u]} sends {total}, expected {TRANSPORT_RATE}"
            )
