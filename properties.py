# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
from bpy.props import (BoolProperty,
                       StringProperty,
                       EnumProperty,
                       FloatProperty,
                       IntProperty,
                       FloatVectorProperty,
                       CollectionProperty,
                       PointerProperty)
from math import pi

patterns=(('agate', "Agate", ""), ('brick', "Brick", ""), ('cells', "Cells", ""),  # ('boxed', "Boxed", ""), 
       ('checker', "Checker", ""), ('crackle', "Crackle", ""),  # ('cylindrical', "Cylindrical", ""),
       ('dents', "Dents", ""), ('density_file', "Density File", ""),('facets', "Facets (Normal only)", ""), ('gradient', "Gradient", ""), # ('function', "Function", ""),
       ('granite', "Granite", ""), ('hexagon', "Hexagon", ""),# ('julia', "Julia", ""), 
       ('leopard', "Leopard", ""), # ('magnet', "Magnet", ""), ('mandel', "Mandelbrot", ""),
       ('marble', "Marble", ""), ('onion', "Onion", ""), ('pavement', "Pavement", ""),# ('planar', "Planar", ""), 
       ('quilted', "Quilted", ""), ('ripples', "Ripples", ""),  ('radial', "Radial", ""),  ('ridged', "Ridged", ""),  ('slope', "Slope", ""),
       ('spiral1', "Spiral1", ""), ('spiral2', "Spiral2", ""), ('spotted', "Spotted", ""), #('spherical', "Spherical", ""),
       ('square', "Square", ""),('tiling', "Tiling", ""),('triangular', "Triangular", ""),
       ('waves', "Waves", ""), ('wood', "Wood", ""),('wrinkles', "Wrinkles", ""))

def material_texture_name_from_uilist(self,context):
    mat = context.scene.view_layers["View Layer"].objects.active.active_material
    index = mat.pov.active_texture_index
    name = mat.povray_texture_slots[index].name
    newname = mat.povray_texture_slots[index].texture
    tex = bpy.data.textures[name]
    tex.name = newname
    mat.povray_texture_slots[index].name = newname


def material_texture_name_from_search(self,context):
    mat = context.scene.view_layers["View Layer"].objects.active.active_material
    index = mat.pov.active_texture_index
    name = mat.povray_texture_slots[index].texture_search
    try:
        tex = bpy.data.textures[name]
        mat.povray_texture_slots[index].name = name
        mat.povray_texture_slots[index].texture = name
    except:
        pass


def world_texture_name_from_uilist(self,context):
    mat = context.scene.view_layers["View Layer"].objects.active.active_material
    index = mat.pov.active_texture_index
    name = mat.povray_texture_slots[index].name
    newname = mat.povray_texture_slots[index].texture
    tex = bpy.data.textures[name]
    tex.name = newname
    mat.povray_texture_slots[index].name = newname


def world_texture_name_from_search(self,context):
    mat = context.scene.view_layers["View Layer"].objects.active.active_material
    index = mat.pov.active_texture_index
    name = mat.povray_texture_slots[index].texture_search
    try:
        tex = bpy.data.textures[name]
        mat.povray_texture_slots[index].name = name
        mat.povray_texture_slots[index].texture = name
    except:
        pass


def use_texture_color_ramp(self, context):

    tex=context.texture
    if tex.povray.texture_density:
        tex.use_color_ramp = True
    else:
        tex.use_color_ramp = False

def image_replace_callback(self, context):
    tex = context.texture
    if tex.povray.image == "":
        tex.image = None
    else:
        tex.image = bpy.data.images[tex.povray.image]

def meta_update_callback(self, context):
    bpy.ops.object.mode_set(mode="EDIT")
    ob = context.object
    if ob.type == 'META':
        metaelem = ob.data.elements.active
        blob_strength = ob.povray.blob_strength
        strength = abs(blob_strength)
        if strength > 10:
            strength = 10
        if blob_strength < 0:
            metaelem.use_negative = True
        else:
            metaelem.use_negative = False
        metaelem.stiffness = strength
        bpy.ops.object.mode_set(mode="OBJECT")

# def use_material_nodes_callback(self, context):
    # #context.space_data.tree_type = 'ShaderNodeTree'
    # mat=context.object.active_material
    # if mat.povray.use_nodes:
        # mat.use_nodes=True
        # tree = mat.node_tree
        # tree.name=mat.name
        # links = tree.links
        # default = True
        # if len(tree.nodes) == 2:
            # o = 0
            # m = 0
            # for node in tree.nodes:
                # if node.type in {"OUTPUT","MATERIAL"}:
                    # tree.nodes.remove(node)
                    # default = True
            # for node in tree.nodes:
                # if node.bl_idname == 'PovrayOutputNode':
                    # o+=1
                # if node.bl_idname == 'ShaderTextureMapNode':
                    # m+=1
            # if o == 1 and m == 1:
                # default = False
        # elif len(tree.nodes) == 0:
            # default = True
        # else:
            # default = False
        # if default:
            # output = tree.nodes.new('PovrayOutputNode')
            # output.location = 200,200
            # tmap = tree.nodes.new('ShaderTextureMapNode')
            # tmap.location = 0,200
            # links.new(tmap.outputs[0],output.inputs[0]) 
    # else:
        # mat.use_nodes=False


def use_texture_nodes_callback(self, context):
    tex=context.object.active_material.active_texture
    if tex.povray.texture_use_nodes:
        tex.use_nodes=True
        if len(tex.node_tree.nodes)==2:
            for node in tex.node_tree.nodes:
                if node.type in {"OUTPUT","CHECKER"}:
                    tex.node_tree.nodes.remove(node)
    else:
        tex.use_nodes=False

def node_active_callback(self, context):
    items = []
    mat=context.material
    mat.node_tree.nodes
    for node in mat.node_tree.nodes:
        node.select=False
    for node in mat.node_tree.nodes:
        if node.name==mat.povray.material_active_node:
            node.select=True
            mat.node_tree.nodes.active=node

            return node

def node_enum_callback(self, context):
    items = []
    mat=context.material
    nodes=mat.node_tree.nodes
    for node in nodes:
        items.append(("%s"%node.name,"%s"%node.name,""))
    return items

def pigment_normal_callback(self, context):
    render = context.scene.povray.render
    items = [("pigment", "Pigment", ""),("normal", "Normal", "")]
    if render == 'hgpovray':
        items = [("pigment", "Pigment", ""),("normal", "Normal", ""),("modulation", "Modulation", "")]
    return items

def glow_callback(self, context):
    scene = context.scene
    ob = context.object
    ob.povray.mesh_write_as_old = ob.povray.mesh_write_as
    if scene.povray.render == 'uberpov' and ob.povray.glow:
        ob.povray.mesh_write_as = 'NONE'
    else:
        ob.povray.mesh_write_as = ob.povray.mesh_write_as_old

def camera_item_callback(self, context):
    render = context.scene.povray.render
    items = [("perspective", "Perspective", ""),
            ("orthographic", "Orthographic", ""),
            #("mesh_camera", "Mesh", ""),
            ("fisheye", "Fisheye", ""),
            ("ultra_wide_angle", "Ultra-wide angle", ""),
            ("omnimax", "Omnimax", ""),
            ("panoramic", "Panoramic", ""),
            ("cylinder", "Cylindrical", ""),
            ("spherical", "Spherical", "")]
    if render == 'hgpovray':
        items = [("perspective", "Perspective", ""),
                ("aitoff_hammer", "Aitoff Hammer", "ratio 2:1"),
                ("balthasart", "Balthasart", "ratio is about 1.3"),
                ("behrmann", "Behrmann", "ratio is 3π:4 (about 2.36)"),
                ("cube", "Cube", "ratio is 2.5 ( 5:2 )"),
                ("cylinder", "Cylinder", ""),
                ("eckert_iv", "Eckert IV", "ratio 2:1"),
                ("eckert_vi", "Eckert VI", "ratio 2:1"),
                ("edwards", "Edwards", "ratio is about 2"),
                ("fisheye", "Fisheye", ""),
                ("fisheye_equisolid_angle", "Fisheye Equisolid Angle", ""),
                ("fisheye_orthographic", "Fisheye Orthographic", ""),
                ("fisheye_stereographic", "Fisheye Stereographic", ""),
                ("gall", "Gall", "ratio is π:2 or golden ratio (φ) (both near 1.6)"),
                ("hobo_dyer", "Hobo Dyer", "ratio is about 2"),
                ("icosa", "Icosa", "ratio is about 2.1169 ( 11:3√3 )"),
                ("lambert_azimuthal", "Lambert Azimuthal", "ratio 1:1"),
                ("lambert_cylindrical", "Lambert Cylindrical", "ratio is π"),
                ("orthographic", "Orthographic", ""),
                ("mercator", "Mercator", "ratio is up to you, it's impossible to reach the poles"),
                ("miller_cylindrical", "Miller Cylindrical", "ratio 1.3638862 or 1:0.733"),
                ("mollweide", "Mollweide", "ratio 2:1"),
                ("octa", "Octa", "ratio is about 2.3 ( 4:√3 )"),
                ("omni_directional_stereo", "Omni Directional Stereo", ""),
                ("omnimax", "Omnimax", ""),
                ("panoramic", "Panoramic", ""),
                ("peters", "Peters", "ratio is about π:2 or golden ratio φ (not exactly the same thing, but around 1.6)."),
                ("plate_carree", "Plate Carree", "ratio 2:1"),
                ("smyth_craster", "Smyth Craster", "ratio is about 2"),
                ("spherical", "Spherical", ""),
                ("stereo", "Stereo", ""),
                ("tetra", "Tetra", "ratio is about 2.886 ( 5:√3 ) "),
                ("ultra_wide_angle", "Ultra-wide angle", ""),
                ("van_der_grinten", "Van der Grinten", "ratio 1:1")]
    return items

def media_enum_callback(self, context):
    mts = [[("absorption","Absorption","")],[("emission","Emission","")],[("scattering","Scattering","")]]
    items = [] #("absorption","Absorption",""),("emission","Emission",""),("scattering","Scattering","")
    ob = context.object
    num = -1
    mts1 = []
    for slot in ob.material_slots:
        if slot and hasattr(slot, 'material'):
            num+=1
            for mt in mts:
                items.append(mt[0])
            mts1.append(slot.material.povray.media_type)
        #for i in range(len(items)):
            #if mt[0] == media_type_1:
                #items.pop([i])
    return items

def iso_props_update_callback(self,context):
    try:
        bpy.ops.povray.nodeisoadd()
    except:
        pass

def use_object_light_callback(self,context):

    ob = context.object
    ob_data = ob.data
    scene = context.scene

    if ob_data.povray.shape != "":
        ob_light = scene.objects[ob_data.povray.shape]
        copy_transforms = None
        if ob.constraints:
            for const in ob.constraints:
                if const.type == "COPY_TRANSFORMS":
                    const.target = ob_light
                    ob_light.povray.shape_as_light = ob_data.name
        else:
            const = ob.constraints.new(type = "COPY_TRANSFORMS")
            const.target = ob_light
            ob_light.povray.shape_as_light = ob_data.name
        ob_data.povray.shape_old = ob_data.povray.shape
    else:
        if ob_data.povray.shape_old != "":
            ob_light = scene.objects[ob_data.povray.shape_old]
            if ob.constraints:
                for const in ob.constraints:
                    if const.type == "COPY_TRANSFORMS":
                        ob.constraints.remove(const)
                        ob_light.povray.shape_as_light = ""
        ob_data.povray.shape_old = ob_data.povray.shape

def spot_size_callback(self,context):
    lamp = context.object.data
    spot_size = lamp.povray.spot_size*pi/180
    if spot_size < pi/180:
        spot_size = pi/180
    lamp.spot_size = spot_size
def lamp_type_callback(self,context):

    ob = context.object.data
    if ob.povray.light_type in {"point"}:
        ob.type="POINT"
    if ob.povray.light_type in {"spotlight","cylinder"}:
        ob.type="SPOT"
    if ob.povray.light_type == "parallel":
        ob.type="SUN"
    if ob.povray.light_type == "shadowless":
        ob.type="HEMI"

def sky_type_callback(self,context):
    if context.world:
        tex = context.texture
        if tex.povray.sky_sphere in {"image_map"}:
            tex.type="IMAGE"
            tex.use_color_ramp = False
        if tex.povray.sky_sphere in {"gradient"}:
            tex.type="BLEND"
            tex.use_color_ramp = True
        if tex.povray.sky_sphere in {"bozo"}:
            tex.type="CLOUDS"
            tex.use_color_ramp = True

def pattern_callback(self,context):
        tex = context.texture
        tex.type="IMAGE"
        if tex.povray.pattern_or_image == "pattern":
            tex.use_color_ramp = True
        else:
            tex.use_color_ramp = False

def pattern_props_callback(self,context):
        tex = context.texture
        if tex.povray.pattern == "brick":
            tex.povray.vector = (0.25, 0.0525, 0.125)
        if tex.povray.pattern in {"gradient","slope"}:
            tex.povray.vector = (0.0, 1.0, 0.0)

def scale_all_callback(self,context):
        tex = context.texture
        if tex.povray.scale_all_axis:
            for i in range(3):
                tex.povray.scale[i] = tex.povray.scale_all

def turbulence_all_callback(self,context):
        tex = context.texture
        if tex.povray.turbulence_all_axis:
            for i in range(3):
                tex.povray.turbulence[i] = tex.povray.turbulence_all

def boolean_parent_callback(self,context):
    ob = context.object
    if ob.povray.povray_boolean:
        ob.povray.boolean_parent = ob.name
    else:
        ob.povray.boolean_parent = ''
    round_angles = BoolProperty(name = "Round",default = False,update=shapes_inc_callback)

def shapes_inc_callback(self,context):
    op = context.object.povray
    sp = context.scene.povray
    if op.round_angles:
        sp.shapes_inc = True


class PovrayRenderSettings(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.povray = PointerProperty(
                name="Povray Render Settings",
                description="Povray render settings",
                type=cls,
                )

    sdl_window_use : BoolProperty(
            name="SDL Window",
            description="",
            default=True)


    render_scenes_from_file : BoolProperty(
            name="Render scenes from file",
            description="",
            default=False)

    render : EnumProperty(
            name="Render",
            description="",
            items=( ("povray", "Povray", ""),
                    ("uberpov", "Uber", ""),
                    ("hgpovray", "HG", "")),
            default="povray")


    output_advanced : BoolProperty(
            name="Advanced",
            description="Enable the custom settings",
            default=False)

    tempfiles : BoolProperty(
            name="Tempfiles",
            description="Enable the OS-Tempfiles. Otherwise set the path where to save the files",
            default=False)

    workdir : StringProperty(
            name="Scene files location",
            description="Path to directory where the files are created",
            maxlen=1024, subtype="DIR_PATH")

    output_format : EnumProperty(
            name="Output",
            description=" File Output Formats",
            items=(("B", "BMP", "Universal Bitmap image file format"),
                   ("T", "Targa uncompressed", "Uncompressed Targa-24 format"),
                   ("C", "Targa compressed", "Compressed Targa-24 format (RLE, run length encoded)"),
                   ("E", "OpenEXR", "OpenEXR High Dynamic-Range format"),
                   ("H", "Radiance", "Radiance High Dynamic-Range format"),
                   ("J", "JPEG", "JPEG format (Note: This format is not loss-free and will generate compression artifacts)"),
                   ("N", "PNG", "PNG (portable network graphics) format"),
                   ("P", "PPM", "Unix PPM format")),
            default="N")

    adc_bailout_enable : BoolProperty(
            name="Enable",
            description="",
            default=False)

    adc_bailout : FloatProperty(
            name="ADC Bailout",
            description="",
            min=0.0, max=1000.0,default=0.00392156862745, precision=3)

    ambient_light_enable : BoolProperty(
            name="Enable",
            description="",
            default=False)

    ambient_light : FloatVectorProperty(
            name="Ambient Light", description="Ambient light is used to simulate the effect of inter-diffuse reflection",
            precision=4, step=0.01, min=0, soft_max=1,
            default=(1, 1, 1), options={'ANIMATABLE'}, subtype='COLOR')

    assumed_gamma : FloatProperty(
            name="Assumed Gamma",
            description="Assumed gamma",
            min=0.0, max=10.0, default=1.0)

    global_settings_advanced : BoolProperty(
            name="Advanced",
            description="",
            default=False)

    irid_wavelength_enable : BoolProperty(
            name="Enable",
            description="",
            default=False)

    irid_wavelength : FloatVectorProperty(
            name="Irid Wavelength", description="Iridescence calculations depend upon the dominant wavelengths of the primary colors of red, green and blue light.",
            precision=4, step=0.01, min=0, soft_max=1,
            default=(0.25,0.18,0.14), options={'ANIMATABLE'}, subtype='COLOR')

    charset : EnumProperty(
            name="Charset",
            description="This allows you to specify the assumed character set of all text strings.",
            items=(("ascii", "ASCII", ""),
                   ("utf8", "UTF-8", ""),
                   ("sys", "SYS", "")),
            default="utf8")

    max_trace_level : IntProperty(
            name="Max Trace Level",
            description="Number of reflections/refractions allowed on ray path",
            min=0, max=256, default=3)

    max_intersections_enable : BoolProperty(
            name="Enable",
            description="",
            default=False)

    max_intersections : IntProperty(
            name="Max Intersections",
            description="POV-Ray uses a set of internal stacks to collect ray/object intersection points.",
            min=2, max=1024, default=64)

    number_of_waves_enable : BoolProperty(
            name="Enable",
            description="",
            default=False)

    number_of_waves : IntProperty(
            name="Number Waves",
            description="The waves and ripples patterns are generated by summing a series of waves, each with a slightly different center and size.",
            min=1, max=10, default=1000)

    noise_generator_enable : BoolProperty(
            name="Enable",
            description="",
            default=False)

    noise_generator : IntProperty(
            name="Noise Generator",
            description="There are three noise generators implemented.",
            min=1, max=3, default=2)

    ########################## RADIO ###############################################
    radio_enable : BoolProperty(
            name="Enable Radiosity",
            description="Enable POV-Rays radiosity calculation",
            default=False)

    radio_adc_bailout : FloatProperty(
            name="ADC Bailout",
            description="The adc_bailout for radiosity rays. Use "
                        "adc_bailout = 0.01 / brightest_ambient_object for good results",
            min=0.0, max=1000.0, soft_min=0.0, soft_max=1.0, default=0.01, precision=3)

    radio_always_sample : BoolProperty(
            name="Always Sample",
            description="Only use the data from the pretrace step and not gather "
                        "any new samples during the final radiosity pass",
            default=True)

    radio_brightness : FloatProperty(
            name="Brightness",
            description="Amount objects are brightened before being returned "
                        "upwards to the rest of the system",
            min=0.0, max=1000.0, soft_min=0.0, soft_max=10.0, default=1.0)

    radio_count : IntProperty(
            name="Count",
            description="Number of rays for each new radiosity value to be calculated "
                        "(halton sequence over 1600)",
            min=1, max=10000, soft_max=1600, default=35)

    radio_error_bound : FloatProperty(
            name="Error Bound",
            description="One of the two main speed/quality tuning values, "
                        "lower values are more accurate",
            min=0.0, max=1000.0, soft_min=0.1, soft_max=10.0, default=1.8)

    radio_gray_threshold : FloatProperty(
            name="Gray Threshold",
            description="One of the two main speed/quality tuning values, "
                        "lower values are more accurate",
            min=0.0, max=1.0, soft_min=0, soft_max=1, default=0.0)

    radio_low_error_factor : FloatProperty(
            name="Low Error Factor",
            description="Just enough samples is slightly blotchy. Low error changes error "
                        "tolerance for less critical last refining pass",
            min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, default=0.5)

    radio_media : BoolProperty(
            name="Media", description="Radiosity estimation can be affected by media",
            default=False)

    radio_maximum_reuse : FloatProperty(
            name="Maximum Reuse",
            description="The maximum reuse parameter works in conjunction with, and is similar to that of minimum reuse, "
                        "the only difference being that it is an upper bound rather than a lower one.",
            min=0.0, max=1.0,default=0.2, precision=3)

    radio_minimum_reuse : FloatProperty(
            name="Minimum Reuse",
            description="This is the fraction of the screen width which sets the minimum radius of reuse for each sample point",

            min=0.0, max=1.0, soft_min=0.1, soft_max=0.1, default=0.015, precision=3)

    radio_nearest_count : IntProperty(
            name="Nearest Count",
            description="Number of old ambient values blended together to "
                        "create a new interpolated value",
            min=1, max=20, default=5)

    radio_normal : BoolProperty(
            name="Normals", description="Radiosity estimation can be affected by normals",
            default=False)

    radio_recursion_limit : IntProperty(
            name="Recursion Limit",
            description="how many recursion levels are used to calculate "
                        "the diffuse inter-reflection",
            min=1, max=20, default=3)

    radio_pretrace_start : FloatProperty(
            name="Pretrace Start",
            description="Fraction of the screen width which sets the size of the "
                        "blocks in the mosaic preview first pass",
            min=0.01, max=1.00, soft_min=0.02, soft_max=1.0, default=0.08)

    radio_pretrace_end : FloatProperty(
            name="Pretrace End",
            description="Fraction of the screen width which sets the size of the blocks "
                        "in the mosaic preview last pass",
            min=0.001, max=1.00, soft_min=0.01, soft_max=1.00, default=0.04, precision=3)

    radio_subsurface : BoolProperty(
            name="Subsurface",
            description="Subsurface Light Transport",
            default=False)
    ########################### PHOTONS ############################################
    photon_enable : BoolProperty(
            name="Photons",
            description="Enable global photons",
            default=False)

    photon_enable_count : BoolProperty(
            name="Spacing / Count",
            description="Enable count photons",
            default=False)

    photon_count : IntProperty(
            name="Count",
            description="Photons count",
            min=1, max=100000000, default=20000)

    photon_spacing : FloatProperty(
            name="Spacing",
            description="Photons spacing",
            min=0.0001, max=1.0, default=0.01)

    photon_max_trace_level : IntProperty(
            name="Max Trace Level",
            description="Number of reflections/refractions allowed on ray path",
            min=1, max=256, default=5)

    photon_media_enable : BoolProperty(
            name="Photons",
            description="Enable global photons",
            default=False)

    photon_media_steps : IntProperty(
            name="Photons count",
            description="Photons count",
            min=1, max=1000, default=100)

    photon_media_factor : FloatProperty(
            name="Factor",
            description="Photon media factor",
            min=1.0, max=10.0, default=1.0)

    photon_adc : BoolProperty(
            name="Photon ADC",
            description="Photon ADC enable",
            default=False)

    photon_adc_bailout : FloatProperty(
            name="ADC_bailout",
            description="The adc_bailout for photons. Use adc_bailout = "
                        "0.01 / brightest_ambient_object for good results",
            min=0.0, max=1000.0, soft_min=0.0, soft_max=1.0, default=0.1, precision=3)

    photon_gather : BoolProperty(
            name="Gather",
            description="Photon gather",
            default=False)

    photon_gather_min : IntProperty(
            name="Gather Min", description="Minimum number of photons gathered for each point",
            min=1, max=256, default=20)

    photon_gather_max : IntProperty(
            name="Gather Max", description="Maximum number of photons gathered for each point",
            min=1, max=256, default=100)

    photon_autostop : BoolProperty(
            name="Autostop",
            description="Photon autostop",
            default=False)

    photon_autostop_value : FloatProperty(
            name="Value",
            description="Photon autostop value",
            min=0.0, max=1.0, default=0.0)

    photon_jitter_enable : BoolProperty(
            name="Jitter",
            description="Enable jitter",
            default=False)

    photon_jitter : FloatProperty(
            name="Value",
            description="The default value is good and usually does not need to be changed.",
            min=0.0, max=1.0, default=0.4)


    photon_map_file_save_load : EnumProperty(
            name="Operation",
            description="Load or Save photon map file",
            items=(("NONE", "None", ""),
                   ("save", "Save", ""),
                   ("load", "Load", "")),
            default="NONE")

    photon_map_filename : StringProperty(
            name="Filename",
            description="",
            maxlen=1024)

    photon_map_dir : StringProperty(
            name="Directory",
            description="",
            maxlen=1024, subtype="DIR_PATH")

    photon_map_file : StringProperty(
            name="File",
            description="",
            maxlen=1024, subtype="FILE_PATH")
    ########################### SSLT ###############################################

    sslt_enable : BoolProperty(
            name="Subsurface Light Transport",
            description="Subsurface Scattering",
            default=False)

    sslt_radiosity : BoolProperty(
            name="Radiosity",
            description="",
            default=False)

    sslt_samples_max : IntProperty(
            name="Samples max",
            description="",
            min=1, max=1000, default=400)

    sslt_samples_min : IntProperty(
            name="Samples min",
            description="",
            min=1, max=1000, default=40)

    mm_per_unit : IntProperty(
            name="Mm per Unit",
            description="",
            min=1,default=10)
    ######################### Antialiasing #######################################

    antialias_enable : BoolProperty(
            name="Enable", description="Enable Antialiasing",
            default=True)
    antialias_sampling_method : EnumProperty(
            name="Method",
            description="Antialiasing sampling method",
            items=(("1", "Non-recursive", "Type 1 Sampling in POV-Ray"),
                   ("2", "Recursive", "Type 2 Sampling in POV-Ray"),
                   ("3", "Adaptive", "Type 3 Sampling in POV-Ray")),
            default="3")
    antialias_depth : IntProperty(
            name="Depth", description="Depth of pixel for sampling",
            min=1, max=9, default=3)
    antialias_threshold : FloatProperty(
            name="Threshold", description="Tolerance for sub-pixels",
            min=0.0, max=1.0, default=0.1)
    antialias_jitter_enable : BoolProperty(
            name="Jitter",
            description="Enable Jittering. Adds noise into the sampling process (it should be "
                        "avoided to use jitter in animation)",
            default=False)
    antialias_jitter_amount : FloatProperty(
            name="Amount", description="Amount of jittering",
            min=0.0, max=1.0, soft_min=0.01, soft_max=1.0, default=0.0)
    antialias_gamma : FloatProperty(
            name="Gamma",
            description="POV-Ray compares gamma-adjusted values for super sampling. Antialias "
                        "Gamma sets the Gamma before comparison",
            min=0.0, max=5.0, soft_min=0.01, soft_max=2.5, default=2.5)

    #Tools
    points : IntProperty(name = "Points",
                    description = "Points on unit",
                    default = 1000, min = 2, max = 10000)

    tip : FloatProperty(name = "Tip",
                    description = "Tip",
                    default = 0.001, min = 0.0, max = 100.0)

    function_inc : BoolProperty(name="Function.inc",default=False)
    shapes_inc : BoolProperty(name="Shapes.inc",default=False)
    shapes2_inc : BoolProperty(name="Shapes2.inc",default=False)
    shapes3_inc : BoolProperty(name="Shapes3.inc",default=False)

    number_copy : IntProperty(
            name="Copy Number", description="",
            min=1, max=10000, default=1)

    resolution : IntProperty(
            name="Resolution", description="",
            min=1, max=360, default=16)

    axis_select : EnumProperty(
            items=[("0", "X", ""),
                   ("1", "Y", ""),
                   ("2", "Z", "")],
            name="Axis",
            description="",
            default="1")

    number_lists_objects : IntProperty(
            name="Lists", description="",
            min=0, default=1)


    @classmethod
    def unregister(cls):
        del bpy.types.Scene.povray

class PovrayCameraSettings(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        import math

        bpy.types.Camera.povray = PointerProperty(
                name="Povray Camera Settings",
                description="Povray camera settings",
                type=cls,
                )
    cam_type : EnumProperty(
            name="Camera Type",
            description="Camera type",
            items=camera_item_callback)
    cylinder_cam_type : EnumProperty(
            name="Cylinder Camera Type",
            description="Cylinder Camera Type",
            items=(("1", "Vertical Fixed", ""),
                   ("2", "Horizontal Fixed", ""),
                   ("3", "Vertical Moves", ""),
                   ("4", "Horizontal Moves", "")),
            default="1")
    cam_angle : FloatProperty(
            name="Angle", description="Camera angle",
            min=0, max=360, default=50*pi/180, subtype='ANGLE')
    blur_enable : BoolProperty(name="Focal Blur", default=False)
    focal_point : StringProperty(name="Focal Point",maxlen=1024)
    blur_samples_min : IntProperty(name="Min", min = 1, max = 1000, default = 1)
    blur_samples_max : IntProperty(name="Max", min = 1, max = 1000, default = 120)
    aperture : FloatProperty(name="Aperture", min=0.0, max=100.0, default=10.0)
    confidence : FloatProperty(name="Confidence", min=0.0, max=1.0, default=0.0)
    variance : FloatProperty(name="Variance", min=0.00001, max=1.0, default=0.008)
    normal_enable : BoolProperty(name="Perturbated Camera", default=False)
    cam_normal : FloatProperty(name="Normal", min=0.0, max=1.0, default=0.0)
    normal_patterns : EnumProperty(
            name="Pattern",
            description="",
            items=(('agate', "Agate", ""), ('boxed', "Boxed", ""), ('bumps', "Bumps", ""), ('cells', "Cells", ""), 
                   ('crackle', "Crackle", ""),('dents', "Dents", ""),
                   ('granite', "Granite", ""),
                   ('leopard', "Leopard", ""),
                   ('marble', "Marble", ""), ('onion', "Onion", ""), ('pavement', "Pavement", ""), ('planar', "Planar", ""), 
                   ('quilted', "Quilted", ""), ('ripples', "Ripples", ""),  ('radial', "Radial", ""),
                   ('spherical', "Spherical", ""),('spiral1', "Spiral1", ""), ('spiral2', "Spiral2", ""), ('spotted', "Spotted", ""), 
                   ('square', "Square", ""),('tiling', "Tiling", ""),
                   ('waves', "Waves", ""), ('wood', "Wood", ""),('wrinkles', "Wrinkles", "")),
            default='agate')
    turbulence = FloatProperty(name="Turbulence", min=0.0, max=100.0, default=0.1)
    scale = FloatProperty(name="Scale", min=0.0,default=1.0)
    #HG
    stereo_dist : FloatProperty(name="Distance", default = 26)
    parallaxe_0 : FloatProperty(name="X", default = 13.0)
    parallaxe_1 : FloatProperty(name="Y", default = 300.0)
    @classmethod
    def unregister(cls):
        del bpy.types.Camera.povray

class PovrayMaterialTextureSlots(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Material.povray_texture_slots  = CollectionProperty(
                name="povray_texture_slots",
                description="Povray blob settings",
                type=cls,
                )
    texture : StringProperty(update=material_texture_name_from_uilist)
    texture_search : StringProperty(update=material_texture_name_from_search)

    @classmethod
    def unregister(cls):
        del bpy.types.Material.povray_texture_slots

class PovrayMaterialSettings(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Material.povray = PointerProperty(
                name="Povray Material Settings",
                description="Povray material settings",
                type=cls,
                )
    subsurface_scattering_use : BoolProperty(name="SSS", description="",default=False)
    povfilter : FloatProperty(name="Filter", min=0.0, max=1.0, default=0.0)
    transmit : FloatProperty(name="Transmit", min=0.0, max=1.0, default=0.0)
    emit : FloatProperty(name="Emit", min=0.0, max=1.0, default=0.0)
    diffuse_intensity : FloatProperty(name="Intensity", min=0.0, max=1.0, default=1.0)
    diffuse_albedo : BoolProperty(name="Albedo", description="",default=False)
    brilliance : FloatProperty(name="Brilliance", min=0.0, max=10.0, default=1.8)
    ambient : FloatVectorProperty(
            name="Ambient", description="",
            precision=4, step=0.01, min=0, soft_max=1,
            default=(0.0, 0.0, 0.0), options={'ANIMATABLE'}, subtype='COLOR')
    translucency : FloatVectorProperty(
            name="Translucency", description="",
            precision=4, step=0.01, min=0, soft_max=1,
            default=(0.0, 0.0, 0.0), options={'ANIMATABLE'}, subtype='COLOR')
    highlights : EnumProperty(
            name="Highlights",
            description="",
            items=( ("none", "None", ""),
                    ("specular", "Specular", ""),
                    ("phong", "Phong", "")),
            default="none")
    specular_intensity : FloatProperty(name="Intensity", min=0.0, max=1.0, default=1.0)
    specular_albedo : BoolProperty(name="Albedo", description="",default=False)
    specular_roughness : FloatProperty(name="Roughness", min=0.0005, max=1.0, default=0.02)
    specular_metallic : FloatProperty(name="Metallic", min=0.0, max=1.0, default=0.0)
    phong_size : FloatProperty(name="Phong Size", min=1.0, max=250.0, default=40.0)

    exponent : FloatProperty(name="Exponent", min=0.0, max=1.0, default=1.0)
    mirror_color : FloatVectorProperty(
            name="Mirror Color", description="",
            precision=4, step=0.01, min=0, soft_max=1,
            default=(0.0, 0.0, 0.0), options={'ANIMATABLE'}, subtype='COLOR')
    mirror_enable : BoolProperty(name="Reflection", description="",default=False)
    color_min_enable : BoolProperty(name="Color Min Enable", description="",default=False)
    color_min : FloatVectorProperty(
            name="Color Min", description="",
            precision=4, step=0.01, min=0, soft_max=1,
            default=(0.0, 0.0, 0.0), options={'ANIMATABLE'}, subtype='COLOR')
    fresnel : BoolProperty(name="Fresnel", description="",default=False)
    falloff : FloatProperty(name="Falloff", min=0.0, max=1.0, default=0.0)
    metallic : FloatProperty(name="Metallic", min=0.0, max=1.0, default=0.0)
    conserve_energy : BoolProperty(name="Conserve Energy", description="",default=False)
    mirror_roughness : FloatProperty(name="Roughness", min=0.0, max=1.0, default=0.001)

    irid_enable : BoolProperty(name="Iridescence", description="",default=False)
    irid_amount : FloatProperty(
            name="Amount",
            description="Contribution of the iridescence effect to the overall surface color. "
                        "As a rule of thumb keep to around 0.25 (25% contribution) or less, "
                        "but experiment. If the surface is coming out too white, try lowering "
                        "the diffuse and possibly the ambient values of the surface",
            min=0.0, max=1.0, soft_min=0.01, soft_max=1.0, default=0.25)

    irid_thickness : FloatProperty(
            name="Thickness",
            description="A very thin film will have a high frequency of color changes while a "
                        "thick film will have large areas of color",
            min=0.0, max=1000.0, soft_min=0.1, soft_max=10.0, default=1)

    irid_turbulence : FloatProperty(
            name="Turbulence", description="This parameter varies the thickness",
            min=0.0, max=10.0, soft_min=0.000, soft_max=1.0, default=0)
    use_nodes : BoolProperty(name="Use nodes", description="", default=False) #, update=use_material_nodes_callback
    material_active_node : EnumProperty(name="Active node", description="", items=node_enum_callback, update=node_active_callback)
    preview_settings : BoolProperty(name="Preview Settings", description="",default=False)
    object_preview_transform : BoolProperty(name="Transform object", description="",default=False)
    object_preview_scale : FloatProperty(name="XYZ", min=0.5, max=2.0, default=1.0)
    object_preview_rotate : FloatVectorProperty(name="Rotate", description="", min=-180.0, max=180.0,default=(0.0,0.0,0.0), subtype='XYZ')
    object_preview_bgcontrast : FloatProperty(name="Contrast", min=0.0, max=1.0, default=0.5)
    media : EnumProperty(
            name="Media",
            description="",
            items=(('fire', "Fire", ""),
                ('smoke', "Smoke", ""),
                ('other', "Other", "")),
            default='other')
    use_absorption : BoolProperty(name="Absorption", description="", default=False)
    absorption : FloatVectorProperty(
            name="Absorption", description="",
            precision=4, step=0.01, min=0, soft_max=1,
            default=(1.0, 1.0, 1.0), options={'ANIMATABLE'}, subtype='COLOR')
    use_emission : BoolProperty(name="Emission", description="", default=False)
    emission : FloatVectorProperty(
            name="Emission", description="",
            precision=4, step=0.01, min=0, soft_max=1,
            default=(1.0, 1.0, 1.0), options={'ANIMATABLE'}, subtype='COLOR')
    use_scattering : BoolProperty(name="Scattering", description="", default=False)
    scattering : FloatVectorProperty(
            name="Scattering", description="",
            precision=4, step=0.01, min=0, soft_max=1,
            default=(1.0, 1.0, 1.0), options={'ANIMATABLE'}, subtype='COLOR')
    scattering_type : EnumProperty(
            name="Scattering Type",
            description="",
            items=(('1', "1", "Isotropic"),
                ('2', "2", "Mie haze"),
                ('3', "3", "Mie murky"),
                ('4', "4", "Rayleigh"),
                ('5', "5", "Henyey-Greenstein")),
            default='1')
    extinction : FloatProperty(name="Extinction",min = 0.0,max = 1.0,default=1.0)
    eccentricity : FloatProperty(name="Eccentricity",min = -1.0,max = 1.0,default=0.0)
    method : EnumProperty(
            name="Method",
            description="",
            items=(('1', "1", "Recursive"),
                ('2', "2", "Non-recursive"),
                ('3', "3", "Adaptive")),
            default='3') 
    samples_min : IntProperty(name="Min", description="",min=2, max=1024,default=64)
    samples_max : IntProperty(name="Max", description="",min=2, max=1024,default=64)
    aa_level : IntProperty(name="Level", description="",min=0, max=10,default=3)
    aa_threshold : FloatProperty(name="Threshold",min = 0.0,max = 1.0,default=0.1)
    use_aa_jitter : BoolProperty(name="Jitter:", description="", default=False)
    aa_jitter : FloatProperty(name="Value",min = 0.0,max = 1.0,default=0.0)
    confidence : FloatProperty(name="Confidence",min = 0.0,max = 10.0,default=0.9)
    ratio : FloatProperty(name="Ratio",min = 0.0,max = 10.0,default=0.9)
    variance : FloatProperty(name="Variance",min = 0.0,max = 1.0,default=1/128)
    intervals : IntProperty(name="Intervals", description="",min=0, max=10,default=1)
    inputs_number : IntProperty(
            name="Quantity", description="Quantity of sockets of input",
            min=2, default=2)
    uv_x1 : FloatProperty(name="X",description="UV: x1",min=0.00, max=1.00, default=0.0)
    uv_x2 : FloatProperty(name="X",description="UV: x2",min=0.00, max=1.00, default=1.0)
    uv_x3 : FloatProperty(name="X",description="UV: x3",min=0.00, max=1.00, default=1.0)
    uv_x4 : FloatProperty(name="X",description="UV: x4",min=0.00, max=1.00, default=0.0)
    uv_y1 : FloatProperty(name="Y",description="UV: y1",min=0.00, max=1.00, default=0.0)
    uv_y2 : FloatProperty(name="Y",description="UV: y2",min=0.00, max=1.00, default=0.0)
    uv_y3 : FloatProperty(name="Y",description="UV: y3",min=0.00, max=1.00, default=1.0)
    uv_y4 : FloatProperty(name="Y",description="UV: y4",min=0.00, max=1.00, default=1.0)

    @classmethod
    def unregister(cls):
        del bpy.types.Material.povray



class PovrayLightSettings(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Light.povray = PointerProperty(
                name="Povray Lamp Settings",
                description="Povray lamp settings",
                type=cls,
                )
    light_type : EnumProperty(
            name="Map type",
            items=(("parallel", "Parallel", "Sun"),
                   ("shadowless", "Shadowless", "Hemi"),
                   ("cylinder", "Cylinder", "Lazer"),
                   ("spotlight", "Spotlight", "Spot"),
                   ("point", "Point", "Point")),
            default="point",
            update = lamp_type_callback)
    photons_disable : BoolProperty(name="Photons Disable",description="",default=False)
    media_interaction : BoolProperty(name="Media Interaction",description="",default=True)
    media_attenuation : BoolProperty(name="Media Attenuation",description="",default=False)
    fade_power : IntProperty(name="Power", description="",min = 1,max = 10,default=1)
    spot_size : FloatProperty(
            name="Size", description="Spot radius ",
            min=0.0, max=360.0, default=45.0,update = spot_size_callback)
    spot_falloff : FloatProperty(
            name="Falloff", description="Falloff radius ",
            min=0.0, max=360.0, default=60.0)
    tightness : IntProperty(name="Tightness", description="",min = 0,default=0)
    area_enable : BoolProperty(name="Area",description="",default=False)
    samples_1 : IntProperty(name="First", description="",min = 1,max = 100,default=4)
    samples_2 : IntProperty(name="Second", description="",min = 1,max = 100,default=4)
    size_x_1 : FloatProperty(name="X", description="",min = 0.0,default=0.1)
    size_y_1 : FloatProperty(name="Y", description="",min = 0.0,default=0.0)
    size_z_1 : FloatProperty(name="Z", description="",min = 0.0,default=0.0)
    size_x_2 : FloatProperty(name="X", description="",min = 0.0,default=0.0)
    size_y_2 : FloatProperty(name="Y", description="",min = 0.0,default=0.1)
    size_z_2 : FloatProperty(name="Z", description="",min = 0.0,default=0.0)
    area_illumination : BoolProperty(name="Area Illumination",description="",default=False)
    jitter : BoolProperty(name="Jitter",description="",default=False)
    circular : BoolProperty(name="Circular",description="",default=False)
    orient : BoolProperty(name="Orient",description="",default=False)
    adaptive : IntProperty(name="Adaptive", description="",min = 0,max = 3,default=0)
    shape_light : EnumProperty(
            name="Light",
            items=(("looks_like", "Looks Like", ""),
                   ("projected_through", "Projected Through", "")),
            default="looks_like")
    shape : StringProperty(name="Solid Object",maxlen = 1024,update = use_object_light_callback)
    shape_old : StringProperty(maxlen = 1024)

    @classmethod
    def unregister(cls):
        del bpy.types.Light.povray


class PovrayWorldTextureSlots(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Material.povray_texture_slots  = CollectionProperty(
                name="povray_texture_slots",
                description="Povray blob settings",
                type=cls,
                )
    texture : StringProperty(update=world_texture_name_from_uilist)
    texture_search : StringProperty(update=world_texture_name_from_search)

    @classmethod
    def unregister(cls):
        del bpy.types.Material.povray_texture_slots


class PovrayWorldSettings(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.World.povray = PointerProperty(
                name="Povray World Settings",
                description="Povray world settings",
                type=cls,
                )
    active_texture_index : IntProperty(default=0)

    @classmethod
    def unregister(cls):
        del bpy.types.World.povray

class PovrayObjectSettings(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Object.povray = PointerProperty(
                name="Povray Object Settings",
                description="Povray object settings",
                type=cls,
                )
    csg_use: BoolProperty(
            name="csg_enable",
            description="Enable Constructive Solid Geometry",
            default=False)
    nohide_render: BoolProperty(
            name="Renderable",
            description="do not hide from render",
            default=True)
    importance_value: FloatProperty(
            name="Radiosity Importance",
            description="Priority value relative to other objects for sampling radiosity rays. "
                        "Increase to get more radiosity rays at comparatively small yet "
                        "bright objects",
            min=0.01, max=1.00, default=0.50)
    number_operation: IntProperty(name="Number", min=0, default=0)
    queue_number : IntProperty(name = "Queue", min = 0, default = 0)
    used_in_anim : BoolProperty(name = 'Used in animation',default=False)
    dec_only : BoolProperty(name = 'Declare only',default=False)
    use_text : BoolProperty(name = 'Use text',default=False)
    not_loaded : BoolProperty(name = 'Loaded',default=True)
    use_psys_in_csg : BoolProperty(name = 'Use psys in CSG',default=False)
    object_visible : BoolProperty(default=False)
    object_as : StringProperty(default = 'MESH', maxlen=1024)
    smooth_method : EnumProperty(name="Method",items=(("None", "None", ""),("0", "0", ""),("1", "1", ""),("2", "2", ""),("3", "3", "")),default="None")
    object_material : EnumProperty(
            name="Object material",
            items= (("surface", "Surface", ""),
                    ("volume", "Volume", "")),
            default="surface")
    object_material_use_nodes: BoolProperty(default=False)
    scene_object: BoolProperty(default=False)
    mesh_write_as : EnumProperty(
            name="Mesh Write As",
            items=( ("NONE", "None", ""),
                    ("BLOBGRID", "Blob Grid", ""),
                    ("GRID", "Grid", ""),
                    ("MESH", "Mesh", "")),
            default="MESH")
    shape_as_light : StringProperty(name="Light",maxlen=1024)
    percent : FloatProperty(
            name="Percent", description="Percent",
            min=0.0, max=100.0,default=0.0)
    object_ior : FloatProperty(
            name="IOR", description="IOR",
            min=1.0, max=10.0,default=1.0)
    fake_caustics_power : FloatProperty(
            name="Power", description="Fake caustics power",
            min=0.0, max=10.0,default=0.0)
    target : BoolProperty(name="Target",description="",default=False)
    target_value : FloatProperty(
            name="Value", description="",
            min=0.0, max=1.0,default=1.0)
    refraction : BoolProperty(name="Refraction",description="",default=False)
    dispersion : BoolProperty(name="Dispersion",description="",default=False)
    dispersion_value : FloatProperty(
            name="Dispersion", description="Good values are 1.01 to 1.1. ",
            min=1.0, max=1.2,default=1.01)
    dispersion_samples : IntProperty(name="Samples",min=2, max=100,default=7)
    reflection : BoolProperty(name="Reflection",description="",default=False)
    pass_through : BoolProperty(name="Pass through",description="",default=False)
    no_shadow : BoolProperty(name="No Shadow",default=False)
    no_image : BoolProperty(name="No Image",default=False)
    no_reflection : BoolProperty(name="No Reflection",default=False)
    no_radiosity : BoolProperty(name="No Radiosity",default=False)
    inverse : BoolProperty(name="Inverse",default=False)
    sturm : BoolProperty(name="Sturm",default=False)
    double_illuminate : BoolProperty(name="Double Illuminate",default=False)
    hierarchy : BoolProperty(name="Hierarchy",default=False)
    hollow : BoolProperty(name="Hollow",default=False)
    boundorclip : EnumProperty(
            name="Boundorclip",
            items=(("none", "None", ""),
                   ("bounded_by", "Bounded_by", ""),
                   ("clipped_by", "Clipped_by", "")),
            default="none")
    boundorclipob : StringProperty(maxlen=1024)
    addboundorclip : BoolProperty(description="",default=False)
    cylinder_blob : BoolProperty(name = 'Blob',description="",default=False)
    cylinder_radius : FloatProperty(name="Radius",min=0.0, max=10.0,step=1, precision=4, default=0.04)
    cylinder_strength : FloatProperty(name="Strength",min=-10.00, max=10.0, default=1.00)
    cylinder_threshold : FloatProperty(name="Threshold",min=0.00, max=10.0, default=0.6)
    sphere_blob : BoolProperty(name = 'Blob',description="",default=False)
    sphere_radius : FloatProperty(name="Radius",min=0.0, max=10.0,step=1, precision=4, default=0.04)
    blob_strength : FloatProperty(name="Strength",min=-1000.00, max=1000.0, default=2.00,update = meta_update_callback)
    blob_threshold : FloatProperty(name="Threshold",min=0.00, max=10.0, default=0.6)
    res_u : IntProperty(name="U",min=100, max=1000, default=100)
    res_v : IntProperty(name="V",min=100, max=1000, default=100)
    function_text : StringProperty(name="Function Text",maxlen=1024,update=iso_props_update_callback)
    contained_by : EnumProperty(
            name="Contained by",
            items=(("box", "Box", ""),
                   ("sphere", "Sphere", "")),
            default="box")
    container_scale : FloatProperty(name="Container Scale",min=0.0, max=10.0, default=1.00)
    threshold : FloatProperty(name="Threshold",min=0.0, max=10.0, default=0.00)
    accuracy : FloatProperty(name="Accuracy",min=0.0001, max=0.1, default=0.001)
    max_gradient : FloatProperty(name="Max Gradient",min=0.0, max=100.0, default=5.0)
    all_intersections : BoolProperty(name="All Intersections",default=False)
    max_trace : IntProperty(name="Max Trace",min=1, max=100,default=1)
    shape_se_param1 : FloatProperty(
            name="Parameter 1",
            description="",
            min=0.00, max=10.0, default=0.04)

    shape_se_param2 : FloatProperty(
            name="Parameter 2",
            description="",
            min=0.00, max=10.0, default=0.04)
    shape_st_radius_major : FloatProperty(
            name="Major radius",
            description="Major radius",
            min=0.00, max=100.00, default=1.0)

    shape_st_radius_minor : FloatProperty(
            name="Minor radius",
            description="Minor radius",
            min=0.00, max=100.00, default=0.25)

    shape_st_ring :FloatProperty(
            name="Ring",
            description="Ring manipulator",
            min=0.0001, max=100.00, default=1.00)

    shape_st_cross : FloatProperty(
            name="Cross",
            description="Cross manipulator",
            min=0.0001, max=100.00, default=1.00)

    shape_st_accuracy : FloatProperty(
            name="Accuracy",
            description="Supertorus accuracy",
            min=0.00001, max=1.00, default=0.001)

    shape_st_max_gradient : FloatProperty(
            name="Gradient",
            description="Max gradient",
            min=0.0001, max=100.00, default=10.00)

    shape_cone_radius_base : FloatProperty()
    shape_cone_radius_cap : FloatProperty()
    shape_cone_point_base : FloatProperty()
    shape_cone_point_cap : FloatProperty()

    shape_hf_filename : StringProperty(maxlen = 1024)
    shape_hf_gamma : FloatProperty(
            name="Gamma",
            description="Gamma",
            min=0.0001, max=20.0, default=1.0)

    shape_hf_premultiplied : BoolProperty(
            name="Premultiplied",
            description="Premultiplied",
            default=True)

    shape_hf_smooth : BoolProperty(
            name="Smooth",
            description="Smooth",
            default=False)

    shape_hf_water : FloatProperty(
            name="Water Level",
            description="Wather Level",
            min=0.00, max=1.00, default=0.0)

    shape_hf_hierarchy : BoolProperty(
            name="Hierarchy",
            description="Height field hierarchy",
            default=True)
    u_min : FloatProperty(name = "U Min",
                    description = "",
                    default = 0.0)
    v_min : FloatProperty(name = "V Min",
                    description = "",
                    default = 0.0)
    u_max : FloatProperty(name = "U Max",
                    description = "",
                    default = 6.28)
    v_max : FloatProperty(name = "V Max",
                    description = "",
                    default = 12.57)
    x_eq : StringProperty(maxlen=1024, default = "cos(v)*(1+cos(u))*sin(v/8)")
    y_eq : StringProperty(maxlen=1024, default = "sin(u)*sin(v/8)+cos(v/8)*1.5")
    z_eq : StringProperty(maxlen=1024, default = "sin(v)*(1+cos(u))*sin(v/8)")
    cone_root : FloatProperty(name="Root",min=0.0, max=1.0, default=0.003)
    cone_tip : FloatProperty(name="Tip",min=0.0, max=1.0, default=0.0)
    needles : EnumProperty(
            items=[("needles", "Needles", ""),
                   ("branch", "Branch", ""),
                   ("both", "Both", "")],
            name="Needles Branch",
            description="",
            default="both")
    boolean_operation : EnumProperty(
            items=[("DIFFERENCE", "Difference", ""),
                   ("INTERSECT", "Intersection", ""),
                   ("MERGE", "Merge", ""),
                   ("UNION", "Union", "")],
            name="Operation 1",
            description="",
            default="DIFFERENCE")

    boolean_object_1 : StringProperty(
            name="Object",
            description="Select object for boolean operations")

    boolean_group_2 : StringProperty(
            name="Group",
            description="Select group for boolean operations")
            
    boolean_object_2 : StringProperty(
            name="Object",
            description="Select object for boolean operations")

    ngon : IntProperty(name = "NGon",
                    description = "",
                    min = 3, max = 64,default = 5)
    ngonR : FloatProperty(name = "NGon Radius",
                    description = "",
                    default = 0.3)
    circleR : FloatProperty(name = "Circle Radius",
                    description = "",
                    default = 1.0)

    prism_sweep : BoolProperty(name = "Conic Sweep",
                    description = "",
                    default = False)
    text_link : StringProperty()

    # shapes.inc

    round_radius : FloatProperty(name = "Radius",default = 0.01, min = 0.0, max = 1.0)
    round_wire : BoolProperty(name = "Wire",default = False)
    union_merge : BoolProperty(name = "Merge",default = False)
    xmin : FloatProperty()
    ymin : FloatProperty()
    zmin : FloatProperty()
    xmax : FloatProperty()
    ymax : FloatProperty()
    zmax : FloatProperty()
    #HG
    tesselation : EnumProperty(
            items=[("bourke", "bourke", ""),
                   ("cristal", "cristal", ""),
                   ("cubicle", "cubicle", ""),
                   ("heller", "heller", ""),
                   ("tessel", "tessel", ""),
                   ("tesselate", "tesselate", "")],
            name="Tesselation",
            description="",
            default="cubicle")
    accuracy_x : IntProperty(name="X",description="Accuracy X (number of slices in each direction)",min=1, max=1000, default=10)
    accuracy_y : IntProperty(name="Y",description="Accuracy Y (number of slices in each direction)",min=1, max=1000, default=10)
    accuracy_z : IntProperty(name="Z",description="Accuracy Z (number of slices in each direction)",min=1, max=1000, default=10)
    tes_precision : FloatProperty(name="Precision",description="",min=0.00, max=1.00, default=0.0)
    tes_offset : FloatProperty(name="Offset",description="",default=0.0)

    # uberpov
    glow : BoolProperty(name = "Glow",default = False, update = glow_callback)
    glow_type : IntProperty(name="Type",description="",min=0, max=3, default=2)
    glow_size : FloatProperty(name="Size",description="",min=0.00, max=100.00, default=0.05)
    glow_radius : FloatProperty(name="Radius",description="",min=0.00, max=1000.00, default=50.0)
    glow_fade_power : FloatProperty(name="Fade Power",description="",min=0.00, max=10.00, default=1.0)
    glow_color : FloatVectorProperty(
            name="Color", description="",
            precision=4, step=0.01, min=0, soft_max=1,
            default=(1.0, 1.0, 1.0), options={'ANIMATABLE'}, subtype='COLOR')
    @classmethod
    def unregister(cls):
        del bpy.types.Object.povray

class PovrayParticleSettings(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.ParticleSettings.povray = PointerProperty(
                name="Povray Hair Settings",
                description="Povray hair settings",
                type=cls,
                )
    convert : BoolProperty(
            name="Convert",
            description="Convert to mesh",
            default=False)

    particle_texture : StringProperty(
            name="Texture",
            description="",
            default="")

    emitter_uv_image = StringProperty(
            name="Emitter UV-image",
            description="",
            default="")

    object_as_particle : StringProperty(
            name="Object as particle",
            description="",
            default="")

    particle_type : EnumProperty(
            items=[("CONE", "Cone", ""),
                   ("OBJECT", "Object", ""),
                   ("SPHERE", "Sphere", ""),
                   ("SPLINE", "Spline", ""),
                   ("SPHERESWEEP", "Sphere sweep", "")],
            name="Type",
            description="",
            default="CONE")

    spark : BoolProperty(
            name="Spark",
            description="Root to center objects",
            default=False)

    sweep_tolerance : FloatProperty(
            name="Tolerance",
            description="Tolerance in Povray",
            min=1.0, max=100000000.0, default=1.0)

    thickness_root : FloatProperty(
            name="Root",
            description="Thickness of roots of hair",
            min=0.00001, max=1.00, default=0.001)

    thickness_tip : FloatProperty(
            name="Tip",
            description="Thickness of tip of hair",
            min=0.00001, max=1.00, default=0.001)

    @classmethod
    def unregister(cls):
        del bpy.types.ParticleSettings.povray

class PovrayTextSettings(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.TextCurve.povray = PointerProperty(
                name="Povray Texts Settings",
                description="Povray texts settings",
                type=cls,
                )
    text_type : EnumProperty(
            name="Text Type",
            items=(("regular", "Regular", ""),
                   ("bevelled", "Bevelled", "")),
            default="regular")
    text_cuts : IntProperty(name="Cuts", min=0, max=1000, default=10)
    text_bevel_angle : FloatProperty(name="Angle", min=0.0, max=180.0, default=35.0)
    text_bevel_depth : FloatProperty(name="Depth", min=0.0, max=10.0, default=0.045)

    @classmethod
    def unregister(cls):
        del bpy.types.TextCurve.povray


class PovrayMeshSettings(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Mesh.blobbys  = CollectionProperty(
                name="Povray Blob",
                description="Povray blob settings",
                type=cls,
                )
    name : StringProperty(name="name")
    index : IntProperty(name="index")
    radius : FloatProperty(name="radius")

    @classmethod
    def unregister(cls):
        del bpy.types.Mesh.blobbys

class PovrayCSGSettings(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Object.pov_csg = CollectionProperty(type=cls)

    name : StringProperty(name='Operation', default='Operation')
    csg: EnumProperty(
            name="CSG",
            items=(("difference", "Difference", ""),
                   ("intersection", "Intersection", ""),
                   ("merge", "Merge", ""),
                   ("union", "Union", "")),
            default="difference")
    split_union: BoolProperty(name="Split Union",default = True)
    object_collection: EnumProperty(
            name="Object or collection",
            items=(("object", "Object", ""),
                   ("collection", "Collection", "")),
            default="object")
    object_csg : StringProperty(name = "Object",default="")
    collection_csg : StringProperty(name = "Collection",default="")

    @classmethod
    def unregister(cls):
        del bpy.types.Object.pov_csg



classes = (
    PovrayCameraSettings,
    PovrayCSGSettings,
    PovrayLightSettings,
    PovrayMaterialSettings,
    PovrayMeshSettings,
    PovrayObjectSettings,
    PovrayParticleSettings,
    PovrayRenderSettings,
    PovrayTextSettings,
    PovrayWorldSettings,
    PovrayWorldTextureSlots,
    PovrayMaterialTextureSlots,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in classes:
        unregister_class(cls)


