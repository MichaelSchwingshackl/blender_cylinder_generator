import polyscope as ps
import numpy as np
import json
import trimesh
import os

# Load all available generations first
def load_generation(i):
    
    ps.init()
    # Clear everything
    ps.remove_all_structures()

    # Load mesh and log info
    json_path = f"output/cylinders_{i:04d}.json"
    obj_path = f"output/mesh_{i:04d}.obj"

    if not os.path.exists(json_path) or not os.path.exists(obj_path):
        print(f"Skipping missing generation {i}")
        return False

    with open(json_path, "r") as f:
        logs = json.load(f)

    mesh = trimesh.load(obj_path)
    ps.register_surface_mesh("full_log_scene", mesh.vertices, mesh.faces)

    for log in logs:
        p0 = np.array(log["end_endpoints"][0])
        p1 = np.array(log["end_endpoints"][1])
        points = np.array([p0, p1])
        edges = np.array([[0, 1]])

        line = ps.register_curve_network(log["name"], points, edges)
        line.set_radius(log["radius"], relative=False)

    ps.show()  # Blocks until user closes viewer
    return True

# Cycle through generations interactively
for i in range(100):
    success = load_generation(i)
   