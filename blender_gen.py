import bpy
import random
import math
import json
import numpy as np
import os
from mathutils import Vector, Matrix

## handle arguments
import sys
argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"

count = int(argv[0])
out_folder = argv[1]

for gen_i in range(count):
    random.seed(gen_i)
    # === CONFIGURATION ===
    N = random.randint(1, 10)
    log_radius_range = (0.2, 0.6)
    log_length_range = (3, 9.0)
    spawn_area = random.uniform(3, 7)
    min_height = 2
    height_increment = 1
    settled_z_threshold = 0.3
    frame_limit = 500


    # === CLEANUP ===
    def cleanup_scene():
        for obj in bpy.data.objects:
            if obj.name.startswith("Log") or obj.name == "Ground":
                bpy.data.objects.remove(obj, do_unlink=True)

    cleanup_scene()

    # === GROUND PLANE ===
    bpy.ops.mesh.primitive_plane_add(size=spawn_area * 5, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    bpy.ops.rigidbody.object_add()
    ground.rigid_body.type = 'PASSIVE'
    ground.rigid_body.friction = 1


    # === CREATE LOGS ===
    log_infos = []

    for i in range(N):
        radius = random.uniform(*log_radius_range)
        length = random.uniform(*log_length_range)

        x = random.uniform(-spawn_area, spawn_area)
        y = random.uniform(-spawn_area, spawn_area)
        z = min_height + i * height_increment
        z_rot = math.radians(random.uniform(0, 360))

        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius,
            depth=length,
            location=(x, y, z),
            rotation=(0, math.radians(90), z_rot)
        )

        log = bpy.context.active_object
        log.name = f"Log_{i}"

        bpy.ops.rigidbody.object_add()
        log.rigid_body.mass = length * 3.1415 * radius**2 * 480 
        log.rigid_body.friction = 1.0
        log.rigid_body.angular_damping = 0.9
        log.rigid_body.linear_damping = 0.2

        log_infos.append({
            "name": log.name,
            "length": length,
            "radius": radius,
            #"start_matrix": list(log.matrix_world.copy()),
        })

    # === SIMULATE ===
    scene = bpy.context.scene
    scene.frame_set(1)
    scene.frame_start = 1
    scene.frame_end = frame_limit

    bpy.ops.ptcache.free_bake_all()
    bpy.ops.ptcache.bake_all(bake=True)

    # === WAIT UNTIL SETTLED ===
    def is_settled(log_objects, threshold):
        return all(obj.location.z < threshold for obj in log_objects)

    settled_frame = frame_limit
    for frame in range(1, frame_limit + 1):
        scene.frame_set(frame)
        logs = [bpy.data.objects[info["name"]] for info in log_infos]
        if is_settled(logs, settled_z_threshold):
            settled_frame = frame
            break

    rot = Matrix((
        (1, 0, 0, 0),
        (0, 0, 1, 0),
        (0, -1, 0, 0),
        (0, 0, 0, 1)
    ))


    # === GET CYLINDER ENDPOINTS ===
    def get_endpoints(obj, length):
        """
        Get the start and end point of a cylinder aligned along its local Z-axis.
        """
        half = length / 2
        p1_local = Vector((0, 0, -half))
        p2_local = Vector((0, 0, +half))
        p1_world = rot @ obj.matrix_world @ p1_local
        p2_world = rot @ obj.matrix_world @ p2_local

        return p1_world, p2_world

    scene.frame_set(settled_frame)
    for info in log_infos:
        obj = bpy.data.objects[info["name"]]
        p1, p2 = get_endpoints(obj, info["length"])
        info["end_endpoints"] = (list(p1), list(p2))
        


    output_path = f"{out_folder}/cylinders_{gen_i:04d}.json"

    # === WRITE TO FILE ===
    with open(output_path, "w") as f:
        json.dump(log_infos, f)
        
    output_obj_path = f"{out_folder}/mesh_{gen_i:04d}.obj"

    bpy.ops.wm.obj_export(
        filepath=output_obj_path,
        export_selected_objects=False,
        export_materials=False,
        export_normals=True,
        export_uv=True,
        export_triangulated_mesh=True,
        forward_axis='NEGATIVE_Z',
        up_axis='Y'
    )