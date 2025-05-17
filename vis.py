import polyscope as ps
import numpy as np
import json
import trimesh
import os
import argparse

# Argument parser for input path
parser = argparse.ArgumentParser(description="Visualize cylinders and meshes using Polyscope.")
parser.add_argument("input_path", type=str, help="Path to the folder containing .json and .obj files")
args = parser.parse_args()

# Get all valid generations (files with both .json and .obj)
json_files = {f for f in os.listdir(args.input_path) if f.endswith(".json")}
obj_files = {f for f in os.listdir(args.input_path) if f.endswith(".obj")}

generations = sorted([
    int(f[10:14]) for f in json_files
    if f.replace("cylinders", "mesh").replace(".json", ".obj") in obj_files
])

# Cycle through valid generations interactively
for i in generations:
    ps.init()
    ps.remove_all_structures()

    json_path = os.path.join(args.input_path, f"cylinders_{i:04d}.json")
    obj_path = os.path.join(args.input_path, f"mesh_{i:04d}.obj")

    with open(json_path, "r") as f:
        cylinders = json.load(f)

    mesh = trimesh.load(obj_path)
    ps.register_surface_mesh("full_scene", mesh.vertices, mesh.faces)

    for cylinder in cylinders:
        p0 = np.array(cylinder["end_endpoints"][0])
        p1 = np.array(cylinder["end_endpoints"][1])
        points = np.array([p0, p1])
        edges = np.array([[0, 1]])

        line = ps.register_curve_network(cylinder["name"], points, edges)
        line.set_radius(cylinder["radius"], relative=False)

    ps.show()  # Blocks until user closes viewer
