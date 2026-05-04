import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_autumn_hedge(length=10, height=1.6, width=1.4, density=300):
    """Autumn hedge with fall colors (siepe autunnale)"""
    clear_scene()
    random.seed(303)
    
    # Materials
    branch_mat = bpy.data.materials.new(name="AutumnBranch")
    branch_mat.use_nodes = True
    branch_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.3, 0.22, 0.15, 1.0)
    
    # Multiple autumn colors
    autumn_colors = [
        (0.95, 0.5, 0.1, 1.0),   # Orange
        (0.9, 0.3, 0.15, 1.0),   # Red-orange
        (0.85, 0.2, 0.1, 1.0),   # Deep red
        (0.95, 0.8, 0.25, 1.0),  # Yellow
        (0.8, 0.6, 0.2, 1.0),    # Gold
        (0.6, 0.35, 0.15, 1.0),  # Brown
    ]
    
    leaf_materials = []
    for i, color in enumerate(autumn_colors):
        mat = bpy.data.materials.new(name=f"AutumnLeaf_{i}")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = color
        leaf_materials.append(mat)
    
    # Ground

    
    # Branch structure
    num_branches = int(length / 0.45)
    for i in range(num_branches):
        x_pos = -length/2 + (length * i / num_branches)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.03,
            depth=height * random.uniform(0.85, 1.0),
            location=(x_pos, 0, height/2)
        )
        branch = bpy.context.active_object
        branch.data.materials.append(branch_mat)
    
    # Colorful autumn foliage
    for _ in range(density):
        x = random.uniform(-length/2, length/2)
        y = random.uniform(-width/2, width/2)
        z = random.uniform(0.2, height)
        
        leaf_mat = random.choice(leaf_materials)
        
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=random.uniform(0.14, 0.24),
            location=(x, y, z)
        )
        
        foliage = bpy.context.active_object
        foliage.scale = (random.uniform(0.8, 1.3), random.uniform(0.8, 1.3), random.uniform(0.9, 1.2))
        foliage.data.materials.append(leaf_mat)
    
    # Fallen leaves on ground
    for _ in range(100):
        x = random.uniform(-length/2 - 0.5, length/2 + 0.5)
        y = random.uniform(-width/2 - 0.4, width/2 + 0.4)
        
        leaf_mat = random.choice(leaf_materials)
        
        bpy.ops.mesh.primitive_plane_add(
            size=0.1,
            location=(x, y, 0.01)
        )
        
        fallen_leaf = bpy.context.active_object
        fallen_leaf.scale = (random.uniform(0.7, 1.3), random.uniform(0.6, 1.2), 1)
        fallen_leaf.rotation_euler = (random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2), random.uniform(0, 2*math.pi))
        fallen_leaf.data.materials.append(leaf_mat)
    
    print("Autumn hedge generated!")

create_autumn_hedge()
