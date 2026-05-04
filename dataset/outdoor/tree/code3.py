import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_oak_tree(trunk_height=5, trunk_radius=0.5, max_depth=5, leaf_count=500):
    """Generate a sturdy oak tree with broad canopy"""
    clear_scene()
    random.seed(303)
    
    # Materials
    bark_mat = bpy.data.materials.new(name="OakBark")
    bark_mat.use_nodes = True
    bark_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.3, 0.22, 0.15, 1.0)
    bark_mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.95
    
    leaf_mat = bpy.data.materials.new(name="OakLeaves")
    leaf_mat.use_nodes = True
    leaf_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.15, 0.45, 0.1, 1.0)
    
    def create_branch(base_loc, direction, length, radius, depth):
        if depth > max_depth or length < 0.4:
            return
        
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length,
                                            location=base_loc + direction * (length / 2))
        branch = bpy.context.active_object
        branch.name = f"OakBranch_D{depth}"
        
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
            # Oak has thick, spreading branches
            num_branches = random.randint(3, 5) if depth < 2 else random.randint(2, 4)
            
            for i in range(num_branches):
                angle_xz = (2 * math.pi * i / num_branches) + random.uniform(-0.5, 0.5)
                # More horizontal spread
                angle_elevation = random.uniform(math.pi/4, math.pi/2.5)
                
                new_dir = Vector((
                    math.sin(angle_elevation) * math.cos(angle_xz),
                    math.sin(angle_elevation) * math.sin(angle_xz),
                    math.cos(angle_elevation)
                ))
                
                rotation = direction.rotation_difference(Vector((0, 0, 1)))
                new_dir.rotate(rotation)
                
                # Oak branches stay thick longer
                new_length = length * random.uniform(0.65, 0.8)
                new_radius = radius * random.uniform(0.75, 0.85)
                
                create_branch(end_loc, new_dir, new_length, new_radius, depth + 1)
    
    # Create trunk
    create_branch(Vector((0, 0, 0)), Vector((0, 0, 1)), trunk_height, trunk_radius, 0)
    
    # Add dense foliage
    tree_objects = [obj for obj in bpy.context.scene.objects if "OakBranch" in obj.name]
    
    for _ in range(leaf_count):
        if not tree_objects:
            continue
        branch = random.choice(tree_objects)
        
        local_pos = Vector((
            random.uniform(-0.5, 0.5),
            random.uniform(-0.5, 0.5),
            random.uniform(-0.3, 0.3)
        ))
        world_pos = branch.matrix_world @ local_pos
        
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=random.uniform(0.2, 0.35), 
                                               location=world_pos)
        leaf = bpy.context.active_object
        leaf.name = "OakLeaf"
        leaf.data.materials.append(leaf_mat)
        leaf.rotation_euler = (random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi), 
                               random.uniform(0, 2*math.pi))
    
    print("Oak tree generated!")

create_oak_tree()