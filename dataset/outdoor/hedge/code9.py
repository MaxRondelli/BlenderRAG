import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_winter_hedge(length=10, height=1.4, width=1.1, snow_amount=200):
    """Winter bare hedge with snow (siepe invernale)"""
    clear_scene()
    random.seed(909)
    
    # Materials
    branch_mat = bpy.data.materials.new(name="WinterBranch")
    branch_mat.use_nodes = True
    branch_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.18, 0.15, 0.13, 1.0)
    branch_mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 1.0
    
    snow_mat = bpy.data.materials.new(name="Snow")
    snow_mat.use_nodes = True
    snow_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.95, 0.95, 1.0, 1.0)
    snow_mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.3
    
    ground_snow_mat = bpy.data.materials.new(name="GroundSnow")
    ground_snow_mat.use_nodes = True
    ground_snow_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.92, 0.94, 0.97, 1.0)
    
    # Snowy ground
    
    # Bare twisted branches
    num_branches = int(length / 0.35)
    all_branches = []
    
    for i in range(num_branches):
        x_pos = -length/2 + (length * i / num_branches)
        
        # Create gnarled main branch
        segments = 7
        for seg in range(segments):
            t = seg / segments
            z = height * t
            
            # Irregular growth
            twist = math.sin(t * math.pi * 3) * 0.12
            
            seg_height = height / segments
            
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.022 * (1 - t * 0.3),
                depth=seg_height,
                location=(x_pos + twist, random.uniform(-0.1, 0.1), z + seg_height/2)
            )
            
            branch = bpy.context.active_object
            branch.rotation_euler = (random.uniform(-0.15, 0.15), random.uniform(-0.15, 0.15), random.uniform(-0.2, 0.2))
            branch.data.materials.append(branch_mat)
            all_branches.append(branch)
            
            # Side twigs
            if random.random() < 0.5:
                twig_length = random.uniform(0.15, 0.3)
                twig_angle_h = random.uniform(0, 2*math.pi)
                twig_angle_v = random.uniform(math.pi/6, math.pi/3)
                
                twig_dir = Vector((
                    math.sin(twig_angle_v) * math.cos(twig_angle_h),
                    math.sin(twig_angle_v) * math.sin(twig_angle_h),
                    math.cos(twig_angle_v)
                ))
                
                twig_end = Vector((x_pos + twist, 0, z)) + twig_dir * twig_length
                
                bpy.ops.mesh.primitive_cylinder_add(
                    radius=0.008,
                    depth=twig_length,
                    location=(Vector((x_pos + twist, 0, z)) + twig_end) / 2
                )
                
                twig = bpy.context.active_object
                
                # Align twig
                up = Vector((0, 0, 1))
                rotation_axis = up.cross(twig_dir)
                if rotation_axis.length > 0.001:
                    rotation_angle = math.acos(min(1.0, max(-1.0, up.dot(twig_dir))))
                    twig.rotation_mode = 'AXIS_ANGLE'
                    twig.rotation_axis_angle = (rotation_angle, *rotation_axis.normalized())
                
                twig.data.materials.append(branch_mat)
                all_branches.append(twig)
    
    # Snow accumulation on branches
    for _ in range(snow_amount):
        if not all_branches:
            continue
        
        branch = random.choice(all_branches)
        
        # Snow on top of branches
        local_pos = Vector((
            random.uniform(-0.1, 0.1),
            random.uniform(-0.1, 0.1),
            random.uniform(0.02, 0.15)
        ))
        
        world_pos = branch.matrix_world @ local_pos
        
        if world_pos.z > 0.1:  # Only add snow above ground
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=1,
                radius=random.uniform(0.06, 0.12),
                location=world_pos
            )
            
            snow = bpy.context.active_object
            snow.scale = (random.uniform(0.8, 1.3), random.uniform(0.8, 1.3), random.uniform(0.5, 0.8))
            snow.data.materials.append(snow_mat)
    
    # Snow drifts at base
    for _ in range(30):
        x = random.uniform(-length/2 - 0.3, length/2 + 0.3)
        y = random.uniform(-width/2 - 0.2, width/2 + 0.2)
        
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=random.uniform(0.2, 0.4),
            location=(x, y, random.uniform(0, 0.1))
        )
        
        drift = bpy.context.active_object
        drift.scale = (random.uniform(1.2, 1.8), random.uniform(1.0, 1.5), random.uniform(0.3, 0.6))
        drift.data.materials.append(snow_mat)
    
    print("Winter hedge generated!")

create_winter_hedge()
