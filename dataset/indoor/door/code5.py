import bpy
import bmesh
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_wooden_door():
    """Create a realistic wooden door with vertical panels using boolean operations"""
    
    # Door dimensions (in meters)
    door_width = 0.9
    door_height = 2.1
    door_thickness = 0.045
    
    # Create main door slab (solid rectangular piece)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, door_height/2))
    door_slab = bpy.context.active_object
    door_slab.name = "Door_Slab"
    door_slab.scale = (door_width/2, door_thickness/2, door_height/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Panel recess parameters
    panel_inset = 0.08  # Distance from edge to panel
    panel_depth = 0.012  # How deep panels are recessed into door
    
    # Define 3 vertical panel areas to recess
    panel_configs = [
        {"x": -0.2, "width": 0.18},   # Left panel
        {"x": 0.0, "width": 0.18},    # Middle panel
        {"x": 0.2, "width": 0.18}     # Right panel
    ]
    
    # Create recessed panels by subtracting boxes from the door slab
    cutters = []
    for i, config in enumerate(panel_configs):
        # Create cutting box for front side
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(config["x"], panel_depth/2, door_height/2)
        )
        cutter_front = bpy.context.active_object
        cutter_front.name = f"Cutter_Front_{i}"
        cutter_front.scale = (
            config["width"]/2,
            panel_depth/2,
            (door_height - 2*panel_inset)/2
        )
        bpy.ops.object.transform_apply(scale=True)
        cutters.append(cutter_front)
        
        # Create cutting box for back side
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(config["x"], -panel_depth/2, door_height/2)
        )
        cutter_back = bpy.context.active_object
        cutter_back.name = f"Cutter_Back_{i}"
        cutter_back.scale = (
            config["width"]/2,
            panel_depth/2,
            (door_height - 2*panel_inset)/2
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
    bpy.ops.mesh.bevel(offset=0.002, segments=2)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create door handle
    handle_height = 1.05
    handle_offset = 0.16  # Distance from edge
    
    # Handle base plate (rectangular)
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(handle_offset, door_thickness/2 - 0.008, handle_height)
    )
    handle_base = bpy.context.active_object
    handle_base.name = "Handle_Base"
    handle_base.scale = (0.035, 0.008, 0.12)
    bpy.ops.object.transform_apply(scale=True)

    # Handle lever (rectangular modern style)
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(handle_offset - 0.06, door_thickness/2-0.002, handle_height)
    )
    handle_lever = bpy.context.active_object
    handle_lever.name = "Handle_Lever"
    handle_lever.scale = (0.09, 0.008, 0.018)
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
    """Create a realistic dark charcoal wood material"""
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
    
    # Dark charcoal wood color
    node_bsdf.inputs['Base Color'].default_value = (0.15, 0.12, 0.10, 1.0)
    node_bsdf.inputs['Roughness'].default_value = 0.6
    
    # Add wood texture
    node_tex_coord = nodes.new(type='ShaderNodeTexCoord')
    node_tex_coord.location = (-800, 0)
    
    node_mapping = nodes.new(type='ShaderNodeMapping')
    node_mapping.location = (-600, 0)
    node_mapping.inputs['Scale'].default_value = (1, 8, 1)
    node_mapping.inputs['Rotation'].default_value = (0, 0, 1.5708)
    
    node_wave = nodes.new(type='ShaderNodeTexWave')
    node_wave.location = (-400, 100)
    node_wave.wave_type = 'BANDS'
    node_wave.inputs['Scale'].default_value = 20.0
    node_wave.inputs['Distortion'].default_value = 1.5
    node_wave.inputs['Detail'].default_value = 3.0
    
    node_color_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_color_ramp.location = (-200, 100)
    node_color_ramp.color_ramp.elements[0].color = (0.08, 0.06, 0.05, 1)
    node_color_ramp.color_ramp.elements[1].color = (0.22, 0.18, 0.15, 1)
    
    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-400, -100)
    node_noise.inputs['Scale'].default_value = 60.0
    node_noise.inputs['Detail'].default_value = 12.0
    
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
    """Create a dark metal material for the door handle"""
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
    
    # Dark brushed metal appearance
    node_bsdf.inputs['Base Color'].default_value = (0.3, 0.3, 0.3, 1.0)
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