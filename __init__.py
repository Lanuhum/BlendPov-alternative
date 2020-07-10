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

bl_info = {
    "name": "Povray with BlendPov-alternative exporter",
    "author": "Lanuhum",
    "version": (1,0,0),
    "blender": (2, 90, 0),
    "location": "3D-View > Engine to use for rendering: 'Povray render'",
    "description": "Alternate addon for Povray-3.8",
    "category": "Render"}

import bpy
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
import sys, os, re
import subprocess
import time
from . import render
from .utils import new_name

class DisabledShaderNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ShaderNodeTree'

node_categories = [
    DisabledShaderNodeCategory("SHADERS", "Shaders", items=[
        NodeItem("ShaderNodeAddShader"),
        NodeItem("ShaderNodeBsdfDiffuse"),
        NodeItem("ShaderNodeEmission"),
        NodeItem("ShaderNodeBsdfGlass"),
        NodeItem("ShaderNodeBsdfGlossy"),
        NodeItem("ShaderNodeHoldout"),
        NodeItem("ShaderNodeMixShader"),
        NodeItem("ShaderNodeBsdfPrincipled"),
        NodeItem("ShaderNodeVolumePrincipled"),
        NodeItem("ShaderNodeBsdfRefraction"),
        NodeItem("ShaderNodeEeveeSpecular"),
        NodeItem("ShaderNodeSubsurfaceScattering"),
        NodeItem("ShaderNodeBsdfTranslucent"),
        NodeItem("ShaderNodeBsdfTransparent"),
        NodeItem("ShaderNodeVolumeAbsorption"),
        NodeItem("ShaderNodeVolumeScatter"),
        ]),
    DisabledShaderNodeCategory("MATERIAL_OUT", "Material_out", items=[
        NodeItem("ShaderNodeOutputMaterial"),
        ]),
    ]

class PovrayPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    binary : bpy.props.StringProperty(
                name="Povray Binary Location",
                subtype='FILE_PATH',
                )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "binary")


class PovrayRender(bpy.types.RenderEngine):
    bl_idname = 'POVRAY'
    bl_label = "Povray"
    bl_use_eevee_viewport = True
    bl_use_shading_nodes_custom = False
    bl_use_preview = True
    DELAY = 0.1

    @staticmethod
    def _locate_binary():
        if sys.platform[:3] == "win":
            import winreg
            win_reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\POV-Ray\\v3.7\\Windows")
            win_home = winreg.QueryValueEx(win_reg_key, "Home")[0]
            if platform.architecture()[0]=='64bit':
                pov_binary = os.path.join(win_home, "bin", "pvengine64.exe")
                if os.path.exists(pov_binary):
                    return pov_binary
            if platform.architecture()[0]=='32bit':
                pov_binary = os.path.join(win_home, "bin", "pvengine.exe")
                if os.path.exists(pov_binary):
                    return pov_binary

        pov_binary_default = "povray"
        os_path_ls = os.getenv("PATH").split(':') + [""]
        for dir_name in os_path_ls:
            pov_binary = os.path.join(dir_name, pov_binary_default)
            if os.path.exists(pov_binary):
                return pov_binary
        return ""

    def _export(self, depsgraph):
        scene = bpy.context.scene
        ext = {
            'B': "bmp",
            'T': "tga",
            'C': "tga",
            'E': "exr",
            'H': "hdr",
            'J': "jpg",
            'N': "png", 
            'P': "ppm", 
        }
        format_ext=ext[scene.povray.output_format]

        import tempfile
        self._temp_work_dir = tempfile.gettempdir()
        if scene.povray.tempfiles:
            self._temp_file_in = tempfile.NamedTemporaryFile(suffix=".pov", delete=False).name
            self._temp_file_out = tempfile.NamedTemporaryFile(suffix=".%s"%format_ext, delete=False).name
            self._temp_file_ini = tempfile.NamedTemporaryFile(suffix=".ini", delete=False).name

        if scene.povray.tempfiles==False:
            povSceneName=new_name(scene.name)
            if scene.povray.workdir !="" and os.path.exists(scene.povray.workdir):
                self._temp_work_dir=scene.povray.workdir
            self._temp_file_in = os.path.join(self._temp_work_dir, "%s.pov"%povSceneName)
            self._temp_file_out = os.path.join(self._temp_work_dir, "%s.%s"%(povSceneName,format_ext))
            self._temp_file_ini = os.path.join(self._temp_work_dir, "%s.ini"%povSceneName)

        def info_callback(txt):
            self.update_stats("", "Povray: " + txt)
        if self.is_preview==False and scene.povray.render_scenes_from_file == False:
            render.write_pov(self._temp_file_in,self._temp_work_dir, scene, info_callback)

    def _render(self, scene):

        try:
            os.remove(self._temp_file_out)
        except OSError:
            pass

        pov_binary = PovrayRender._locate_binary()
        if not pov_binary:
            print("Povray: could not execute povray, possibly POV-Ray isn't installed")
            return False
        if self.is_preview==False:
            render.write_pov_ini(scene, self._temp_file_ini, self._temp_file_in, self._temp_file_out, self._temp_work_dir)

        print ("***-STARTING-***")
        print (pov_binary)
        self._is_windows = False
        if sys.platform[:3] == "win":
            self._is_windows = True

        try:
            if self.is_preview==False:
                env = {'POV_DISPLAY_SCALED': 'off'}
                env.update(os.environ)
                povfile = self._temp_file_ini
                self._process = subprocess.Popen([pov_binary, povfile],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    env=env)

        except OSError:
            print("Povray: could not execute '%s'" % pov_binary)
            import traceback
            traceback.print_exc()
            print ("***-DONE-***")
            return False

        else:
            print("Povray found")
            return True

    def _cleanup(self):
        for f in (self._temp_file_in, self._temp_file_ini, self._temp_file_out):
            for i in range(5):
                try:
                    os.unlink(f)
                    break
                except OSError:
                    time.sleep(self.DELAY)

    def render(self, depsgraph):
        scn=bpy.context.scene
        if self.is_preview:
            pass

        else:
            print("***INITIALIZING***")
            povSceneName = "blendScene"
            #scene.frame_set(scene.frame_current)
            self.update_stats("", "Povray: Exporting data from Blender")
            self._export(depsgraph)
            self.update_stats("", "Povray: Parsing File")
            if not self._render(depsgraph):
                self.update_stats("", "Povray: Not found")
                return
            scene = bpy.context.scene
            r = scene.render
            x = int(r.resolution_x * r.resolution_percentage * 0.01)
            y = int(r.resolution_y * r.resolution_percentage * 0.01)
            def _test_wait():
                time.sleep(self.DELAY)
                if self.test_break():
                    try:
                        self._process.terminate()
                        print("***POV INTERRUPTED***")
                    except OSError:
                        pass
                    return False
    
                poll_result = self._process.poll()
                if poll_result is not None:
                    if poll_result < 0:
                        print("***POV PROCESS FAILED : %s ***" % poll_result)
                        self.update_stats("", "Povray: Failed")
                    return False
    
                return True
            parsing = re.compile(br"= \[Parsing\.\.\.\] =")
            rendering = re.compile(br"= \[Rendering\.\.\.\] =")
            percent = re.compile(r"\(([0-9]{1,3})%\)")
            data = b""
            last_line = ""
            while _test_wait():
                if self._is_windows:
                    self.update_stats("", "Povray: Rendering File")
                else:
                    t_data = self._process.stdout.read(500)
                    if not t_data:
                        continue
                    data += t_data
                    t_data = str(t_data).replace('\\r\\n', '\\n').replace('\\r', '\r')
                    lines = t_data.split('\\n')
                    last_line += lines[0]
                    lines[0] = last_line
                    print('\n'.join(lines), end="")
                    last_line = lines[-1]
                    if rendering.search(data):
                        _pov_rendering = True
                        match = percent.findall(str(data))
                        if match:
                            progress = int(match[-1])
                            pixelsAll = x*y
                            pixels = int(pixelsAll*progress/100)
                            self.update_stats("", "Povray: Rendering File: %s of %s pixels (%s%%)" %(pixels,pixelsAll,progress))
                        else:
                            self.update_stats("", "Povray: Rendering File")
                    elif parsing.search(data):
                        self.update_stats("", "Povray: Parsing File")
            if os.path.exists(self._temp_file_out):
                render = scene.render
                if render.use_border:
                    try:
                        from PIL import Image
                        im_x_min = int(x*render.border_min_x)
                        im_y_min = int(y*render.border_min_y)
                        fore = Image.open(self._temp_file_out)
                        back = Image.open(self._temp_file_out) 
                        back.paste(fore, (-im_x_min,im_y_min+1), fore)
                        back.save(self._temp_file_out)
                    except:
                        pass
                result = self.begin_result(0, 0, x, y)
                lay = result.layers[0]
                time.sleep(self.DELAY)
                try:
                    lay.load_from_file(self._temp_file_out)
                except RuntimeError:
                    print("***POVRAY ERROR WHILE READING OUTPUT FILE***")
                self.end_result(result)
            else:
                print("***POVRAY FILE NOT FOUND***")
            print("***POVRAY FINISHED***")
            self.update_stats("", "")
            if scene.povray.tempfiles:
                self._cleanup()

def register():

    from bpy.utils import register_class

    from . import operators
    from . import properties
    from . import shapes
    from . import ui

    operators.register()
    properties.register()
    shapes.register()
    ui.register()

    register_class(PovrayPreferences)
    register_class(PovrayRender)
    nodeitems_utils.register_node_categories("DISABLEDEEVEENODES", node_categories)

def unregister():

    from bpy.utils import unregister_class

    from . import operators
    from . import properties
    from . import shapes
    from . import ui

    operators.unregister()
    properties.unregister()
    shapes.unregister()
    ui.unregister()

    unregister_class(PovrayRender)
    unregister_class(PovrayPreferences)
    nodeitems_utils.unregister_node_categories("DISABLEDEEVEENODES")

if __name__ == "__main__":
    register()







