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

import bpy, sys, os
from bpy.types import Operator
from bpy.props import IntProperty, StringProperty, FloatProperty, EnumProperty, BoolProperty
from bpy_extras import object_utils
from bpy_extras.io_utils import ImportHelper
from mathutils import Matrix, Vector
from math import *
import random
import tempfile

def string_strip_hyphen(name):
    return name.replace("-", "")

def create_mesh_object(context, verts, edges, faces, name):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, edges, faces)
    mesh.update()
    from bpy_extras import object_utils
    return object_utils.object_data_add(context, mesh, operator=None)

def createFaces(vertIdx1, vertIdx2, closed=False, flipped=False):
    faces = []
    if not vertIdx1 or not vertIdx2:
        return None
    if len(vertIdx1) < 2 and len(vertIdx2) < 2:
        return None
    fan = False
    if (len(vertIdx1) != len(vertIdx2)):
        if (len(vertIdx1) == 1 and len(vertIdx2) > 1):
            fan = True
        else:
            return None
    total = len(vertIdx2)
    if closed:
        if flipped:
            face = [
                vertIdx1[0],
                vertIdx2[0],
                vertIdx2[total - 1]]
            if not fan:
                face.append(vertIdx1[total - 1])
            faces.append(face)

        else:
            face = [vertIdx2[0], vertIdx1[0]]
            if not fan:
                face.append(vertIdx1[total - 1])
            face.append(vertIdx2[total - 1])
            faces.append(face)
    for num in range(total - 1):
        if flipped:
            if fan:
                face = [vertIdx2[num], vertIdx1[0], vertIdx2[num + 1]]
            else:
                face = [vertIdx2[num], vertIdx1[num],
                    vertIdx1[num + 1], vertIdx2[num + 1]]
            faces.append(face)
        else:
            if fan:
                face = [vertIdx1[0], vertIdx2[num], vertIdx2[num + 1]]
            else:
                face = [vertIdx1[num], vertIdx2[num],
                    vertIdx2[num + 1], vertIdx1[num + 1]]
            faces.append(face)

    return faces

def power(a,b):
    if a < 0:
        return -((-a)**b)
    return a**b
    
def supertoroid(R,r,u,v,n1,n2):
    a = 2*pi/u
    b = 2*pi/v
    verts = []
    faces = []
    for i in range(u):
        s = power(sin(i*a),n1)
        c = power(cos(i*a),n1)
        for j in range(v):
            c2 = R+r*power(cos(j*b),n2)
            s2 = r*power(sin(j*b),n2)
            verts.append(Vector((c*c2,s*c2,s2)))
        if i > 0:
            f = createFaces(range((i-1)*v,i*v),range(i*v,(i+1)*v),closed = True)
            faces.extend(f)
    f = createFaces(range((u-1)*v,u*v),range(v),closed=True)
    faces.extend(f)
    return verts, faces

class POVRAY_OBJECT_OT_shape_mesh_edge_add(Operator):
    bl_idname = "pov.addmeshedge"
    bl_label = "Edge"
    def execute(self, context):
            verts = [(-0.5,0,0),(0.5,0,0)]
            edges = [(0,1)]
            faces = []
            obj = create_mesh_object(context, verts, edges, faces, "Edge")
            return {'FINISHED'}


class POVRAY_OBJECT_OT_shape_lathe_add(bpy.types.Operator):
    bl_idname = "pov.addlathe"
    bl_label = "Lathe"
    bl_options = {'REGISTER','UNDO'}
    bl_description = "Create lathe"


    def execute(self, context):
        bpy.ops.curve.primitive_bezier_curve_add(location=(0, 0, 0), rotation=(0, 0, 0))
        ob=context.object
        ob.name = "Lathe_shape"
        ob.povray.object_write_type='LATHE'
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.transform.rotate(value=pi/2, orient_axis='Z')
        bpy.ops.object.mode_set(mode='OBJECT')
        mod = ob.modifiers.new(type='SCREW', name = 'Lathe_mesh')
        mod.axis = 'Y'
        ob.povray.object_as = "LATHE"
        return {'FINISHED'}

class POVRAY_OBJECT_OT_shape_round_box_add(bpy.types.Operator):
    bl_idname = "pov.addroundbox"
    bl_label = "Round Box"
    bl_description = "Create a Round Box"
    bl_options = {'REGISTER', 'UNDO'}

    size_x : FloatProperty(name = "Size X",min = 0,default = 2.0)
    size_y : FloatProperty(name = "Size Y",min = 0,default = 2.0)
    size_z : FloatProperty(name = "Size Z",min = 0,default = 2.0)

    def execute(self,context):
        props = self.properties
        size_x = props.size_x
        size_y = props.size_y
        size_z = props.size_z
        xmax = size_x/2
        xmin = -xmax
        ymax = size_y/2
        ymin = -ymax
        zmax = size_z/2
        zmin = -zmax
        verts=[(xmin,ymin,zmin),(xmin,ymin,zmax),(xmax,ymin,zmax),(xmax,ymin,zmin),(xmin,ymax,zmin),(xmin,ymax,zmax),(xmax,ymax,zmax),(xmax,ymax,zmin)]
        faces=[(0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        obj = create_mesh_object(context, verts, [], faces, "RoundBox_shape")
        engine = context.scene.render.engine
        ob = context.object
        scene = context.scene
        ob.povray.object_as = 'ROUNDBOX'
        ob.povray.xmin = xmin
        ob.povray.ymin = ymin
        ob.povray.zmin = zmin
        ob.povray.xmax = xmax
        ob.povray.ymax = ymax
        ob.povray.zmax = zmax
        scene.povray.shapes_inc = True
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.hide(unselected=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        return {'FINISHED'}


class POVRAY_OBJECT_OT_shape_superellipsoid_add(bpy.types.Operator):
    bl_idname = "pov.addsuperellipsoid"
    bl_label = "Superellipsoid"
    bl_description = "Create a SuperEllipsoid"
    bl_options = {'REGISTER', 'UNDO'}


    u : IntProperty(name = "U-segments",
                    description = "radial segmentation",
                    default = 20, min = 4, max = 265)
    v : IntProperty(name = "V-segments",
                    description = "lateral segmentation",
                    default = 20, min = 4, max = 265)
    n1 : FloatProperty(name = "Ring manipulator",
                      description = "Manipulates the shape of the Ring",
                      default = 1.0, min = 0.01, max = 100.0)
    n2 : FloatProperty(name = "Cross manipulator",
                      description = "Manipulates the shape of the cross-section",
                      default = 1.0, min = 0.01, max = 100.0)
    edit : EnumProperty(items=[("NOTHING", "Nothing", ""),
                                ("NGONS", "N-Gons", ""),
                                ("TRIANGLES", "Triangles", "")],
                        name="Fill up and down",
                        description="",
                        default='TRIANGLES')

    def execute(self,context):
        props = self.properties
        u = props.u
        v = props.v
        n1 = props.n1
        n2 = props.n2
        edit = props.edit
        verts=[]
        r=1
        stepSegment=360/v*pi/180
        stepRing=pi/u
        angSegment=0
        angRing=-pi/2

        step=0
        for ring in range(0,u-1):
            angRing+=stepRing
            for segment in range(0,v):
                step+=1
                angSegment+=stepSegment
                x=r*(abs(cos(angRing))**n1)*(abs(cos(angSegment))**n2)
                if (cos(angRing) < 0 and cos(angSegment) > 0) or (cos(angRing) > 0 and cos(angSegment) < 0):
                    x=-x
                y=r*(abs(cos(angRing))**n1)*(abs(sin(angSegment))**n2)
                if (cos(angRing) < 0 and sin(angSegment) > 0) or (cos(angRing) > 0 and sin(angSegment) < 0):
                    y=-y
                z=r*(abs(sin(angRing))**n1)
                if sin(angRing) < 0:
                    z=-z
                x=round(x,4)
                y=round(y,4)
                z=round(z,4)
                verts.append((x,y,z))
        if edit == 'TRIANGLES':
            verts.append((0,0,1))
            verts.append((0,0,-1))
        faces=[]
        for i in range(0,u-2):
            m=i*v
            for p in range(0,v):
                if p < v-1:
                    face=(m+p,1+m+p,v+1+m+p,v+m+p)
                if p == v-1:
                    face=(m+p,m,v+m,v+m+p)
                faces.append(face)
        if edit == 'TRIANGLES':
            indexUp=len(verts)-2
            indexDown=len(verts)-1
            indexStartDown=len(verts)-2-v
            for i in range(0,v):
                if i < v-1:
                    face=(indexDown,i,i+1)
                    faces.append(face)
                if i == v-1:
                    face=(indexDown,i,0)
                    faces.append(face)
            for i in range(0,v):
                if i < v-1:
                    face=(indexUp,i+indexStartDown,i+indexStartDown+1)
                    faces.append(face)
                if i == v-1:
                    face=(indexUp,i+indexStartDown,indexStartDown)
                    faces.append(face)
        if edit == 'NGONS':
            face=[]
            for i in range(0,v):
                face.append(i)
            faces.append(face)
            face=[]
            indexUp=len(verts)-1
            for i in range(0,v):
                face.append(indexUp-i)
            faces.append(face)
        obj = create_mesh_object(context, verts, [], faces, "SuperEllipsoid_shape")
        engine = context.scene.render.engine
        ob = context.object
        ob.povray.object_as = 'SUPERELLIPSOID'
        ob.povray.shape_se_param1 = props.n2
        ob.povray.shape_se_param2 = props.n1
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.hide(unselected=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        return {'FINISHED'}



class POVRAY_OBJECT_OT_shape_supertorus_add(bpy.types.Operator):
    bl_idname = "pov.addsupertorus"
    bl_label = "Supertorus"
    bl_description = "Create a SuperTorus"
    bl_options = {'REGISTER', 'UNDO'}

    R : FloatProperty(name = "big radius",
                      description = "The radius inside the tube",
                      default = 1.0, min = 0.01, max = 100.0)
    r : FloatProperty(name = "small radius",
                      description = "The radius of the tube",
                      default = 0.3, min = 0.01, max = 100.0)
    u : IntProperty(name = "U-segments",
                    description = "radial segmentation",
                    default = 16, min = 3, max = 265)
    v : IntProperty(name = "V-segments",
                    description = "lateral segmentation",
                    default = 8, min = 3, max = 265)
    n1 : FloatProperty(name = "Ring manipulator",
                      description = "Manipulates the shape of the Ring",
                      default = 1.0, min = 0.01, max = 100.0)
    n2 : FloatProperty(name = "Cross manipulator",
                      description = "Manipulates the shape of the cross-section",
                      default = 1.0, min = 0.01, max = 100.0)
    ie : BoolProperty(name = "Use Int.+Ext. radii",
                      description = "Use internal and external radii",
                      default = False)
    edit : BoolProperty(name="",
                        description="",
                        default=False,
                        options={'HIDDEN'})

    def execute(self,context):
        props = self.properties
        if props.ie:
            rad1 = (props.R+props.r)/2
            rad2 = (props.R-props.r)/2
            if rad2 > rad1:
                [rad1,rad2] = [rad2,rad1]
        else:
            rad1 = props.R
            rad2 = props.r
            if rad2 > rad1:
                rad1 = rad2
        verts,faces = supertoroid(rad1,
                                  rad2,
                                  props.u,
                                  props.v,
                                  props.n1,
                                  props.n2)
        obj = create_mesh_object(context, verts, [], faces, "SuperTorus_shape")
        engine = context.scene.render.engine
        ob = context.object
        ob.povray.object_as = 'SUPERTORUS'
        ob.povray.shape_st_radius_major = props.R
        ob.povray.shape_st_radius_minor = props.r
        ob.povray.shape_st_ring = props.n1
        ob.povray.shape_st_cross = props.n2
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.hide(unselected=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        return {'FINISHED'}



class POVRAY_OBJECT_OT_shape_box_add(bpy.types.Operator):
    bl_idname = "pov.addbox"
    bl_label = "Box"
    bl_description = "Add Box"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        bpy.ops.mesh.primitive_cube_add()
        ob = context.object
        ob.name = 'Box_shape'
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.hide(unselected=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        ob.povray.object_as = "BOX"
        return {'FINISHED'}



class POVRAY_OBJECT_OT_shape_cone_add(bpy.types.Operator):
    bl_idname = "pov.addcone"
    bl_label = "Cone"
    bl_description = "Add Cone"
    bl_options = {'REGISTER', 'UNDO'}

    base : FloatProperty(name = "Base radius",
                      description = "The radius inside the tube",
                      default = 1.0, min = 0.01, max = 100.0)
    cap : FloatProperty(name = "Cap radius",
                      description = "The radius of the tube",
                      default = 0.3, min = 0.0, max = 100.0)
    seg : IntProperty(name = "Segments",
                    description = "radial segmentation",
                    default = 16, min = 3, max = 265)
    height : FloatProperty(name = "Height",
                      description = "",
                      default = 2.0, min = 0.01, max = 100.0)
    def execute(self,context):
        verts = []
        faces = []
        props = self.properties
        base = props.base
        cap = props.cap
        seg = props.seg
        height = props.height
        zc = height/2
        zb = -zc
        angle = 2*pi/seg
        t=0
        for i in range(seg):
            xb = base*cos(t)
            yb = base*sin(t)
            xc = cap*cos(t)
            yc = cap*sin(t)
            verts.append((xb,yb,zb))
            verts.append((xc,yc,zc))
            t+=angle
        for i in range(seg):
            f = i*2
            if i == seg-1:
                faces.append([f,f+1,1,0])
            else:
                faces.append([f,f+1,f+3,f+2])
        if base != 0:
            base_face = []
            for i in range(seg):
                p = i*2
                base_face.append(p)
            faces.append(base_face)
        if cap != 0:
            cap_face = []
            for i in range(seg):
                p = i*2+1
                cap_face.append(p)
            faces.append(cap_face)
        obj = create_mesh_object(context, verts, [], faces, "Cone_shape")
        ob = context.object
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.remove_doubles(threshold=0.0001, use_unselected=False)
        bpy.ops.mesh.hide(unselected=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        ob.povray.object_as = "CONE"
        ob.povray.shape_cone_radius_base = base
        ob.povray.shape_cone_radius_cap = cap
        ob.povray.shape_cone_point_base = zb
        ob.povray.shape_cone_point_cap = zc
        return {'FINISHED'}



class POVRAY_OBJECT_OT_shape_cylinder_add(bpy.types.Operator):
    bl_idname = "pov.addcylinder"
    bl_label = "Cylinder"
    bl_description = "Add Cylinder"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        bpy.ops.mesh.primitive_cylinder_add()
        ob = context.object
        ob.name = 'Cylinder_shape'
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.hide(unselected=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        ob.povray.object_as = "CYLINDER"

        return {'FINISHED'}



class POVRAY_OBJECT_OT_shape_height_field_add(bpy.types.Operator, ImportHelper):
    bl_idname = "pov.addheightfield"
    bl_label = "Height Field"
    bl_description = "Add Height Field "
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext : ".png"
    filter_glob : StringProperty(
            default="*.exr;*.gif;*.hdr;*.iff;*.jpeg;*.jpg;*.pgm;*.png;*.pot;*.ppm;*.sys;*.tga;*.tiff;*.EXR;*.GIF;*.HDR;*.IFF;*.JPEG;*.JPG;*.PGM;*.PNG;*.POT;*.PPM;*.SYS;*.TGA;*.TIFF",
            options={'HIDDEN'},
            )

    quality : IntProperty(name = "Quality",
                      description = "",
                      default = 100, min = 1, max = 100)

    def execute(self,context):
        impath = bpy.path.abspath(self.filepath)
        img = bpy.data.images.load(impath)
        im_name = img.name
        im_name, file_extension = os.path.splitext(im_name)
        hf_tex = bpy.data.textures.new('%s_hf_image'%im_name, type = 'IMAGE')
        hf_tex.image = img

        quality = self.quality
        res = 100/quality
        w,h = hf_tex.image.size[:]
        w = int(w/res)
        h = int(h/res)
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=10, y_subdivisions=10,size = 2)
        ob = context.object
        ob.name = '%s'%im_name
        mod = ob.modifiers.new(type='DISPLACE',name='Height Field')
        mod.texture = hf_tex
        ob.povray.object_as = 'HEIGHT_FIELD'
        ob.povray.shape_hf_filename = impath
        return {'FINISHED'}



class POVRAY_OBJECT_OT_shape_sphere_add(bpy.types.Operator):
    bl_idname = "pov.addsphere"
    bl_label = "Sphere"
    bl_description = "Add Sphere Shape"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self,context):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4)
        ob = context.object
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.hide(unselected=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.shade_smooth()
        ob.povray.object_as = "SPHERE"
        ob.name = 'Sphere_shape'
        return {'FINISHED'}

class POVRAY_OBJECT_OT_shape_plane_add(bpy.types.Operator):
    bl_idname = "pov.addplane"
    bl_label = "Plane"
    bl_description = "Add Plane"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        bpy.ops.mesh.primitive_plane_add(100000000)
        ob = context.object
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.hide(unselected=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.shade_smooth()
        ob.povray.object_as = "PLANE"
        return {'FINISHED'}

class POVRAY_OBJECT_OT_shape_sphere_sweep_add(bpy.types.Operator):
    bl_idname = "pov.addspheresweep"
    bl_label = "Sphere Sweep"
    bl_description = "Create Prism"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        bpy.ops.curve.primitive_nurbs_curve_add()
        ob = context.object
        ob.name = "Sphere_sweep"
        ob.povray.object_as = "SPHERE_SWEEP"
        ob.data.bevel_depth = 0.02
        ob.data.bevel_resolution = 4
        ob.data.fill_mode = 'FULL'
        #ob.data.splines[0].order_u = 4
        return {'FINISHED'}

class POVRAY_OBJECT_OT_shape_blob_add(bpy.types.Operator):
    bl_idname = "pov.addblob"
    bl_label = "Blob"
    bl_description = "Add Blob Sphere"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):

        bpy.ops.object.metaball_add(type = 'BALL')
        ob = context.object
        ob.name = "Blob"
        return {'FINISHED'}

class POVRAY_OBJECT_OT_shape_torus_add(bpy.types.Operator):
    bl_idname = "pov.addtorus"
    bl_label = "Torus"
    bl_description = "Add Torus"
    bl_options = {'REGISTER', 'UNDO'}
    mas : IntProperty(name = "Major Segments",
                    description = "",
                    default = 48, min = 3, max = 720)
    mis : IntProperty(name = "Minor Segments",
                    description = "",
                    default = 12, min = 3, max = 720)
    mar : FloatProperty(name = "Major Radius",
                    description = "",
                    default = 1.0)
    mir : FloatProperty(name = "Minor Radius",
                    description = "",
                    default = 0.25)
    def execute(self,context):
        props = self.properties
        mar = props.mar
        mir = props.mir
        mas = props.mas
        mis = props.mis
        bpy.ops.mesh.primitive_torus_add(major_segments=mas, minor_segments=mis,major_radius=mar, minor_radius=mir)
        ob = context.object
        ob.name = "Torus_shape"
        ob.povray.object_as = "TORUS"
        ob.povray.shape_st_radius_major = mar
        ob.povray.shape_st_radius_minor = mir
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.hide(unselected=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        return {'FINISHED'}

class POVRAY_OBJECT_OT_shape_prism_add(bpy.types.Operator):
    bl_idname = "pov.addprism"
    bl_label = "Prism"
    bl_description = "Create Prism"
    bl_options = {'REGISTER', 'UNDO'}


    n : IntProperty(name = "Sides",
                    description = "Number of sides",
                    default = 16, min = 3, max = 720)
    r : FloatProperty(name = "Radius",
                    description = "Radius",
                    default = 1.0)

    def execute(self,context):
        
        props = self.properties
        prism_data = bpy.data.curves.new('Prism', type='CURVE')
        prism_data.dimensions = '2D'
        prism_data.resolution_u = 2
        n=props.n
        r=props.r
        coords = []
        z = 0
        angle = 0
        for p in range(n):
            x = r*cos(angle)
            y = r*sin(angle)
            coords.append((x,y,z))
            angle+=pi*2/n
        poly = prism_data.splines.new('POLY')
        poly.points.add(len(coords)-1)
        for i, coord in enumerate(coords):
            x,y,z = coord
            poly.points[i].co = (x, y, z, 1)
        poly.use_cyclic_u = True
        ob = object_utils.object_data_add(context,prism_data,None,'Prism_shape')
        ob.povray.object_as = "PRISM"
        ob.name = "Prism"
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.spline_type_set(type='BEZIER', use_handles=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        return {'FINISHED'}



class POVRAY_OBJECT_OT_shape_polygon_to_circle_add(bpy.types.Operator):
    bl_idname = "pov.addpolygontocircle"
    bl_label = "Polygon To Circle Blending"
    bl_description = "Add Shape Polygon To Circle Blending"
    bl_options = {'REGISTER', 'UNDO'}


    resolution : IntProperty(name = "Resolution",
                    description = "",
                    default = 3, min = 0, max = 256)
    ngon : IntProperty(name = "NGon",
                    description = "",
                    min = 3, max = 64,default = 5)
    ngonR : FloatProperty(name = "NGon Radius",
                    description = "",
                    default = 0.3)
    circleR : FloatProperty(name = "Circle Radius",
                    description = "",
                    default = 1.0)


    def execute(self,context):
        props = self.properties
        ngon = props.ngon
        ngonR = props.ngonR
        circleR = props.circleR
        resolution = props.resolution
        bpy.ops.mesh.primitive_circle_add(vertices=ngon, radius=ngonR, fill_type='NGON',enter_editmode=True)
        bpy.ops.transform.translate(value=(0, 0, 1))
        bpy.ops.mesh.subdivide(number_cuts=resolution)
        numCircleVerts = ngon + (ngon*resolution)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.primitive_circle_add(vertices=numCircleVerts, radius=circleR, fill_type='NGON',enter_editmode=True)
        bpy.ops.transform.translate(value=(0, 0, -1))
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bridge_edge_loops()
        if ngon < 5:
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_circle_add(vertices=ngon, radius=ngonR, fill_type='TRIFAN',enter_editmode=True)
            bpy.ops.transform.translate(value=(0, 0, 1))
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode='OBJECT')
        ob = context.object
        ob.name = "Polygon_To_Circle"
        ob.povray.object_as = "POLYCIRCLE"
        ob.povray.ngon = ngon
        ob.povray.ngonR = ngonR
        ob.povray.circleR = circleR
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.hide(unselected=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        return {'FINISHED'}


class POVRAY_MT_shapes_add_menu(bpy.types.Menu):
    """Define the menu with presets"""
    bl_idname = "POVRAY_MT_shapes_add_menu"
    bl_label = "Povray"
    COMPAT_ENGINES = {'POVRAY_RENDER'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine == 'POVRAY_RENDER')

    def draw(self,context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("pov.addblob", icon = 'META_BALL')
        layout.operator("pov.addbox", icon = 'CUBE')
        layout.operator("pov.addcone", icon = 'CONE')
        layout.operator("pov.addcylinder", icon = 'MESH_CYLINDER')
        layout.operator("pov.addheightfield", icon ='RNDCURVE')
        layout.operator("pov.addlathe", icon = 'EXPERIMENTAL')
        layout.operator("pov.addmeshedge", icon = 'REMOVE')
        layout.operator("pov.addplane", icon = 'MESH_PLANE')
        layout.operator("pov.addpolygontocircle", icon = 'CLIPUV_DEHLT')
        layout.operator("pov.addprism", icon = 'MESH_CUBE')
        layout.operator("pov.addroundbox", icon = 'META_PLANE')
        layout.operator("pov.addsphere", icon = 'SPHERE')
        layout.operator("pov.addspheresweep", icon ='CURVE_NCURVE')
        layout.operator("pov.addsuperellipsoid", icon ='SURFACE_NSPHERE')
        layout.operator("pov.addsupertorus", icon ='SURFACE_NTORUS')
        layout.operator("pov.addtorus", icon ='MESH_TORUS')


def menu_povray_shapes_add(self, context):
    engine = context.scene.render.engine
    if engine == 'POVRAY':
        self.layout.menu("POVRAY_MT_shapes_add_menu", icon="EVENT_P")



classes = (
    POVRAY_OBJECT_OT_shape_blob_add,
    POVRAY_OBJECT_OT_shape_box_add,
    POVRAY_OBJECT_OT_shape_cone_add,
    POVRAY_OBJECT_OT_shape_cylinder_add,
    POVRAY_OBJECT_OT_shape_height_field_add,
    POVRAY_OBJECT_OT_shape_lathe_add,
    POVRAY_OBJECT_OT_shape_mesh_edge_add,
    POVRAY_OBJECT_OT_shape_plane_add,
    POVRAY_OBJECT_OT_shape_polygon_to_circle_add,
    POVRAY_OBJECT_OT_shape_prism_add,
    POVRAY_OBJECT_OT_shape_round_box_add,
    POVRAY_OBJECT_OT_shape_sphere_add,
    POVRAY_OBJECT_OT_shape_sphere_sweep_add,
    POVRAY_OBJECT_OT_shape_superellipsoid_add,
    POVRAY_OBJECT_OT_shape_supertorus_add,
    POVRAY_OBJECT_OT_shape_torus_add,
    POVRAY_MT_shapes_add_menu,

)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.VIEW3D_MT_add.prepend(menu_povray_shapes_add)


def unregister():
    from bpy.utils import unregister_class

    for cls in classes:
        unregister_class(cls)

    bpy.types.VIEW3D_MT_add.remove(menu_povray_shapes_add)
