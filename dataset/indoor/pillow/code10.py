import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove existing materials
for material in bpy.data.materials:
    bpy.data.materials.remove(material)

def create_pillow_material(name="PillowMaterial", base_color=(0.85, 0.75, 0.65)):
    """Create a fabric-like material for the pillow"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Create Principled BSDF
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (300, 0)
    node_bsdf.inputs['Base Color'].default_value = (*base_color, 1)
    node_bsdf.inputs['Roughness'].default_value = 0.9
    node_bsdf.inputs['Metallic'].default_value = 0.0
    
    # Add diamond pattern texture
    node_wave = nodes.new(type='ShaderNodeTexWave')
    node_wave.location = (-300, 200)
    node_wave.wave_type = 'BANDS'
    node_wave.wave_profile = 'SAW'
    node_wave.inputs['Scale'].default_value = 15.0
    node_wave.inputs['Distortion'].default_value = 2.0
    
    node_wave2 = nodes.new(type='ShaderNodeTexWave')
    node_wave2.location = (-300, -100)
    node_wave2.wave_type = 'BANDS'
    node_wave2.wave_profile = 'SAW'
    node_wave2.inputs['Scale'].default_value = 15.0
    node_wave2.inputs['Distortion'].default_value = 2.0
    node_wave2.inputs['Phase Offset'].default_value = 1.57
    
    # Mix the two wave patterns for diamond effect
    node_mix = nodes.new(type='ShaderNodeMix')
    node_mix.location = (-100, 50)
    node_mix.data_type = 'RGBA'
    node_mix.blend_type = 'MULTIPLY'
    node_mix.inputs['Factor'].default_value = 0.8
    
    # Create texture coordinates
    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-500, 0)
    
    # Create output node
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (600, 0)
    
    # Link nodes
    mat.node_tree.links.new(node_coord.outputs['Generated'], node_wave.inputs['Vector'])
    mat.node_tree.links.new(node_coord.outputs['Generated'], node_wave2.inputs['Vector'])
    mat.node_tree.links.new(node_wave.outputs['Color'], node_mix.inputs['A'])
    mat.node_tree.links.new(node_wave2.outputs['Color'], node_mix.inputs['B'])
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_pillow(location=(0, 0, 0), size=(1.2, 1.2, 0.2), color=(0.85, 0.75, 0.65)):
    """
    Create a realistic pillow with soft, rounded edges
    
    Parameters:
    - location: (x, y, z) position
    - size: (width, depth, height) dimensions
    - color: (r, g, b) color values (0-1)
    """
    
    # Create base cube
    bpy.ops.mesh.primitive_cube_add(location=location, scale=(size[0]/2, size[1]/2, size[2]/2))
    pillow = bpy.context.active_object
    pillow.name = "Pillow"
    
    # Enter edit mode to modify the mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Add subdivision for smoother geometry
    bpy.ops.mesh.subdivide(number_cuts=4)
    
    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add Subdivision Surface modifier for smooth appearance
    subsurf = pillow.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 3
    subsurf.render_levels = 4
    subsurf.subdivision_type = 'CATMULL_CLARK'
    
    # Add Simple Deform modifier for slight bend/sag
    simple_deform = pillow.modifiers.new(name="Bend", type='SIMPLE_DEFORM')
    simple_deform.deform_method = 'BEND'
    simple_deform.angle = math.radians(8)
    simple_deform.deform_axis = 'Y'
    
    # Add Displace modifier for subtle surface variation
    # First create a texture
    tex = bpy.data.textures.new("PillowTexture", type='CLOUDS')
    tex.noise_scale = 0.3
    tex.noise_depth = 3
    
    displace = pillow.modifiers.new(name="Displace", type='DISPLACE')
    displace.texture = tex
    displace.strength = 0.03
    displace.mid_level = 0.5
    
    # Add Cloth modifier for natural pillow deformation
    cloth = pillow.modifiers.new(name="Cloth", type='CLOTH')
    cloth.settings.quality = 6
    cloth.settings.mass = 0.25
    cloth.settings.tension_stiffness = 8
    cloth.settings.compression_stiffness = 8
    cloth.settings.shear_stiffness = 8
    cloth.settings.bending_stiffness = 2
    cloth.settings.use_pressure = True
    cloth.settings.uniform_pressure_force = 2.5
    
    # Create and apply material
    pillow_mat = create_pillow_material("PillowMaterial", color)
    pillow.data.materials.append(pillow_mat)
    
    # Bake the cloth simulation for a frame or two to get natural sag
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 20
    bpy.context.scene.frame_set(1)
    
    # Set pillow as active object
    bpy.context.view_layer.objects.active = pillow
    
    return pillow

def setup_scene():
    """Setup camera and lighting for the pillow"""
    
    # Add a plane as surface for the pillow to rest on
    bpy.ops.mesh.primitive_plane_add(location=(0, 0, -0.11), scale=(3, 3, 1))
    plane = bpy.context.active_object
    plane.name = "Surface"
    
    # Create surface material
    surface_mat = bpy.data.materials.new(name="SurfaceMat")
    surface_mat.use_nodes = True
    nodes = surface_mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.8, 0.75, 0.7, 1)
    bsdf.inputs['Roughness'].default_value = 0.5
    plane.data.materials.append(surface_mat)
    
    # Add camera
    bpy.ops.object.camera_add(location=(2.5, -2.5, 1.8), rotation=(math.radians(70), 0, math.radians(45)))
    camera = bpy.context.active_object
    camera.name = "Camera"
    bpy.context.scene.camera = camera
    
    # Add key light (sun)
    bpy.ops.object.light_add(type='SUN', location=(3, -3, 5))
    sun = bpy.context.active_object
    sun.name = "KeyLight"
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(45), 0, math.radians(45))
    
    # Add fill light (area)
    bpy.ops.object.light_add(type='AREA', location=(-2, -1, 2))
    area = bpy.context.active_object
    area.name = "FillLight"
    area.data.energy = 50
    area.data.size = 2.0
    area.rotation_euler = (math.radians(60), 0, math.radians(-45))
    
    # Add rim light
    bpy.ops.object.light_add(type='POINT', location=(1, 2, 1.5))
    point = bpy.context.active_object
    point.name = "RimLight"
    point.data.energy = 100
    
    print("Scene setup complete!")

def create_pillow_scene():
    """Generate a complete scene with a pillow"""
    
    # Create the main pillow
    pillow = create_pillow(
        location=(0, 0, 0),
        size=(1.2, 1.2, 0.2),
        color=(0.85, 0.75, 0.65) 
    )
    
    # Setup the scene
    #setup_scene()
    
    print("Pillow generated successfully!")
    print("Note: The cloth simulation will give the pillow a natural saggy appearance.")
    print("You can adjust the simulation by going to frame 10-20 in the timeline.")
    print("Or disable the Cloth modifier if you want a perfectly smooth pillow.")

# Generate the pillow scene
create_pillow_scene()