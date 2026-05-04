import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_birch_tree(trunk_height=7, trunk_radius=0.2, max_depth=6, leaf_count=250):
    """Generate a slender birch tree with white bark"""
    clear_scene()
    random.seed(606)
    
    # Materials
    bark_mat = bpy.data.materials.new(name="BirchBark")
    bark_mat.use_nodes = True
    # White bark with dark markings
    bark_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.95, 0.95, 0.9, 1.0)
    
    leaf_mat = bpy.data.materials.new(name="BirchLeaves")
    leaf_mat.use_nodes = True
    leaf_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.4, 0.7, 0.2, 1.0)
    
    def create_branch(base_loc, direction, length, radius, depth):
        if depth > max_depth or length < 0.25:
            return
        
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length,
                                            location=base_loc + direction * (length / 2))
        branch = bpy.context.active_object
        branch.name = f"BirchBranch_D{depth}"
        
        up = Vector((0, 0, 1))
        if direction.length > 0:
            direction_normalized = direction.normalized()
            rotation_axis = up.cross(direction_normalized)
            if rotation_axis.length > 0.001:
                rotation_angle = math.acos(min(1.0, max(-1.0, up.dot(direction_normalized))))
                branch.rotation_mode = 'AXIS_ANGLE'
                branch.rotation_axis_angle = (rotation_angle, *rotation_axis.normalized())
        
        branch.data.materials.append(bark_mat)
        
        # Add dark markings to trunk segments
        if depth < 2 and random.random() < 0.6:
            marking_height = random.uniform(0.2, 0.8)
            marking_pos = base_loc + direction * (length * marking_height)
            
            bpy.ops.mesh.primitive_torus_add(
                major_radius=radius * 1.05,
                minor_radius=radius * 0.15,
                location=marking_pos
            )
            marking = bpy.context.active_object
            marking.name = "BirchMarking"
            
            # Dark material for markings
            if not bpy.data.materials.get("BirchMarking"):
                marking_mat = bpy.data.materials.new(name="BirchMarking")
                marking_mat.use_nodes = True
                marking_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.1, 0.1, 0.1, 1.0)
            else:
                marking_mat = bpy.data.materials.get("BirchMarking")
            
            marking.data.materials.append(marking_mat)
            marking.rotation_euler = (math.pi/2, 0, 0)
        
        end_loc = base_loc + direction * length
        
        if depth < max_depth:
            # Birch: delicate, upward-reaching branches
            num_branches = random.randint(2, 3) if depth < 3 else random.randint(1, 2)
            
            for i in range(num_branches):
                angle_xz = random.uniform(0, 2 * math.pi)
                # Mostly upward
                angle_elevation = random.uniform(math.pi/6, math.pi/3.5)
                
                new_dir = Vector((
                    math.sin(angle_elevation) * math.cos(angle_xz),
                    math.sin(angle_elevation) * math.sin(angle_xz),
                    math.cos(angle_elevation)
                ))
                
                rotation = direction.rotation_difference(Vector((0, 0, 1)))
                new_dir.rotate(rotation)
                
                # Thin branches
                new_length = length * random.uniform(0.55, 0.7)
                new_radius = radius * 0.6
                
                create_branch(end_loc, new_dir, new_length, new_radius, depth + 1)
    
    # Create trunk (slightly tapered)
    create_branch(Vector((0, 0, 0)), Vector((0, 0, 1)), trunk_height, trunk_radius, 0)
    
    # Add delicate leaves
    tree_objects = [obj for obj in bpy.context.scene.objects if "BirchBranch" in obj.name]
    
    for _ in range(leaf_count):
        if not tree_objects:
            continue
        branch = random.choice(tree_objects)
        
        local_pos = Vector((
            random.uniform(-0.2, 0.2),
            random.uniform(-0.2, 0.2),
            random.uniform(0.1, 0.4)
        ))
        world_pos = branch.matrix_world @ local_pos
        
        # Small, delicate leaves
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.1, location=world_pos)
        leaf = bpy.context.active_object
        leaf.scale = (1.2, 0.6, 0.4)
        leaf.name = "BirchLeaf"
        leaf.data.materials.append(leaf_mat)
    
    print("Birch tree generated!")

create_birch_tree()