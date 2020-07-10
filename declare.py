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
from .utils import *

def declare_blob(tabWrite,shape_name,ob,file):
    povMatName = 'Default_texture'
    matrix=ob.matrix_world
    meta = ob.data
    elements = [elem for elem in meta.elements if elem.type in {'BALL','CAPSULE'}]
    if elements:
        tabWrite("#declare data_%s_ob = blob {\n"%shape_name)
        tabWrite("threshold %.4g\n" % meta.threshold)
        for elem in elements:
            if ob.active_material:
                povMatName = new_name(ob.active_material.name)
            tex = "texture {%s}"%povMatName
            radius = elem.radius/1.175
            if elem.type == 'BALL':
                tabWrite("sphere { <0,0,0>, %.4g, %.4g %s\n" %(radius, ob.povray.blob_strength, tex))
            if elem.type == 'CAPSULE':
                co = '<%.4f,%.4f,%.4f>'%elem.co[:]
                tabWrite("cylinder { <-10,0,0>, <10,0,0>, %.4f, %.4f %s translate %s\n" %(radius, ob.povray.blob_strength, tex, co))
            writeMatrix(file,matrix)
            tabWrite('}\n')
    if ob.children:
        for child in ob.children:
            if child.active_material:
                povMatName = new_name(child.active_material.name)
            tex = "texture {%s}"%povMatName
            if len(elements)>1:
                tex = ''
            matrixC=child.matrix_world
            meta = child.data
            elements = [elem for elem in meta.elements if elem.type in {'BALL','CAPSULE'}]
            if elements:
                for elem in elements:
                    radius = elem.radius/1.175
                    if elem.type == 'BALL':
                        tabWrite("sphere { <0,0,0>, %.4g, %.4g %s\n" %(radius, child.povray.blob_strength, tex))
                    if elem.type == 'CAPSULE':
                        tabWrite("cylinder { <-10,0,0>, <10,0,0>, %.4f, %.4f %s\n" %(radius, child.povray.blob_strength, tex))
                    writeMatrix(file,matrixC)
                    tabWrite('}\n')

    tabWrite("}\n")


def declare_blobsea(tabWrite,shape_name,ob,file):
    povMatName = 'Default_texture'
    if ob.active_material:
        povMatName = new_name(ob.active_material.name)
    matrix=ob.matrix_world
    tabWrite("#declare data_%s_ob = blob {\n"%shape_name)
    tabWrite("threshold %.4g\n" % ob.povray.blob_threshold)
    data = ob.data
    verts = data.vertices
    edges = data.edges
    st=ob.povray.blob_strength
    tex = "texture {%s}"%povMatName
    r = ob.povray.cylinder_radius
    for i,edge in enumerate(edges):
        if i > 3:
            co_0 = verts[edge.vertices[0]].co[:]
            co_1 = verts[edge.vertices[1]].co[:]
            co_0 = '<%.6f,%.6f,%.6f>'%co_0
            co_1 = '<%.6f,%.6f,%.6f>'%co_1
            tabWrite("cylinder {%s, %s, %.4f, %.4f %s " %(co_0,co_1,r,st,tex))
            writeMatrix(file,matrix)
            tabWrite("}")
    if ob.particle_systems:
        r=ob.povray.sphere_radius
        #r*=ob.scale[1]
        scale_x = 'scale <%.6f,1,1>'%ob.povray.scale_x
        for psys in ob.particle_systems:
            for p in psys.particles:
                if p.alive_state in {'ALIVE'}:
                    loc = p.location[:]
                    trans = 'translate <%.6f,%.6f,%.6f>'%(loc[0],loc[1],0)
                    tabWrite("sphere {<0,0,0>, %.4f, %.4f %s %s %s}\n" %(r,st,scale_x,trans,tex))
    tabWrite("}\n")

def declare_box(tabWrite,shape_name):
    tabWrite("#declare data_%s_ob = box { -1, 1\n"%shape_name)


def declare_cone(tabWrite,shape_name,ob):
    rb = ob.povray.shape_cone_radius_base
    rc = ob.povray.shape_cone_radius_cap
    pb = ob.povray.shape_cone_point_base
    pc = ob.povray.shape_cone_point_cap
    tabWrite("#declare data_%s_ob = cone { <0,0,%.4f>,%.4f,<0,0,%.4f>,%.4f\n"%(shape_name,pb,rb,pc,rc))


def declare_cylinder(tabWrite,shape_name):
    tabWrite("#declare data_%s_ob = cylinder { <0,0,1>,<0,0,-1>,1\n"%shape_name)


def declare_from_text(tabWrite,shape_name,ob):
    text = bpy.data.texts[ob.name]
    for line in text.lines:
        tabWrite('%s\n'%line.body)


def declare_hf(tabWrite,shape_name,ob):
    data = ""
    filename = ob.povray.shape_hf_filename
    data += '"%s"'%filename
    gamma = ' gamma %.4f'%ob.povray.shape_hf_gamma
    data += gamma
    if ob.povray.shape_hf_premultiplied:
        data += ' premultiplied on'
    if ob.povray.shape_hf_smooth:
        data += ' smooth'
    if ob.povray.shape_hf_water > 0:
        data += ' water_level %.4f'%ob.povray.shape_hf_water
    #hierarchy = ob.povray.shape_hf_hierarchy
    tabWrite('#declare data_%s_ob = height_field { %s\n'%(shape_name,data))
    tabWrite("rotate x*90\n")
    tabWrite("translate <-0.5,0.5,0>\n")


def declare_lathe(tabWrite,shape_name,ob):
    try:
        ob.data.splines[0].type in {'BEZIER'}
        spl = ob.data.splines[0]
        points=spl.bezier_points
        lenCur=len(points)-1
        lenPts=lenCur*4
        tabWrite("#declare data_%s_ob = lathe { bezier_spline %s,\n"%(shape_name,lenPts))
        for i in range(0,lenCur):
            if ob.data.shape_keys:
                num_keys = 0
                value_sh = 0
                co_sh_x = 0
                co_sh_y = 0
                co0_sh_x = 0
                co0_sh_y = 0
                hr_sh_x = 0
                hr_sh_y = 0
                hl_sh_x = 0
                hl_sh_y = 0
                p1 = []
                pR = []
                pL = []
                p2 = []
                for n, key in enumerate(ob.data.shape_keys.key_blocks):
                    if n != 0:
                        num_keys += 1
                        value_sh += key.value
                        co_sh_x += key.data[i].co[0]
                        co_sh_y += key.data[i].co[1]
                        hr_sh_x += key.data[i].handle_right[0]
                        hr_sh_y += key.data[i].handle_right[1]
                        hl_sh_x += key.data[i+1].handle_left[0]
                        hl_sh_y += key.data[i+1].handle_left[1]
                        co0_sh_x += key.data[i+1].co[0]
                        co0_sh_y += key.data[i+1].co[1]
                value_sh /= num_keys
                co_sh_x /= num_keys
                co_sh_y /= num_keys
                co0_sh_x /= num_keys
                co0_sh_y /= num_keys
                hr_sh_x /= num_keys
                hr_sh_y /= num_keys
                hl_sh_x /= num_keys
                hl_sh_y /= num_keys
                
                p1x=points[i].co[0] + ((co_sh_x - points[i].co[0]) * value_sh)
                p1y=points[i].co[1] + ((co_sh_y - points[i].co[1]) * value_sh)
                p1.append(p1x)
                p1.append(p1y)
                
                pRx=points[i].handle_right[0] + ((hr_sh_x - points[i].handle_right[0]) * value_sh)
                pRy=points[i].handle_right[1] + ((hr_sh_y - points[i].handle_right[1]) * value_sh)
                pR.append(pRx)
                pR.append(pRy)
                
                end = i+1
                pLx=points[end].handle_left[0] + ((hl_sh_x - points[end].handle_left[0]) * value_sh)
                pLy=points[end].handle_left[1] + ((hl_sh_y - points[end].handle_left[1]) * value_sh)
                pL.append(pLx)
                pL.append(pLy)
    
                p2x=points[end].co[0] + ((co0_sh_x - points[end].co[0]) * value_sh)
                p2y=points[end].co[1] + ((co0_sh_y - points[end].co[1]) * value_sh)
                p2.append(p2x)
                p2.append(p2y)
    
                line="<%.4g,%.4g>"%(p1[0],p1[1])
                line+="<%.4g,%.4g>"%(pR[0],pR[1])
                line+="<%.4g,%.4g>"%(pL[0],pL[1])
                line+="<%.4g,%.4g>"%(p2[0],p2[1])
                tabWrite("%s\n" %line)
            else:
                p1=points[i].co
                pR=points[i].handle_right
                end = i+1
                if i == lenCur-1 and ob.povray.curveshape in {'prism'}:
                    end = 0
                pL=points[end].handle_left
                p2=points[end].co
                line="<%.4g,%.4g>"%(p1[0],p1[1])
                line+="<%.4g,%.4g>"%(pR[0],pR[1])
                line+="<%.4g,%.4g>"%(pL[0],pL[1])
                line+="<%.4g,%.4g>"%(p2[0],p2[1])
                tabWrite("%s\n" %line)
    except:
        tabWrite("#declare data_%s_ob = box { -1, 1\n"%shape_name)

def declare_plane(tabWrite,shape_name):
    tabWrite("#declare data_%s_ob = plane{ <0,0,1>,1\n"%shape_name)


def declare_prism(tabWrite,shape_name,ob):
    try:
        for spl in ob.data.splines:
            spl.type in {'BEZIER'}

        lenAllPts = 0
        splPts = []
    
    
        for spl in ob.data.splines:
            lenSplPts = len(spl.bezier_points)
            splPts.append(lenSplPts)
            lenAllPts += lenSplPts
    
        height = ob.data.extrude
        param = '-%s, %s,'%(height, height)
        tabWrite("#declare data_%s_ob = prism { bezier_spline %s %s,\n"%(shape_name,param,lenAllPts*4))
        for i,spl in enumerate(ob.data.splines):

            points=spl.bezier_points
            lenCur=splPts[i]


            for i in range(0,lenCur):
                p1=points[i-1].co
                pR=points[i-1].handle_right
                pL=points[i].handle_left
                p2=points[i].co
                line="<%.4f,%.4f>"%(p1[0],p1[1])
                line+="<%.4f,%.4f>"%(pR[0],pR[1])
                line+="<%.4f,%.4f>"%(pL[0],pL[1])
                line+="<%.4f,%.4f>"%(p2[0],p2[1])
                tabWrite("%s\n" %line)
        tabWrite("rotate x*90\n")
    except:
        tabWrite("#declare data_%s_ob = box { -1, 1\n"%shape_name)


def declare_roundbox(tabWrite,shape_name,ob):
    xmax = ob.povray.xmax
    xmin = ob.povray.xmin
    ymax = ob.povray.ymax
    ymin = ob.povray.ymin
    zmax = ob.povray.zmax
    zmin = ob.povray.zmin
    minimum = '<%.4f,%.4f,%.4f>'%(xmin,ymin,zmin)
    maximum = '<%.4f,%.4f,%.4f>'%(xmax,ymax,zmax)
    merge = '0'
    if ob.povray.union_merge:
        merge = '1'
    tabWrite("#declare data_%s_ob = object {Round_Box (%s,%s,%.6f,%s)\n"%(shape_name,minimum,maximum,ob.povray.round_radius,merge))

def declare_sphere(tabWrite,shape_name):
    tabWrite("#declare data_%s_ob = sphere { 0,1\n"%shape_name)

def declare_superellipsoid(tabWrite,shape_name,ob):
    p1=ob.povray.shape_se_param1
    p2=ob.povray.shape_se_param2
    tabWrite("#declare data_%s_ob = superellipsoid{ <%.4f,%.4f>\n"%(shape_name,p1,p2))


def declare_supertorus(tabWrite,shape_name,ob):
    rMajor = ob.povray.shape_st_radius_major
    rMinor = ob.povray.shape_st_radius_minor
    ring = ob.povray.shape_st_ring
    cross = ob.povray.shape_st_cross
    accuracy=ob.povray.shape_st_accuracy
    gradient=ob.povray.shape_st_max_gradient
    tabWrite("#declare data_%s_ob = object{ Supertorus( %.4g,%.4g,%.4g,%.4g,%.4g,%.4g)\n"%(shape_name,rMajor,rMinor,ring,cross,accuracy,gradient))
    tabWrite("rotate x*90\n")

def declare_torus(tabWrite,shape_name,ob):
    minor = ob.povray.shape_st_radius_minor
    major = ob.povray.shape_st_radius_major
    tabWrite("#declare data_%s_ob = torus { %.4f,%.4f\n"%(shape_name,major,minor))
    tabWrite("rotate x*90\n")

def declare_mesh2(tabWrite,shape_name,ob,scene,workDir,matrix,file):
    tab = 4 * " "
    tabLevel = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    ob_eval = ob.evaluated_get(depsgraph)
    try:
        me = ob_eval.to_mesh()
    except:
        pass

    #importance = ob.pov.importance_value
    if me:
        me.calc_loop_triangles()
        me_materials = me.materials
        me_faces = me.loop_triangles[:]

    uv_layers = me.uv_layers
    if len(uv_layers) > 0:
        if me.uv_layers.active and uv_layers.active.data:
            uv_layer = uv_layers.active.data
    else:
        uv_layer = None

    try:
        vcol_layer = me.vertex_colors.active.data
    except AttributeError:
        vcol_layer = None

    faces_verts = [f.vertices[:] for f in me_faces]
    faces_normals = [f.normal[:] for f in me_faces]
    verts_normals = [v.normal[:] for v in me.vertices]

    # Use named declaration to allow reference e.g. for baking. MR
    file.write("\n")
    tabWrite("#declare data_%s_ob =\n" % shape_name)
    tabWrite("mesh2 {\n")
    tabWrite("vertex_vectors {\n")
    tabWrite("%d" % len(me.vertices))  # vert count

    tabStr = tab * tabLevel
    for v in me.vertices:

        file.write(",\n")
        file.write(tabStr + "<%.6f, %.6f, %.6f>" % v.co[:])  # vert count

    file.write("\n")
    tabWrite("}\n")

    # Build unique Normal list
    uniqueNormals = {}
    for fi, f in enumerate(me_faces):
        fv = faces_verts[fi]
        # [-1] is a dummy index, use a list so we can modify in place
        if f.use_smooth:  # Use vertex normals
            for v in fv:
                key = verts_normals[v]
                uniqueNormals[key] = [-1]
        else:  # Use face normal
            key = faces_normals[fi]
            uniqueNormals[key] = [-1]

    tabWrite("normal_vectors {\n")
    tabWrite("%d" % len(uniqueNormals))  # vert count
    idx = 0
    tabStr = tab * tabLevel
    for no, index in uniqueNormals.items():
        file.write(",\n")
        file.write(tabStr + "<%.6f, %.6f, %.6f>" % no)  # vert count
        index[0] = idx
        idx += 1
    file.write("\n")
    tabWrite("}\n")

    # Vertex colors
    vertCols = {}  # Use for material colors also.

    if uv_layer:
        # Generate unique UV's
        uniqueUVs = {}
        #n = 0
        for f in me_faces: # me.faces in 2.7
            uvs = [uv_layer[l].uv[:] for l in f.loops]

            for uv in uvs:
                uniqueUVs[uv[:]] = [-1]

        tabWrite("uv_vectors {\n")
        #print unique_uvs
        tabWrite("%d" % len(uniqueUVs))  # vert count
        idx = 0
        tabStr = tab * tabLevel
        for uv, index in uniqueUVs.items():
            file.write(",\n")
            file.write(tabStr + "<%.6f, %.6f>" % uv)

            index[0] = idx
            idx += 1
        '''
        else:
            # Just add 1 dummy vector, no real UV's
            tabWrite('1') # vert count
            file.write(',\n\t\t<0.0, 0.0>')
        '''
        file.write("\n")
        tabWrite("}\n")

    if me.vertex_colors:
        #Write down vertex colors as a texture for each vertex
        tabWrite("texture_list {\n")
        tabWrite("%d\n" % (len(me_faces) * 3)) # assumes we have only triangles
        VcolIdx=0
        if comments:
            file.write("\n  //Vertex colors: one simple pigment texture per vertex\n")
        for fi, f in enumerate(me_faces):
            # annoying, index may be invalid
            material_index = f.material_index
            try:
                material = me_materials[material_index]
            except:
                material = None
            if material: #and material.use_vertex_color_paint: #Always use vertex color when there is some for now

                cols = [vcol_layer[l].color[:] for l in f.loops]

                for col in cols:
                    key = col[0], col[1], col[2], material_index  # Material index!
                    VcolIdx+=1
                    vertCols[key] = [VcolIdx]
                    tabWrite("texture {pigment{ color srgb <%6f,%6f,%6f> }}\n" % (col[0], col[1], col[2]))

            else:
                if material:
                    # Multiply diffuse with SSS Color
                    if material.pov_subsurface_scattering.use:
                        diffuse_color = [i * j for i, j in zip(material.pov_subsurface_scattering.color[:], material.diffuse_color[:])]
                        key = diffuse_color[0], diffuse_color[1], diffuse_color[2], \
                              material_index
                        vertCols[key] = [-1]
                    else:
                        diffuse_color = material.diffuse_color[:]
                        key = diffuse_color[0], diffuse_color[1], diffuse_color[2], \
                              material_index
                        vertCols[key] = [-1]

        tabWrite("\n}\n")
        # Face indices
        tabWrite("\nface_indices {\n")
        tabWrite("%d" % (len(me_faces)))  # faces count
        tabStr = tab * tabLevel

        for fi, f in enumerate(me_faces):
            fv = faces_verts[fi]
            material_index = f.material_index

            if vcol_layer:
                cols = [vcol_layer[l].color[:] for l in f.loops]

            if not me_materials or me_materials[material_index] is None:  # No materials
                file.write(",\n")
                # vert count
                file.write(tabStr + "<%d,%d,%d>" % (fv[0], fv[1], fv[2]))

            else:
                material = me_materials[material_index]
                if me.vertex_colors: #and material.use_vertex_color_paint:
                    # Color per vertex - vertex color

                    col1 = cols[0]
                    col2 = cols[1]
                    col3 = cols[2]

                    ci1 = vertCols[col1[0], col1[1], col1[2], material_index][0]
                    ci2 = vertCols[col2[0], col2[1], col2[2], material_index][0]
                    ci3 = vertCols[col3[0], col3[1], col3[2], material_index][0]
                else:
                    # Color per material - flat material color
                    if material.pov_subsurface_scattering.use:
                        diffuse_color = [i * j for i, j in zip(material.pov_subsurface_scattering.color[:], material.diffuse_color[:])]
                    else:
                        diffuse_color = material.diffuse_color[:]
                    ci1 = ci2 = ci3 = vertCols[diffuse_color[0], diffuse_color[1], \
                                      diffuse_color[2], f.material_index][0]
                    # ci are zero based index so we'll subtract 1 from them

                file.write(",\n")
                file.write(tabStr + "<%d,%d,%d>, %d,%d,%d" % \
                           (fv[0], fv[1], fv[2], ci1-1, ci2-1, ci3-1))  # vert count


        file.write("\n")
        tabWrite("}\n")

        # normal_indices indices
        tabWrite("normal_indices {\n")
        tabWrite("%d" % (len(me_faces)))  # faces count
        tabStr = tab * tabLevel
        for fi, fv in enumerate(faces_verts):

            if me_faces[fi].use_smooth:
                file.write(",\n")
                file.write(tabStr + "<%d,%d,%d>" %\
                (uniqueNormals[verts_normals[fv[0]]][0],\
                 uniqueNormals[verts_normals[fv[1]]][0],\
                 uniqueNormals[verts_normals[fv[2]]][0]))  # vert count

            else:
                idx = uniqueNormals[faces_normals[fi]][0]

                file.write(",\n")
                file.write(tabStr + "<%d,%d,%d>" % (idx, idx, idx))  # vert count


        file.write("\n")
        tabWrite("}\n")

        if uv_layer:
            tabWrite("uv_indices {\n")
            tabWrite("%d" % (len(me_faces)))  # faces count
            tabStr = tab * tabLevel
            for f in me_faces:
                uvs = [uv_layer[l].uv[:] for l in f.loops]
                file.write(",\n")
                file.write(tabStr + "<%d,%d,%d>" % (
                         uniqueUVs[uvs[0]][0],\
                         uniqueUVs[uvs[1]][0],\
                         uniqueUVs[uvs[2]][0]))


            file.write("\n")
            tabWrite("}\n")



        tabWrite("}\n")  # End of mesh block
    else:
        facesMaterials = [] # WARNING!!!!!!!!!!!!!!!!!!!!!!
        if me_materials:
            for f in me_faces:
                if f.material_index not in facesMaterials:
                    facesMaterials.append(f.material_index)
        # No vertex colors, so write material colors as vertex colors
        for i, material in enumerate(me_materials):

            if material:  # WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # Multiply diffuse with SSS Color
                if material.povray.subsurface_scattering_use:
                    diffuse_color = [i * j for i, j in zip(material.pov_subsurface_scattering.color[:], material.diffuse_color[:])]
                    key = diffuse_color[0], diffuse_color[1], diffuse_color[2], i  # i == f.mat
                    vertCols[key] = [-1]
                else:
                    diffuse_color = material.diffuse_color[:]
                    key = diffuse_color[0], diffuse_color[1], diffuse_color[2], i  # i == f.mat
                    vertCols[key] = [-1]




        # Vert Colors
        tabWrite("texture_list {\n")
        # In case there's is no material slot, give at least one texture
        #(an empty one so it uses pov default)
        if len(vertCols)==0:
            file.write(tabStr + "1")
        else:
            file.write(tabStr + "%s" % (len(vertCols)))  # vert count






        # WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        if facesMaterials:
            for index in facesMaterials:
                faceMaterial = new_name(me_materials[index].name)
                file.write("\n texture{%s}\n" % faceMaterial)
        # END!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        else:
            file.write(" texture{Default_texture}\n")
        tabWrite("}\n")

        # Face indices
        tabWrite("face_indices {\n")
        tabWrite("%d" % (len(me_faces)))  # faces count
        tabStr = tab * tabLevel

        for fi, f in enumerate(me_faces):
            fv = faces_verts[fi]
            ci1 = ci2 = ci3 = f.material_index
            file.write(",\n")
            file.write(tabStr + "<%d,%d,%d>, %d,%d,%d" % \
                       (fv[0], fv[1], fv[2], ci1, ci2, ci3))  # vert count


        file.write("\n")
        tabWrite("}\n")

        # normal_indices indices
        tabWrite("normal_indices {\n")
        tabWrite("%d" % (len(me_faces)))  # faces count
        tabStr = tab * tabLevel
        for fi, fv in enumerate(faces_verts):
            if me_faces[fi].use_smooth:

                file.write(",\n")
                file.write(tabStr + "<%d,%d,%d>" %\
                (uniqueNormals[verts_normals[fv[0]]][0],\
                 uniqueNormals[verts_normals[fv[1]]][0],\
                 uniqueNormals[verts_normals[fv[2]]][0]))  # vert count

            else:
                idx = uniqueNormals[faces_normals[fi]][0]
                file.write(",\n")
                file.write(tabStr + "<%d,%d,%d>" % (idx, idx, idx)) # vertcount


        file.write("\n")
        tabWrite("}\n")

        if uv_layer:
            tabWrite("uv_indices {\n")
            tabWrite("%d" % (len(me_faces)))  # faces count
            tabStr = tab * tabLevel
            for f in me_faces:
                uvs = [uv_layer[l].uv[:] for l in f.loops]

                file.write(",\n")
                file.write(tabStr + "<%d,%d,%d>" % (
                         uniqueUVs[uvs[0]][0],\
                         uniqueUVs[uvs[1]][0],\
                         uniqueUVs[uvs[2]][0]))


            file.write("\n")
            tabWrite("}\n")

        #XXX BOOLEAN
        onceCSG = 0
        for mod in ob.modifiers:
            if onceCSG == 0:
                if mod :
                    if mod.type == 'BOOLEAN':
                        if ob.pov.boolean_mod == "POV":
                            file.write("\tinside_vector <%.6g, %.6g, %.6g>\n" %
                                       (ob.pov.inside_vector[0],
                                        ob.pov.inside_vector[1],
                                        ob.pov.inside_vector[2]))
                            onceCSG = 1


        tabWrite("}\n")  # End of mesh block



    ob_eval.to_mesh_clear()


def declare_shape(tabWrite,shape_name,ob,scene,workDir,file,matrix,texture_name,end):
    if ob.type in {'META'}:
        declare_blob(tabWrite,shape_name,ob,file)
    if ob.povray.object_as in {'BLOBSEA'}:
        declare_blobsea(tabWrite,shape_name,ob,file)
    if ob.povray.object_as in {'BOX'}:
        declare_box(tabWrite,shape_name)
    if ob.povray.object_as in {'CONE'}:
        declare_cone(tabWrite,shape_name,ob)
    if ob.povray.object_as in {'CYLINDER'}:
        declare_cylinder(tabWrite,shape_name)
    if ob.type in {'FONT'}:
        declare_font(tabWrite,shape_name)
    if ob.povray.object_as in {'FROMTEXT'}:
        declare_from_text(tabWrite,shape_name,ob)
    if ob.povray.object_as in {'HEIGHT_FIELD'}:
        declare_hf(tabWrite,shape_name,ob)
    if ob.povray.object_as in {'LATHE'}:
        declare_lathe(tabWrite,shape_name,ob)
    if ob.povray.object_as in {'MESH'} and ob.type in {'MESH'}:
        declare_mesh2(tabWrite,shape_name,ob,scene,workDir,matrix,file)
    if ob.povray.object_as in {'PLANE'}:
        declare_plane(tabWrite,shape_name)
    if ob.povray.object_as in {'PRISM'}:
        declare_prism(tabWrite,shape_name,ob)
    if ob.povray.object_as in {'ROUNDBOX'}:
        declare_roundbox(tabWrite,shape_name,ob)
    if ob.povray.object_as in {'SPHERE'}:
        declare_sphere(tabWrite,shape_name)
    if ob.povray.object_as in {'SUPERELLIPSOID'}:
        declare_superellipsoid(tabWrite,shape_name,ob)
    if ob.povray.object_as in {'SUPERTORUS'}:
        declare_supertorus(tabWrite,shape_name,ob)
    if ob.povray.object_as in {'TORUS'}:
        declare_torus(tabWrite,shape_name,ob)

    if (ob.type in {'META'}) or (ob.type in {'MESH'} and ob.povray.object_as in {'MESH'}):
        pass
    elif ob.povray.object_as in {'BLOBSEA'}:
        pass
    else:
        if ob.povray.object_as not in {'FROMTEXT'}:
            material = ob.active_material
            if material:
                texture_name = new_name(material.name)
            tabWrite("texture {%s}\n"%texture_name)
        if matrix:
            writeMatrix(file,matrix)
        if end:
            tabWrite("}\n")


