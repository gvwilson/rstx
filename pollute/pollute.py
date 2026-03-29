import networkx as nx
import polars as pl
import altair as alt

# mccole: constants
# River network: 5 nodes in a directed tree (upstream to downstream).
# Node indices correspond to NODE_NAMES.
NODE_NAMES = ["upstream_a", "upstream_b", "junction", "reach", "outlet"]

# Node 4 (outlet) is the sink: pollutant that arrives there is not transported further.
SINK = 4

# Initial spill: unit concentration at upstream_a only.
SPILL_NODE = 0

# Fraction of concentration at each non-sink node transported downstream per step.
# At 0.4, roughly 40 % of mass moves forward each time step.
TRANSPORT_RATE = 0.4

N_STEPS = 20
SNAPSHOT_INTERVAL = 5
# mccole: /constants


# mccole: build-network
def build_network():
    """Return a directed graph representing the river network.

    Edge weights represent relative mean discharge (arbitrary units) and
    are used for visualization only; transport uses a uniform rate.
    """
    G = nx.DiGraph()
    G.add_nodes_from(range(len(NODE_NAMES)))
    # upstream_a and upstream_b both drain into the junction.
    G.add_edge(0, 2, weight=3.0)
    G.add_edge(1, 2, weight=5.0)
    # junction drains to reach, reach drains to outlet.
    G.add_edge(2, 3, weight=8.0)
    G.add_edge(3, 4, weight=8.0)
    return G
# mccole: /build-network


# mccole: build-upstream
def build_upstream(G):
    """Return upstream[v] = list of (u, fraction) pairs for each node v.

    For each edge u -> v, the fraction of u's concentration that flows to v
    in one step is TRANSPORT_RATE divided by the number of downstream
    neighbours of u.  A node with no upstream neighbours has an empty list.
    """
    n = len(NODE_NAMES)
    upstream = {v: [] for v in range(n)}
    for u in range(n):
        if u == SINK:
            continue
        succs = list(G.successors(u))
        if not succs:
            continue
        fraction = TRANSPORT_RATE / len(succs)
        for v in succs:
            upstream[v].append((u, fraction))
    return upstream
# mccole: /build-upstream


# mccole: simulate
def simulate(G):
    """Simulate pollutant transport and return concentration snapshots.

    For each time step the new concentration at node v is:

        new_c[v] = c[v] * (1 - outflow_rate[v])
                   + sum(fraction * c[u] for (u, fraction) in upstream[v])

    where outflow_rate[v] is TRANSPORT_RATE for non-sink nodes (0 for the sink).
    The sink retains everything it receives and sends nothing downstream.
    """
    n = len(NODE_NAMES)
    c = [0.0] * n
    c[SPILL_NODE] = 1.0

    upstream = build_upstream(G)

    # Outflow rate for each node: TRANSPORT_RATE for non-sink nodes that have
    # at least one downstream successor; 0 for the sink and for isolated nodes.
    outflow = [0.0] * n
    for u in range(n):
        if u != SINK and list(G.successors(u)):
            outflow[u] = TRANSPORT_RATE

    records = _snapshot(c, 0)
    for step in range(1, N_STEPS + 1):
        new_c = [0.0] * n
        for v in range(n):
            retained = c[v] * (1.0 - outflow[v])
            inflow = sum(fraction * c[u] for (u, fraction) in upstream[v])
            new_c[v] = retained + inflow
        c = new_c
        if step % SNAPSHOT_INTERVAL == 0:
            records += _snapshot(c, step)
    return pl.DataFrame(records)


def _snapshot(c, step):
    return [
        {"node": NODE_NAMES[i], "concentration": float(c[i]), "step": step}
        for i in range(len(NODE_NAMES))
    ]
# mccole: /simulate


# mccole: plot
def plot(df):
    """Return an Altair line chart of concentration at each node over time."""
    return (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("step:O", title="Time step"),
            y=alt.Y(
                "concentration:Q",
                title="Concentration",
                scale=alt.Scale(domain=[0.0, 1.0]),
            ),
            color=alt.Color("node:N", title="Node", sort=NODE_NAMES),
        )
        .properties(width=350, height=250)
    )
# mccole: /plot


if __name__ == "__main__":
    G = build_network()
    df = simulate(G)
    chart = plot(df)
    chart.save("pollute.svg")
    print(f"Saved pollute.svg ({len(df)} rows)")
