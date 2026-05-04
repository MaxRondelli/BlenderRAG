import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_conifer_hedge(length=10, height=2.5, width=1.2, density=450):
    """Evergreen conifer hedge - dense and dark green (siepe di conifere)"""
    clear_scene()
    random.seed(404)
    
    # Materials
    branch_mat = bpy.data.materials.new(name="ConiferBranch")
    branch_mat.use_nodes = True
    branch_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.25, 0.18, 0.12, 1.0)
    
    needle_mat = bpy.data.materials.new(name="ConiferNeedles")
    needle_mat.use_nodes = True
    needle_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.05, 0.25, 0.08, 1.0)
    
    # Ground

    # Dense vertical branch structure
    num_branches = int(length / 0.35)
    for i in range(num_branches):
        x_pos = -length/2 + (length * i / num_branches)
        branch_height = height * random.uniform(0.95, 1.0)
        
        # Main vertical branch
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.04,
            depth=branch_height,
            location=(x_pos, 0, branch_height/2)
        )
        main_branch = bpy.context.active_object
        main_branch.data.materials.append(branch_mat)
        
        # Horizontal layers
        for layer in range(6):
            layer_z = branch_height * (layer / 6)
            
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.025,
                depth=width * 0.9,
                location=(x_pos, 0, layer_z)
            )
            h_branch = bpy.context.active_object
            h_branch.rotation_euler = (0, math.pi/2, 0)
            h_branch.data.materials.append(branch_mat)
    
    # Very dense needle-like foliage
    for _ in range(density):
        x = random.uniform(-length/2, length/2)
        y = random.uniform(-width/2, width/2)
        z = random.uniform(0.1, height)
        
        # Tight columnar shape
        edge = 0.1
        if abs(y) > width/2 - edge:
            y = (width/2 - edge) * (1 if y > 0 else -1)
        
        # Create needle cluster (elongated cone)
        bpy.ops.mesh.primitive_cone_add(
            vertices=6,
            radius1=0.08,
            radius2=0.02,
            depth=random.uniform(0.18, 0.28),
            location=(x, y, z)
        )
        
        needles = bpy.context.active_object
        needles.rotation_euler = (random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3), random.uniform(0, 2*math.pi))
        needles.data.materials.append(needle_mat)
    
    print("Conifer hedge generated!")

create_conifer_hedge()
