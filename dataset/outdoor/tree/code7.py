import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_baobab_tree(trunk_height=6, trunk_radius=1.2, max_depth=3, leaf_count=150):
    """Generate a baobab tree with massive trunk and sparse crown"""
    clear_scene()
    random.seed(707)
    
    # Materials
    bark_mat = bpy.data.materials.new(name="BaobabBark")
    bark_mat.use_nodes = True
    bark_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.5, 0.4, 0.3, 1.0)
    bark_mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.9
    
    leaf_mat = bpy.data.materials.new(name="BaobabLeaves")
    leaf_mat.use_nodes = True
    leaf_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.3, 0.55, 0.2, 1.0)
    
    # Create massive trunk (tapered cylinder)
    segments = 6
    for i in range(segments):
        height = trunk_height * i / segments
        segment_height = trunk_height / segments
        
        # Taper: wider at base, narrower at top
        radius_scale = 1.0 - (i / segments) * 0.4
        segment_radius = trunk_radius * radius_scale
        
        # Slight bulge in middle
        if i == 2 or i == 3:
            segment_radius *= 1.15
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=segment_radius,
            depth=segment_height,
            location=(0, 0, height + segment_height/2)
        )
        
        segment = bpy.context.active_object
        segment.name = f"BaobabTrunk_Seg{i}"
        segment.data.materials.append(bark_mat)
    
    # Create sparse, gnarled branches at top
    crown_height = trunk_height
    num_main_branches = random.randint(5, 8)
    
    def create_branch(base_loc, direction, length, radius, depth):
        if depth > max_depth or length < 0.5:
            return
        
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length,
                                            location=base_loc + direction * (length / 2))
        branch = bpy.context.active_object
        branch.name = f"BaobabBranch_D{depth}"
        
        up = Vector((0, 0, 1))
        if direction.length > 0:
            direction_normalized = direction.normalized()
            rotation_axis = up.cross(direction_normalized)
            if rotation_axis.length > 0.001:
                rotation_angle = math.acos(min(1.0, max(-1.0, up.dot(direction_normalized))))
                branch.rotation_mode = 'AXIS_ANGLE'
                branch.rotation_axis_angle = (rotation_angle, *rotation_axis.normalized())
        
        branch.data.materials.append(bark_mat)
        
        end_loc = base_loc + direction * length
        
        if depth < max_depth:
            # Sparse branching
            num_branches = random.randint(1, 2)
            
            for i in range(num_branches):
                angle_xz = random.uniform(0, 2 * math.pi)
                # Spread out horizontally
                angle_elevation = random.uniform(math.pi/3, math.pi/2.5)
                
                new_dir = Vector((
                    math.sin(angle_elevation) * math.cos(angle_xz),
                    math.sin(angle_elevation) * math.sin(angle_xz),
                    math.cos(angle_elevation)
                ))
                
                rotation = direction.rotation_difference(Vector((0, 0, 1)))
                new_dir.rotate(rotation)
                
                new_length = length * random.uniform(0.65, 0.8)
                new_radius = radius * 0.7
                
                create_branch(end_loc, new_dir, new_length, new_radius, depth + 1)
    
    # Create main branches from top of trunk
    for i in range(num_main_branches):
        angle = (2 * math.pi * i / num_main_branches) + random.uniform(-0.3, 0.3)
        elevation = random.uniform(math.pi/4, math.pi/2.8)
        
        branch_dir = Vector((
            math.sin(elevation) * math.cos(angle),
            math.sin(elevation) * math.sin(angle),
            math.cos(elevation)
        ))
        
        branch_length = random.uniform(2.5, 3.5)
        branch_radius = trunk_radius * 0.25
        
        create_branch(Vector((0, 0, crown_height)), branch_dir, branch_length, branch_radius, 0)
    
    # Add sparse foliage at branch ends
    tree_objects = [obj for obj in bpy.context.scene.objects if "BaobabBranch" in obj.name]
    
    for _ in range(leaf_count):
        if not tree_objects:
            continue
        
        # Prefer outer branches
        eligible = [obj for obj in tree_objects if "D2" in obj.name or "D3" in obj.name]
        if not eligible:
            eligible = tree_objects
        
        branch = random.choice(eligible)
        
        local_pos = Vector((
            random.uniform(-0.3, 0.3),
            random.uniform(-0.3, 0.3),
            random.uniform(0.2, 0.5)
        ))
        world_pos = branch.matrix_world @ local_pos
        
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.15, location=world_pos)
        leaf = bpy.context.active_object
        leaf.name = "BaobabLeaf"
        leaf.data.materials.append(leaf_mat)
    
    print("Baobab tree generated!")

create_baobab_tree()