import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_bramble_hedge(length=10, height=1.5, width=1.8, density=250):
    """Wild bramble/berry hedge - unruly and natural (siepe di rovi)"""
    clear_scene()
    random.seed(606)
    
    # Materials
    branch_mat = bpy.data.materials.new(name="BrambleBranch")
    branch_mat.use_nodes = True
    branch_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.3, 0.2, 0.15, 1.0)
    
    leaf_mat = bpy.data.materials.new(name="BrambleLeaves")
    leaf_mat.use_nodes = True
    leaf_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.2, 0.45, 0.18, 1.0)
    
    berry_mat = bpy.data.materials.new(name="Berry")
    berry_mat.use_nodes = True
    berry_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.15, 0.05, 0.15, 1.0)

    thorn_mat = bpy.data.materials.new(name="Thorn")
    thorn_mat.use_nodes = True
    thorn_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.4, 0.35, 0.3, 1.0)
    
    # Ground

    
    # Twisted, irregular branches
    num_branches = int(length / 0.6)
    for i in range(num_branches):
        x_pos = -length/2 + (length * i / num_branches)
        
        # Create twisted main branch
        segments = 8
        for seg in range(segments):
            t = seg / segments
            z = height * t
            
            # Add twist and irregularity
            x_offset = math.sin(t * math.pi * 2) * 0.15
            y_offset = math.cos(t * math.pi * 3) * 0.2
            
            seg_height = height / segments
            
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.025,
                depth=seg_height,
                location=(x_pos + x_offset, y_offset, z + seg_height/2)
            )
            
            branch = bpy.context.active_object
            branch.rotation_euler = (random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2), random.uniform(-0.3, 0.3))
            branch.data.materials.append(branch_mat)
            
            # Add thorns
            if random.random() < 0.4:
                thorn_angle = random.uniform(0, 2*math.pi)
                thorn_dist = 0.03
                thorn_pos = Vector((
                    x_pos + x_offset + math.cos(thorn_angle) * thorn_dist,
                    y_offset + math.sin(thorn_angle) * thorn_dist,
                    z
                ))
                
                bpy.ops.mesh.primitive_cone_add(
                    vertices=4,
                    radius1=0.015,
                    radius2=0.001,
                    depth=0.08,
                    location=thorn_pos
                )
                
                thorn = bpy.context.active_object
                thorn.rotation_euler = (math.pi/2, 0, thorn_angle)
                thorn.data.materials.append(thorn_mat)
    
    # Wild, irregular foliage
    for _ in range(density):
        x = random.uniform(-length/2 - 0.2, length/2 + 0.2)
        y = random.uniform(-width/2 * 1.4, width/2 * 1.4)
        z = random.uniform(0.15, height * 1.2)
        
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=random.uniform(0.12, 0.25),
            location=(x, y, z)
        )
        
        foliage = bpy.context.active_object
        foliage.scale = (random.uniform(0.7, 1.5), random.uniform(0.7, 1.5), random.uniform(0.8, 1.3))
        foliage.data.materials.append(leaf_mat)
    
    # Add dark berries
    for _ in range(80):
        x = random.uniform(-length/2, length/2)
        y = random.uniform(-width/2, width/2)
        z = random.uniform(0.3, height * 0.9)
        
        # Berry cluster
        for berry in range(random.randint(2, 5)):
            offset = Vector((random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), random.uniform(-0.03, 0.03)))
            
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=8,
                ring_count=6,
                radius=0.025,
                location=(x + offset.x, y + offset.y, z + offset.z)
            )
            
            berry_obj = bpy.context.active_object
            berry_obj.data.materials.append(berry_mat)
    
    print("Bramble hedge generated!")

create_bramble_hedge()
