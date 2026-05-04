import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_rose_hedge(length=10, height=1.3, width=1.1, density=80):
    """Optimized rose hedge with instancing"""
    clear_scene()
    random.seed(1010)
    
    # Materials
    branch_mat = bpy.data.materials.new(name="RoseBranch")
    branch_mat.use_nodes = True
    branch_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.25, 0.3, 0.22, 1.0)
    
    leaf_mat = bpy.data.materials.new(name="RoseLeaves")
    leaf_mat.use_nodes = True
    leaf_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.18, 0.45, 0.2, 1.0)
    
    # Rose colors
    pink_rose = bpy.data.materials.new(name="PinkRose")
    pink_rose.use_nodes = True
    pink_rose.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (1.0, 0.5, 0.65, 1.0)
    
    red_rose = bpy.data.materials.new(name="RedRose")
    red_rose.use_nodes = True
    red_rose.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.85, 0.1, 0.15, 1.0)
    
    white_rose = bpy.data.materials.new(name="WhiteRose")
    white_rose.use_nodes = True
    white_rose.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.98, 0.95, 0.92, 1.0)
    
    thorn_mat = bpy.data.materials.new(name="Thorn")
    thorn_mat.use_nodes = True
    thorn_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.4, 0.35, 0.28, 1.0)
    
    # Create base objects for instancing
    # Foliage cluster
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.15, location=(0, 0, 0))
    foliage_base = bpy.context.active_object
    foliage_base.name = "FoliageBase"
    foliage_base.data.materials.append(leaf_mat)
    foliage_base.hide_viewport = True
    foliage_base.hide_render = False
    
    # Thorn base
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.012, radius2=0.001, depth=0.06, location=(0, 0, 0))
    thorn_base = bpy.context.active_object
    thorn_base.name = "ThornBase"
    thorn_base.data.materials.append(thorn_mat)
    thorn_base.hide_viewport = True
    thorn_base.hide_render = False
    
    # Create collection for instances
    foliage_collection = bpy.data.collections.new("Foliage")
    bpy.context.scene.collection.children.link(foliage_collection)
    
    # Simplified canes (fewer segments)
    num_canes = int(length / 0.6)
    
    for i in range(num_canes):
        x_pos = -length/2 + (length * i / num_canes)
        
        # Fewer segments per cane
        segments = 3
        for seg in range(segments):
            t = seg / segments
            z = height * (t - t*t * 0.5)
            y_offset = random.uniform(-0.15, 0.15)
            
            seg_height = height / segments
            
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.018,
                depth=seg_height,
                location=(x_pos, y_offset, z)
            )
            
            cane = bpy.context.active_object
            cane.rotation_euler = (random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2), 0)
            cane.data.materials.append(branch_mat)
            
            # Add fewer thorns using instancing
            if random.random() < 0.4:
                thorn_angle = random.uniform(0, 2*math.pi)
                thorn_dist = 0.025
                thorn_pos = Vector((
                    x_pos + math.cos(thorn_angle) * thorn_dist,
                    y_offset + math.sin(thorn_angle) * thorn_dist,
                    z
                ))
                
                # Instance thorn
                thorn_instance = bpy.data.objects.new("Thorn", thorn_base.data)
                foliage_collection.objects.link(thorn_instance)
                thorn_instance.location = thorn_pos
                thorn_instance.rotation_euler = (math.pi/2 + random.uniform(-0.3, 0.3), 0, thorn_angle)
    
    # Instance foliage (much lighter)
    for _ in range(density):
        x = random.uniform(-length/2, length/2)
        y = random.uniform(-width/2 * 1.15, width/2 * 1.15)
        z = random.uniform(0.15, height * 0.95)
        
        foliage_instance = bpy.data.objects.new("Foliage", foliage_base.data)
        foliage_collection.objects.link(foliage_instance)
        foliage_instance.location = (x, y, z)
        foliage_instance.scale = (random.uniform(1.1, 1.4), random.uniform(0.7, 1.0), random.uniform(0.8, 1.2))
    
    # Simplified roses (fewer roses, simpler geometry)
    num_roses = 25
    for _ in range(num_roses):
        x = random.uniform(-length/2, length/2)
        y = random.uniform(-width/2, width/2)
        z = random.uniform(0.3, height * 0.85)
        
        rose_mat = random.choice([pink_rose, red_rose, white_rose])
        
        # Simpler rose with fewer petals
        num_petals = 6
        petal_radius = 0.08
        
        for petal in range(num_petals):
            angle = (2 * math.pi * petal / num_petals)
            
            petal_offset = Vector((
                math.cos(angle) * petal_radius,
                math.sin(angle) * petal_radius,
                0
            ))
            
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=4,
                ring_count=3,
                radius=0.035,
                location=(x + petal_offset.x, y + petal_offset.y, z + petal_offset.z)
            )
            
            petal_obj = bpy.context.active_object
            petal_obj.scale = (1.3, 0.7, 0.6)
            petal_obj.rotation_euler = (0, angle, 0)
            petal_obj.data.materials.append(rose_mat)
        
        # Rose center
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=4,
            ring_count=3,
            radius=0.025,
            location=(x, y, z)
        )
        center = bpy.context.active_object
        center.data.materials.append(rose_mat)
    
    print("Optimized rose hedge generated!")

create_rose_hedge()