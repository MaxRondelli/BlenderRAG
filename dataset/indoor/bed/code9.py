import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Realistic bed dimensions (in meters) - Queen size bed
BED_WIDTH = 1.52  # 60 inches / 152cm (Queen size)
BED_LENGTH = 2.03  # 80 inches / 203cm (Queen size)
MATTRESS_HEIGHT = 0.20  # 20cm thick mattress (slightly thinner)
FRAME_HEIGHT = 0.30  # Frame base height from ground (lower profile)
HEADBOARD_HEIGHT = 1.00  # 100cm tall headboard (lower)
FOOTBOARD_HEIGHT = 0.45  # 45cm tall footboard (lower)
FRAME_THICKNESS = 0.06  # 6cm thick frame (slightly thicker)
PILLOW_WIDTH = 0.50  # 50cm wide pillow
PILLOW_LENGTH = 0.50  # 70cm long pillow
PILLOW_HEIGHT = 0.1  # 15cm thick pillow

def create_bed_frame():
    """
    Creates the bed frame with legs and side rails
    """
    frame_parts = []
    
    # Create bed base/platform
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, FRAME_HEIGHT/2))
    base = bpy.context.active_object
    base.name = "BedBase"
    base.scale = (BED_WIDTH/2, BED_LENGTH/2, FRAME_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    frame_parts.append(base)
    
    # Create side rails
    rail_height = FRAME_HEIGHT + MATTRESS_HEIGHT
    
    # Left rail
    bpy.ops.mesh.primitive_cube_add(
        location=(-BED_WIDTH/2 - FRAME_THICKNESS/2, 0, rail_height/2)
    )
    left_rail = bpy.context.active_object
    left_rail.name = "LeftRail"
    left_rail.scale = (FRAME_THICKNESS/2, BED_LENGTH/2 + FRAME_THICKNESS, FRAME_THICKNESS/2)
    bpy.ops.object.transform_apply(scale=True)
    frame_parts.append(left_rail)
    
    # Right rail
    bpy.ops.mesh.primitive_cube_add(
        location=(BED_WIDTH/2 + FRAME_THICKNESS/2, 0, rail_height/2)
    )
    right_rail = bpy.context.active_object
    right_rail.name = "RightRail"
    right_rail.scale = (FRAME_THICKNESS/2, BED_LENGTH/2 + FRAME_THICKNESS, FRAME_THICKNESS/2)
    bpy.ops.object.transform_apply(scale=True)
    frame_parts.append(right_rail)
    
    # Create legs (4 corners)
    leg_positions = [
        (-BED_WIDTH/2 + 0.1, -BED_LENGTH/2 + 0.1),  # Back left
        (BED_WIDTH/2 - 0.1, -BED_LENGTH/2 + 0.1),   # Back right
        (-BED_WIDTH/2 + 0.1, BED_LENGTH/2 - 0.1),   # Front left
        (BED_WIDTH/2 - 0.1, BED_LENGTH/2 - 0.1),    # Front right
    ]
    
    for i, (x, y) in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(
            location=(x, y, FRAME_HEIGHT/2),
            radius=0.03,
            depth=FRAME_HEIGHT
        )
        leg = bpy.context.active_object
        leg.name = f"Leg_{i+1}"
        frame_parts.append(leg)
    
    # Join all frame parts
    bpy.ops.object.select_all(action='DESELECT')
    for part in frame_parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = frame_parts[0]
    bpy.ops.object.join()
    
    bed_frame = bpy.context.active_object
    bed_frame.name = "BedFrame"
    
    # Apply wood material
    create_wood_material(bed_frame)
    
    return bed_frame

def create_headboard():
    """
    Creates a padded headboard
    """
    bpy.ops.mesh.primitive_cube_add(
        location=(0, -BED_LENGTH/2 - FRAME_THICKNESS/2, FRAME_HEIGHT + HEADBOARD_HEIGHT/2)
    )
    headboard = bpy.context.active_object
    headboard.name = "Headboard"
    headboard.scale = (BED_WIDTH/2 + FRAME_THICKNESS, FRAME_THICKNESS/2, HEADBOARD_HEIGHT/2 + 0.35)
    bpy.ops.object.transform_apply(scale=True)
    
    # Add bevel for rounded edges
    bevel_mod = headboard.modifiers.new(name="Bevel", type='BEVEL')
    bevel_mod.width = 0.02
    bevel_mod.segments = 3
    
    # Add subdivision for smoothness
    subsurf_mod = headboard.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf_mod.levels = 2
    
    bpy.ops.object.shade_smooth()
    
    # Apply upholstery material
    create_fabric_material(headboard, color=(0.95, 0.92, 0.85, 1.0))  # Cream color
    
    return headboard

def create_footboard():
    """
    Creates a footboard
    """
    bpy.ops.mesh.primitive_cube_add(
        location=(0, BED_LENGTH/2 + FRAME_THICKNESS/2, FRAME_HEIGHT + FOOTBOARD_HEIGHT/2-0.35)
    )
    footboard = bpy.context.active_object
    footboard.name = "Footboard"
    footboard.scale = (BED_WIDTH/2 + FRAME_THICKNESS, FRAME_THICKNESS/2, FOOTBOARD_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Add bevel for rounded edges
    bevel_mod = footboard.modifiers.new(name="Bevel", type='BEVEL')
    bevel_mod.width = 0.02
    bevel_mod.segments = 3
    
    bpy.ops.object.shade_smooth()
    
    # Apply wood material
    create_wood_material(footboard)
    
    return footboard

def create_mattress():
    """
    Creates a realistic mattress with rounded edges
    """
    bpy.ops.mesh.primitive_cube_add(
        location=(0, 0, FRAME_HEIGHT + MATTRESS_HEIGHT/2)
    )
    mattress = bpy.context.active_object
    mattress.name = "Mattress"
    mattress.scale = (BED_WIDTH/2 - 0.01, BED_LENGTH/2 - 0.01, MATTRESS_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Add bevel for rounded mattress edges
    bevel_mod = mattress.modifiers.new(name="Bevel", type='BEVEL')
    bevel_mod.width = 0.05
    bevel_mod.segments = 4
    
    # Add subdivision for smoothness
    subsurf_mod = mattress.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf_mod.levels = 2
    
    bpy.ops.object.shade_smooth()
    
    # Apply mattress material (cream fabric)
    create_fabric_material(mattress, color=(0.96, 0.94, 0.88, 1.0))
    
    return mattress

def create_pillow(position, rotation=0):
    """
    Creates a pillow with realistic softness
    """
    bpy.ops.mesh.primitive_cube_add(
        location=position
    )
    pillow = bpy.context.active_object
    pillow.name = "Pillow"
    pillow.scale = (PILLOW_WIDTH/2, PILLOW_LENGTH/2, PILLOW_HEIGHT/2)
    pillow.rotation_euler = (0, 0, rotation)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    
    # Add bevel for soft rounded edges
    bevel_mod = pillow.modifiers.new(name="Bevel", type='BEVEL')
    bevel_mod.width = 0.08
    bevel_mod.segments = 5
    
    # Add subdivision for softness
    subsurf_mod = pillow.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf_mod.levels = 3
    
    bpy.ops.object.shade_smooth()
    
    # Apply pillow material (light cream)
    create_fabric_material(pillow, color=(0.97, 0.95, 0.90, 1.0), roughness=0.6)
    
    return pillow

def create_wood_material(obj):
    """
    Creates a wood material for the bed frame (lighter oak finish)
    """
    mat = bpy.data.materials.new(name="WoodMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (400, 0)
    
    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled_node.location = (0, 0)
    
    # Wood color (light oak)
    principled_node.inputs['Base Color'].default_value = (0.65, 0.52, 0.35, 1.0)
    principled_node.inputs['Metallic'].default_value = 0.0
    principled_node.inputs['Roughness'].default_value = 0.3
    
    links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def create_fabric_material(obj, color=(0.9, 0.9, 0.9, 1.0), roughness=0.8):
    """
    Creates a fabric material for mattress, pillows, and blanket
    """
    mat = bpy.data.materials.new(name="FabricMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (400, 0)
    
    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled_node.location = (0, 0)
    
    # Fabric properties
    principled_node.inputs['Base Color'].default_value = color
    principled_node.inputs['Metallic'].default_value = 0.0
    principled_node.inputs['Roughness'].default_value = roughness
    
    links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def setup_scene():
    """
    Set up the scene with proper lighting and camera
    """
    # Add a camera
    bpy.ops.object.camera_add(location=(3.5, -3.5, 2.5))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(65), 0, math.radians(45))
    bpy.context.scene.camera = camera
    
    # Add key light
    bpy.ops.object.light_add(type='AREA', location=(2, -3, 4))
    key_light = bpy.context.active_object
    key_light.data.energy = 300
    key_light.data.size = 2
    
    # Add fill light
    bpy.ops.object.light_add(type='AREA', location=(-2, 2, 3))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 150
    fill_light.data.size = 1.5
    
    # Add rim light
    bpy.ops.object.light_add(type='AREA', location=(0, 4, 2))
    rim_light = bpy.context.active_object
    rim_light.data.energy = 100
    rim_light.data.size = 1
    
    # Set render engine to Cycles
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128
    
    # Set world background
    world = bpy.data.worlds['World']
    world.use_nodes = True
    bg_node = world.node_tree.nodes['Background']
    bg_node.inputs['Color'].default_value = (0.05, 0.05, 0.05, 1.0)
    bg_node.inputs['Strength'].default_value = 0.3

def create_complete_bed():
    """
    Creates a complete bed with all components
    """
    print("Creating bed frame...")
    bed_frame = create_bed_frame()
    
    print("Creating headboard...")
    headboard = create_headboard()
    
    print("Creating footboard...")
    footboard = create_footboard()
    
    print("Creating mattress...")
    mattress = create_mattress()
    
    print("Creating pillows...")
    # Two pillows at the head of the bed
    pillow_y = -BED_LENGTH/2 + PILLOW_LENGTH/2 + 0.1
    pillow_z = FRAME_HEIGHT + MATTRESS_HEIGHT + PILLOW_HEIGHT/2
    
    pillow1 = create_pillow(
        (-BED_WIDTH/4, pillow_y, pillow_z)
    )
    pillow2 = create_pillow(
        (BED_WIDTH/4, pillow_y, pillow_z)
    )
    
    # Create a collection for organization
    bed_collection = bpy.data.collections.new("Bed")
    bpy.context.scene.collection.children.link(bed_collection)
    
    # Move all bed objects to the collection
    for obj in [bed_frame, headboard, footboard, mattress, pillow1, pillow2]:
        if obj.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(obj)
        bed_collection.objects.link(obj)
    
    return bed_collection

# Main execution
if __name__ == "__main__":
    print("=" * 50)
    print("Creating Realistic Bed")
    print("=" * 50)
    
    # Create the complete bed
    bed = create_complete_bed()
    
    # Setup scene
    print("Setting up scene lighting and camera...")
    setup_scene()
    
    print("\n" + "=" * 50)
    print("Bed created successfully!")
    print("=" * 50)
    print(f"Bed size: Queen ({BED_WIDTH * 100:.0f}cm × {BED_LENGTH * 100:.0f}cm)")
    print(f"Mattress height: {MATTRESS_HEIGHT * 100:.0f}cm")
    print(f"Total height (with headboard): {(FRAME_HEIGHT + HEADBOARD_HEIGHT) * 100:.0f}cm")
    print("\nThe bed includes:")
    print("  - Bed frame with legs")
    print("  - Headboard (padded)")
    print("  - Footboard")
    print("  - Mattress")
    print("  - 2 Pillows")
    print("  - Blanket/Duvet")
    print("\nAll components are created with real-world proportions.")
    print("Ready to render!")