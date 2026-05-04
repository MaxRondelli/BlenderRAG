import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove existing materials
for material in bpy.data.materials:
    bpy.data.materials.remove(material)

def create_material(name, color, metallic=0.0, roughness=0.5):
    """Create a material with given properties"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Create Principled BSDF
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_bsdf.inputs['Base Color'].default_value = (*color, 1)
    node_bsdf.inputs['Metallic'].default_value = metallic
    node_bsdf.inputs['Roughness'].default_value = roughness
    
    # Create output node
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (300, 0)
    
    # Link nodes
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_fridge_body(location=(0, 0, 0), size=(0.9, 0.8, 1.8)):
    """Create the main body of the refrigerator"""
    
    # Main body
    bpy.ops.mesh.primitive_cube_add(
        location=(location[0], location[1], location[2] + size[2]/2),
        scale=(size[0]/2, size[1]/2, size[2]/2)
    )
    body = bpy.context.active_object
    body.name = "Fridge_Body"
    
    # Create material for body (dark stainless steel)
    body_mat = create_material("FridgeMaterial", (0.15, 0.15, 0.18), metallic=0.85, roughness=0.15)
    body.data.materials.append(body_mat)
    
    return body

def create_fridge_door(location, size, name="Door"):
    """Create a refrigerator door"""
    
    # Door panel
    bpy.ops.mesh.primitive_cube_add(
        location=location,
        scale=(size[0]/2, size[1]/2, size[2]/2)
    )
    door = bpy.context.active_object
    door.name = name
    
    # Create material for door (black stainless steel)
    door_mat = create_material(f"{name}_Material", (0.12, 0.12, 0.15), metallic=0.9, roughness=0.1)
    door.data.materials.append(door_mat)
    
    return door

def create_door_handle(location, size, orientation='vertical'):
    """Create a door handle"""
    
    if orientation == 'vertical':
        bpy.ops.mesh.primitive_cylinder_add(
            location=location,
            rotation=(0, math.radians(90), 0),
            scale=(0.08, size/2, 0.015)
        )
    else:
        bpy.ops.mesh.primitive_cylinder_add(
            location=location,
            rotation=(0, 0, math.radians(90)),
            scale=(0.015, size/2, 0.015)
        )
    
    handle = bpy.context.active_object
    handle.name = "Handle"
    
    # Create metallic material for handle (brushed steel)
    handle_mat = create_material("HandleMaterial", (0.4, 0.4, 0.45), metallic=0.95, roughness=0.1)
    handle.data.materials.append(handle_mat)
    
    return handle

def create_fridge(location=(0, 0, 0)):
    """
    Create a complete refrigerator
    
    Parameters:
    - location: (x, y, z) position
    """
    
    # Dimensions
    fridge_width = 0.9
    fridge_depth = 0.8
    fridge_height = 1.8
    
    freezer_height = 0.6
    fridge_door_height = fridge_height - freezer_height
    
    door_thickness = 0.08  # Thicker doors
    door_gap = 0.02
    
    # Create main body
    body = create_fridge_body(
        location=location,
        size=(fridge_width, fridge_depth, fridge_height)
    )
    
    # Create freezer door (top)
    freezer_door_z = location[2] + fridge_height - freezer_height/2
    freezer_door_y = location[1] + fridge_depth/2 + door_thickness/2 + door_gap
    
    freezer_door = create_fridge_door(
        location=(location[0], freezer_door_y, freezer_door_z),
        size=(fridge_width - 0.02, door_thickness, freezer_height - 0.02),
        name="Freezer_Door"
    )
    
    # Create freezer handle
    freezer_handle = create_door_handle(
        location=(location[0] + fridge_width/2 - 0.1, freezer_door_y + door_thickness/2, freezer_door_z - 0.1),
        size=0.1,
        orientation='vertical'
    )
    
    # Create main fridge door (bottom)
    fridge_door_z = location[2] + fridge_door_height/2
    fridge_door_y = location[1] + fridge_depth/2 + door_thickness/2 + door_gap
    
    main_door = create_fridge_door(
        location=(location[0], fridge_door_y, fridge_door_z),
        size=(fridge_width - 0.02, door_thickness, fridge_door_height - 0.02),
        name="Main_Door"
    )
    
    # Create main door handle
    main_handle = create_door_handle(
        location=(location[0] + fridge_width/2 - 0.1, fridge_door_y + door_thickness/2 + 0.02, fridge_door_z + fridge_door_height/2 - 0.15),
        size=0.1,
        orientation='vertical'
    )
    
    # Add ice/water dispenser panel on freezer door
    dispenser_panel = create_dispenser_panel(
        location=(location[0] - fridge_width/4, freezer_door_y + door_thickness/2 + 0.005, freezer_door_z )
    )
    
    # Add some detail lines/grooves on doors
    add_door_details(freezer_door, main_door)
    
    print("Refrigerator generated successfully!")
    
    return body

def create_dispenser_panel(location):
    """Create ice/water dispenser panel"""
    
    # Dispenser housing
    bpy.ops.mesh.primitive_cube_add(
        location=location,
        scale=(0.15, 0.02, 0.25)
    )
    dispenser = bpy.context.active_object
    dispenser.name = "Dispenser"
    
    # Dark plastic material
    dispenser_mat = create_material("DispenserMaterial", (0.05, 0.05, 0.08), metallic=0.0, roughness=0.6)
    dispenser.data.materials.append(dispenser_mat)
    
    # Dispenser opening
    bpy.ops.mesh.primitive_cube_add(
        location=(location[0], location[1] + 0.01, location[2] - 0.12),
        scale=(0.08, 0.015, 0.08)
    )
    opening = bpy.context.active_object
    opening.name = "Dispenser_Opening"
    
    # Very dark material for opening
    opening_mat = create_material("OpeningMaterial", (0.02, 0.02, 0.02), metallic=0.0, roughness=0.8)
    opening.data.materials.append(opening_mat)
    
    return dispenser

def add_door_details(freezer_door, main_door):
    """Add subtle details to doors"""
    
    # Add bevel modifier for rounded edges
    for door in [freezer_door, main_door]:
        bevel = door.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width = 0.01
        bevel.segments = 3
        bevel.limit_method = 'ANGLE'

def create_floor():
    """Create a floor surface"""
    bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0), scale=(5, 5, 1))
    floor = bpy.context.active_object
    floor.name = "Floor"
    
    floor_mat = create_material("FloorMaterial", (0.7, 0.7, 0.72), metallic=0.0, roughness=0.4)
    floor.data.materials.append(floor_mat)

def setup_scene():
    """Setup camera and lighting"""
    
    # Add camera
    bpy.ops.object.camera_add(
        location=(3, -3, 2),
        rotation=(math.radians(70), 0, math.radians(45))
    )
    camera = bpy.context.active_object
    camera.name = "Camera"
    bpy.context.scene.camera = camera
    
    # Add key light (sun)
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 8))
    sun = bpy.context.active_object
    sun.name = "KeyLight"
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(45), 0, math.radians(45))
    
    # Add fill light (area)
    bpy.ops.object.light_add(type='AREA', location=(-3, -2, 3))
    area = bpy.context.active_object
    area.name = "FillLight"
    area.data.energy = 100
    area.data.size = 3.0
    
    # Add rim light
    bpy.ops.object.light_add(type='POINT', location=(2, 3, 2.5))
    point = bpy.context.active_object
    point.name = "RimLight"
    point.data.energy = 150
    
    print("Scene setup complete!")

def create_fridge_scene():
    """Generate a complete scene with a refrigerator"""
    

    # Create the refrigerator
    fridge = create_fridge(location=(0, 0, 0))
    setup_scene()
    print("Fridge scene generated successfully!")

# Generate the fridge scene
create_fridge_scene()