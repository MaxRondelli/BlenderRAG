import bpy
import bmesh
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_glass_door():
    """Create a modern glass door with metal frame using boolean operations"""
    
    # Door dimensions (in meters)
    door_width = 0.9
    door_height = 2.1
    door_thickness = 0.045
    
    # Create main door frame (metal frame)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, door_height/2))
    door_frame = bpy.context.active_object
    door_frame.name = "Door_Frame"
    door_frame.scale = (door_width/2, door_thickness/2, door_height/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Create glass cutout (center area for glass)
    glass_inset = 0.05  # Frame width around the edges
    glass_width = door_width - 2*glass_inset
    glass_height = door_height - 2*glass_inset
    
    # Create cutting box for glass area
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, door_height/2)
    )
    glass_cutter = bpy.context.active_object
    glass_cutter.name = "Glass_Cutter"
    glass_cutter.scale = (
        glass_width/2,
        (door_thickness + 0.01)/2,
        glass_height/2
    )
    bpy.ops.object.transform_apply(scale=True)
    
    # Apply boolean difference to create frame
    bpy.context.view_layer.objects.active = door_frame
    bool_modifier = door_frame.modifiers.new(name="Boolean", type='BOOLEAN')
    bool_modifier.operation = 'DIFFERENCE'
    bool_modifier.object = glass_cutter
    bpy.ops.object.modifier_apply(modifier=bool_modifier.name)
    bpy.data.objects.remove(glass_cutter, do_unlink=True)
    
    # Create single continuous glass panel
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, door_height/2)
    )
    glass_panel = bpy.context.active_object
    glass_panel.name = "Glass_Panel"
    glass_panel.scale = (
        (glass_width - 0.01)/2,
        0.004,  # Very thin glass
        (glass_height - 0.01)/2
    )
    bpy.ops.object.transform_apply(scale=True)
    
    # Add horizontal dividers (optional - for multi-panel look)
    divider_thickness = 0.03
    divider_positions = [0.7, 1.4]  # Heights for horizontal dividers
    
    dividers = []
    for pos in divider_positions:
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(0, 0, pos)
        )
        divider = bpy.context.active_object
        divider.name = f"Divider_{pos}"
        divider.scale = (
            glass_width/2,
            door_thickness/2,
            divider_thickness/2
        )
        bpy.ops.object.transform_apply(scale=True)
        dividers.append(divider)
    
    # Add bevels to frame edges for realism
    bpy.context.view_layer.objects.active = door_frame
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bevel(offset=0.002, segments=2)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create realistic door handle
    handle_height = 1.05  # MODIFY THIS to move handle up/down (Z-axis)
    handle_offset_x = door_width/2 + -0.3  # Position with correct offset
    handle_depth = 0.04  # How far handle extends from door
    handle_length = 0.30  # Vertical length of handle bar
    handle_y_offset = -0.021  # ADD VALUE to move handle forward/backward
    
    # Handle mounting plates (flush against door)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.020,
        depth=0.008,
        location=(handle_offset_x, door_thickness/2 + 0.004 + handle_y_offset, handle_height + handle_length/2 - 0.02)
    )
    handle_mount1 = bpy.context.active_object
    handle_mount1.name = "Handle_Mount1"
    handle_mount1.rotation_euler = (1.5708, 0, 0)  # Flat against door

    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.020,
        depth=0.008,
        location=(handle_offset_x, door_thickness/2 + 0.004 + handle_y_offset, handle_height - handle_length/2 + 0.02)
    )
    handle_mount2 = bpy.context.active_object
    handle_mount2.name = "Handle_Mount2"
    handle_mount2.rotation_euler = (1.5708, 0, 0)  # Flat against door
    
    # Connecting rods (extend from door to grab bar)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.010,
        depth=handle_depth,
        location=(handle_offset_x, door_thickness/2 + handle_depth/2 + handle_y_offset, handle_height + handle_length/2 - 0.02)
    )
    handle_rod1 = bpy.context.active_object
    handle_rod1.name = "Handle_Rod1"
    handle_rod1.rotation_euler = (1.5708, 0, 0)

    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.010,
        depth=handle_depth,
        location=(handle_offset_x, door_thickness/2 + handle_depth/2 + handle_y_offset, handle_height - handle_length/2 + 0.02)
    )
    handle_rod2 = bpy.context.active_object
    handle_rod2.name = "Handle_Rod2"
    handle_rod2.rotation_euler = (1.5708, 0, 0)

    # Handle grab bar (vertical bar you hold)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.013,
        depth=handle_length,
        location=(handle_offset_x, door_thickness/2 + handle_depth + handle_y_offset, handle_height)
    )
    handle_bar = bpy.context.active_object
    handle_bar.name = "Handle_Bar"
    handle_bar.rotation_euler = (0, 0, 0)  # Vertical orientation
    
    # Add smooth shading to handle parts
    for obj in [handle_bar, handle_mount1, handle_mount2, handle_rod1, handle_rod2]:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
        obj.select_set(False)
    
    # Create materials
    create_metal_frame_material()
    create_glass_material()
    create_handle_material()
    
    # Apply metal material to frame and dividers
    if len(door_frame.data.materials) == 0:
        door_frame.data.materials.append(bpy.data.materials.get("Metal_Frame_Material"))
    else:
        door_frame.data.materials[0] = bpy.data.materials.get("Metal_Frame_Material")
    
    for divider in dividers:
        if len(divider.data.materials) == 0:
            divider.data.materials.append(bpy.data.materials.get("Metal_Frame_Material"))
        else:
            divider.data.materials[0] = bpy.data.materials.get("Metal_Frame_Material")
    
    # Apply glass material to glass panel
    if len(glass_panel.data.materials) == 0:
        glass_panel.data.materials.append(bpy.data.materials.get("Glass_Material"))
    else:
        glass_panel.data.materials[0] = bpy.data.materials.get("Glass_Material")
    
    # Apply handle material to handle parts
    for obj in [handle_bar, handle_mount1, handle_mount2, handle_rod1, handle_rod2]:
        if len(obj.data.materials) == 0:
            obj.data.materials.append(bpy.data.materials.get("Handle_Material"))
        else:
            obj.data.materials[0] = bpy.data.materials.get("Handle_Material")
    
    # Join handle parts together
    bpy.ops.object.select_all(action='DESELECT')
    handle_bar.select_set(True)
    handle_mount1.select_set(True)
    handle_mount2.select_set(True)
    handle_rod1.select_set(True)
    handle_rod2.select_set(True)
    bpy.context.view_layer.objects.active = handle_bar
    bpy.ops.object.join()
    handle_bar.name = "Door_Handle"
    
    # Add smooth shading to frame
    door_frame.select_set(True)
    bpy.context.view_layer.objects.active = door_frame
    bpy.ops.object.shade_smooth()
    
    # Add smooth shading to dividers
    for divider in dividers:
        divider.select_set(True)
        bpy.context.view_layer.objects.active = divider
        bpy.ops.object.shade_smooth()
    
    door_frame.name = "Glass_Door_Frame"
    
    print(f"Glass door created with dimensions: {door_width}m x {door_height}m x {door_thickness}m")
    
    return door_frame

def create_metal_frame_material():
    """Create a black metal material for the door frame"""
    mat = bpy.data.materials.new(name="Metal_Frame_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create nodes
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (400, 0)
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    
    # Black metal appearance
    node_bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1.0)
    node_bsdf.inputs['Metallic'].default_value = 1.0
    node_bsdf.inputs['Roughness'].default_value = 0.2
    
    # Add subtle texture
    node_tex_coord = nodes.new(type='ShaderNodeTexCoord')
    node_tex_coord.location = (-600, 0)
    
    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-400, -100)
    node_noise.inputs['Scale'].default_value = 100.0
    node_noise.inputs['Detail'].default_value = 8.0
    
    node_color_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_color_ramp.location = (-200, -100)
    node_color_ramp.color_ramp.elements[0].color = (0.03, 0.03, 0.03, 1)
    node_color_ramp.color_ramp.elements[1].color = (0.07, 0.07, 0.07, 1)
    
    # Connect nodes
    links.new(node_tex_coord.outputs['Generated'], node_noise.inputs['Vector'])
    links.new(node_noise.outputs['Fac'], node_color_ramp.inputs['Fac'])
    links.new(node_color_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])
    links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_glass_material():
    """Create a transparent glass material"""
    mat = bpy.data.materials.new(name="Glass_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create nodes
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (200, 0)
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    
    # Glass properties - more transparent
    node_bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.98, 1.0)
    node_bsdf.inputs['Alpha'].default_value = 0.15
    node_bsdf.inputs['IOR'].default_value = 1.45
    node_bsdf.inputs['Roughness'].default_value = 0.0
    # Use Transmission Weight for Blender 4.0+ compatibility
    try:
        node_bsdf.inputs['Transmission Weight'].default_value = 1.0
    except KeyError:
        node_bsdf.inputs['Transmission'].default_value = 1.0
    
    # Set material blend mode
    mat.blend_method = 'BLEND'
    if hasattr(mat, 'shadow_method'):
        mat.shadow_method = 'HASHED'
    
    links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_handle_material():
    """Create a brushed steel material for the door handle"""
    mat = bpy.data.materials.new(name="Handle_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create nodes
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (200, 0)
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    
    # Brushed steel appearance
    node_bsdf.inputs['Base Color'].default_value = (0.7, 0.7, 0.7, 1.0)
    node_bsdf.inputs['Metallic'].default_value = 1.0
    node_bsdf.inputs['Roughness'].default_value = 0.3
    
    links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def setup_scene():
    """Setup camera and lighting for the scene"""
    # Add camera
    bpy.ops.object.camera_add(location=(3, -3, 2))
    camera = bpy.context.active_object
    camera.rotation_euler = (1.1, 0, 0.785)
    bpy.context.scene.camera = camera
    
    # Add lighting
    # Key light
    bpy.ops.object.light_add(type='AREA', location=(2, -2, 3))
    key_light = bpy.context.active_object
    key_light.data.energy = 200
    key_light.data.size = 2
    
    # Fill light
    bpy.ops.object.light_add(type='AREA', location=(-2, -1, 2))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 100
    fill_light.data.size = 2
    
    # Back light for glass visibility
    bpy.ops.object.light_add(type='AREA', location=(0, 2, 1.5))
    back_light = bpy.context.active_object
    back_light.data.energy = 80
    back_light.data.size = 1.5
    
    # Set render engine to Cycles for better quality
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128
    
    # Enable transparency in viewport
    bpy.context.scene.render.film_transparent = False

# Main execution
if __name__ == "__main__":
    door = create_glass_door()
    setup_scene()