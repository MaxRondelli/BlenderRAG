import bpy
import math

# Ensure we're in object mode first
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

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

def create_pot(location=(0, 0, 0), radius=0.32, height=0.38):
    """
    Create a realistic cooking pot with lid and handles
    
    Parameters:
    - location: (x, y, z) position
    - radius: radius of the pot
    - height: height of the pot
    """
    
    # Create pot body using a cylinder with more segments
    bpy.ops.mesh.primitive_cylinder_add(
        location=(location[0], location[1], location[2] + height/2),
        scale=(radius, radius, height/2),
        vertices=64
    )
    pot_body = bpy.context.active_object
    pot_body.name = "Pot_Body"
    
    # Enter edit mode to create the hollow interior
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    
    # Select top face
    bpy.ops.mesh.select_mode(type='FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    for poly in pot_body.data.polygons:
        if poly.normal.z > 0.9:  # Top face
            poly.select = True
    
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Inset the top face for wall thickness - slightly thicker walls
    bpy.ops.mesh.inset(thickness=0.024, depth=0)
    
    # Extrude down to create hollow interior
    bpy.ops.mesh.extrude_region_move(
        TRANSFORM_OT_translate={"value": (0, 0, -height * 0.85)}
    )
    
    # Slightly taper the interior
    bpy.ops.transform.resize(value=(0.98, 0.98, 1.0))
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add Subdivision Surface for smooth appearance
    subsurf = pot_body.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3
    
    # Add Bevel for rounded edges
    bevel = pot_body.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.004
    bevel.segments = 4
    bevel.limit_method = 'ANGLE'
    
    # Create pot material (matte black non-stick)
    pot_mat = create_material("PotMaterial", (0.08, 0.08, 0.08), metallic=0.05, roughness=0.85)
    pot_body.data.materials.append(pot_mat)
    
    # Create pot rim (rolled edge) - copper accent
    bpy.ops.mesh.primitive_torus_add(
        location=(location[0], location[1], location[2] + height + 0.005),
        major_radius=radius - 0.008,
        minor_radius=0.012,
        major_segments=64,
        minor_segments=16
    )
    rim = bpy.context.active_object
    rim.name = "Pot_Rim"
    
    rim_mat = create_material("RimMaterial", (0.72, 0.45, 0.20), metallic=0.85, roughness=0.15)
    rim.data.materials.append(rim_mat)
    
    # Create pot handles (elegant loop handles) - copper colored
    handle_height = location[2] + height * 0.7
    handle_offset = radius + 0.065
    
    handle_positions = [
        (location[0] + handle_offset -0.025, location[1], handle_height),
        (location[0] - handle_offset +0.025, location[1], handle_height)
    ]
    
    for i, (hx, hy, hz) in enumerate(handle_positions):
        # Create torus for main handle loop - slightly thicker
        bpy.ops.mesh.primitive_torus_add(
            location=(hx, hy, hz),
            rotation=(0, math.radians(90), 0),
            major_radius=0.055,
            minor_radius=0.014,
            major_segments=32,
            minor_segments=12
        )
        handle = bpy.context.active_object
        handle.name = f"Pot_Handle_{i+1}"
        
        handle_subsurf = handle.modifiers.new(name="Subdivision", type='SUBSURF')
        handle_subsurf.levels = 2
        
        # Handle material (brushed copper)
        handle_mat = create_material(f"PotHandleMat_{i}", (0.72, 0.45, 0.20), metallic=0.90, roughness=0.25)
        handle.data.materials.append(handle_mat)
        
        # Handle mounting bracket
        mount_x = location[0] + (radius * 0.98 if i == 0 else -(radius * 0.98))
        
        # Upper mount
        bpy.ops.mesh.primitive_cylinder_add(
            location=(mount_x, hy, hz + 0.035),
            rotation=(0, math.radians(90), 0),
            scale=(0.013, 0.022, 0.013),
            vertices=16
        )
        upper_mount = bpy.context.active_object
        upper_mount.name = f"Pot_Handle_Mount_Upper_{i+1}"
        upper_mount.data.materials.append(handle_mat)
        
        # Lower mount
        bpy.ops.mesh.primitive_cylinder_add(
            location=(mount_x, hy, hz - 0.035),
            rotation=(0, math.radians(90), 0),
            scale=(0.013, 0.022, 0.013),
            vertices=16
        )
        lower_mount = bpy.context.active_object
        lower_mount.name = f"Pot_Handle_Mount_Lower_{i+1}"
        lower_mount.data.materials.append(handle_mat)
        
        # Add connecting piece between handle and mounts
        connector_x = location[0] + (radius * 0.99 if i == 0 else -(radius * 0.99)) + (0.015 if i == 0 else -0.015)
        
        bpy.ops.mesh.primitive_cube_add(
            location=(connector_x, hy, hz),
            scale=(0.02, 0.015, 0.055)
        )
        connector = bpy.context.active_object
        connector.name = f"Pot_Handle_Connector_{i+1}"
        
        # Add bevel to connector for smooth edges
        connector_bevel = connector.modifiers.new(name="Bevel", type='BEVEL')
        connector_bevel.width = 0.003
        connector_bevel.segments = 2
        
        connector.data.materials.append(handle_mat)
    
    # Create realistic pot lid - matte black
    lid_z = location[2] + height + 0.025
    
    # Lid main body (slightly domed)
    bpy.ops.mesh.primitive_uv_sphere_add(
        location=(location[0], location[1], lid_z + 0.025),
        scale=(radius + 0.015, radius + 0.015, 0.04),
        segments=64,
        ring_count=32
    )
    lid = bpy.context.active_object
    lid.name = "Pot_Lid"
    
    # Remove bottom half of sphere
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    for vert in lid.data.vertices:
        if vert.co.z < 0:
            vert.select = True
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add subdivision for smooth lid
    lid_subsurf = lid.modifiers.new(name="Subdivision", type='SUBSURF')
    lid_subsurf.levels = 3
    
    lid_mat = create_material("LidMaterial", (0.10, 0.10, 0.10), metallic=0.05, roughness=0.80)
    lid.data.materials.append(lid_mat)
    
    # Lid rim (sits inside pot) - copper accent
    bpy.ops.mesh.primitive_cylinder_add(
        location=(location[0], location[1], lid_z - 0.005),
        scale=(radius - 0.025, radius - 0.025, 0.015),
        vertices=64
    )
    lid_rim = bpy.context.active_object
    lid_rim.name = "Lid_Rim"
    
    lid_rim_subsurf = lid_rim.modifiers.new(name="Subdivision", type='SUBSURF')
    lid_rim_subsurf.levels = 2
    
    lid_rim_mat = create_material("LidRimMaterial", (0.72, 0.45, 0.20), metallic=0.85, roughness=0.15)
    lid_rim.data.materials.append(lid_rim_mat)
    
    # Lid knob/handle - copper
    bpy.ops.mesh.primitive_cylinder_add(
        location=(location[0], location[1], lid_z + 0.055),
        scale=(0.025, 0.025, 0.025),
        vertices=32
    )
    knob_base = bpy.context.active_object
    knob_base.name = "Lid_Knob_Base"
    
    knob_base_subsurf = knob_base.modifiers.new(name="Subdivision", type='SUBSURF')
    knob_base_subsurf.levels = 2
    
    # Copper knob material
    knob_mat = create_material("KnobMaterial", (0.72, 0.45, 0.20), metallic=0.85, roughness=0.25)
    knob_base.data.materials.append(knob_mat)
    
    # Knob top (rounded)
    bpy.ops.mesh.primitive_uv_sphere_add(
        location=(location[0], location[1], lid_z + 0.088),
        scale=(0.028, 0.028, 0.018),
        segments=24,
        ring_count=16
    )
    knob_top = bpy.context.active_object
    knob_top.name = "Lid_Knob_Top"
    
    knob_top_subsurf = knob_top.modifiers.new(name="Subdivision", type='SUBSURF')
    knob_top_subsurf.levels = 2
    
    knob_top.data.materials.append(knob_mat)
    
    print(f"Realistic cooking pot created at {location}")
    return pot_body

def setup_scene():
    """Setup camera and lighting"""
    
    # Add camera
    bpy.ops.object.camera_add(
        location=(2, -2.5, 1.5),
        rotation=(math.radians(75), 0, math.radians(40))
    )
    camera = bpy.context.active_object
    camera.name = "Camera"
    bpy.context.scene.camera = camera
    
    # Add key light (sun)
    bpy.ops.object.light_add(type='SUN', location=(4, -4, 6))
    sun = bpy.context.active_object
    sun.name = "KeyLight"
    sun.data.energy = 3.5
    sun.rotation_euler = (math.radians(50), 0, math.radians(45))
    
    # Add fill light (area)
    bpy.ops.object.light_add(type='AREA', location=(-2, -1, 2))
    area = bpy.context.active_object
    area.name = "FillLight"
    area.data.energy = 150
    area.data.size = 2.5
    
    # Add rim light for metallic highlights
    bpy.ops.object.light_add(type='POINT', location=(1.5, 2, 1.8))
    point = bpy.context.active_object
    point.name = "RimLight"
    point.data.energy = 200
    
    print("Scene setup complete!")

def create_cookware_scene():
    """Generate a complete scene with pot"""
   
    # Create cooking pot with flat base and properly attached handles
    pot = create_pot(
        location=(0, 0, 0.01),
        radius=0.32,
        height=0.38
    )
    
    # Setup scene
    setup_scene()
    
    print("Realistic pot generated successfully!")
    print("Features: FLAT BASE, properly attached handles, domed lid, matte black with copper accents")

# Generate the pot
create_cookware_scene()