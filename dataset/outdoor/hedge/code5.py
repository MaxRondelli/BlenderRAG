import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_lavender_hedge(length=10, height=0.8, width=0.9, density=280):
    """Lavender hedge with purple flowers (siepe di lavanda)"""
    clear_scene()
    random.seed(505)
    
    # Materials
    stem_mat = bpy.data.materials.new(name="LavenderStem")
    stem_mat.use_nodes = True
    stem_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.35, 0.4, 0.3, 1.0)
    
    leaf_mat = bpy.data.materials.new(name="LavenderLeaves")
    leaf_mat.use_nodes = True
    leaf_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.4, 0.5, 0.45, 1.0)
    
    flower_mat = bpy.data.materials.new(name="LavenderFlower")
    flower_mat.use_nodes = True
    flower_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.5, 0.3, 0.7, 1.0)
    

    
    # Many thin stems
    num_stems = int(length / 0.15)
    for i in range(num_stems):
        x_pos = -length/2 + (length * i / num_stems) + random.uniform(-0.05, 0.05)
        y_pos = random.uniform(-width/2, width/2)
        stem_height = height * random.uniform(0.85, 1.0)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.01,
            depth=stem_height,
            location=(x_pos, y_pos, stem_height/2)
        )
        
        stem = bpy.context.active_object
        stem.rotation_euler = (random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), 0)
        stem.data.materials.append(stem_mat)
        
        # Add flower spike on top
        spike_height = stem_height * 0.25
        
        bpy.ops.mesh.primitive_cone_add(
            vertices=6,
            radius1=0.04,
            radius2=0.01,
            depth=spike_height,
            location=(x_pos, y_pos, stem_height + spike_height/2)
        )
        
        spike = bpy.context.active_object
        spike.data.materials.append(flower_mat)
    
    # Silvery-green foliage at base
    for _ in range(density):
        x = random.uniform(-length/2, length/2)
        y = random.uniform(-width/2 * 1.1, width/2 * 1.1)
        z = random.uniform(0.05, height * 0.6)
        
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=random.uniform(0.08, 0.15),
            location=(x, y, z)
        )
        
        foliage = bpy.context.active_object
        foliage.scale = (random.uniform(1.2, 1.6), random.uniform(0.6, 0.9), random.uniform(0.8, 1.2))
        foliage.data.materials.append(leaf_mat)
    
    # Additional purple flower clusters
    for _ in range(150):
        x = random.uniform(-length/2, length/2)
        y = random.uniform(-width/2, width/2)
        z = random.uniform(height * 0.7, height * 1.1)
        
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=6,
            ring_count=4,
            radius=0.03,
            location=(x, y, z)
        )
        
        flower_cluster = bpy.context.active_object
        flower_cluster.data.materials.append(flower_mat)
    
    print("Lavender hedge generated!")

create_lavender_hedge()
