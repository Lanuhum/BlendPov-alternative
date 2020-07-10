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
import bmesh
import subprocess, os, sys, platform
import time
from math import atan, pi, degrees, sqrt, modf
import re
import random
import mathutils
import tempfile
from . import df3
from .utils import *
from .declare import declare_shape, declare_from_text
global_matrix = mathutils.Matrix.Rotation(-pi / 2.0, 4, 'X')

def writeMatrix(File,matrix):
    File.write("    matrix <%.6f, %.6f, %.6f,  %.6f, %.6f, %.6f,  %.6f, %.6f, %.6f,  %.6f, %.6f, %.6f>\n" %
         (matrix[0][0], matrix[1][0], matrix[2][0],
          matrix[0][1], matrix[1][1], matrix[2][1],
          matrix[0][2], matrix[1][2], matrix[2][2],
          matrix[0][3], matrix[1][3], matrix[2][3]))

tabLevel = 0

def write_global_setting(scene, file):
    file.write("global_settings {\n")
    file.write("    assumed_gamma %.6f\n"%scene.povray.assumed_gamma)
    file.write("    max_trace_level %s\n"%scene.povray.max_trace_level)    
    if scene.povray.charset != 'ascii':
        file.write("    charset %s\n"%scene.povray.charset)
    if scene.povray.global_settings_advanced:
        if scene.povray.adc_bailout_enable and scene.povray.radio_enable == False:
            file.write("    adc_bailout %.6f\n"%scene.povray.adc_bailout)
        if scene.povray.ambient_light_enable:
            file.write("    ambient_light <%.6f,%.6f,%.6f>\n"%scene.povray.ambient_light[:])
        if scene.povray.irid_wavelength_enable:
            file.write("    irid_wavelength <%.6f,%.6f,%.6f>\n"%scene.povray.irid_wavelength[:])
        if scene.povray.max_intersections_enable:
            file.write("    max_intersections %s\n"%scene.povray.max_intersections)
        if scene.povray.number_of_waves_enable:
            file.write("    number_of_waves %s\n"%scene.povray.number_of_waves)
        if scene.povray.noise_generator_enable:
            file.write("    noise_generator %s\n"%scene.povray.noise_generator) 
    if scene.povray.sslt_enable:
        file.write("    mm_per_unit %s\n"%scene.povray.mm_per_unit) 
        file.write("    subsurface {\n")
        file.write("        samples %s, %s\n"%(scene.povray.sslt_samples_max,scene.povray.sslt_samples_min))
        if scene.povray.sslt_radiosity:
            file.write("        radiosity on\n")
        file.write("}\n")

    if scene.povray.radio_enable:
        file.write("    radiosity {\n")
        file.write("        pretrace_start %.6f\n"%scene.povray.radio_pretrace_start) 
        file.write("        pretrace_end %.6f\n"%scene.povray.radio_pretrace_end) 
        file.write("        count %s\n"%scene.povray.radio_count) 
        file.write("        nearest_count %s\n"%scene.povray.radio_nearest_count) 
        file.write("        error_bound %.6f\n"%scene.povray.radio_error_bound)         
        file.write("        recursion_limit %s\n"%scene.povray.radio_recursion_limit) 
        file.write("        low_error_factor %.6f\n"%scene.povray.radio_low_error_factor) 
        file.write("        gray_threshold %.6f\n"%scene.povray.radio_gray_threshold) 
        file.write("        maximum_reuse %.6f\n"%scene.povray.radio_maximum_reuse) 
        file.write("        minimum_reuse %.6f\n"%scene.povray.radio_minimum_reuse) 
        file.write("        brightness %.6f\n"%scene.povray.radio_brightness) 
        file.write("        adc_bailout %.6f\n"%scene.povray.radio_adc_bailout)
        if scene.povray.radio_normal:
            file.write("        normal on\n") 
        if scene.povray.radio_always_sample:
            file.write("        always_sample on\n") 
        if scene.povray.radio_media:
            file.write("        media on\n") 
        if scene.povray.radio_subsurface:
            file.write("        subsurface on\n")
        file.write("    }\n")

    if scene.povray.photon_enable:
        file.write("    photons {\n")
        if scene.povray.photon_enable_count:
            file.write("        count %s\n"%scene.povray.photon_count)
        else:
            file.write("        spacing %.6g\n"%scene.povray.photon_spacing)
        if scene.povray.photon_gather:
            file.write("        gather %s, %s\n"%(scene.povray.photon_gather_min,scene.povray.photon_gather_max))
        if scene.povray.photon_autostop:
            file.write("        autostop %.4g\n"%scene.povray.photon_autostop_value)
        if scene.povray.photon_jitter_enable:
            file.write("        jitter %.4g\n"%scene.povray.photon_jitter)
        file.write("        max_trace_level %s\n"%scene.povray.photon_max_trace_level)
        if scene.povray.photon_adc:
            file.write("        adc_bailout %.6f\n"%scene.povray.photon_adc_bailout)
        if scene.povray.photon_media_enable:
            file.write("        media %s, %s\n"%(scene.povray.photon_media_steps,scene.povray.photon_media_factor))
        if scene.povray.photon_map_file_save_load in {'save'}:
            filePhName = 'Photon_map_file.ph'
            if scene.povray.photon_map_file != '':
                filePhName = scene.povray.photon_map_file+'.ph'
            filePhDir = tempfile.gettempdir()
            path = bpy.path.abspath(scene.povray.photon_map_dir)
            if os.path.exists(path):
                filePhDir = path
            fullFileName = os.path.join(filePhDir,filePhName)
            file.write('        save_file "%s"\n'%fullFileName)
            scene.povray.photon_map_file = fullFileName
        if scene.povray.photon_map_file_save_load in {'load'}:
            fullFileName = bpy.path.abspath(scene.povray.photon_map_file)
            if os.path.exists(fullFileName):
                file.write('        load_file "%s"\n'%fullFileName)
        file.write("}\n")
    file.write("}\n")

def write_object_modifiers(scene,ob,File):
    if ob.povray.hollow:
        File.write("hollow\n")
    if ob.povray.double_illuminate:
        File.write("double_illuminate\n")
    if ob.povray.sturm:
        File.write("sturm\n")
    if ob.povray.no_shadow:
        File.write("no_shadow\n")
    if ob.povray.no_image:
        File.write("no_image\n")
    if ob.povray.no_reflection:
        File.write("no_reflection\n")
    if ob.povray.no_radiosity:
        File.write("no_radiosity\n")
    if ob.povray.inverse:
        File.write("inverse\n")
    if ob.povray.hierarchy:
        File.write("hierarchy\n")
    if scene.povray.photon_enable:
        File.write("photons {\n")
        if ob.povray.target:
            File.write("target %.4g\n"%ob.povray.target_value)
        if ob.povray.refraction:
            File.write("refraction on\n")
        if ob.povray.reflection:
            File.write("reflection on\n")
        if ob.povray.pass_through:
            File.write("pass_through\n")
        File.write("}\n")
    if ob.povray.object_ior > 1:
        File.write("interior {\n")
        File.write("ior %.4g\n"%ob.povray.object_ior)
        if scene.povray.photon_enable and ob.povray.target and ob.povray.refraction and ob.povray.dispersion:
            File.write("dispersion %.4g\n"%ob.povray.dispersion_value)
            File.write("dispersion_samples %s\n"%ob.povray.dispersion_samples) 
        if scene.povray.photon_enable == False:
            File.write("caustics %.4g\n"%ob.povray.fake_caustics_power)
        File.write("}\n")

def write_output_material(povMatName,ntree):
                for node in ntree.nodes:
                    if node:
                        if node.bl_idname == "PovrayOutputNode":
                            if node.inputs["Material"].is_linked:
                                for link in ntree.links:
                                    if link.to_node.bl_idname == "PovrayOutputNode":
                                        povMatName=new_name(link.from_node.name)+"_%s"%povMatName
                            else:
                                file.write('#declare %s = texture {%s}\n'%(povMatName,color))

def write_modifiers(tex,File):
    if tex.povray.turbulence_enable:
        if tex.povray.turbulence_all_axis:
            File.write('        turbulence %.4f\n'%tex.povray.turbulence_all)
        else:
            File.write('        turbulence <%.4f,%.4f,%.4f>\n'%tex.povray.turbulence[:])
        File.write('        octaves %s\n'%tex.povray.octaves)
        File.write('        omega %.4f\n'%tex.povray.omega)
        File.write('        lambda %.4f\n'%tex.povray.lambdat)
        File.write('        frequency %.4f\n'%tex.povray.frequency)
        File.write('        phase %.4f\n'%tex.povray.phase)

def write_transform(tex, File):
    tp = tex.povray
    if tp.translate != (0,0,0):
        File.write('        translate <%.4f,%.4f,%.4f>\n'%tp.translate[:])
    if tp.rotate != (0,0,0):
        File.write('        rotate <%.4f,%.4f,%.4f>\n'%tp.rotate[:])
    sb = 1
    if tp.pattern == 'brick':
        sb = tp.brick_scale
    if tp.scale_all_axis and tp.scale_all != 1:
        File.write('        scale %.4f/%s\n'%(tp.scale_all,sb))
    else:
        if tp.scale != (1,1,1):
            scale = '<%.4f,%.4f,%.4f>'%tp.scale[:]
            File.write('        scale %s/%s\n'%(scale,sb))

def write_warps(tex,File):
    tp = tex.povray
    if tp.warp_types != "UV":
        orient = tp.warp_orientation
        exp = tp.warp_dist_exp
        if tp.warp_types == "REPEAT":
            if tp.warp_repeat_x:
                offset=""
                if tp.rx_offset_value != 0:
                    offset=" offset %s*%.4g"%(tp.rx_offset,tp.rx_offset_value)
                flip=""
                x,y,z=0,0,0
                if tp.rx_flip_x or tp.rx_flip_y or tp.rx_flip_z:
                    if tp.rx_flip_x:
                        x=1
                    if tp.rx_flip_y:
                        y=1
                    if tp.rx_flip_z:
                        z=1
                    flip=" flip <%s,%s,%s>"%(x,y,z)
                File.write("        warp {repeat x*%.4g%s%s}\n"%(1/tp.rx_value,offset,flip))
            if tp.warp_repeat_y:
                offset=""
                if tp.ry_offset_value != 0:
                    offset=" offset %s*%.4g"%(tp.ry_offset,tp.ry_offset_value)
                flip=""
                x,y,z=0,0,0
                if tp.ry_flip_x or tp.ry_flip_y or tp.ry_flip_z:
                    if tp.ry_flip_x:
                        x=1
                    if tp.ry_flip_y:
                        y=1
                    if tp.ry_flip_z:
                        z=1
                    flip=" flip <%s,%s,%s>"%(x,y,z)
                File.write("        warp {repeat y*%.4g%s%s}\n"%(1/tp.ry_value,offset,flip))
            if tp.warp_repeat_z:
                offset=""
                if tp.rz_offset_value != 0:
                    offset=" offset %s*%.4g"%(tp.rz_offset,tp.rz_offset_value)
                flip=""
                x,y,z=0,0,0
                if tp.rz_flip_x or tp.rz_flip_y or tp.rz_flip_z:
                    if tp.rz_flip_x:
                        x=1
                    if tp.rz_flip_y:
                        y=1
                    if tp.rz_flip_z:
                        z=1
                    flip=" flip <%s,%s,%s>"%(x,y,z)
                File.write("        warp {repeat z*%.4g%s%s}\n"%(1/tp.rz_value,offset,flip))
        if tp.warp_types == "CUBIC":
            File.write("        warp {cubic}\n")
        if tp.warp_types == "PLANAR":
            File.write("        warp {planar %s %.4g}\n"%(orient,exp))
        if tp.warp_types == "SPHERICAL":
            File.write("        warp {spherical orientation %s dist_exp %.4g}\n"%(orient,exp)) 
        if tp.warp_types == "CYLINDRICAL":
            File.write("        warp {cylindrical orientation %s dist_exp %.4g}\n"%(orient,exp)) 
        if tp.warp_types == "TOROIDAL":
            radius = tp.warp_tor_major_radius
            File.write("        warp {toroidal orientation %s dist_exp %.4g major_radius %.4g}\n"%(orient,exp,radius))

def write_pig_nor(tex,ctx,uv,File):
    tp = tex.povray

    pattern = tp.pattern
    if tp.pattern == 'ridged':
        pattern = 'function{f_ridged_mf(x, y, z, %.4f,%.4f,%.4f,%.4f,%.4f,%.4f)}'%(tp.ridged_p0,tp.ridged_p1,tp.ridged_p2,tp.ridged_p3,tp.ridged_p4,tp.ridged_p5)
    if ctx == "pig":
        File.write('    pigment{%s %s \n'%(uv,pattern))
    if ctx == "nor":
        File.write('    normal{%s %s %.4f\n'%(uv,pattern,tp.normal_value))
    if tp.pattern in {'tiling'}:
        File.write('        %s\n'%tp.tiling_number)
    if tp.pattern in {'quilted'}:
        File.write('        control0 %.4f control1 %.4f\n'%(tp.control0,tp.control1))
    if tp.pattern in {'pavement'}:
        sides = tp.pave_sides
        pattern = 1
        if tp.pave_tiles == '3':
            if tp.pave_sides == '4':
                pattern = tp.pave_pat_2
            if tp.pave_sides == '6':
                pattern = tp.pave_pat_3
        if tp.pave_tiles == '4':
            if tp.pave_sides == '3':
                pattern = tp.pave_pat_3
            if tp.pave_sides == '4':
                pattern = tp.pave_pat_5
            if tp.pave_sides == '6':
                pattern = tp.pave_pat_7
        if tp.pave_tiles == '5':
            if tp.pave_sides == '3':
                pattern = tp.pave_pat_4
            if tp.pave_sides == '4':
                pattern = tp.pave_pat_12
            if tp.pave_sides == '6':
                pattern = tp.pave_pat_22
        if tp.pave_tiles == '6':
            sides = tp.pave_sides_6
            if tp.pave_sides_6 == '3':
                pattern = tp.pave_pat_12
            if tp.pave_sides_6 == '4':
                pattern = tp.pave_pat_35
        File.write('        number_of_sides %s number_of_tiles %s pattern %s'%(sides,tp.pave_tiles,pattern))
        if tp.pave_tiles == '6' or tp.pave_sides != '6':
            File.write(' exterior %s'%tp.pave_exterior)
        File.write(' interior %s form %s\n'%(tp.pave_interior,tp.pave_form))
    if tp.pattern in {'gradient'}:
        File.write('        <%.4f,%.4f,%.4f>\n'%tp.vector[:])
    if tp.pattern in {'slope'}:
        vector = '<%.4f,%.4f,%.4f>'%tp.vector[:]
        File.write('        { %s,%.4f,%.4f}\n'%(vector,tp.lo_slope,tp.hi_slope))
    if tp.pattern in {'spiral1','spiral2'}:
        File.write('        %.4f\n'%tp.spiral_arms)
    if ctx == "pig":
        if tp.pattern not in {'brick','checker','cubic','hexagon','square','triangular'}:
            File.write('        color_map{\n')
            for el in tex.color_ramp.elements:
                r,g,b,a = el.color[:]
                if tp.alpha_mode == 'filter':
                    povcolor = "srgbf <%.4f,%.4f,%.4f,%.4f>"%(r,g,b,1-a)
                else:
                    povcolor = "srgbt <%.4f,%.4f,%.4f,%.4f>"%(r,g,b,1-a)
                File.write('            [%.4f %s]\n'%(el.position,povcolor))
            File.write('        }\n')
        else:
            for i in range(len(tex.color_ramp.elements)):
                el = tex.color_ramp.elements[i]
                r,g,b,a = el.color[:]
                if tp.alpha_mode == 'filter':
                    File.write('            srgbf <%.4f,%.4f,%.4f,%.4f>\n'%(r,g,b,1-a))
                else:
                    File.write('            srgbt <%.4f,%.4f,%.4f,%.4f>\n'%(r,g,b,1-a))
                if tp.pattern in {'brick','checker'} and i>=1:
                    break
                if tp.pattern in {'hexagon'} and i>=2:
                    break
                if tp.pattern in {'square'} and i>=3:
                    break
                if tp.pattern in {'cubic','triangular'} and i>=5:
                    break
    if tp.pattern in {'brick'}:
        size = '<%.4f,%.4f,%.4f>'%tp.vector[:]
        sb = tp.brick_scale
        File.write('        brick_size %s*%s mortar %.4f*%s\n'%(size,sb,tp.mortar,sb))



def write_simple_texture(scene,mat,povMatName,file):
    def write_image(tex,ctx,uv):
        impath = bpy.path.abspath(tex.image.filepath)
        if tex.povray.image_sequence:
            imdir = os.path.dirname(impath)
            frame = scene.frame_current
            imname = "{:04d}".format(frame)+'.png'
            impath = os.path.join(imdir,imname)
        image_map = '"%s" '%impath
        image_map += 'gamma %.4f '%tex.povray.gamma
        if tex.povray.map_type != 'uv_mapping':
            image_map += 'map_type %s '%tex.povray.map_type
        if tex.povray.once:
            image_map += 'once '
        image_map += 'interpolate %s '%tex.povray.interpolate
        if ctx == "pig":
            image_map += 'filter all %.4f '%pov.povfilter
            image_map += 'transmit all %.4f'%pov.transmit
            file.write('    pigment{%s image_map{%s}\n'%(uv,image_map))
        if ctx == "nor":
            image_map += 'bump_size %.4f'%tex.povray.normal_value
            file.write('    normal{%s bump_map{%s}\n'%(uv,image_map))
        write_modifiers(tex,file)
        write_transform(tex,file)
        file.write('        }\n')

    def write_pattern(tex,ctx,uv):
        write_pig_nor(tex,ctx,uv,file)
        write_modifiers(tex,file)
        write_warps(tex,file)
        write_transform(tex,file)
        file.write('        }\n')

    pov = mat.povray

    file.write('#declare %s = texture{\n'%povMatName)

    pigment_texture = False

    for slot in mat.povray_texture_slots:
        if slot and slot.texture and slot.texture.povray.pigment_normal=="pigment":
            tex = slot.texture
            uv = ''
            
            if tex.povray.pattern_or_image == "image" and tex.povray.image != '':
                if tex.povray.map_type == 'uv_mapping':
                    uv = 'uv_mapping'
                pigment_texture = True
                ctx = "pig"
                write_image(tex,ctx,uv)
            if tex.povray.pattern_or_image == "pattern":
                if tex.povray.warp_types == 'UV':
                    uv = 'uv_mapping'
                pigment_texture = True
                ctx = "pig"
                write_pattern(tex,ctx,uv)
    if pigment_texture == False:
        r,g,b,a = mat.diffuse_color[:]
        color = "%.4f,%.4f,%.4f"%(r,g,b)
        pigment = "color srgbft <%s,%.4f,%.4f>"%(color,pov.povfilter,1-a)
        file.write('    pigment{%s}\n'%pigment)

    for slot in mat.povray_texture_slots:
        if slot and slot.texture and slot.texture.povray.pigment_normal=="normal":
            tex = slot.texture
            uv = ''
            if tex.povray.pattern_or_image == "image" and tex.povray.image:
                if tex.povray.map_type == 'uv_mapping':
                    uv = 'uv_mapping'
                ctx = "nor"
                write_image(tex,ctx,uv)
            if tex.povray.pattern_or_image == "pattern":
                if tex.povray.warp_types == 'UV':
                    uv = 'uv_mapping'
                pigment_texture = True
                ctx = "nor"
                write_pattern(tex,ctx,uv)
    finish = ""
    diffuse = "        diffuse"
    if mat.povray.diffuse_albedo:
        diffuse += " albedo"
    diffuse += " %.4f\n"%mat.povray.diffuse_intensity
    finish += diffuse
    if pov.brilliance > 0:
        brilliance = "        brilliance %.4f\n"%pov.brilliance
        finish += brilliance
    if mat.povray.emit > 0:
        emit = "        emission %.4f\n"%mat.povray.emit
        finish += emit
    r,g,b = pov.ambient[:]
    if r==g==b==0:
        pass
    else:
        ambient = "        ambient <%.4f,%.4f,%.4f>\n"%pov.ambient[:]
        finish += ambient
    if pov.highlights in {"specular","phong"}:
        if pov.highlights in {"specular"}:
            spec = "        specular"
        if pov.highlights in {"phong"}:
            spec = "        phong"
        if pov.specular_albedo:
            spec += " albedo"
        spec += " %.4f\n"%pov.specular_intensity
        if pov.highlights in {"specular"}:
            spec += "        roughness %.4f\n"%pov.specular_roughness
        if pov.highlights in {"phong"}:
            spec += "        phong_size %.4f\n"%pov.phong_size
        if pov.highlights_metallic > 0:
            spec += "        metallic %.4f\n"%pov.specular_metallic
        finish += spec
    if pov.mirror_enable:
        reflection = "        reflection{"
        if pov.color_min_enable:
            reflection += "<%.4f,%.4f,%.4f>,"%pov.color_min[:]
        color = mat.mirror_color
        reflection += "<%.4f,%.4f,%.4f>"%color[:]
        if scene.povray.render == 'uberpov' and pov.mirror_roughness > 0:
            reflection += " roughness %.6f"%(pov.mirror_roughness)
        if pov.fresnel:
            reflection += " fresnel"
        if pov.falloff > 0:
            reflection += " falloff %.4f"%pov.falloff
        if mat.raytrace_mirror.reflect_factor > 0:
            reflection += " exponent %.4f"%mat.raytrace_mirror.reflect_factor
        if pov.metallic > 0:
            reflection += " metallic %.4f"%pov.metallic
        reflection += "}\n"
        finish += reflection
    if pov.conserve_energy:
        finish += "        conserve_energy\n"
    if scene.povray.sslt_enable:
        finish += "        subsurface{translucency <%.4f,%.4f,%.4f>}\n"%pov.translucency[:]
    if pov.irid_enable:
        irid = "        irid{%.4f "%pov.irid_amount
        irid += "thickness %.4f "%pov.irid_thickness
        irid += "turbulence %.4f}\n"%pov.irid_turbulence
        finish += irid
    file.write('    finish{\n%s          }\n'%finish)
    file.write('}\n')

def write_pov(filename, workDir, scene, info_callback=None):

    file = open(filename, "w")
    scene = bpy.context.scene
    render = scene.render
    world = scene.world
    tab = 4 * " "

    def tabWrite(str_o):
        if not scene.povray.tempfiles:
            global tabLevel
            brackets = str_o.count("{") - str_o.count("}") + str_o.count("[") - str_o.count("]")
            if brackets < 0:
                tabLevel = tabLevel + brackets
            if tabLevel < 0:
                print("Indentation Warning: tabLevel = %s" % tabLevel)
                tabLevel = 0
            if tabLevel >= 1:
                file.write("%s" % tab * tabLevel)
            file.write(str_o)
            if brackets > 0:
                tabLevel = tabLevel + brackets
        else:
            file.write(str_o)

    def exportWorld(scene):
        render = scene.render
        camera = scene.camera
        world = scene.world

        if not world:
            return
        if world:
            tabWrite("sky_sphere {\n")
            tabWrite("pigment {rgb<%.3f, %.3f, %.3f>}\n" % (world.color[:]))
            tabWrite("}\n\n")


    def exportFogs(scene):
        if scene.use_nodes == True:
            tree = scene.node_tree
            for node in tree.nodes:
                if node.bl_idname == 'PovrayFogNode':
                    inp = node.inputs
                    tabWrite("fog {\n")
                    tabWrite("distance %s\n"%(inp["Distance"].default_value))
                    r,g,b,a = inp["Color"].default_value[:]
                    f = inp["Filter"].default_value
                    tabWrite("color rgbft <%.3f,%.3f,%.3f,%.3f,%.3f>\n"%(r,g,b,f,1-a))
                    fog_type = 1
                    if inp["Ground"].default_value:
                        fog_type = 2
                    tabWrite("fog_type %s\n"%(fog_type))
                    tabWrite("fog_offset %.4f\n"%(inp["Offset"].default_value))
                    alt = inp["Altitude"].default_value
                    if alt == 0.0:
                        alt = 0.0000001
                    tabWrite("fog_alt %.7f\n"%(alt))
                    tabWrite("turbulence <%.4f,%.4f,%.4f>\n"%(inp["Turbulence"].default_value[:]))
                    tabWrite("turb_depth %.4f\n"%(inp["Depth"].default_value))
                    tabWrite("}\n")

    def exportLamps(lamps):

        global lampCount
        lampCount = 0
        for ob in lamps:
            lamp = ob.data
            lp = lamp.povray
            matrix = global_matrix @ ob.matrix_world
            color = tuple([c * lamp.energy/1000 for c in lamp.color])
            tabWrite("light_source {\n")
            tabWrite("<%.3g,%.3g,%.3g>\n"%matrix.translation[:])
            tabWrite("color rgb<%.3g, %.3g, %.3g>\n" % color)
            if lp.light_type in {'point'} and lp.shape != "":
                is_shape = False
                for ob in scene.objects:
                    if ob.type in {'MESH','CURVE','TEXT','META'} and ob.name == lp.shape:
                        is_shape = True
                if is_shape:
                    ob_light = "looks_like"
                    if lp.shape_light == "projected_through":
                        ob_light = "projected_through"
                    povName = string_strip_hyphen(bpy.path.clean_name(lp.shape))
                    tabWrite('%s{ data_%s_ob '%(ob_light,povName))
                    tabWrite("scale  <%.4f, %.4f, %.4f>}\n" %(matrix.to_scale()[:]))
                    tabWrite("rotate  <%.4f, %.4f, %.4f>\n" % \
                             tuple([degrees(e) for e in matrix.to_3x3().to_euler()]))

            if lp.light_type not in {'point'}:
                tabWrite("%s\n"%lp.light_type)
            if lp.light_type in {'spotlight','cylinder'}:
                tabWrite("radius %.6g\n" %lp.spot_size)
                tabWrite("falloff %.6g\n" %lp.spot_falloff)
                tabWrite("tightness %s\n"%(lp.tightness))
                trackTo = None
                for const in ob.constraints:
                    if const and const.type == "TRACK_TO" and const.target: 
                        trackTo = const.target
                        trackToMatrix = global_matrix * trackTo.matrix_world
                        tabWrite("point_at  <%.3g, %.3g, %.3g>\n"%(trackToMatrix[0][3], trackToMatrix[1][3], trackToMatrix[2][3]))
                        break
                if trackTo == None:
                    tabWrite("point_at  <0, 0, -1>\n")
            if lp.area_enable:
                if lp.light_type in {'parallel','spotlight','point'}:
                    is_area = True
                    if lp.light_type in {'point'} and (lp.shape != "" and lp.shape_light == "looks_like"):
                        is_area = False
                    if is_area:
                        size_1 = "%.4f,%.4f,%.4f"%(lp.size_x_1,lp.size_y_1,lp.size_z_1)
                        samples_1 = lp.samples_1
                        size_2 = "%.4f,%.4f,%.4f"%(lp.size_x_2,lp.size_y_2,lp.size_z_2)
                        samples_2 = lp.samples_2
                        tabWrite("area_light <%s>,<%s> %d, %d\n" %(size_1, size_2, samples_1, samples_2))
                        tabWrite("adaptive %s\n"% lp.adaptive)
                        if lp.area_illumination:
                            tabWrite("area_illumination on\n")
                        if lp.jitter:
                            tabWrite("jitter\n")
                        if lp.circular:
                            tabWrite("circular\n")
                        if lp.orient:
                            tabWrite("orient\n")


            distance = lamp.distance
            if distance < 0.000000001:
                distance = 0.000000001
                
            tabWrite("fade_distance %.10f\n" %distance)
            tabWrite("fade_power %s\n" %lp.fade_power)
            if lp.media_interaction == False:
                tabWrite("media_interaction off\n")
            if lp.media_attenuation:
                tabWrite("media_attenuation on\n")
            if lp.photons_disable:
                tabWrite("photons { reflection off refraction off }\n")
            tabWrite("}\n")
            lampCount += 1

    def exportCamera():
        camera = scene.camera
        campov = camera.data.povray

        matrix = global_matrix @ camera.matrix_world
        Qsize = float(render.resolution_x) / float(render.resolution_y)
        trackTo = None
        for const in camera.constraints:
            if const and const.type == "TRACK_TO" and const.target: 
                trackTo = const.target
                trackToMatrix = global_matrix @ trackTo.matrix_world
                break
        tabWrite("camera {\n")
        tabWrite("%s\n"%(campov.cam_type))
        if campov.cam_type in {'stereo','omni_directional_stereo'}:
            tabWrite("distance (%.6f)\n"%(campov.stereo_dist))
        if campov.cam_type in {'stereo'}:
            tabWrite("parallaxe atan2(%.6f,%.6f)\n"%(campov.parallaxe_0,campov.parallaxe_1))
        if campov.cam_type == "cylinder":
            tabWrite("%s\n"%(campov.cylinder_cam_type))
        if trackTo == None:
            tabWrite("location  <0,0,0>\n")
            tabWrite("look_at  <0,0,-1>\n")
        else:
            tabWrite("location  <%.6f, %.6f, %.6f>\n" % matrix.translation[:])
            tabWrite("look_at  <%.6f, %.6f, %.6f>\n"%(trackToMatrix[0][3], trackToMatrix[1][3], trackToMatrix[2][3]))
        tabWrite("right <%s, 0, 0>\n" % - Qsize)
        tabWrite("up <0, 1, 0>\n")
        if campov.cam_type in {'perspective','orthographic','fisheye','fisheye_orthographic','fisheye_equisolid_angle','fisheye_stereographic',
                                    'stereo','ultra_wide_angle','omnimax','panoramic','cylinder','spherical'}:
            tabWrite("angle  %f\n" % (360.0 * atan(16.0 / camera.data.lens) / pi))
        if trackTo == None:
            tabWrite("rotate  <%.6f, %.6f, %.6f>\n" % \
                     tuple([degrees(e) for e in matrix.to_3x3().to_euler()]))
            tabWrite("translate <%.6f, %.6f, %.6f>\n" % matrix.translation[:])
        else:
            if campov.blur_enable:
                tabWrite("blur_samples %s, %s\n"%(campov.blur_samples_min,campov.blur_samples_max))
                tabWrite("aperture %.4f\n"%(campov.aperture))
                tabWrite("confidence %.4f\n"%(campov.confidence))
                tabWrite("variance %.6f\n"%(campov.variance))
                if campov.focal_point == "":
                    tabWrite("focal_point <%.6f, %.6f, %.6f>\n"%(trackToMatrix[0][3], trackToMatrix[1][3], trackToMatrix[2][3]))
                else:
                    focalOb = scene.objects[campov.focal_point]
                    matrixBlur = global_matrix * focalOb.matrix_world
                    tabWrite("focal_point <%.4f,%.4f,%.4f>\n"% matrixBlur.translation[:])
        if campov.normal_enable:
            tabWrite("normal {%s %.4f turbulence %.4f scale %.4f}\n"%(campov.normal_patterns,campov.cam_normal,campov.turbulence,campov.scale))
        tabWrite("}\n")

    def exportObjects(ob):
        matrix=global_matrix
        tabWrite("object {data_%s_ob\n"%(new_name(ob.name)))
        write_object_modifiers(scene,ob,file)
        writeMatrix(file,matrix)
        tabWrite("}\n")



# !!! start write povray file !!!

    file.write("#version 3.7;\n\n")
    file.write('#include "functions.inc"\n')
    file.write('#include "shapes.inc"\n\n')
    write_global_setting(scene, file)
    exportWorld(scene)
    file.write("#declare Default_texture = texture{pigment {rgb 0.8}}\n\n")


    ob_declare = []
    csg_declare = []
    ob_render = []
    lamps = []

    for ob in scene.objects:
        if ob.type in {'LIGHT'}:
            lamps.append(ob)
        if (ob.type in {'MESH','CURVE','FONT'}) or (ob.type in {'META'} and ob.parent == None):
            if ob.povray.csg_use:
                csg_declare.append(ob)
            ob_declare.append(ob)
            if ob.povray.nohide_render:
                ob_render.append(ob)

    all_materials=[]
    for ob in ob_declare:
        if (ob.type in {'MESH'}) and (ob.povray.object_as in {'MESH'}):
            for slot in ob.material_slots:
                mat = slot.material
                if mat not in all_materials:
                    all_materials.append(mat)
        else:
            if ob.active_material:
                mat = ob.active_material
                if mat not in all_materials:
                    all_materials.append(mat)
            if ob.children:
                for child in ob.children:
                    if child.active_material:
                        mat = child.active_material
                        if mat not in all_materials:
                            all_materials.append(mat)

    for mat in all_materials:
        povMatName=new_name(mat.name)
        r,g,b,a = mat.diffuse_color[:]
        color = "pigment {rgbt <%.4g,%.4g,%.4g,%.4g>}"%(r,g,b,1-a)
        if mat.povray.use_nodes:
            ntree = mat.node_tree

            if len(ntree.nodes)==0:
                file.write('#declare %s = texture {%s}\n'%(povMatName,color))
            else:
                write_nodes(scene,povMatName,ntree,file)

            for node in ntree.nodes:
                if node:
                    if node.bl_idname == "PovrayOutputNode":
                        if node.inputs["Texture"].is_linked:
                            for link in ntree.links:
                                if link.to_node.bl_idname == "PovrayOutputNode":
                                    povMatName=new_name(link.from_node.name)+"_%s"%povMatName
                        else:
                            file.write('#declare %s = texture {%s}\n'%(povMatName,color))

        else:
            write_simple_texture(scene,mat,povMatName,file)


    for ob in ob_declare:
        shape_name = new_name(ob.name)
        matrix = ob.matrix_world
        texture_name = 'Default_texture'
        end = True
        declare_shape(tabWrite,shape_name,ob,scene,workDir,file,matrix,texture_name,end)
    if csg_declare != []:
        for i in range(0,scene.povray.declare_layers+1):
            for ob in csg_declare:
                if ob.povray.declare_layer == i:
                    shape_name = new_name(ob.name)
                    declare_from_text(tabWrite,shape_name,ob)


    for ob in ob_render:
        exportObjects(ob)


    exportLamps([l for l in lamps])
    exportCamera()
    file.close()


def write_pov_ini(scene, filename_ini, filename_pov, filename_image, workDir):
    scene = bpy.context.scene
    render = scene.render
    x = int(render.resolution_x * render.resolution_percentage * 0.01)
    y = int(render.resolution_y * render.resolution_percentage * 0.01)

    file = open(filename_ini, "w")
    file.write("Version=3.7\n")
    file.write("Input_File_Name='%s'\n" % filename_pov)
    file.write("Output_File_Name='%s'\n" % filename_image)
    file.write('Library_Path="%s"\n'%workDir)
    addonDir=os.path.dirname(__file__)
    incDir=os.path.join(addonDir, "include")
    file.write('Library_Path="%s"\n'%incDir)
    file.write('Library_Path="/usr/share/povray-3.7/include"\n')
    file.write("Width=%d\n" % x)
    file.write("Height=%d\n" % y)

    # Border render.
    if render.use_border:
        file.write("Start_Column=%4g\n" % render.border_min_x)
        file.write("End_Column=%4g\n" % (render.border_max_x))

        file.write("Start_Row=%4g\n" % (1.0 - render.border_max_y))
        file.write("End_Row=%4g\n" % (1.0 - render.border_min_y))

    file.write("Bounding_Method=2\n")  # The new automatic BSP is faster in most scenes

    # Activated (turn this back off when better live exchange is done between the two programs
    # (see next comment)
    display = 1
    if scene.povray.sdl_window_use == False:
        display = 0
    file.write("Display=%s\n"%display)
    #file.write("Display_Gamma=%.4g\n"%scene.pov.display_gamma)
    file.write("Pause_When_Done=0\n")
    file.write("Output_File_Type=%s\n"%scene.povray.output_format)
    file.write("Output_Alpha=1\n")

    if scene.povray.antialias_enable:
        file.write("Antialias=on\n")
        file.write("Sampling_Method=%s\n" % scene.povray.antialias_sampling_method)
        file.write("Antialias_Depth=%d\n" % scene.povray.antialias_depth)
        file.write("Antialias_Threshold=%.3g\n" % scene.povray.antialias_threshold)
        file.write("Antialias_Gamma=%.3g\n" % scene.povray.antialias_gamma)
        if scene.povray.antialias_jitter_enable:
            file.write("Jitter=on\n")
            file.write("Jitter_Amount=%3g\n" % scene.povray.antialias_jitter_amount)
        else:
            file.write("Jitter=off\n")
    else:
        file.write("Antialias=off\n")
    file.close()







