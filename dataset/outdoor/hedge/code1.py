import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_boxwood_hedge(length=10, height=1.2, width=1.0, density=400):
    """Formal boxwood hedge - perfectly trimmed, deep green (siepe di bosso)"""
    clear_scene()
    random.seed(101)
    
    # Materials - Dark green boxwood
    branch_mat = bpy.data.materials.new(name="BoxwoodBranch")
    branch_mat.use_nodes = True
    branch_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.2, 0.15, 0.1, 1.0)
    
    leaf_mat = bpy.data.materials.new(name="BoxwoodLeaves")
    leaf_mat.use_nodes = True
    leaf_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.08, 0.3, 0.1, 1.0)
    leaf_mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.7
    
    # Ground

    
    # Dense branch structure
    num_branches = int(length / 0.3)
    for i in range(num_branches):
        x_pos = -length/2 + (length * i / num_branches)
        
        for layer in range(4):
            layer_height = height * (layer / 4)
            
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.02,
                depth=width * 0.8,
                location=(x_pos, 0, layer_height)
            )
            branch = bpy.context.active_object
            branch.rotation_euler = (0, math.pi/2, 0)
            branch.data.materials.append(branch_mat)
    
    # Very dense, perfectly trimmed foliage
    for _ in range(density):
        x = random.uniform(-length/2, length/2)
        y = random.uniform(-width/2, width/2)
        z = random.uniform(0.15, height)
        
        # Strict rectangular bounds
        tolerance = 0.08
        if abs(y) > width/2 - tolerance:
            y = (width/2 - tolerance) * (1 if y > 0 else -1)
        if z > height - tolerance:
            z = height - tolerance
        
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=random.uniform(0.12, 0.18),
            location=(x, y, z)
        )
        
        foliage = bpy.context.active_object
        foliage.scale = (random.uniform(0.9, 1.1), random.uniform(0.9, 1.1), random.uniform(0.95, 1.05))
        foliage.data.materials.append(leaf_mat)
    
    print("Formal boxwood hedge generated!")

create_boxwood_hedge()
