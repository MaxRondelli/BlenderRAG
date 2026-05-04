import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_spring_flowering_hedge(length=10, height=1.8, width=1.3, density=350):
    """Spring flowering hedge with pink/white flowers (siepe fiorita primaverile)"""
    clear_scene()
    random.seed(202)
    
    # Materials
    branch_mat = bpy.data.materials.new(name="SpringBranch")
    branch_mat.use_nodes = True
    branch_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.28, 0.2, 0.15, 1.0)
    
    leaf_mat = bpy.data.materials.new(name="SpringLeaves")
    leaf_mat.use_nodes = True
    leaf_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.3, 0.6, 0.25, 1.0)
    
    # Flower materials
    pink_flower = bpy.data.materials.new(name="PinkFlower")
    pink_flower.use_nodes = True
    pink_flower.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (1.0, 0.6, 0.75, 1.0)
    
    white_flower = bpy.data.materials.new(name="WhiteFlower")
    white_flower.use_nodes = True
    white_flower.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.98, 0.95, 0.92, 1.0)
    
    # Ground
    
    # Branch structure
    num_branches = int(length / 0.4)
    for i in range(num_branches):
        x_pos = -length/2 + (length * i / num_branches)
        branch_height = height * random.uniform(0.9, 1.0)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.025,
            depth=branch_height,
            location=(x_pos, 0, branch_height/2)
        )
        branch = bpy.context.active_object
        branch.data.materials.append(branch_mat)
    
    # Light green foliage
    for _ in range(int(density * 0.6)):
        x = random.uniform(-length/2, length/2)
        y = random.uniform(-width/2 * 1.1, width/2 * 1.1)
        z = random.uniform(0.2, height * 0.95)
        
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=random.uniform(0.15, 0.22),
            location=(x, y, z)
        )
        
        foliage = bpy.context.active_object
        foliage.scale = (random.uniform(0.8, 1.3), random.uniform(0.8, 1.3), random.uniform(0.9, 1.2))
        foliage.data.materials.append(leaf_mat)
    
    # Add flowers
    num_flowers = 200
    for _ in range(num_flowers):
        x = random.uniform(-length/2, length/2)
        y = random.uniform(-width/2, width/2)
        z = random.uniform(0.3, height * 0.9)
        
        flower_mat = random.choice([pink_flower, white_flower])
        
        # Create flower cluster
        for petal in range(4):
            offset = Vector((
                random.uniform(-0.05, 0.05),
                random.uniform(-0.05, 0.05),
                random.uniform(-0.02, 0.02)
            ))
            
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=6,
                ring_count=4,
                radius=0.04,
                location=(x + offset.x, y + offset.y, z + offset.z)
            )
            
            flower = bpy.context.active_object
            flower.data.materials.append(flower_mat)
    
    print("Spring flowering hedge generated!")

create_spring_flowering_hedge()
