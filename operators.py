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

############ To get POV-Ray specific objects In and Out of Blender ###########

import bpy
import os.path
from bpy_extras.io_utils import ImportHelper
from bpy_extras import object_utils
from math import atan, pi, degrees, sqrt, cos, sin


from bpy.props import (
        StringProperty,
        BoolProperty,
        IntProperty,
        FloatProperty,
        FloatVectorProperty,
        EnumProperty,
        PointerProperty,
        CollectionProperty,
        )

from mathutils import (
    Vector,
    Matrix,
)

def string_strip_hyphen(name):
    return name.replace(".", "_")

class POVRAY_OT_csg_settings_add(bpy.types.Operator):
    bl_idname = "pov.csg_settings_add"
    bl_label = "Add"
    bl_description = "Add operation"
    bl_options = {'REGISTER', 'UNDO'}
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        ob = context.object
        return (ob and ob.type in{'MESH','CURVE','CURVETEXT','META'} and engine in cls.COMPAT_ENGINES)

    def execute(self, context):

        item = context.object.pov_csg.add()
        digit_name = len(context.object.pov_csg)-1
        item.name = "%s"%(digit_name)
        context.object.povray.number_operation = digit_name

        return {'FINISHED'}

class POVRAY_OT_csg_settings_remove(bpy.types.Operator):
    bl_idname = "pov.csg_settings_remove"
    bl_label = "Remove"
    bl_description = "Remove operation"
    bl_options = {'REGISTER', 'UNDO'}
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        ob = context.object
        return (ob and ob.type in{'MESH','CURVE','CURVETEXT','META'} and engine in cls.COMPAT_ENGINES)

    def execute(self, context):
        number = context.object.povray.number_operation
        item = context.object.pov_csg.remove(number)

        return {'FINISHED'}


class POVRAY_OT_csg_write(bpy.types.Operator):
    bl_idname = "pov.csg_write"
    bl_label = "Write"
    bl_description = "Write operations"
    bl_options = {'REGISTER', 'UNDO'}
    COMPAT_ENGINES = {'POVRAY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        ob = context.object
        return (ob and ob.type in{'MESH','CURVE','CURVETEXT','META'} and engine in cls.COMPAT_ENGINES)

    def execute(self, context):
        scn = context.scene
        ob = context.object
        csg = ob.pov_csg
        povParentName = string_strip_hyphen(bpy.path.clean_name(ob.name))
        data = [("",povParentName)]
        collections = {}
        for i, item in enumerate(csg):
            child = None
            objs = []
            operation = item.csg
            try:
                if item.object_collection in {"object"} and item.object_csg != "":
                    child = item.object_csg.split()[-1]
                    scn.objects[child].povray.dec_only = True
                elif item.object_collection in {"collection"} and item.collection_csg != "":
                    child = item.collection_csg.split()[-1]
                    for ob_child in bpy.data.collections[child].objects:
                        objs.append(ob_child.name)
                data.append((operation,child))
            except:
                pass
            if objs != []:
                collections[child] = objs
        if len(data) > 1:
            try:
                bpy.data.texts.remove(bpy.data.texts[ob.name])
            except:
                pass
            text = bpy.data.texts.new(name = ob.name)
            if len(collections) > 0:
                for i,key in enumerate(collections):
                    text.write("#declare data_%s_ob = union {\n"%key)
                    key_objs = collections[key]
                    for name in key_objs:
                        povName = string_strip_hyphen(bpy.path.clean_name(name))
                        text.write("    object {data_%s_ob}\n"%povName)
                        scn.objects[name].povray.dec_only = True
                    text.write("}\n")

            #text.write("#declare data_%s_csg = \n"%povParentName)
            end = ""
            bs = {}
            bs["difference"] = "             "
            bs["intersection"] = "               "
            bs["merge"] = "        "
            bs["union"] = "        "
            bs[""] = ""
            back = ""
            for i, val in enumerate(data):
                end += "}"
                try:
                    data[i+1][1] != ""
                    text.write("%s%s { object {data_%s_ob}\n"%(back,data[i+1][0],val[1]))
                    back+=bs[data[i+1][0]]
                except:
                    text.write("%sobject {data_%s_ob%s\n"%(back,val[1],end))
            #text.write("object {data_%s_csg}\n"%povParentName)
            ob.povray.use_text = True






        # 
        # text.write("%s {\n"%(data[0][0]))
        # text.write("object {data_%s_ob}\n"%povParentName)




                # objs.append(ob)
            # if item.collection_csg != "":
                # col = item.object_csg.split()[-1]
                # for ob in bpy.data.collections[col]:
                    # objs.append(ob.name)
            # if len(objs) > 0:
                # data.append((operation,objs))
        # if len(data) > 0:
            # text = bpy.data.texts.new(name = ob.name)
            # text.write("#declare data_%s_csg =\n"%povParentName)
            # text.write("%s {\n"%(data[0][0]))
            # text.write("object {data_%s_ob}\n"%povParentName)
            # for i in range(len(data)-1):







                # if i == 0:

                # if item.object_csg != "":
                    # name = item.object_csg.split()[0]
                    # scn.objects[name].povray.dec_only = True
                    # povName = string_strip_hyphen(bpy.path.clean_name(name))
                    # text.write("object {data_%s_ob}\n"%povName)
                # if i == len(csg)-1:
                    # text.write("}\n")
                    # text.write("object {data_%s_csg}\n"%povParentName)
                    # 
        return {'FINISHED'}



classes = (
    POVRAY_OT_csg_settings_add,
    POVRAY_OT_csg_settings_remove,
    POVRAY_OT_csg_write,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in classes:
        unregister_class(cls)
