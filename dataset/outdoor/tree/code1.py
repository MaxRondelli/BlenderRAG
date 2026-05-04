import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_mangrove_tree(trunk_height=4, trunk_radius=0.25, num_aerial_roots=8, leaf_count=200):
    """Generate a mangrove tree with characteristic aerial prop roots"""
    clear_scene()
    random.seed(1111)
    
    # Materials
    bark_mat = bpy.data.materials.new(name="MangroveBark")
    bark_mat.use_nodes = True
    bark_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.28, 0.22, 0.16, 1.0)
    bark_mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.95
    
    root_mat = bpy.data.materials.new(name="MangroveRoot")
    root_mat.use_nodes = True
    root_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.32, 0.24, 0.18, 1.0)
    
    leaf_mat = bpy.data.materials.new(name="MangroveLeaf")
    leaf_mat.use_nodes = True
    leaf_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.15, 0.4, 0.2, 1.0)
    
    water_mat = bpy.data.materials.new(name="Water")
    water_mat.use_nodes = True
    water_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.1, 0.3, 0.35, 0.7)
    water_mat.node_tree.nodes["Principled BSDF"].inputs['Metallic'].default_value = 0.3
    water_mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.1
    
    # Create water plane
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
    water = bpy.context.active_object
    water.name = "Water"
    water.data.materials.append(water_mat)
    
    # Create main trunk (twisted)
    segments = 10
    for i in range(segments):
        t = i / segments
        height = trunk_height * t
        
        # Twist and curve
        twist_angle = t * math.pi * 0.5
        offset_x = math.sin(twist_angle) * 0.2
        offset_y = math.cos(twist_angle) * 0.2
        
        segment_height = trunk_height / segments
        radius = trunk_radius * (1 - t * 0.3)
        
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=radius,
            depth=segment_height,
            location=(offset_x, offset_y, height + segment_height/2)
        )
        
        segment = bpy.context.active_object
        segment.name = f"MangroveTrunk_{i}"
        segment.rotation_euler = (0, 0, twist_angle)
        segment.data.materials.append(bark_mat)
    
    # Create aerial prop roots
    for i in range(num_aerial_roots):
        # Starting position on trunk
        start_height = random.uniform(trunk_height * 0.3, trunk_height * 0.7)
        trunk_t = start_height / trunk_height
        twist_at_height = trunk_t * math.pi * 0.5
        
        start_x = math.sin(twist_at_height) * 0.2
        start_y = math.cos(twist_at_height) * 0.2
        start_pos = Vector((start_x, start_y, start_height))
        
        # End position on ground (spread out)
        angle = (2 * math.pi * i / num_aerial_roots) + random.uniform(-0.3, 0.3)
        distance = random.uniform(1.2, 2.0)
        end_pos = Vector((
            math.cos(angle) * distance,
            math.sin(angle) * distance,
            0
        ))
        
        # Create curved root with multiple segments
        root_segments = 8
        for seg in range(root_segments):
            t_seg = seg / root_segments
            
            # Bezier-like curve
            control_point = Vector((
                (start_pos.x + end_pos.x) / 2 + random.uniform(-0.3, 0.3),
                (start_pos.y + end_pos.y) / 2 + random.uniform(-0.3, 0.3),
                start_height * 0.5
            ))
            
            # Quadratic bezier interpolation
            p0 = start_pos
            p1 = control_point
            p2 = end_pos
            
            current_t = t_seg
            next_t = (seg + 1) / root_segments
            
            current_pos = (1-current_t)**2 * p0 + 2*(1-current_t)*current_t * p1 + current_t**2 * p2
            next_pos = (1-next_t)**2 * p0 + 2*(1-next_t)*next_t * p1 + next_t**2 * p2
            
            seg_length = (next_pos - current_pos).length
            seg_dir = (next_pos - current_pos).normalized()
            
            root_radius = 0.08 * (1 - t_seg * 0.4)
            
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=6,
                radius=root_radius,
                depth=seg_length,
                location=(current_pos + next_pos) / 2
            )
            
            root_seg = bpy.context.active_object
            root_seg.name = f"AerialRoot_{i}_{seg}"
            
            # Align root segment
            up = Vector((0, 0, 1))
            if seg_dir.length > 0:
                rotation_axis = up.cross(seg_dir)
                if rotation_axis.length > 0.001:
                    rotation_angle = math.acos(min(1.0, max(-1.0, up.dot(seg_dir))))
                    root_seg.rotation_mode = 'AXIS_ANGLE'
                    root_seg.rotation_axis_angle = (rotation_angle, *rotation_axis.normalized())
            
            root_seg.data.materials.append(root_mat)
    
    # Create crown branches
    crown_height = trunk_height
    num_branches = 6
    
    for i in range(num_branches):
        angle = (2 * math.pi * i / num_branches) + random.uniform(-0.4, 0.4)
        
        branch_length = random.uniform(2.0, 2.8)
        branch_dir = Vector((
            math.cos(angle) * 0.8,
            math.sin(angle) * 0.8,
            random.uniform(0.3, 0.5)
        )).normalized()
        
        twist_at_top = (crown_height / trunk_height) * math.pi * 0.5
        start_x = math.sin(twist_at_top) * 0.2
        start_y = math.cos(twist_at_top) * 0.2
        start_pos = Vector((start_x, start_y, crown_height))
        
        end_pos = start_pos + branch_dir * branch_length
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.12,
            depth=branch_length,
            location=(start_pos + end_pos) / 2
        )
        
        branch = bpy.context.active_object
        branch.name = f"MangroveBranch_{i}"
        
        # Align branch
        up = Vector((0, 0, 1))
        rotation_axis = up.cross(branch_dir)
        if rotation_axis.length > 0.001:
            rotation_angle = math.acos(min(1.0, max(-1.0, up.dot(branch_dir))))
            branch.rotation_mode = 'AXIS_ANGLE'
            branch.rotation_axis_angle = (rotation_angle, *rotation_axis.normalized())
        
        branch.data.materials.append(bark_mat)
        
        # Add sub-branches
        for j in range(3):
            sub_t = random.uniform(0.5, 1.0)
            sub_start = start_pos + branch_dir * (branch_length * sub_t)
            
            sub_angle = angle + random.uniform(-0.6, 0.6)
            sub_length = random.uniform(1.0, 1.5)
            sub_dir = Vector((
                math.cos(sub_angle) * 0.7,
                math.sin(sub_angle) * 0.7,
                random.uniform(0.1, 0.4)
            )).normalized()
            
            sub_end = sub_start + sub_dir * sub_length
            
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.08,
                depth=sub_length,
                location=(sub_start + sub_end) / 2
            )
            
            sub_branch = bpy.context.active_object
            sub_branch.name = f"MangroveSubBranch_{i}_{j}"
            
            rotation_axis = up.cross(sub_dir)
            if rotation_axis.length > 0.001:
                rotation_angle = math.acos(min(1.0, max(-1.0, up.dot(sub_dir))))
                sub_branch.rotation_mode = 'AXIS_ANGLE'
                sub_branch.rotation_axis_angle = (rotation_angle, *rotation_axis.normalized())
            
            sub_branch.data.materials.append(bark_mat)
    
    # Add dense foliage
    tree_objects = [obj for obj in bpy.context.scene.objects 
                    if "MangroveBranch" in obj.name or "MangroveSubBranch" in obj.name]
    
    for _ in range(leaf_count):
        if not tree_objects:
            continue
        branch = random.choice(tree_objects)
        
        local_pos = Vector((
            random.uniform(-0.3, 0.3),
            random.uniform(-0.3, 0.3),
            random.uniform(0.2, 0.5)
        ))
        world_pos = branch.matrix_world @ local_pos
        
        # Elongated leaves
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.15, location=world_pos)
        leaf = bpy.context.active_object
        leaf.scale = (1.5, 0.5, 0.3)
        leaf.name = "MangroveLeaf"
        leaf.data.materials.append(leaf_mat)
        leaf.rotation_euler = (random.uniform(0, 2*math.pi), 
                               random.uniform(0, 2*math.pi), 
                               random.uniform(0, 2*math.pi))
    
    print("Mangrove tree generated!")

create_mangrove_tree()