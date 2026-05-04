import bpy
import bmesh
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_wooden_door():
    """Create a realistic wooden door with horizontal panels using boolean operations"""
    
    # Door dimensions (in meters) - slightly thicker for vintage look
    door_width = 0.9
    door_height = 2.1
    door_thickness = 0.055  # Increased thickness
    
    # Create main door slab (solid rectangular piece)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, door_height/2))
    door_slab = bpy.context.active_object
    door_slab.name = "Door_Slab"
    door_slab.scale = (door_width/2, door_thickness/2, door_height/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Panel recess parameters
    panel_inset = 0.08  # Distance from edge to panel
    panel_depth = 0.015  # Slightly deeper panels for vintage look
    
    # Define 3 panel areas to recess (matching the reference image)
    panel_configs = [
        {"z": 0.35, "height": 0.55},   # Bottom panel
        {"z": 1.05, "height": 0.55},   # Middle panel
        {"z": 1.75, "height": 0.55}    # Top panel
    ]
    
    # Create recessed panels by subtracting boxes from the door slab
    cutters = []
    for i, config in enumerate(panel_configs):
        # Create cutting box for front side
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(0, panel_depth/2, config["z"])
        )
        cutter_front = bpy.context.active_object
        cutter_front.name = f"Cutter_Front_{i}"
        cutter_front.scale = (
            (door_width - 2*panel_inset)/2,
            panel_depth/2,
            config["height"]/2
        )
        bpy.ops.object.transform_apply(scale=True)
        cutters.append(cutter_front)
        
        # Create cutting box for back side
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(0, -panel_depth/2, config["z"])
        )
        cutter_back = bpy.context.active_object
        cutter_back.name = f"Cutter_Back_{i}"
        cutter_back.scale = (
            (door_width - 2*panel_inset)/2,
            panel_depth/2,
            config["height"]/2
        )
        bpy.ops.object.transform_apply(scale=True)
        cutters.append(cutter_back)
    
    # Apply boolean difference operations to create recessed panels
    bpy.context.view_layer.objects.active = door_slab
    for cutter in cutters:
        # Add boolean modifier
        bool_modifier = door_slab.modifiers.new(name="Boolean", type='BOOLEAN')
        bool_modifier.operation = 'DIFFERENCE'
        bool_modifier.object = cutter
        
        # Apply the modifier
        bpy.ops.object.modifier_apply(modifier=bool_modifier.name)
        
        # Delete the cutter object
        bpy.data.objects.remove(cutter, do_unlink=True)
    
    # Add bevels to edges for realism
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bevel(offset=0.003, segments=2)  # Slightly larger bevel
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create door handle
    handle_height = 1.05
    handle_offset = 0.16  # Distance from edge
    
    # Handle base plate (more ornate circular design)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.035,  # Larger ornate base
        depth=0.012,   # Thicker base
        location=(handle_offset, door_thickness/2 - 0.011, handle_height)
    )
    handle_base = bpy.context.active_object
    handle_base.name = "Handle_Base"
    handle_base.rotation_euler = (1.5708, 0.5, 0)  # Rotate to face outward

    # Handle lever
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(handle_offset - 0.05, door_thickness/2-0.002, handle_height)
    )
    handle_lever = bpy.context.active_object
    handle_lever.name = "Handle_Lever"
    handle_lever.scale = (0.08, 0.005, 0.012)
    bpy.ops.object.transform_apply(scale=True)
    
    # Add smooth shading to handle
    handle_base.select_set(True)
    bpy.context.view_layer.objects.active = handle_base
    bpy.ops.object.shade_smooth()
    
    # Create materials
    create_wood_material()
    create_metal_material()
    
    # Apply wood material to door
    if len(door_slab.data.materials) == 0:
        door_slab.data.materials.append(bpy.data.materials.get("Wood_Material"))
    else:
        door_slab.data.materials[0] = bpy.data.materials.get("Wood_Material")
    
    # Apply metal material to handle parts
    if len(handle_base.data.materials) == 0:
        handle_base.data.materials.append(bpy.data.materials.get("Metal_Material"))
    else:
        handle_base.data.materials[0] = bpy.data.materials.get("Metal_Material")
    
    if len(handle_lever.data.materials) == 0:
        handle_lever.data.materials.append(bpy.data.materials.get("Metal_Material"))
    else:
        handle_lever.data.materials[0] = bpy.data.materials.get("Metal_Material")
    
    # Join handle parts together
    bpy.ops.object.select_all(action='DESELECT')
    handle_lever.select_set(True)
    handle_base.select_set(True)
    bpy.context.view_layer.objects.active = handle_base
    bpy.ops.object.join()
    handle_base.name = "Door_Handle"
    
    # Add smooth shading to door
    door_slab.select_set(True)
    bpy.context.view_layer.objects.active = door_slab
    bpy.ops.object.shade_smooth()
    
    door_slab.name = "Wooden_Door"
    
    print(f"Door created with dimensions: {door_width}m x {door_height}m x {door_thickness}m")
    
    return door_slab

def create_wood_material():
    """Create a realistic mahogany wood material"""
    mat = bpy.data.materials.new(name="Wood_Material")
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
    
    # Darker mahogany wood color
    node_bsdf.inputs['Base Color'].default_value = (0.25, 0.08, 0.04, 1.0)
    node_bsdf.inputs['Roughness'].default_value = 0.5
    node_bsdf.inputs['IOR'].default_value = 1.4
    
    # Add wood texture
    node_tex_coord = nodes.new(type='ShaderNodeTexCoord')
    node_tex_coord.location = (-800, 0)
    
    node_mapping = nodes.new(type='ShaderNodeMapping')
    node_mapping.location = (-600, 0)
    node_mapping.inputs['Scale'].default_value = (2, 2, 2)
    
    node_wave = nodes.new(type='ShaderNodeTexWave')
    node_wave.location = (-400, 100)
    node_wave.wave_type = 'BANDS'
    node_wave.inputs['Scale'].default_value = 18.0
    node_wave.inputs['Distortion'].default_value = 3.0
    node_wave.inputs['Detail'].default_value = 3.0
    
    node_color_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_color_ramp.location = (-200, 100)
    node_color_ramp.color_ramp.elements[0].color = (0.18, 0.05, 0.02, 1)
    node_color_ramp.color_ramp.elements[1].color = (0.32, 0.11, 0.06, 1)
    
    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-400, -100)
    node_noise.inputs['Scale'].default_value = 60.0
    node_noise.inputs['Detail'].default_value = 18.0
    
    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.location = (-200, -200)
    node_bump.inputs['Strength'].default_value = 0.15
    
    # Connect nodes
    links.new(node_tex_coord.outputs['Generated'], node_mapping.inputs['Vector'])
    links.new(node_mapping.outputs['Vector'], node_wave.inputs['Vector'])
    links.new(node_wave.outputs['Color'], node_color_ramp.inputs['Fac'])
    links.new(node_color_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])
    
    links.new(node_mapping.outputs['Vector'], node_noise.inputs['Vector'])
    links.new(node_noise.outputs['Fac'], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])
    
    links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_metal_material():
    """Create an antique brass material for the door handle"""
    mat = bpy.data.materials.new(name="Metal_Material")
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
    
    # Antique brass appearance
    node_bsdf.inputs['Base Color'].default_value = (0.72, 0.58, 0.35, 1.0)
    node_bsdf.inputs['Metallic'].default_value = 1.0
    node_bsdf.inputs['Roughness'].default_value = 0.4
    
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
    
    # Set render engine to Cycles for better quality
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128

# Main execution
if __name__ == "__main__":
    door = create_wooden_door()
    setup_scene()