import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_redtip_photinia_hedge(length=10, height=2.0, width=1.3, density=380):
    """Red tip photinia hedge with red new growth (siepe di fotinia)"""
    clear_scene()
    random.seed(808)
    
    # Materials
    branch_mat = bpy.data.materials.new(name="PhotiniaBranch")
    branch_mat.use_nodes = True
    branch_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.26, 0.19, 0.14, 1.0)
    
    # Mature green leaves
    green_leaf = bpy.data.materials.new(name="GreenLeaf")
    green_leaf.use_nodes = True
    green_leaf.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.15, 0.4, 0.18, 1.0)
    green_leaf.node_tree.nodes["Principled BSDF"].inputs['Metallic'].default_value = 0.1
    
    # New red growth
    red_leaf = bpy.data.materials.new(name="RedLeaf")
    red_leaf.use_nodes = True
    red_leaf.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.8, 0.15, 0.2, 1.0)
    
    # Transitional burgundy
    burgundy_leaf = bpy.data.materials.new(name="BurgundyLeaf")
    burgundy_leaf.use_nodes = True
    burgundy_leaf.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.5, 0.2, 0.15, 1.0)
    
    # Ground

    
    # Dense branching structure
    num_branches = int(length / 0.38)
    for i in range(num_branches):
        x_pos = -length/2 + (length * i / num_branches)
        branch_height = height * random.uniform(0.92, 1.0)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.032,
            depth=branch_height,
            location=(x_pos, 0, branch_height/2)
        )
        
        main_branch = bpy.context.active_object
        main_branch.data.materials.append(branch_mat)
    
    # Layered foliage - green base
    for _ in range(int(density * 0.65)):
        x = random.uniform(-length/2, length/2)
        y = random.uniform(-width/2, width/2)
        z = random.uniform(0.2, height * 0.85)
        
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=random.uniform(0.16, 0.23),
            location=(x, y, z)
        )
        
        foliage = bpy.context.active_object
        foliage.scale = (random.uniform(0.9, 1.25), random.uniform(0.9, 1.25), random.uniform(0.95, 1.15))
        foliage.data.materials.append(green_leaf)
    
    # Red new growth at top and tips
    for _ in range(int(density * 0.25)):
        x = random.uniform(-length/2, length/2)
        y = random.uniform(-width/2 * 0.9, width/2 * 0.9)
        z = random.uniform(height * 0.7, height * 1.05)
        
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=random.uniform(0.12, 0.18),
            location=(x, y, z)
        )
        
        foliage = bpy.context.active_object
        foliage.scale = (random.uniform(0.85, 1.15), random.uniform(0.85, 1.15), random.uniform(0.9, 1.1))
        foliage.data.materials.append(red_leaf)
    
    # Burgundy transitional leaves
    for _ in range(int(density * 0.1)):
        x = random.uniform(-length/2, length/2)
        y = random.uniform(-width/2, width/2)
        z = random.uniform(height * 0.5, height * 0.8)
        
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=random.uniform(0.14, 0.2),
            location=(x, y, z)
        )
        
        foliage = bpy.context.active_object
        foliage.scale = (random.uniform(0.9, 1.2), random.uniform(0.9, 1.2), random.uniform(0.95, 1.12))
        foliage.data.materials.append(burgundy_leaf)
    
    print("Red tip photinia hedge generated!")

create_redtip_photinia_hedge()
