import bpy
import bmesh
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_metal_door():
    """Create a painted metal door with vertical panels using boolean operations"""
    
    # Door dimensions (in meters)
    door_width = 0.9
    door_height = 2.1
    door_thickness = 0.035
    
    # Create main door slab (solid rectangular piece)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, door_height/2))
    door_slab = bpy.context.active_object
    door_slab.name = "Door_Slab"
    door_slab.scale = (door_width/2, door_thickness/2, door_height/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Panel recess parameters
    panel_inset = 0.1  # Distance from edge to panel
    panel_depth = 0.008  # How deep panels are recessed into door
    
    # Define 3 vertical panel areas to recess
    panel_configs = [
        {"x": -0.2, "width": 0.18},   # Left panel
        {"x": 0, "width": 0.18},      # Middle panel  
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
    bpy.ops.mesh.bevel(offset=0.001, segments=2)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create door handle
    handle_height = 1.05
    handle_offset = 0.16  # Distance from edge
    
    # Handle base (spherical)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.035,
        location=(handle_offset, door_thickness/2 + 0.02, handle_height)
    )
    handle_base = bpy.context.active_object
    handle_base.name = "Handle_Base"

    # Handle stem
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.012,
        depth=0.035,
        location=(handle_offset, door_thickness/2 + 0.003, handle_height)
    )
    handle_stem = bpy.context.active_object
    handle_stem.name = "Handle_Stem"
    handle_stem.rotation_euler = (1.5708, 0, 0)  # Rotate to face outward
    
    # Add smooth shading to handle
    handle_base.select_set(True)
    bpy.context.view_layer.objects.active = handle_base
    bpy.ops.object.shade_smooth()
    
    # Create materials
    create_painted_metal_material()
    create_chrome_material()
    
    # Apply painted metal material to door
    if len(door_slab.data.materials) == 0:
        door_slab.data.materials.append(bpy.data.materials.get("Painted_Metal_Material"))
    else:
        door_slab.data.materials[0] = bpy.data.materials.get("Painted_Metal_Material")
    
    # Apply chrome material to handle parts
    if len(handle_base.data.materials) == 0:
        handle_base.data.materials.append(bpy.data.materials.get("Chrome_Material"))
    else:
        handle_base.data.materials[0] = bpy.data.materials.get("Chrome_Material")
    
    if len(handle_stem.data.materials) == 0:
        handle_stem.data.materials.append(bpy.data.materials.get("Chrome_Material"))
    else:
        handle_stem.data.materials[0] = bpy.data.materials.get("Chrome_Material")
    
    # Join handle parts together
    bpy.ops.object.select_all(action='DESELECT')
    handle_stem.select_set(True)
    handle_base.select_set(True)
    bpy.context.view_layer.objects.active = handle_base
    bpy.ops.object.join()
    handle_base.name = "Door_Handle"
    
    # Add smooth shading to door
    door_slab.select_set(True)
    bpy.context.view_layer.objects.active = door_slab
    bpy.ops.object.shade_smooth()
    
    door_slab.name = "Metal_Door"
    
    print(f"Door created with dimensions: {door_width}m x {door_height}m x {door_thickness}m")
    
    return door_slab

def create_painted_metal_material():
    """Create a painted metal material"""
    mat = bpy.data.materials.new(name="Painted_Metal_Material")
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
    
    # Dark blue painted metal
    node_bsdf.inputs['Base Color'].default_value = (0.15, 0.25, 0.45, 1.0)
    node_bsdf.inputs['Roughness'].default_value = 0.2
    node_bsdf.inputs['Metallic'].default_value = 0.1
    
    # Add subtle texture
    node_tex_coord = nodes.new(type='ShaderNodeTexCoord')
    node_tex_coord.location = (-600, 0)
    
    node_mapping = nodes.new(type='ShaderNodeMapping')
    node_mapping.location = (-400, 0)
    node_mapping.inputs['Scale'].default_value = (50, 50, 50)
    
    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-200, 0)
    node_noise.inputs['Scale'].default_value = 100.0
    node_noise.inputs['Detail'].default_value = 5.0
    
    node_color_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_color_ramp.location = (-50, 100)
    node_color_ramp.color_ramp.elements[0].color = (0.12, 0.22, 0.42, 1)
    node_color_ramp.color_ramp.elements[1].color = (0.18, 0.28, 0.48, 1)
    
    # Connect nodes
    links.new(node_tex_coord.outputs['Generated'], node_mapping.inputs['Vector'])
    links.new(node_mapping.outputs['Vector'], node_noise.inputs['Vector'])
    links.new(node_noise.outputs['Fac'], node_color_ramp.inputs['Fac'])
    links.new(node_color_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])
    
    links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_chrome_material():
    """Create a chrome material for the door handle"""
    mat = bpy.data.materials.new(name="Chrome_Material")
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
    
    # Chrome appearance
    node_bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)
    node_bsdf.inputs['Metallic'].default_value = 1.0
    node_bsdf.inputs['Roughness'].default_value = 0.05
    
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
    door = create_metal_door()
    setup_scene()