import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_golden_privet_hedge(length=10, height=1.5, width=1.2, density=350):
    """Golden privet hedge with yellow-green variegated leaves (siepe di ligustro dorato)"""
    clear_scene()
    random.seed(707)
    
    # Materials
    branch_mat = bpy.data.materials.new(name="PrivetBranch")
    branch_mat.use_nodes = True
    branch_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.28, 0.22, 0.16, 1.0)
    
    # Variegated yellow-green leaves
    leaf_colors = [
        (0.7, 0.8, 0.3, 1.0),   # Yellow-green
        (0.8, 0.85, 0.4, 1.0),  # Golden yellow
        (0.5, 0.7, 0.35, 1.0),  # Medium green
        (0.75, 0.75, 0.25, 1.0) # Lime yellow
    ]
    
    leaf_materials = []
    for i, color in enumerate(leaf_colors):
        mat = bpy.data.materials.new(name=f"GoldenLeaf_{i}")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = color
        mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.6
        leaf_materials.append(mat)
    

    
    # Regular branch structure
    num_branches = int(length / 0.4)
    for i in range(num_branches):
        x_pos = -length/2 + (length * i / num_branches)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.028,
            depth=height * random.uniform(0.9, 1.0),
            location=(x_pos, 0, height/2)
        )
        
        main_branch = bpy.context.active_object
        main_branch.data.materials.append(branch_mat)
        
        # Side branches
        for side in range(3):
            side_height = height * (side + 1) / 4
            side_y = random.choice([-1, 1]) * width/3
            
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.018,
                depth=width * 0.6,
                location=(x_pos, side_y/2, side_height)
            )
            
            side_branch = bpy.context.active_object
            side_branch.rotation_euler = (0, math.pi/2, 0)
            side_branch.data.materials.append(branch_mat)
    
    # Mixed golden-green foliage
    for _ in range(density):
        x = random.uniform(-length/2, length/2)
        y = random.uniform(-width/2 * 1.05, width/2 * 1.05)
        z = random.uniform(0.2, height)
        
        # Semi-trimmed appearance
        tolerance = 0.12
        if abs(y) > width/2 - tolerance:
            y = (width/2 - tolerance + random.uniform(-0.05, 0.05)) * (1 if y > 0 else -1)
        
        leaf_mat = random.choice(leaf_materials)
        
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=random.uniform(0.13, 0.2),
            location=(x, y, z)
        )
        
        foliage = bpy.context.active_object
        foliage.scale = (random.uniform(0.85, 1.2), random.uniform(0.85, 1.2), random.uniform(0.9, 1.15))
        foliage.data.materials.append(leaf_mat)
    
    print("Golden privet hedge generated!")

create_golden_privet_hedge()
