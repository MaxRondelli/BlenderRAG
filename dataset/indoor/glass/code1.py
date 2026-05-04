import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Champagne flute dimensions - slightly wider bowl for elegance
bowl_bottom_radius = 0.015  # 1.5cm at bottom of bowl (wider)
bowl_top_radius = 0.030     # 3.0cm at rim (wider)
bowl_height = 0.14          # 14cm bowl height
stem_radius = 0.0025        # 2.5mm stem thickness
stem_height = 0.12          # 12cm stem height
base_radius = 0.032         # 3.2cm base radius
base_thickness = 0.003      # 3mm base thickness
glass_thickness = 0.0015    # 1.5mm glass wall thickness (slightly thicker)

# STEP 1: Create the hollow bowl walls using curves
curve_data = bpy.data.curves.new('bowl_profile', type='CURVE')
curve_data.dimensions = '3D'
curve_data.resolution_u = 32

# Create a spline for the bowl walls
spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(3)  # 4 points total

# Define the profile points (from bottom to top of bowl)
# Point 0: Bottom inside
spline.bezier_points[0].co = (bowl_bottom_radius - glass_thickness, 0, 0)
spline.bezier_points[0].handle_left_type = 'AUTO'
spline.bezier_points[0].handle_right_type = 'AUTO'

# Point 1: Bottom outside
spline.bezier_points[1].co = (bowl_bottom_radius, 0, 0)
spline.bezier_points[1].handle_left_type = 'AUTO'
spline.bezier_points[1].handle_right_type = 'AUTO'

# Point 2: Top outside
spline.bezier_points[2].co = (bowl_top_radius, 0, bowl_height)
spline.bezier_points[2].handle_left_type = 'AUTO'
spline.bezier_points[2].handle_right_type = 'AUTO'

# Point 3: Top inside
spline.bezier_points[3].co = (bowl_top_radius - glass_thickness, 0, bowl_height)
spline.bezier_points[3].handle_left_type = 'AUTO'
spline.bezier_points[3].handle_right_type = 'AUTO'

# Close the spline
spline.use_cyclic_u = True

# Create curve object
bowl_curve_obj = bpy.data.objects.new('bowl_curve', curve_data)
bpy.context.collection.objects.link(bowl_curve_obj)
bowl_curve_obj.location = (0, 0, stem_height)

# Add screw modifier
bpy.context.view_layer.objects.active = bowl_curve_obj
bowl_curve_obj.select_set(True)

screw_mod = bowl_curve_obj.modifiers.new(name="Screw", type='SCREW')
screw_mod.axis = 'Z'
screw_mod.steps = 64
screw_mod.render_steps = 64
screw_mod.angle = math.radians(360)
screw_mod.use_smooth_shade = True

# Convert to mesh
bpy.ops.object.convert(target='MESH')
bowl = bpy.context.active_object
bowl.name = "Bowl"

# STEP 2: Create the bottom cap (closed bottom)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=64,
    radius=bowl_bottom_radius - glass_thickness/2,
    depth=glass_thickness,
    location=(0, 0, stem_height + glass_thickness/2)
)
bottom_cap = bpy.context.active_object
bottom_cap.name = "Bottom_Cap"
bpy.ops.object.shade_smooth()

# STEP 3: Create stem as a simple uniform cylinder
stem_penetration = 0.002  # 2mm penetration into bowl
stem_actual_height = stem_height - base_thickness + stem_penetration
stem_center_z = base_thickness + stem_actual_height/2

bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=stem_radius,
    depth=stem_actual_height,
    location=(0, 0, stem_center_z)
)
stem = bpy.context.active_object
stem.name = "Stem"
bpy.ops.object.shade_smooth()

# STEP 4: Create base (flat disc)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=64,
    radius=base_radius,
    depth=base_thickness,
    location=(0, 0, base_thickness/2)
)
base = bpy.context.active_object
base.name = "Base"
bpy.ops.object.shade_smooth()

# STEP 5: Mark stem edges as sharp BEFORE joining to prevent subdivision
bpy.context.view_layer.objects.active = stem
stem.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.mark_sharp()
bpy.ops.object.mode_set(mode='OBJECT')

# Now join all parts
bpy.ops.object.select_all(action='DESELECT')
bowl.select_set(True)
bottom_cap.select_set(True)
stem.select_set(True)
base.select_set(True)
bpy.context.view_layer.objects.active = bowl
bpy.ops.object.join()

champagne_flute = bpy.context.active_object
champagne_flute.name = "Champagne_Flute"

# Add subdivision surface modifier with edge split to preserve sharp edges
edge_split = champagne_flute.modifiers.new(name="EdgeSplit", type='EDGE_SPLIT')
edge_split.use_edge_angle = False
edge_split.use_edge_sharp = True

# Then add subdivision
subsurf = champagne_flute.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 1
subsurf.render_levels = 2

# Apply shade smooth
bpy.ops.object.shade_smooth()

# STEP 6: Create amber glass material
mat = bpy.data.materials.new(name="Amber_Glass_Material")
mat.use_nodes = True
nodes = mat.node_tree.nodes
nodes.clear()

# Glass BSDF
glass_bsdf = nodes.new(type='ShaderNodeBsdfGlass')
glass_bsdf.location = (0, 0)
glass_bsdf.inputs['IOR'].default_value = 1.52
glass_bsdf.inputs['Roughness'].default_value = 0.005
glass_bsdf.inputs['Color'].default_value = (1.0, 0.7, 0.3, 1.0)  # Warm amber color

# Output
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (200, 0)

# Link nodes
links = mat.node_tree.links
links.new(glass_bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign material
if champagne_flute.data.materials:
    champagne_flute.data.materials[0] = mat
else:
    champagne_flute.data.materials.append(mat)

# Enable transparency
mat.blend_method = 'BLEND'

# STEP 7: Setup camera
bpy.ops.object.camera_add(location=(0.25, -0.25, 0.2))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(45))
bpy.context.scene.camera = camera

# STEP 8: Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0

bpy.ops.object.light_add(type='AREA', location=(0, -0.3, 0.4))
area = bpy.context.active_object
area.data.energy = 50
area.data.size = 0.5

# STEP 9: Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.film_transparent = True

print("Amber champagne flute generated successfully!")
print(f"Dimensions:")
print(f"  - Bowl diameter (rim): {bowl_top_radius * 2 * 100:.1f}cm")
print(f"  - Bowl height: {bowl_height * 100:.1f}cm")
print(f"  - Stem height: {stem_height * 100:.1f}cm")
print(f"  - Base diameter: {base_radius * 2 * 100:.1f}cm")
print(f"  - Glass thickness: {glass_thickness * 1000:.2f}mm")
print(f"  - Total height: {(stem_height + bowl_height) * 100:.1f}cm")
print("\nVariation features:")
print("  ✓ Warm amber-tinted glass")
print("  ✓ Wider bowl for elegant silhouette")
print("  ✓ Slightly thicker glass walls")
print("  ✓ Higher IOR for premium glass look")