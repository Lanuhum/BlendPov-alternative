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

import os
import bpy
import bpy.utils.previews
from bpy.types import Panel, Menu, Operator, Header
from bpy.types import Curve, SurfaceCurve, TextCurve
from bl_ui.properties_texture import context_tex_datablock
from bpy.utils import register_class,unregister_class

from bl_ui.properties_render import RENDER_PT_color_management
RENDER_PT_color_management.COMPAT_ENGINES.add('POVRAY')
from bl_ui import properties_output
for member in dir(properties_output):
    subclass = getattr(properties_output, member)
    try:
        subclass.COMPAT_ENGINES.add('POVRAY')
    except:
        pass
del properties_output

from bl_ui import properties_material
for member in dir(properties_material):
    subclass = getattr(properties_material, member)
    try:
        subclass.COMPAT_ENGINES.add('POVRAY')
    except:
        pass
del properties_material

from bl_ui import properties_view_layer
for member in dir(properties_view_layer):
    subclass = getattr(properties_view_layer, member)
    try:
        subclass.COMPAT_ENGINES.add('POVRAY')
    except:
        pass
del properties_view_layer

from bl_ui import properties_data_light
properties_data_light.DATA_PT_context_light.COMPAT_ENGINES.add('POVRAY')
del properties_data_light

from bl_ui import properties_data_mesh
for member in dir(properties_data_mesh):
    subclass = getattr(properties_data_mesh, member)
    try:
        subclass.COMPAT_ENGINES.add('POVRAY')
    except:
        pass
del properties_data_mesh

from bl_ui import properties_particle as properties_particle
for member in dir(properties_particle):
    subclass = getattr(properties_particle, member)
    try:
        subclass.COMPAT_ENGINES.add('POVRAY')
    except:
        pass
del properties_particle

addonDir=os.path.dirname(__file__)
iconDir=os.path.join(addonDir, "icons")

def particle_get_settings(context):
    if context.particle_system:
        return context.particle_system.settings
    elif isinstance(context.space_data.pin_id, bpy.types.ParticleSettings):
        return context.space_data.pin_id
    return None

def find_node_input(node, name):
    for input in node.inputs:
        if input.name == name:
            return input

class ParticleButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "particle"


class TextureButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"


class MaterialButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"


class RenderButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

class SceneButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

class ObjectButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"


class CurveButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"


class DataButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"


class CameraButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"


class WorldButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"


class View3DPanel():
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'


class POVRAY_VIEW3D_PT_tools(View3DPanel, Panel):
    bl_category = "Povray"
    bl_context = "objectmode"
    bl_label = "Tools"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        ob = context.object
        return ob and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        scn=context.scene
        layout = self.layout
        box = layout.box()
        box.prop(scn.povray,'number_copy')
        box.prop(scn.povray,'axis_select')
        box.operator("object.copyaround")
        box = layout.box()
        box.prop(scn.povray,'resolution')
        box.operator("povray.lathemesh")

class POVRAY_CAMERA_PT_camera(CameraButtonsPanel, bpy.types.Panel):
    bl_label = "Camera settings"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):

        ob = context.object
        engine = context.scene.render.engine
        return (ob.type in {"CAMERA"} and engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        camera = context.camera
        layout=self.layout
        layout.prop(camera.povray,"cam_type")
        if camera.povray.cam_type in {'stereo','omni_directional_stereo'}:
            layout.prop(camera.povray,"stereo_dist")
        if camera.povray.cam_type in {'stereo'}:
            box = layout.box()
            box.label('Parallaxe:')
            row = box.row()
            row.prop(camera.povray,"parallaxe_0")
            row.prop(camera.povray,"parallaxe_1")
        if camera.povray.cam_type == "cylinder":
            layout.prop(camera.povray,"cylinder_cam_type")
        layout.prop(camera,"lens")
        layout.prop(camera.povray,"blur_enable")
        if camera.povray.blur_enable:
            ob = None
            for obj in context.scene.objects:
                if obj.type == "CAMERA" and obj.data.name == camera.name:
                    ob = obj
            trackTo = None
            for const in ob.constraints:
                if const and const.type == "TRACK_TO" and const.target: 
                    trackTo = const.target
                    break
            if trackTo == None:
                layout.label('Constraint "Track To" isn\'t found!',icon = "ERROR")
            else:
                layout.prop_search(camera.povray,"focal_point", context.blend_data, "objects")
                box = layout.box()
                box.label("Sampling:")
                row = box.row()
                row.prop(camera.povray,"blur_samples_min")
                row.prop(camera.povray,"blur_samples_max")
                layout.prop(camera.povray,"aperture")
                layout.prop(camera.povray,"confidence")
                layout.prop(camera.povray,"variance")
        layout.prop(camera.povray,"normal_enable")
        if camera.povray.normal_enable:
            layout.prop(camera.povray,"normal_patterns")
            layout.prop(camera.povray,"cam_normal")
            layout.prop(camera.povray,"turbulence")
            layout.prop(camera.povray,"scale")
        layout.label("Shift:")
        row = layout.row()
        row.prop(camera,"shift_x",text='X')
        row.prop(camera,"shift_y",text='Y')


class POVRAY_LIGHT_PT_light(DataButtonsPanel, bpy.types.Panel):
    bl_label = "Lamp settings"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):

        ob = context.object
        engine = context.scene.render.engine
        return (ob.type in {"LIGHT"} and engine in cls.COMPAT_ENGINES)

    def draw(self, context):

        light = context.light
        lp = light.povray
        layout=self.layout
        layout.prop(lp,"light_type",expand = True)
        layout.prop(light,"color")
        layout.prop(light,"energy")
        layout.prop(lp,"photons_disable")
        layout.prop(lp,"media_interaction")
        layout.prop(lp,"media_attenuation")
        if lp.light_type in {'point'}:
            layout.prop(lp,"shape_light",expand = True)
            layout.prop_search(lp,"shape",context.blend_data,"objects")
        box = layout.box()
        box.label(text="Fade:")
        row=box.row()
        row.prop(light,"distance")
        row.prop(lp,"fade_power")
        if lp.light_type in {"spotlight","cylinder"}:
            row=layout.row()
            row.prop(lp,"spot_size",text="Radius")
            row.prop(lp,"spot_falloff")
            layout.prop(lp,"tightness")

        if lp.light_type in {'parallel','spotlight','point'}:
            is_area = True
            if lp.light_type in {'point'} and (lp.shape != "" and lp.shape_light == "looks_like"):
                is_area = False
            if is_area:
                box = layout.box()
                box.prop(lp,"area_enable")
                if lp.area_enable:
                    box.label("Size:")
                    row=box.row()
                    col=row.column(align=True)
                    col.prop(lp,"size_x_1")
                    col.prop(lp,"size_y_1")
                    col.prop(lp,"size_z_1")
                    col=row.column(align=True)
                    col.prop(lp,"size_x_2")
                    col.prop(lp,"size_y_2")
                    col.prop(lp,"size_z_2")
                    box.label("Sampling:")
                    row=box.row()
                    row.prop(lp,"samples_1")
                    row.prop(lp,"samples_2")
        
                    box.prop(lp,"area_illumination")
                    box.prop(lp,"jitter")
                    box.prop(lp,"circular")
                    box.prop(lp,"orient")
                    box.prop(lp,"adaptive")

class POVRAY_OBJECT_PT_shape(ObjectButtonsPanel, bpy.types.Panel):
    bl_label = "Povray object"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        scene = context.scene
        ob = context.object
        layout=self.layout
        text = ob.povray.object_as
        if ob.type == "MESH" and text == "":
            text = "MESH"
            if scene.povray.render == 'uberpov' and ob.povray.glow:
                text = 'GLOW'
        if ob.type == "CURVE":
            pass
        if ob.type == "FONT" and text == "":
            text = "TEXT"
        if ob.type == "META" and text == "":
            text = "BLOB"
        if ob.type == "SURFACE" and text == "":
            text = "BICUBIC_PATCH"
        layout.label(text="Oblect: %s"%text)
        layout.prop(ob.povray,"scene_object", text="Used in scene")
        layout.prop(ob.povray,"dec_only")
        layout.prop(ob.povray,"use_text")
        layout.prop(ob.povray,"used_in_anim")
        if scene.povray.render == 'uberpov':
            layout.prop(ob.povray,"glow")
        if scene.povray.render != 'uberpov' or (scene.povray.render == 'uberpov' and ob.povray.glow == False):
            row = layout.row()
            row.label(text='Material:')
            row.prop(ob.povray,"object_material",expand = True)
            if ob.povray.object_material == 'surface':
                if ob.type == "CURVE":
                    layout.prop(ob.povray,"curveshape")
                    if ob.povray.curveshape in {'loft','birail'}:
                        layout.prop(ob.povray,"res_u")
                        layout.prop(ob.povray,"res_v")
        
                if text == "MESH":
                    layout.prop(ob.povray,"use_psys_in_csg")
                    layout.label(text='Mesh Write As:')
                    layout.prop(ob.povray,"mesh_write_as",expand = True)
    
                    if ob.povray.mesh_write_as in {'prism'}:
                        row = layout.row()
                        row.label(text='Height random:')
                        row.prop(ob.povray,"percent",text = '%')
                        layout.prop(ob.povray,"prism_sweep")
    
                    if ob.povray.mesh_write_as in {'GRID'}:
                        box = layout.box()
                        box.label(text='Edges: Cylinders')
                        row = box.row()
                        row.prop(ob.povray,"cylinder_radius")
                        row.prop(ob.povray,"cylinder_blob")
                        if ob.povray.cylinder_blob:
                            row = box.row()
                            row.prop(ob.povray,"cylinder_threshold")
                            row.prop(ob.povray,"cylinder_strength")
                        box = layout.box()
                        box.label('Vertices: Spheres')
                        row = box.row()
                        row.prop(ob.povray,"sphere_radius")
                        row.prop(ob.povray,"sphere_blob")
                        if ob.povray.sphere_blob:
                            row = box.row()
                            row.prop(ob.povray,"blob_threshold")
                            row.prop(ob.povray,"blob_strength")
                    if ob.povray.mesh_write_as in {'BLOBGRID'}:
                        box = layout.box()
                        row = box.row()
                        row.label(text='Edges: Cylinders')
                        row.prop(ob.povray,"cylinder_radius")
                        row = box.row()
                        row.label(text='Vertices: Spheres')
                        row.prop(ob.povray,"sphere_radius")
                        row = box.row()
                        row.prop(ob.povray,"blob_threshold")
                        row.prop(ob.povray,"blob_strength")
        
                if text in {"ISOSURFACE","PARAMETRIC"}:
                    if text in {"ISOSURFACE"}:
                        layout.prop_search(ob.povray,"function_text", context.blend_data, "texts")
                    layout.label('Contained by:')
                    layout.prop(ob.povray,"contained_by",expand = True)
                    layout.prop(ob.povray,"container_scale")
                    if text in {"ISOSURFACE"}:
                        layout.prop(ob.povray,"threshold")
                    layout.prop(ob.povray,"accuracy")
                    layout.prop(ob.povray,"max_gradient")
                    if text in {"ISOSURFACE"}:
                        layout.prop(ob.povray,"all_intersections")
                        if ob.povray.all_intersections == False:
                            layout.prop(ob.povray,"max_trace")
                    node_tree = bpy.context.scene.node_tree
                    if node_tree:
                        for node in node_tree.nodes:
                            if node.bl_idname == "IsoPropsNode" and node.label == ob.name:
                                layout.context_pointer_set("node", node)
                                if hasattr(node, "draw_buttons_ext"):
                                    node.draw_buttons_ext(context, layout)
                                elif hasattr(node, "draw_buttons"):
                                    node.draw_buttons(context, layout)
                                value_inputs = [socket for socket in node.inputs if socket.enabled and not socket.is_linked]
                                if value_inputs:
                                    layout.separator()
                                    layout.label("Inputs:")
                                    for socket in value_inputs:
                                        row = layout.row()
                                        socket.draw(context, row, node, socket.name)
                if text == 'HEIGHT_FIELD':
                    layout.prop(ob.povray,"shape_hf_gamma")
                    layout.prop(ob.povray,"shape_hf_premultiplied")
                    layout.prop(ob.povray,"shape_hf_smooth")
                    layout.prop(ob.povray,"shape_hf_water")
                    layout.prop(ob.povray,"shape_hf_hierarchy")
        
                if text == 'BOOLEAN':
        
                    layout.prop(ob.povray, "boolean_operation", text="")
                    layout.prop_search(ob.povray, "boolean_object_2", context.scene, "objects")
                    layout.prop_search(ob.povray, "boolean_group_2", context.blend_data, "groups")
                    layout.operator("povray.booleanmesh",text='Apply')
        
                if text == 'SUPERTORUS':
                    layout.prop(ob.povray,"shape_st_radius_major")
                    layout.prop(ob.povray,"shape_st_radius_minor")
                    layout.prop(ob.povray,"shape_st_ring")
                    layout.prop(ob.povray,"shape_st_cross")
    
                if text == "NEEDLES":
                    layout.prop(ob.povray,"needles",expand = True)
                    if ob.povray.needles in {'branch','both'}:
                        layout.label('Branch:')
                        layout.prop(ob.povray,"sphere_radius")
                        row = layout.row()
                        row.prop(ob.povray,"blob_threshold")
                        row.prop(ob.povray,"blob_strength")
                    if ob.povray.needles in {'needles','both'}:
                        layout.label('Needles:')
                        row=layout.row()
                        row.prop(ob.povray,"cone_root")
                        row.prop(ob.povray,"cone_tip")
    
                if text == "CONESWEEP":
                    row = layout.row()
                    row.prop(ob.povray,"blob_threshold")
                    row.prop(ob.povray,"blob_strength")
    
                if text in {'ROUNDBOX'}:
                    layout.prop(ob.povray,"round_radius")
                    layout.prop(ob.povray,"round_wire")
                    layout.prop(ob.povray,"union_merge")
    
                # if ob.type == "MESH" and text != 'MESH':
                    # layout.operator('povray.mesh')
    
                if scene.povray.render == 'hgpovray':
                    if text != "MESH":
                        layout.label('Tesselation:')
                        row = layout.row()
                        col = row.column()
                        col.prop(ob.povray,"tesselation",expand = True)
                        col = row.column()
                        col.prop(ob.povray,"accuracy_x")
                        col.prop(ob.povray,"accuracy_y")
                        col.prop(ob.povray,"accuracy_z")
                        col.prop(ob.povray,"tes_precision")
                        col.prop(ob.povray,"tes_offset")
                    layout.label('HG smooth method:')
                    layout.prop(ob.povray,"smooth_method",expand = True)

        if scene.povray.render == 'uberpov' and ob.povray.glow:
            layout.prop(ob.povray,"glow_type")
            layout.prop(ob.povray,"glow_size")
            layout.prop(ob.povray,"glow_radius")
            layout.prop(ob.povray,"glow_fade_power")
            layout.prop(ob.povray,"glow_color")

class POVRAY_OBJECT_PT_interior(ObjectButtonsPanel, bpy.types.Panel):
    bl_label = "Povray Object Interior"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        scene = context.scene
        ob = context.object
        layout=self.layout
        layout.prop(ob.povray,"object_ior")
        if scene.povray.photon_enable == False and ob.povray.object_ior > 1.0:
            layout.label("Fake caustics:")
            layout.prop(ob.povray,"fake_caustics_power") 

class POVRAY_OBJECT_PT_photons(ObjectButtonsPanel, bpy.types.Panel):
    bl_label = "Povray Object Photons"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        engine = context.scene.render.engine
        return (scene.povray.photon_enable and (engine in cls.COMPAT_ENGINES))

    def draw(self, context):
        ob = context.object
        layout=self.layout
        if ob.povray.pass_through == False:
            row = layout.row()
            row.prop(ob.povray,"target")
            if ob.povray.target:
                row.prop(ob.povray,"target_value")
                layout.prop(ob.povray,"refraction")
                if ob.povray.refraction:
                    layout.prop(ob.povray,"dispersion")
                    if ob.povray.dispersion:
                        layout.prop(ob.povray,"dispersion_value")
                        layout.prop(ob.povray,"dispersion_samples")
                layout.prop(ob.povray,"reflection")
        if ob.povray.target == False:
            layout.prop(ob.povray,"pass_through")

class POVRAY_OBJECT_PT_modifiers(ObjectButtonsPanel, bpy.types.Panel):
    bl_label = "Povray Object Modifiers"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):

        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):

        ob = context.object
        layout=self.layout
        layout.prop(ob.povray,"hollow")
        layout.prop(ob.povray,"double_illuminate")
        layout.prop(ob.povray,"sturm")
        layout.prop(ob.povray,"no_shadow")
        layout.prop(ob.povray,"no_image")
        layout.prop(ob.povray,"no_reflection")
        layout.prop(ob.povray,"no_radiosity")
        layout.prop(ob.povray,"inverse")
        layout.prop(ob.povray,"hierarchy")
        layout.prop(ob.povray,"boundorclip",text="Bound / Clip")
        if ob.povray.boundorclip != "none":
            layout.prop_search(ob.povray,"boundorclipob",context.blend_data,"objects",text="Object")
            text = "Clipped by"
            if ob.povray.boundorclip == "clipped_by":
                text = "Bounded by"
            layout.prop(ob.povray,"addboundorclip",text=text)

class POVRAY_OBJECT_PT_csg(ObjectButtonsPanel, bpy.types.Panel):
    bl_label = "POV-Ray: CSG"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):

        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
        ob = context.object
        self.layout.prop(ob.povray, "csg_enable", text="")

    def draw(self, context):
        obj = context.object
        if obj.povray.csg_enable:
            layout = self.layout
            split = layout.split()
            col = split.column()
            col.label(text = 'Constructive Solid Geometry:')
            row = col.row()
            row.label(text='Operation:')
            row.operator("pov.csg_settings_add", icon='ADD')
            row = col.row()
            row.prop(obj.povray,"number_operation")
            row.operator("pov.csg_settings_remove", icon = 'REMOVE')
            col.operator("pov.csg_write")
            for i, value in enumerate(obj.pov_csg):
                layout.label(text='Operation  %s:'%i)
                layout.prop(obj.pov_csg[i],"csg",expand = True)
                if obj.pov_csg[i].csg == 'union':
                    layout.prop(obj.pov_csg[i],"split_union")
                layout.prop(obj.pov_csg[i],"object_collection",expand = True)
                if obj.pov_csg[i].object_collection in {"object"}:
                    layout.prop_search(obj.pov_csg[i],"object_csg", bpy.data, "objects")
                if obj.pov_csg[i].object_collection in {"collection"}:
                    layout.prop_search(obj.pov_csg[i],"collection_csg", bpy.data, "collections")

class POVRAY_TEXT_PT_text(CurveButtonsPanel, bpy.types.Panel):
    bl_label = "Povray Settings"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        curve = context.curve
        #is_surf = type(curve) is SurfaceCurve
        #is_curve = type(curve) is Curve
        is_text = type(curve) is TextCurve
        return (engine in cls.COMPAT_ENGINES and is_text)

    def draw(self, context):
        curve = context.curve
        cupov = curve.povray
        layout=self.layout
        layout.prop(cupov,"text_type")
        if cupov.text_type == "bevelled":
            layout.prop(cupov,"text_cuts")
            layout.prop(cupov,"text_bevel_angle")
            layout.prop(cupov,"text_bevel_depth")
        layout.prop(curve,"extrude")

class POVRAY_PARTICLES_PT_particles(ParticleButtonsPanel, bpy.types.Panel):
    bl_label = "Povray Particles"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        pSys = context.particle_system
        rd = context.scene.render
        return pSys and pSys.settings.type == 'HAIR' and (rd.engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        part = particle_get_settings(context)
        pType = context.particle_system.settings.type
        layout=self.layout
        if part:
            layout.prop(part.povray,"particle_type")
            if part.povray.particle_type == 'OBJECT':
                layout.prop_search(part.povray,"object_as_particle", context.blend_data, "objects")
            else:
                layout.prop_search(part.povray,"particle_texture", context.blend_data, "materials",text="Texture")
                layout.prop_search(part.povray,"emitter_uv_image", context.blend_data, "images")
                layout.prop(part.povray,"spark")
                if part.povray.particle_type == "SPHERESWEEP":
                    layout.prop(part.povray,"sweep_tolerance")
                layout.label(text="Thickness")
                row=layout.row(align=True)
                row.prop(part.povray,"thickness_root")
                row.prop(part.povray,"thickness_tip")

class TEXTURE_PT_context(TextureButtonsPanel, Panel):
    bl_label = ""
    bl_context = "texture"
    bl_options = {'HIDE_HEADER'}
    COMPAT_ENGINES = {'POVRAY', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}

    def draw(self, context):
        engine = context.scene.render.engine
        if engine == 'POVRAY':
            pass
        else:
            layout = self.layout
            tex = context.texture
            space = context.space_data
            pin_id = space.pin_id
            use_pin_id = space.use_pin_id
            user = context.texture_user
    
            col = layout.column()
    
            if not (use_pin_id and isinstance(pin_id, bpy.types.Texture)):
                pin_id = None
    
            if not pin_id:
                col.template_texture_user()
    
            if user or pin_id:
                col.separator()
    
                if pin_id:
                    col.template_ID(space, "pin_id")
                else:
                    propname = context.texture_user_property.identifier
                    col.template_ID(user, propname, new="texture.new")
    
                if tex:
                    col.separator()
    
                    split = col.split(factor=0.2)
                    split.label(text="Type")
                    split.prop(tex, "type", text="")

class POVRAY_TEXTURE_PT_texslot(TextureButtonsPanel, bpy.types.Panel):
    bl_label = "Textures"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        if not hasattr(context, "texture_slot"):
            return False
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        space = context.space_data
        mat = context.material
        world=context.world
        slot = getattr(context, "texture_slot", None)
        idblock = context_tex_datablock(context)
        pin_id = space.pin_id
        layout = self.layout
        #layout.prop(space, "texture_context", expand=True)       
        if mat or context.world:
            row = layout.row()
            row.template_list("TEXTURE_UL_texslots", "", idblock, "texture_slots", idblock, "active_texture_index", rows=2)        
            col = row.column(align=True)
            col.operator("texture.slot_move", text="").type = 'UP'
            col.operator("texture.slot_move", text="").type = 'DOWN'
            col = layout.column(align=True)
            col.template_ID(idblock, "active_texture", new="texture.new")

class POVRAY_TEXTURE_PT_preview(TextureButtonsPanel, bpy.types.Panel):
    bl_label = "Preview"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        if not hasattr(context, "texture_slot"):
            return False
        tex=context.texture
        return (tex and (engine in cls.COMPAT_ENGINES))

    def draw(self, context):
        tex = context.texture
        layout=self.layout
        idblock = context_tex_datablock(context)
        slot = getattr(context, "texture_slot", None)
        if idblock:
            layout.template_preview(tex, parent=idblock, slot=slot)
        else:
            layout.template_preview(tex, slot=slot)

        layout.operator('tex.preview_update')

class POVRAY_TEXTURE_PT_blender_particles(TextureButtonsPanel, bpy.types.Panel):
    bl_label = "Texture"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        if not hasattr(context, "texture_slot"):
            return False
        part = context.particle_system
        tex=context.texture
        return (part and (engine in cls.COMPAT_ENGINES))

    def draw(self, context):
        tex = context.texture
        mat=context.material
        scene=context.scene
        ob=context.object
        align=True
        layout=self.layout
        idblock = context_tex_datablock(context)
        row = layout.row()

        row.template_list("TEXTURE_UL_texslots", "", idblock, "texture_slots", idblock, "active_texture_index", rows=2)

        col = row.column(align=True)
        col.operator("texture.slot_move", text="").type = 'UP'
        col.operator("texture.slot_move", text="").type = 'DOWN'
        col.menu("TEXTURE_MT_specials", icon='DOWNARROW_HLT', text="")
        layout.template_ID(idblock, "active_texture", new="texture.new")
        if tex:
            layout.prop(tex, "type")
            if tex.type == 'CLOUDS':
                layout.prop(tex, "cloud_type", expand=True)
                layout.label(text="Noise:")
                layout.prop(tex, "noise_type", text="Type", expand=True)
                layout.prop(tex, "noise_basis", text="Basis")
                split = layout.split()
                col = split.column()
                col.prop(tex, "noise_scale", text="Size")
                col.prop(tex, "noise_depth", text="Depth")
                split.prop(tex, "nabla", text="Nabla")
            if tex.type == 'WOOD':
                layout.prop(tex, "noise_basis_2", expand=True)
                layout.prop(tex, "wood_type", expand=True)
                col = layout.column()
                col.active = tex.wood_type in {'RINGNOISE', 'BANDNOISE'}
                col.label(text="Noise:")
                col.row().prop(tex, "noise_type", text="Type", expand=True)
                layout.prop(tex, "noise_basis", text="Basis")
                split = layout.split()
                split.active = tex.wood_type in {'RINGNOISE', 'BANDNOISE'}
                col = split.column()
                col.prop(tex, "noise_scale", text="Size")
                col.prop(tex, "turbulence")
                split.prop(tex, "nabla")
            if tex.type == 'MARBLE':
                layout.prop(tex, "marble_type", expand=True)
                layout.prop(tex, "noise_basis_2", expand=True)
                layout.label(text="Noise:")
                layout.prop(tex, "noise_type", text="Type", expand=True)
                layout.prop(tex, "noise_basis", text="Basis")
                split = layout.split()
                col = split.column()
                col.prop(tex, "noise_scale", text="Size")
                col.prop(tex, "noise_depth", text="Depth")
                col = split.column()
                col.prop(tex, "turbulence")
                col.prop(tex, "nabla")
            if tex.type == 'MAGIC':
                row.prop(tex, "noise_depth", text="Depth")
                row.prop(tex, "turbulence")
            if tex.type == 'BLEND':
                layout.prop(tex, "progression")
                sub = layout.row()
                sub.active = (tex.progression in {'LINEAR', 'QUADRATIC', 'EASING', 'RADIAL'})
                sub.prop(tex, "use_flip_axis", expand=True)
            if tex.type == 'STUCCI':
                layout.prop(tex, "stucci_type", expand=True)
                layout.label(text="Noise:")
                layout.prop(tex, "noise_type", text="Type", expand=True)
                layout.prop(tex, "noise_basis", text="Basis")
                row = layout.row()
                row.prop(tex, "noise_scale", text="Size")
                row.prop(tex, "turbulence")
            if tex.type == 'IMAGE':
                layout.template_image(tex, "image", tex.image_user)
                layout.prop(tex, "extension")
                split = layout.split()
                if tex.extension == 'REPEAT':
                    col = split.column(align=True)
                    col.label(text="Repeat:")
                    col.prop(tex, "repeat_x", text="X")
                    col.prop(tex, "repeat_y", text="Y")
                    col = split.column(align=True)
                    col.label(text="Mirror:")
                    row = col.row(align=True)
                    row.prop(tex, "use_mirror_x", text="X")
                    row.active = (tex.repeat_x > 1)
                    row = col.row(align=True)
                    row.prop(tex, "use_mirror_y", text="Y")
                    row.active = (tex.repeat_y > 1)
                    layout.separator()
                elif tex.extension == 'CHECKER':
                    col = split.column(align=True)
                    row = col.row(align=True)
                    row.prop(tex, "use_checker_even", text="Even")
                    row.prop(tex, "use_checker_odd", text="Odd")
                    col = split.column()
                    col.prop(tex, "checker_distance", text="Distance")
                    layout.separator()
                split = layout.split()
                col = split.column(align=True)
                # col.prop(tex, "crop_rectangle")
                col.label(text="Crop Minimum:")
                col.prop(tex, "crop_min_x", text="X")
                col.prop(tex, "crop_min_y", text="Y")
                col = split.column(align=True)
                col.label(text="Crop Maximum:")
                col.prop(tex, "crop_max_x", text="X")
                col.prop(tex, "crop_max_y", text="Y")
            if tex.type == 'MUSGRAVE':
                layout.prop(tex, "musgrave_type")
                split = layout.split()
                col = split.column()
                col.prop(tex, "dimension_max", text="Dimension")
                col.prop(tex, "lacunarity")
                col.prop(tex, "octaves")
                musgrave_type = tex.musgrave_type
                col = split.column()
                if musgrave_type in {'HETERO_TERRAIN', 'RIDGED_MULTIFRACTAL', 'HYBRID_MULTIFRACTAL'}:
                    col.prop(tex, "offset")
                col.prop(tex, "noise_intensity", text="Intensity")
                if musgrave_type in {'RIDGED_MULTIFRACTAL', 'HYBRID_MULTIFRACTAL'}:
                    col.prop(tex, "gain")
                layout.label(text="Noise:")
                layout.prop(tex, "noise_basis", text="Basis")
                row = layout.row()
                row.prop(tex, "noise_scale", text="Size")
                row.prop(tex, "nabla")
            if tex.type == 'VORONOI':
                split = layout.split()
                col = split.column()
                col.label(text="Distance Metric:")
                col.prop(tex, "distance_metric", text="")
                sub = col.column()
                sub.active = tex.distance_metric == 'MINKOVSKY'
                sub.prop(tex, "minkovsky_exponent", text="Exponent")
                col.label(text="Coloring:")
                col.prop(tex, "color_mode", text="")
                col.prop(tex, "noise_intensity", text="Intensity")
                col = split.column()
                sub = col.column(align=True)
                sub.label(text="Feature Weights:")
                sub.prop(tex, "weight_1", text="1", slider=True)
                sub.prop(tex, "weight_2", text="2", slider=True)
                sub.prop(tex, "weight_3", text="3", slider=True)
                sub.prop(tex, "weight_4", text="4", slider=True)
                layout.label(text="Noise:")
                row = layout.row()
                row.prop(tex, "noise_scale", text="Size")
                row.prop(tex, "nabla")
            if tex.type == 'DISTORTED_NOISE':
                layout.prop(tex, "noise_distortion")
                layout.prop(tex, "noise_basis", text="Basis")
                split = layout.split()
                col = split.column()
                col.prop(tex, "distortion", text="Distortion")
                col.prop(tex, "noise_scale", text="Size")
                split.prop(tex, "nabla")


class POVRAY_TEXTURE_PT_blender_mapping(TextureButtonsPanel, Panel):
    bl_label = "Mapping"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        if not getattr(context, "texture_slot", None):
            return False
        part = context.particle_system
        engine = context.scene.render.engine
        return (part and engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        idblock = context_tex_datablock(context)

        tex = context.texture_slot


        split = layout.split(percentage=0.3)
        col = split.column()
        col.label(text="Coordinates:")
        col = split.column()
        col.prop(tex, "texture_coords", text="")

        if tex.texture_coords == 'UV':
            split = layout.split(percentage=0.3)
            split.label(text="Map:")
            ob = context.object
            if ob and ob.type == 'MESH':
                split.prop_search(tex, "uv_layer", ob.data, "uv_textures", text="")
            else:
                split.prop(tex, "uv_layer", text="")

        elif tex.texture_coords == 'OBJECT':
            split = layout.split(percentage=0.3)
            split.label(text="Object:")
            split.prop(tex, "object", text="")

        elif tex.texture_coords == 'ALONG_STROKE':
            split = layout.split(percentage=0.3)
            split.label(text="Use Tips:")
            split.prop(tex, "use_tips", text="")




        row = layout.row()
        row.column().prop(tex, "offset")
        row.column().prop(tex, "scale")


class POVRAY_TEXTURE_PT_blender_influence(TextureButtonsPanel, Panel):
    bl_label = "Influence"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        if not getattr(context, "texture_slot", None):
            return False
        part = context.particle_system
        engine = context.scene.render.engine
        return (part and engine in cls.COMPAT_ENGINES)

    def draw(self, context):

        layout = self.layout

        idblock = context_tex_datablock(context)

        tex = context.texture_slot

        def factor_but(layout, toggle, factor, name):
            row = layout.row(align=True)
            row.prop(tex, toggle, text="")
            sub = row.row(align=True)
            sub.active = getattr(tex, toggle)
            sub.prop(tex, factor, text=name, slider=True)
            return sub  # XXX, temp. use_map_normal needs to override.



        split = layout.split()

        col = split.column()
        col.label(text="General:")
        factor_but(col, "use_map_time", "time_factor", "Time")
        factor_but(col, "use_map_life", "life_factor", "Lifetime")
        factor_but(col, "use_map_density", "density_factor", "Density")
        factor_but(col, "use_map_size", "size_factor", "Size")

        col = split.column()
        col.label(text="Physics:")
        factor_but(col, "use_map_velocity", "velocity_factor", "Velocity")
        factor_but(col, "use_map_damp", "damp_factor", "Damp")
        factor_but(col, "use_map_gravity", "gravity_factor", "Gravity")
        factor_but(col, "use_map_field", "field_factor", "Force Fields")

        layout.label(text="Hair:")

        split = layout.split()

        col = split.column()
        factor_but(col, "use_map_length", "length_factor", "Length")
        factor_but(col, "use_map_clump", "clump_factor", "Clump")

        col = split.column()
        factor_but(col, "use_map_kink_amp", "kink_amp_factor", "Kink Amplitude")
        factor_but(col, "use_map_kink_freq", "kink_freq_factor", "Kink Frequency")
        factor_but(col, "use_map_rough", "rough_factor", "Rough")





class POVRAY_TEXTURE_PT_map(TextureButtonsPanel, bpy.types.Panel):
    bl_label = "Map"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        if not hasattr(context, "texture_slot"):
            return False
        tex=context.texture
        part = context.particle_system
        return (tex and (engine in cls.COMPAT_ENGINES) and not part)

    def draw(self, context):
        tex = context.texture
        mat=context.material
        scene=context.scene
        ob=context.object
        align=True
        layout=self.layout
        if mat:
            if ob.povray.object_material=="surface":
                layout.prop(tex.povray, "pigment_normal",expand = True)
                if (scene.povray.render == 'hgpovray' and tex.povray.pigment_normal == 'modulation'):
                    layout.prop(tex.povray, "modulation_type",expand = True)
                layout.prop(tex.povray, "modulation_amount")
                layout.prop(tex.povray, "pattern_or_image",expand = True)
                if tex.povray.pigment_normal == "normal":
                    text = "Normal"
                    if  tex.povray.pattern_or_image == "image":
                        text = "Bump"
                    layout.prop(tex.povray, "normal_value",text = text)
                if tex.povray.pattern_or_image == "pattern":
                    layout.prop(tex.povray, "pattern")
                if tex.povray.pattern_or_image == "image":
                    layout.prop_search(tex.povray, "image",bpy.data,"images")
                    layout.operator("povray.openimage")
                    if tex.povray.image:
                        layout.prop(tex.povray, "gamma",slider=True)
                        layout.prop(tex.povray, "map_type")
                        layout.prop(tex.povray, "interpolate")
                        layout.prop(tex.povray, "once")
                if tex and (tex.povray.pattern_or_image == "pattern"):
                    if tex.povray.pattern in {'brick','gradient','slope'}:
                        if tex.povray.pattern in {'brick'}:
                            layout.label('Size')
                        row = layout.row()
                        col = row.column()
                        col.prop(tex.povray, "vector",text='')
                    if tex.povray.pattern in {'brick'}:
                        col = row.column()
                        col.prop(tex.povray, "mortar")
                        col.prop(tex.povray, "brick_scale")
                    if tex.povray.pattern in {'slope'}:
                        col = row.column(align = True)
                        col.prop(tex.povray, "lo_slope")
                        col.prop(tex.povray, "hi_slope")
                    if tex.povray.pattern in {'spiral'}:
                        layout.prop(tex.povray, "spiral_arms")
                    if tex.povray.pattern in {'tiling'}:
                        layout.prop(tex.povray, "tiling_number")
                    if tex.povray.pattern in {'quilted'}:
                        row = layout.row()
                        row.prop(tex.povray, "control0")
                        row.prop(tex.povray, "control1")
                    if tex.povray.pattern in {'ridged'}:
                        row = layout.row()
                        col = row.column(align = True)
                        col.prop(tex.povray, "ridged_p0")
                        col.prop(tex.povray, "ridged_p1")
                        col.prop(tex.povray, "ridged_p2")
                        col = row.column(align = True)
                        col.prop(tex.povray, "ridged_p3")
                        col.prop(tex.povray, "ridged_p4")
                        col.prop(tex.povray, "ridged_p5")
                    if tex.povray.pattern in {'pavement'}:
                        layout.label('Tiles:')
                        layout.prop(tex.povray, "pave_tiles",expand = True)
                        layout.label('Sides:')
                        if tex.povray.pave_tiles == "6":
                            layout.prop(tex.povray, "pave_sides_6",expand = True)
                        else:
                            layout.prop(tex.povray, "pave_sides",expand = True)
                        layout.label('Form:')
                        layout.prop(tex.povray, "pave_form",expand = True)
                        layout.label('Interior:')
                        layout.prop(tex.povray, "pave_interior",expand = True)
                        layout.label('Exterior:')
                        layout.prop(tex.povray, "pave_exterior",expand = True)
                        text="Pattern"
                        if tex.povray.pave_tiles == '3':
                            if tex.povray.pave_sides == '4':
                                layout.prop(tex.povray, "pave_pat_2", text=text)
                            if tex.povray.pave_sides == '6':
                                layout.prop(tex.povray, "pave_pat_3", text=text)
                        if tex.povray.pave_tiles == '4':
                            if tex.povray.pave_sides == '3':
                                layout.prop(tex.povray, "pave_pat_3", text=text)
                            if tex.povray.pave_sides == '4':
                                layout.prop(tex.povray, "pave_pat_5", text=text)
                            if tex.povray.pave_sides == '6':
                                layout.prop(tex.povray, "pave_pat_7", text=text)
                        if tex.povray.pave_tiles == '5':
                            if tex.povray.pave_sides == '3':
                                layout.prop(tex.povray, "pave_pat_4", text=text)
                            if tex.povray.pave_sides == '4':
                                layout.prop(tex.povray, "pave_pat_12", text=text)
                            if tex.povray.pave_sides == '6':
                                layout.prop(tex.povray, "pave_pat_22", text=text)
                        if tex.povray.pave_tiles == '6':
                            if tex.povray.pave_sides_6 == '3':
                                layout.prop(tex.povray, "pave_pat_12", text=text)
                            if tex.povray.pave_sides_6 == '4':
                                layout.prop(tex.povray, "pave_pat_35", text=text)

                    if tex.povray.pigment_normal == "pigment" or (scene.povray.render == 'hgpovray' and tex.povray.pigment_normal == 'modulation'):
                        layout.template_color_ramp(tex, "color_ramp", expand=True)
                    if tex.povray.pigment_normal == "pigment":
                        layout.label("Alpha as:")
                        layout.prop(tex.povray, "alpha_mode",expand = True)
                    

            if ob.povray.object_material=="volume":
                row = layout.row()
                row.prop(tex.povray, "texture_density")
                if tex.povray.texture_density:
                    row.prop(tex.povray, "density_lines")
                    layout.prop(tex.povray, "pattern")
                    if tex.povray.pattern == 'density_file':
                        layout.prop(tex.povray, "df3")
                        if tex.povray.df3 == False:
                            text = 'None'
                            df3path = tex.povray.density_file
                            if df3path != '':
                                text = df3path
                            layout.operator('povray.loaddensityfile')
                            layout.label('Density File:')
                            layout.label(text)

                    if tex.povray.density_lines > 32:
                        layout.prop(tex.povray, "texture_use_nodes")
                    else:
                        layout.template_color_ramp(tex, "color_ramp", expand=True)
                    layout.operator("povray.loadmap",text="Load map")
        if context.world:
            layout.label("Sky Sphere:")
            layout.prop(tex.povray, "sky_sphere",expand = True)
            if tex and (tex.type in {"CLOUDS","BLEND"}):
                layout.template_color_ramp(tex, "color_ramp", expand=True)
            if tex.povray.sky_sphere == "image_map":
                layout.template_image(tex, "image", tex.image_user)
                if tex and tex.type == "IMAGE" and tex.image and tex.image.filepath:
                    layout.label("Povray Texture Settings:")
                    if tex.type == "IMAGE":
                        layout.prop(tex.povray, "gamma",slider=True)
                        layout.prop(tex.povray, "map_type")
                        layout.prop(tex.povray, "interpolate")
            if tex and tex.type == "BLEND":
                layout.prop(tex, "use_flip_axis")
            if tex and tex.type == "CLOUDS":
                layout.prop(tex, "noise_scale",text="Scale")
                layout.prop(tex.povray,"turbulence",text='Turb')
                layout.prop(tex.povray,"octaves")
                layout.prop(tex.povray,"omega")
                layout.prop(tex.povray,"lambdat")
                layout.prop(tex.povray,"translate")
                layout.prop(tex.povray,"rotate")
                layout.prop(tex.povray,"scale")
        if context.particle_system:
            layout.prop(tex,"type")

class POVRAY_TEXTURE_PT_mapping(TextureButtonsPanel, bpy.types.Panel):
    bl_label = "Mapping"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        if not hasattr(context, "texture_slot"):
            return False
        tex=context.texture
        return (tex and ((tex.povray.pattern_or_image=="image" and tex.povray.image != "") or tex.povray.pattern_or_image=="pattern") and(engine in cls.COMPAT_ENGINES))

    def draw(self, context):
        tex = context.texture
        ob = context.object
        tp = tex.povray
        layout=self.layout
        if tex:
            layout.prop(tp, "warp_types", text="Warp types") #warp
            if tp.warp_types == "REPEAT":
                row=layout.row()
                row.prop(tp, "warp_repeat_x")
                if tp.warp_repeat_x:
                    row.prop(tp, "rx_value")
                    row=layout.row()
                    row.prop(tp, "rx_offset")
                    row.prop(tp, "rx_offset_value")
                    row=layout.row()
                    row.label(text="Flip:")
                    row.prop(tp, "rx_flip_x")
                    row.prop(tp, "rx_flip_y")
                    row.prop(tp, "rx_flip_z")
                row=layout.row()
                row.prop(tp, "warp_repeat_y")
                if tp.warp_repeat_y:
                    row.prop(tp, "ry_value")
                    row=layout.row()
                    row.prop(tp, "ry_offset")
                    row.prop(tp, "ry_offset_value")
                    row=layout.row()
                    row.label(text="Flip:")
                    row.prop(tp, "ry_flip_x")
                    row.prop(tp, "ry_flip_y")
                    row.prop(tp, "ry_flip_z")
                row=layout.row()
                row.prop(tp, "warp_repeat_z")
                if tp.warp_repeat_z:
                    row.prop(tp, "rz_value")
                    row=layout.row()
                    row.prop(tp, "rz_offset")
                    row.prop(tp, "rz_offset_value")
                    row=layout.row()
                    row.label(text="Flip:")
                    row.prop(tp, "rz_flip_x")
                    row.prop(tp, "rz_flip_y")
                    row.prop(tp, "rz_flip_z")
            if tp.warp_types == "TOROIDAL":
                layout.prop(tp, "warp_tor_major_radius", text="Major radius",slider=True)
            if tp.warp_types not in {"CUBIC","NONE","REPEAT","UV"}:
                layout.prop(tp, "warp_orientation", text="Warp orientation",slider=True)
                layout.prop(tp, "warp_dist_exp", text="Distance exponent",slider=True)        


class POVRAY_TEXTURE_PT_modifiers(TextureButtonsPanel, bpy.types.Panel):
    bl_label = "Turbulence"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        if not hasattr(context, "texture_slot"):
            return False
        tex=context.texture
        return (tex and ((tex.povray.pattern_or_image=="image" and tex.povray.image != "") or tex.povray.pattern_or_image=="pattern") and(engine in cls.COMPAT_ENGINES))

    def draw(self, context):
        tex = context.texture
        layout=self.layout
        if tex:
            layout.prop(tex.povray, "turbulence_enable")
            if tex.povray.turbulence_enable:
                layout.prop(tex.povray, "turbulence_all_axis")
                row = layout.row()
                col = row.column()
                if tex.povray.turbulence_all_axis:
                    col.prop(tex.povray, "turbulence_all")
                else:
                    col.prop(tex.povray, "turbulence",text='')
                col = row.column(align = True)
                col.prop(tex.povray, "octaves")
                col.prop(tex.povray, "omega")
                col.prop(tex.povray, "lambdat")
                row = layout.row()
                row.prop(tex.povray, "frequency")
                row.prop(tex.povray, "phase")

class POVRAY_TEXTURE_PT_transform(TextureButtonsPanel, bpy.types.Panel):
    bl_label = "Transform"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        if not hasattr(context, "texture_slot"):
            return False
        tex=context.texture
        return (tex and ((tex.povray.pattern_or_image=="image" and tex.povray.image != "") or tex.povray.pattern_or_image=="pattern") and(engine in cls.COMPAT_ENGINES))

    def draw(self, context):
        tex = context.texture
        layout=self.layout
        if tex:
            layout.prop(tex.povray, "scale_all_axis")
            row = layout.row()
            col = row.column()
            col.prop(tex.povray, "translate")
            col = row.column()
            col.prop(tex.povray, "rotate")
            col = row.column()
            if tex.povray.scale_all_axis:
                col.label('Scale:')
                col.prop(tex.povray, "scale_all")
            if tex.povray.scale_all_axis == False:
                col.prop(tex.povray, "scale")


#class TEXTURE_PT_density(TextureButtonsPanel, bpy.types.Panel):
    #bl_label = "Density"
    #COMPAT_ENGINES = {'POVRAY'}

    #@classmethod
    #def poll(cls, context):
        #engine = context.scene.render.engine
        #mat=context.material
        #tex=context.texture
        #return tex and mat and mat.povray.mat_type == "volume" and (engine in cls.COMPAT_ENGINES)

    #def draw(self, context):
        #tex=context.texture
        #layout=self.layout
        #layout.prop(tex.povray, "texture_density")
        #if tex.povray.texture_density:
            #row = layout.row()
            #row.prop(tex.povray, "fire_texture_density")
            #row.prop(tex.povray, "smoke_texture_density")
            #layout.prop(tex.povray, "density_lines")
            #if tex.povray.density_lines > 32:
                #layout.prop(tex.povray, "texture_use_nodes")
            #else:
                #layout.template_color_ramp(tex, "color_ramp", expand=True)
            #layout.operator("povray.loadmap",text="Load map")

#class TEXTURE_PT_sky_sphere(TextureButtonsPanel, bpy.types.Panel):
    #bl_label = "Sky Sphere"
    #COMPAT_ENGINES = {'POVRAY'}

    #@classmethod
    #def poll(cls, context):
        #engine = context.scene.render.engine
        #tex = bpy.context.scene.world.active_texture
        #return tex and (engine in cls.COMPAT_ENGINES)

    #def draw(self, context):
        #layout=self.layout
        #tex = bpy.context.scene.world.active_texture
        #idblock = context_tex_datablock(context)
        #slot = getattr(context, "texture_slot", None)
        #if idblock:
            #layout.template_preview(tex, parent=idblock, slot=slot)
        #else:
            #layout.template_preview(tex, slot=slot)
        #layout.template_image(tex, "image", tex.image_user)
        #if tex.image.filepath:
            #align = True
            #layout.label("Povray texture settings")
            #layout.prop(tex.povray, "gamma")
            #layout.prop(tex.povray, "map_type")
            #layout.prop(tex.povray, "interpolate")
            #layout.label("Translate")
            #row = layout.row(align = align)
            #row.prop(tex.povray, "translate_x")
            #row.prop(tex.povray, "translate_y")
            #row.prop(tex.povray, "translate_z")
            #layout.label("Rotate")
            #row = layout.row(align = align)
            #row.prop(tex.povray, "rotate_x")
            #row.prop(tex.povray, "rotate_y")
            #row.prop(tex.povray, "rotate_z")
            #layout.label("Scale")
            #row = layout.row(align = align)
            #row.prop(tex.povray, "scale_x")
            #row.prop(tex.povray, "scale_y")
            #row.prop(tex.povray, "scale_z")

# class POVRAY_MATERIAL_PT_material(MaterialButtonsPanel, bpy.types.Panel):    ######################### ADD povray parameters
    # bl_label = "Material"
    # bl_context = "material"
    # COMPAT_ENGINES = {'POVRAY'}

    # @classmethod
    # def poll(cls, context):
        # engine = context.scene.render.engine
        # return (engine in cls.COMPAT_ENGINES)

    # def draw(self, context):
        # layout = self.layout
        # ob = context.object
        # mat = context.material
        # try:
            # bpy.data.node_groups[ob.name]
            # #layout.operator("povray.remove_node_tree", icon = 'NODETREE')
        # except:
            # #layout.operator("povray.new_node_tree", icon = 'NODETREE')
            # row = layout.row()
            # row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=1)
            # col = row.column(align=True)
            # col.operator("object.material_slot_add", text="", icon = 'ADD')
            # col.operator("object.material_slot_remove", text="", icon = 'REMOVE')
            # layout.template_ID(ob, "active_material", new="material.new")
            # layout.prop(mat.povray,'use_nodes')
            # if mat:
                # if ob.mode == 'EDIT':
                    # row = layout.row(align=True)
                    # row.operator("object.material_slot_assign", text="Assign")
                    # row.operator("object.material_slot_select", text="Select")
                    # row.operator("object.material_slot_deselect", text="Deselect")
                # layout.prop(ob.povray,"object_ior",text="Object IOR",slider=True)

# class POVRAY_MATERIAL_PT_preview(MaterialButtonsPanel, bpy.types.Panel):    ######################### ADD povray parameters
    # bl_label = "Preview"
    # bl_context = "material"
    # bl_options = {'DEFAULT_CLOSED'}
    # COMPAT_ENGINES = {'POVRAY'}

    # @classmethod
    # def poll(cls, context):
        # engine = context.scene.render.engine
        # mat = context.material
        # return (mat and engine in cls.COMPAT_ENGINES)

    # def draw(self, context):
        # layout = self.layout
        # mat = context.material
        # layout.template_preview(mat)
        # layout.prop(mat.povray,"preview_settings")
        # if mat.povray.preview_settings:
            # box = layout.box()
            # box.prop(mat.povray,"object_preview_transform")
            # if mat.povray.object_preview_transform:
                # row = box.row()
                # col = row.column()
                # col.prop(mat.povray,"object_preview_rotate",slider=True)
                # col = row.column()
                # col.label('Scale:')
                # col.prop(mat.povray,"object_preview_scale",slider=True)
            # box = layout.box()
            # box.label('Background:')
            # box.prop(mat.povray,"object_preview_bgcontrast",slider=True)
# class POVRAY_MATERIAL_PT_pigment(MaterialButtonsPanel, Panel):
    # bl_label = "Pigment"
    # bl_context = "material"
    # #bl_options = {'DEFAULT_CLOSED'}
    # COMPAT_ENGINES = {'POVRAY'}

    # @classmethod
    # def poll(cls, context):
        # engine = context.scene.render.engine
        # mat=context.material
        # ob = context.object
        # return mat and ob.povray.object_material == "surface" and mat.povray.use_nodes==False and (engine in cls.COMPAT_ENGINES)

    # def draw(self, context):
        # layout = self.layout
        # ob = context.object
        # mat = context.material
        # pov = mat.povray
        # layout.prop(mat,"diffuse_color",text="Color")
        # layout.prop(pov,"povfilter",slider=True)


# class POVRAY_MATERIAL_PT_diffuse(MaterialButtonsPanel, Panel):
    # bl_label = "Diffuse"
    # bl_context = "material"
    # #bl_options = {'DEFAULT_CLOSED'}
    # COMPAT_ENGINES = {'POVRAY'}

    # @classmethod
    # def poll(cls, context):
        # engine = context.scene.render.engine
        # mat=context.material
        # ob = context.object
        # return mat and ob.povray.object_material == "surface" and mat.povray.use_nodes==False and (engine in cls.COMPAT_ENGINES)

    # def draw(self, context):
        # layout = self.layout
        # ob = context.object
        # mat = context.material
        # pov = mat.povray
        # layout.prop(pov,"diffuse_intensity")
        # layout.prop(pov,"diffuse_albedo")

# class POVRAY_MATERIAL_PT_highlights(MaterialButtonsPanel, Panel):
    # bl_label = "Highlights"
    # bl_context = "material"
    # #bl_options = {'DEFAULT_CLOSED'}
    # COMPAT_ENGINES = {'POVRAY'}

    # @classmethod
    # def poll(cls, context):
        # engine = context.scene.render.engine
        # mat=context.material
        # ob = context.object
        # return mat and ob.povray.object_material == "surface" and mat.povray.use_nodes==False and (engine in cls.COMPAT_ENGINES)

    # def draw(self, context):
        # layout = self.layout
        # ob = context.object
        # mat = context.material
        # pov = mat.povray
        # layout.prop(mat.povray,"highlights",expand = True)
        # if pov.highlights in {"specular","phong"}:
            # layout.prop(pov,"specular_albedo")
            # layout.prop(pov,"specular_metallic",slider=True)
            # layout.prop(pov,"specular_intensity",text="Intensity")
        # if pov.highlights in {"specular"}:
            # layout.prop(pov,"specular_roughness",slider=True)
        # if pov.highlights in {"phong"}:
            # layout.prop(pov,"phong_size",slider=True)

# class POVRAY_MATERIAL_PT_reflection(MaterialButtonsPanel, Panel):
    # bl_label = "Mirror"
    # bl_context = "material"
    # #bl_options = {'DEFAULT_CLOSED'}
    # COMPAT_ENGINES = {'POVRAY'}

    # @classmethod
    # def poll(cls, context):
        # engine = context.scene.render.engine
        # mat=context.material
        # ob = context.object
        # return mat and ob.povray.object_material == "surface" and mat.povray.use_nodes==False and (engine in cls.COMPAT_ENGINES)

    # def draw_header(self, context):
        # layout = self.layout
        # ob = context.object
        # pov = context.material.povray
        # layout.prop(pov,"mirror_enable",text="")

    # def draw(self, context):
        # layout = self.layout
        # ob = context.object
        # scn = context.scene
        # mat = context.material
        # pov = mat.povray
        # if pov.mirror_enable:
            # layout.prop(pov,"mirror_color",text="Color")
            # layout.prop(pov,"color_min_enable")
            # if pov.color_min_enable:
                # layout.prop(pov,"color_min")
            # if scn.povray.render == 'uberpov':
                # layout.prop(pov,"mirror_roughness",slider=True)
            # layout.prop(pov,"metallic",slider=True)
            # layout.prop(pov,"exponent",text="Exponent")
            # layout.prop(pov,"falloff",slider=True)
            # layout.prop(pov,"fresnel")
            # layout.prop(pov,"conserve_energy")

# class POVRAY_MATERIAL_PT_shading(MaterialButtonsPanel, Panel):
    # bl_label = "Shading"
    # bl_context = "material"
    # #bl_options = {'DEFAULT_CLOSED'}
    # COMPAT_ENGINES = {'POVRAY'}

    # @classmethod
    # def poll(cls, context):
        # engine = context.scene.render.engine
        # mat=context.material
        # ob = context.object
        # return mat and ob.povray.object_material == "surface" and mat.povray.use_nodes==False and (engine in cls.COMPAT_ENGINES)

    # def draw(self, context):
        # layout = self.layout
        # ob = context.object
        # mat = context.material
        # pov = mat.povray
        # layout.prop(pov,"brilliance",slider=True)
        # layout.prop(pov,"emit")
        # layout.prop(pov,"ambient")
        # layout.prop(pov,"translucency")

# class POVRAY_MATERIAL_PT_iridescence(MaterialButtonsPanel, Panel):
    # bl_label = "Iridescence"
    # bl_context = "material"
    # #bl_options = {'DEFAULT_CLOSED'}
    # COMPAT_ENGINES = {'POVRAY'}

    # @classmethod
    # def poll(cls, context):
        # engine = context.scene.render.engine
        # mat=context.material
        # ob = context.object
        # return mat and ob.povray.object_material == "surface" and mat.povray.use_nodes==False and (engine in cls.COMPAT_ENGINES)

    # def draw_header(self, context):
        # layout = self.layout
        # ob = context.object
        # mat = context.material
        # layout.prop(mat.povray,"irid_enable",text="")

    # def draw(self, context):
        # layout = self.layout
        # ob = context.object
        # mat = context.material
        # pov = mat.povray
        # if pov.irid_enable:
            # layout.prop(pov,"irid_amount",slider=True)
            # layout.prop(pov,"irid_thickness",slider=True)
            # layout.prop(pov,"irid_turbulence",slider=True)

# class POVRAY_MATERIAL_PT_bicubic_UV(MaterialButtonsPanel, Panel):
    # bl_label = "UV"
    # bl_context = "material"
    # #bl_options = {'DEFAULT_CLOSED'}
    # COMPAT_ENGINES = {'POVRAY'}

    # @classmethod
    # def poll(cls, context):
        # engine = context.scene.render.engine
        # mat=context.material
        # ob = context.object
        # return mat and ob.povray.object_material == "surface" and ob.type == 'SURFACE' and mat.povray.use_nodes==False and (engine in cls.COMPAT_ENGINES)

    # def draw(self, context):
        # layout = self.layout
        # ob = context.object
        # mat = context.material
        # pov = mat.povray
        # row = layout.row()
        # row.prop(pov,"uv_x1")
        # row.prop(pov,"uv_y1")
        # row = layout.row()
        # row.prop(pov,"uv_x2")
        # row.prop(pov,"uv_y2")
        # row = layout.row()
        # row.prop(pov,"uv_x3")
        # row.prop(pov,"uv_y3")
        # row = layout.row()
        # row.prop(pov,"uv_x4")
        # row.prop(pov,"uv_y4")

# class POVRAY_MATERIAL_PT_active_node(MaterialButtonsPanel, Panel):
    # bl_label = "Active Node Settings"
    # bl_context = "material"
    # bl_options = {'DEFAULT_CLOSED'}
    # COMPAT_ENGINES = {'POVRAY'}

    # @classmethod
    # def poll(cls, context):
        # engine = context.scene.render.engine
        # mat=context.material
        # ob = context.object
        # return mat and ob.povray.object_material == "surface" and (engine in cls.COMPAT_ENGINES) and mat.povray.use_nodes


    # def draw(self, context):
        # layout = self.layout
        # mat = context.material
        # node_tree = mat.node_tree
        # if node_tree:
            # node = node_tree.nodes.active
            # if mat.use_nodes:
                # if node:
                    # layout.prop(mat.povray,"material_active_node")
                    # if node.bl_idname=="PovrayMaterialNode":
                        # layout.context_pointer_set("node", node)
                        # if hasattr(node, "draw_buttons_ext"):
                            # node.draw_buttons_ext(context, layout)
                        # elif hasattr(node, "draw_buttons"):
                            # node.draw_buttons(context, layout)
                        # value_inputs = [socket for socket in node.inputs if socket.enabled and not socket.is_linked]
                        # if value_inputs:
                            # layout.separator()
                            # layout.label("Inputs:")
                            # for socket in value_inputs:
                                # row = layout.row()
                                # socket.draw(context, row, node, socket.name)
                    # else:
                        # layout.context_pointer_set("node", node)
                        # if hasattr(node, "draw_buttons_ext"):
                            # node.draw_buttons_ext(context, layout)
                        # elif hasattr(node, "draw_buttons"):
                            # node.draw_buttons(context, layout)
                        # value_inputs = [socket for socket in node.inputs if socket.enabled and not socket.is_linked]
                        # if value_inputs:
                            # layout.separator()
                            # layout.label("Inputs:")
                            # for socket in value_inputs:
                                # row = layout.row()
                                # socket.draw(context, row, node, socket.name)
                # else:
                    # layout.label("You have no nodes!")

# class POVRAY_MATERIAL_PT_media(MaterialButtonsPanel, Panel):
    # bl_label = "Media"
    # bl_context = "material"
    # #bl_options = {'DEFAULT_CLOSED'}
    # COMPAT_ENGINES = {'POVRAY'}

    # @classmethod
    # def poll(cls, context):
        # engine = context.scene.render.engine
        # mat=context.material
        # ob = context.object
        # return mat and ob.povray.object_material == "volume" and (engine in cls.COMPAT_ENGINES)

    # def draw(self, context):
        # layout = self.layout
        # mat = context.material
        # layout.prop(mat.povray, "media",expand = True)
        # box = layout.box()
        # row=box.row()
        # row.prop(mat.povray, "use_absorption")
        # if mat.povray.use_absorption:
            # row.prop(mat.povray, "absorption",text="")
        # box = layout.box()
        # row=box.row()
        # row.prop(mat.povray, "use_emission")
        # if mat.povray.use_emission:
            # row.prop(mat.povray, "emission",text="")
        # box = layout.box()
        # row=box.row()
        # row.prop(mat.povray, "use_scattering")
        # if mat.povray.use_scattering:
            # row.prop(mat.povray, "scattering",text="")
            # box.prop(mat.povray, "extinction")
            # row = box.row()
            # row.label('Type:')
            # row.prop(mat.povray, "scattering_type",expand = True)
            # if mat.povray.scattering_type == '5':
                # box.prop(mat.povray, "eccentricity")
        # row=layout.row()
        # row.label('Method:')
        # row.prop(mat.povray, "method",expand = True)
        # row=layout.row()
        # row.label('Samples:')
        # row.prop(mat.povray, "samples_min")
        # row.prop(mat.povray, "samples_max")
        # row=layout.row()
        # row.prop(mat.povray, "intervals")
        # row.prop(mat.povray, "confidence")
        # row=layout.row()
        # row.prop(mat.povray, "ratio")
        # row.prop(mat.povray, "variance")
        # box = layout.box()
        # box.label('Anti-Aliasing:')
        # row=box.row()
        # row.prop(mat.povray, "aa_level")
        # row.prop(mat.povray, "aa_threshold")
        # row=box.row()
        # row.prop(mat.povray, "use_aa_jitter")
        # if mat.povray.use_aa_jitter:
            # row.prop(mat.povray, "aa_jitter")


class POVRAY_RENDER_PT_files(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Output"
    bl_context = "render"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        scene=context.scene
        layout = self.layout
        layout.prop(scene.render.image_settings,"file_format",text="Format")
        layout.prop(scene.render,"filepath",text="Filename")
        layout.prop(scene.povray,"output_advanced")
        if scene.povray.output_advanced:
            layout.prop(scene.povray,"tempfiles")
            if scene.povray.tempfiles==False:
                layout.prop(scene.povray,"workdir")
            layout.prop(scene.povray,"output_format",text="Povray output")

class POVRAY_RENDER_PT_antialias(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Anti-Aliasing:"
    bl_context = "render"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        scene=context.scene
        layout = self.layout
        layout.prop(scene.povray,"antialias_enable")
        if scene.povray.antialias_enable:
            row = layout.row()
            row.prop(scene.povray,"antialias_sampling_method")
            row.prop(scene.povray,"antialias_depth")
            row = layout.row()
            row.prop(scene.povray,"antialias_threshold")
            row.prop(scene.povray,"antialias_gamma")
            row = layout.row()
            row.prop(scene.povray,"antialias_jitter_enable")
            if scene.povray.antialias_jitter_enable:
                row.prop(scene.povray,"antialias_jitter_amount")


class POVRAY_RENDER_PT_global_settings(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Povray Global Settings"
    bl_context = "render"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        scene=context.scene
        layout = self.layout
        layout.prop(scene.povray,"render_scenes_from_file")
        layout.prop(scene.povray,"render",expand = True)
        row = layout.row()
        row.prop(scene.povray,"assumed_gamma")
        row.prop(scene.povray,"max_trace_level")
        layout.prop(scene.povray,"charset")
        layout.prop(scene.povray,"global_settings_advanced")
        if scene.povray.global_settings_advanced:
            align = True
            row = layout.row(align = align)
            row.prop(scene.povray,"adc_bailout_enable",text = "")
            row.prop(scene.povray,"adc_bailout")
            row = layout.row(align = align)
            row.prop(scene.povray,"ambient_light_enable",text = "")
            row.prop(scene.povray,"ambient_light")
            row = layout.row(align = align)
            row.prop(scene.povray,"irid_wavelength_enable",text = "")
            row.prop(scene.povray,"irid_wavelength")
            row = layout.row(align = align)
            row.prop(scene.povray,"max_intersections_enable",text = "")        
            row.prop(scene.povray,"max_intersections")
            row = layout.row(align = align)
            row.prop(scene.povray,"number_of_waves_enable",text = "")        
            row.prop(scene.povray,"number_of_waves")
            row = layout.row(align = align)
            row.prop(scene.povray,"noise_generator_enable",text = "")
            row.prop(scene.povray,"noise_generator")

class POVRAY_RENDER_PT_radiosity(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Radiosity"
    bl_context = "render"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
        scene = context.scene
        self.layout.prop(scene.povray, "radio_enable", text="")

    def draw(self, context):
        scene=context.scene
        layout = self.layout
        if scene.povray.radio_enable:
            layout.prop(scene.povray, "radio_pretrace_start")
            layout.prop(scene.povray, "radio_pretrace_end")
            layout.prop(scene.povray, "radio_count")
            layout.prop(scene.povray, "radio_nearest_count")
            layout.prop(scene.povray, "radio_error_bound", text="Error Bound")
            layout.prop(scene.povray, "radio_recursion_limit", text="Recursions")
            layout.prop(scene.povray, "radio_low_error_factor")
            layout.prop(scene.povray, "radio_gray_threshold")
            layout.prop(scene.povray, "radio_maximum_reuse", text="Max Reuse")
            layout.prop(scene.povray, "radio_minimum_reuse", text="Min Reuse")
            layout.prop(scene.povray, "radio_brightness")
            layout.prop(scene.povray, "radio_adc_bailout")
            layout.prop(scene.povray, "radio_normal")
            layout.prop(scene.povray, "radio_always_sample")
            layout.prop(scene.povray, "radio_media")
            layout.prop(scene.povray, "radio_subsurface")

class POVRAY_RENDER_PT_photons(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Photons"
    bl_context = "render"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
        scene = context.scene
        self.layout.prop(scene.povray, "photon_enable", text="")

    def draw(self, context):
        scene = context.scene
        if scene.povray.photon_enable:
            layout = self.layout
            align=True
            layout.prop(scene.povray, "photon_enable_count")
            if scene.povray.photon_enable_count:
                layout.prop(scene.povray, "photon_count")
            else:
                layout.prop(scene.povray, "photon_spacing")
            layout.prop(scene.povray, "photon_max_trace_level")
            layout.prop(scene.povray, "photon_media_enable", text="Photon media enable")
            if scene.povray.photon_media_enable:
                row=layout.row(align=align)
                row.prop(scene.povray, "photon_media_steps", text="Max steps")
                row.prop(scene.povray, "photon_media_factor", text="Factor")
            col = layout.column(align=align)
            row=col.row()
            row.prop(scene.povray, "photon_adc")
            if scene.povray.photon_adc:
                row.prop(scene.povray, "photon_adc_bailout")
            col.prop(scene.povray,"photon_gather")
            if scene.povray.photon_gather:
                row=col.row()
                row.prop(scene.povray, "photon_gather_min")
                row.prop(scene.povray, "photon_gather_max")
            row=col.row()
            row.prop(scene.povray,"photon_autostop")
            if scene.povray.photon_autostop:
                row.prop(scene.povray,"photon_autostop_value")
            row=col.row()
            row.prop(scene.povray,"photon_jitter_enable")
            if scene.povray.photon_jitter_enable:
                row.prop(scene.povray,"photon_jitter")
            box = layout.box()
            box.label('Photon Map File:')
            row = box.row()
            row.prop(scene.povray, "photon_map_file_save_load",expand = True)
            if scene.povray.photon_map_file_save_load in {'save'}:
                box.prop(scene.povray, "photon_map_dir")
                box.prop(scene.povray, "photon_map_filename")
            if scene.povray.photon_map_file_save_load in {'load'}:
                box.prop(scene.povray, "photon_map_file")

class POVRAY_RENDER_PT_sslt(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Subsurface Light Transport"
    bl_context = "render"
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.prop(scene.povray,"sslt_enable",text="")

    def draw(self, context):
        scene=context.scene
        layout = self.layout
        if scene.povray.sslt_enable:
            box=layout.box()
            box.label("Millimeters per Unit:")
            box.prop(scene.povray, "mm_per_unit",text="")
            box=layout.box()
            box.label("Sampling:")
            row=box.row()
            row.prop(scene.povray, "sslt_samples_max", text="Max")
            row.prop(scene.povray, "sslt_samples_min", text="Min")
            layout.prop(scene.povray, "sslt_radiosity")


def sdl_window_use(self, context):
    scene = context.scene
    engine = scene.render.engine
    if engine == 'POVRAY':
        self.layout.prop(scene.povray,"sdl_window_use")

classes = (
    TEXTURE_PT_context,
    POVRAY_CAMERA_PT_camera,
    POVRAY_LIGHT_PT_light,
    # POVRAY_MATERIAL_PT_active_node,
    # POVRAY_MATERIAL_PT_bicubic_UV,
    # POVRAY_MATERIAL_PT_diffuse,
    # POVRAY_MATERIAL_PT_highlights,
    # POVRAY_MATERIAL_PT_iridescence,
    # POVRAY_MATERIAL_PT_material,
    # POVRAY_MATERIAL_PT_media,
    # POVRAY_MATERIAL_PT_pigment,
    # POVRAY_MATERIAL_PT_preview,
    # POVRAY_MATERIAL_PT_reflection,
    # POVRAY_MATERIAL_PT_shading,
    POVRAY_OBJECT_PT_csg,
    POVRAY_OBJECT_PT_interior,
    POVRAY_OBJECT_PT_modifiers,
    POVRAY_OBJECT_PT_photons,
    POVRAY_OBJECT_PT_shape,
    POVRAY_PARTICLES_PT_particles,
    POVRAY_RENDER_PT_antialias,
    POVRAY_RENDER_PT_files,
    POVRAY_RENDER_PT_global_settings,
    POVRAY_RENDER_PT_photons,
    POVRAY_RENDER_PT_radiosity,
    POVRAY_RENDER_PT_sslt,
    POVRAY_TEXTURE_PT_blender_influence,
    POVRAY_TEXTURE_PT_blender_mapping,
    POVRAY_TEXTURE_PT_blender_particles,
    POVRAY_TEXTURE_PT_map,
    POVRAY_TEXTURE_PT_mapping,
    POVRAY_TEXTURE_PT_modifiers,
    POVRAY_TEXTURE_PT_preview,
    POVRAY_TEXTURE_PT_texslot,
    POVRAY_TEXTURE_PT_transform,
    POVRAY_TEXT_PT_text,

    #POVRAY_VIEW3D_PT_bezier,
    #POVRAY_VIEW3D_PT_bicubic,
    #POVRAY_VIEW3D_PT_povray_blobsweep,
    #POVRAY_VIEW3D_PT_tools,
)


def register():
    for cls in classes:
        register_class(cls)
    bpy.types.RENDER_PT_context.append(sdl_window_use)

def unregister():
    for cls in classes:
        unregister_class(cls)
    bpy.types.RENDER_PT_context.remove(sdl_window_use)




