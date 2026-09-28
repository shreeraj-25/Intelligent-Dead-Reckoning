"""Optional OSM road matching helpers. OSMnx is imported lazily so core IDR code works without it."""
import numpy as np

def load_road_graph(bbox):
    """
    bbox: (north, south, east, west) in decimal degrees.

    osmnx changed graph_from_bbox's argument signature across major versions
    (positional north/south/east/west in <1.6, a single (left,bottom,right,top)
    tuple from ~1.6 onward). We try both call styles so this doesn't silently
    break on whatever osmnx version ends up installed on your machine.
    """
    try:
        import osmnx as ox
    except ImportError as e:
        raise ImportError('Install osmnx to use map matching: pip install osmnx') from e
    north, south, east, west = map(float, bbox)
    try:
        # osmnx >= 1.6 style: single bbox tuple (left, bottom, right, top)
        return ox.graph_from_bbox((west, south, east, north), network_type='drive', simplify=True)
    except TypeError:
        # osmnx < 1.6 style: separate keyword arguments
        return ox.graph_from_bbox(north=north, south=south, east=east, west=west,
                                   network_type='drive', simplify=True)

def nearest_road_candidates(position_enu,graph,k=5):
    if k<=0: return []
    # Caller should provide graph edges already transformed to the same ENU frame.
    candidates=list(graph.edges(data=True))
    pos=np.asarray(position_enu,float)
    def dist(e): return float(e[2].get('distance',np.inf))
    return sorted(candidates,key=dist)[:k]

def road_score(distance_m,heading_diff_deg,continuity,ekf_uncertainty,weights=(1,1,1,1)):
    w=np.asarray(weights,float); terms=np.array([float(distance_m),abs(float(heading_diff_deg))/180.,1-float(np.clip(continuity,0,1)),max(float(ekf_uncertainty),0)])
    return float(np.dot(w,terms))

def soft_correct_position(position_enu,best_candidate,ekf_uncertainty):
    p=np.asarray(position_enu,float)
    if best_candidate is None: return p.copy()
    target=np.asarray(best_candidate,dtype=float).reshape(-1)
    if target.size<2: return p.copy()
    # Higher uncertainty -> stronger correction, capped for safety.
    alpha=float(np.clip(float(ekf_uncertainty)/(float(ekf_uncertainty)+5.),0,0.35))
    return (1-alpha)*p+alpha*target[:2]
