"""
Atmosphere
Copyright: Charles Rowland, 2017
Written for CINEMA 4D R16 and up

Modified Date: 03/05/2017
"""

import os
import c4d
import datetime
import webbrowser
from c4d import plugins, utils, bitmaps, gui, documents

# Your Plugin Number for "Bubble Type" is: 1038835
PLUGIN_ID = 1038836
VERSION = 1
now = datetime.datetime.now()
YEAR = now.year
C4DVNUM = int(str(c4d.GetC4DVersion())[:2])  # just get the first 2 digits of the c4d version number

# TODO: add check to ignore background in the add/remove material buttons methods
# TODO: Add background object if one does not exist
# TODO: Add a new material for BG object. 2D_V gradient in luma channel
# TODO: hook up background link checkbox.
#   When Unlink Background Color is UNCHECKED, all of the gradient chips on the background will match the
#   second color chip on the Atmosphere color so that the atmosphere gradient blends into the background seamlessly.
#   When Unlink Background Color is CHECKED, you would control the start and end by adjusting the gradient chips because
#   the mapping would always be the same (2D V)
# TODO: Atmosphere Strength controls transparency
#   Think of it as if on that material you turned on the transparency and the Atmosphere strength controls
#   the transparency strength
# TODO: make new render settings preset for Atmosphere rendering
#   Output channel copied, Save channel copied, Multi-pass channel disabled, AA set to non


class CRUtils(object):
    def __init__(self, arg):
        super(CRUtils, self).__init__()

    @staticmethod
    def open_website(web):
        # opens the default web browser to the given url
        webbrowser.open(web, 2)

    @staticmethod
    def about(plugin_name, version, year, author, website, twitter):
        # Show About information dialog box
        gui.MessageDialog("{0} v{1}\nCopyright (C) {2} {3}.\nAll rights reserved.\n\n{4}\n{5}\n".format(plugin_name, version, year, author, website, twitter), c4d.GEMB_OK)

    @staticmethod
    def show_error(msg):
        gui.MessageDialog(msg, c4d.GEMB_OK)
        return False

    @staticmethod
    def get_activedoc():
        # Returns doc object
        activeDoc = documents.GetActiveDocument()
        return(activeDoc)

    @staticmethod
    def get_active_objects():
        # Returns a list of active objects
        doc = documents.GetActiveDocument()
        objList = doc.GetActiveObjects(True)
        return objList

    @staticmethod
    def get_all_objects():
        doc = documents.GetActiveDocument()
        op = doc.GetFirstObject()
        objects = []

        if len(objects) > 0:
            objects[:] = []

        if op is None:
            return

        while op:
            objects.append(op)
            op = CRUtils.next_object(op)

        return objects

    @staticmethod
    def get_all_objects_types():
        doc = documents.GetActiveDocument()
        op = doc.GetFirstObject()
        object_types = []

        if len(object_types) > 0:
            object_types[:] = []

        if op is None:
            return

        while op:
            object_types.append(op.GetType())
            op = CRUtils.next_object(op)

        return object_types

    @staticmethod
    def next_object(op):
        if op is None:
            return None

        if op.GetDown():
            return op.GetDown()

        while not op.GetNext() and op.GetUp():
            op = op.GetUp()

        return op.GetNext()

    @staticmethod
    def get_object_by_name(name):
        doc = documents.GetActiveDocument()
        op = doc.GetFirstObject()

        if op is None:
            return None

        if name is None:
            return None

        while op:
            if op.GetName() == name:
                return op
            else:
                op = CRUtils.next_object(op)

    @staticmethod
    def get_first_object_of_type(obj_type):
        doc = documents.GetActiveDocument()
        op = doc.GetFirstObject()

        if op is None:
            return None

        if obj_type is None:
            return None

        while op:
            if op.GetType() == obj_type:
                obj = op
            else:
                op = CRUtils.next_object(op)

    @staticmethod
    def verify_object_by_type(obj_type):

        if obj_type is None:
            return None

        obj_types = CRUtils.get_all_objects_types()
        if obj_type in obj_types:
            return True
        else:
            return False

    @staticmethod
    def get_materials():
        return CRUtils.get_activedoc().GetMaterials()

    @staticmethod
    def get_material_gradient(material, channel, objtype):
        if channel == "luminance":
            gradient_object = material[c4d.MATERIAL_LUMINANCE_SHADER]
            actual_gradient = gradient_object[c4d.SLA_GRADIENT_GRADIENT]

        if channel == "alpha":
            gradient_object = material[c4d.MATERIAL_ALPHA_SHADER]
            actual_gradient = gradient_object[c4d.SLA_GRADIENT_GRADIENT]

        if objtype == "gradient_object":
            return gradient_object
        else:
            return actual_gradient

    @staticmethod
    def reset_psr(obj):
        obj.SetMl(c4d.Matrix())

    @staticmethod
    def assign_atmosphere_texture_tag(tag_type, material, obj, name):
        has_texture_tag = False
        tags = obj.GetTags()
        tag_list = []

        if material is not None:
            for tag in tags:
                tag_list.append(tag)
                if tag.GetType() == tag_type and tag.GetName() == name:
                    # it's a texture tag and its the atmosphere texture tag
                    has_texture_tag = True

                    material_link = tag[c4d.TEXTURETAG_MATERIAL]
                    if material_link is None:
                        # tag already exists but the link is broken, lets fix it
                        tag[c4d.TEXTURETAG_MATERIAL] = material
                        if name == "Atmosphere Background Texture":
                            tag[c4d.TEXTURETAG_PROJECTION] = c4d.TEXTURETAG_PROJECTION_FRONTAL
                        else:
                            tag[c4d.TEXTURETAG_PROJECTION] = c4d.TEXTURETAG_PROJECTION_UVW

            # we know the material exists, if no texture tag named atmosphere texture, make it
            if not has_texture_tag:
                tag = c4d.BaseTag(c4d.Ttexture)
                tag[c4d.TEXTURETAG_MATERIAL] = material
                tag.SetName(name)
                if len(tag_list) > 0:
                    obj.InsertTag(tag, tag_list[-1])
                else:
                    obj.InsertTag(tag)
                has_texture_tag = True
                
                if name == "Atmosphere Background Texture":
                    tag[c4d.TEXTURETAG_PROJECTION] = c4d.TEXTURETAG_PROJECTION_FRONTAL
                else:
                    tag[c4d.TEXTURETAG_PROJECTION] = c4d.TEXTURETAG_PROJECTION_UVW
        else:
            # the material does not exist. check for the plugin texture tag and remove it if its there
            for tag in tags:
                if tag.GetType() == tag_type and tag.GetName() == name:
                    tag.Remove()
                    has_texture_tag = False

        c4d.EventAdd()
        return has_texture_tag

    @staticmethod
    def check_for_tag_by_name(obj, name, tag_type=None):
        tags = obj.GetTags()
        has_tag = False
        tag_names = []
        tag_types = []

        for tag in tags:
            tag_names.append(tag.GetName())
            tag_types.append(tag.GetType())

        if tag_type is not None:
            if tag_type in tag_types and name in tag_names:
                has_tag = True
        else:
            if name in tag_names:
                has_tag = True

        return has_tag

    @staticmethod
    def create_background_object(name="Background"):
        bg_object = c4d.BaseObject(c4d.Obackground)
        bg_object.SetName(name)
        CRUtils.get_activedoc().InsertObject(bg_object)
        return bg_object


class Atmosphere(plugins.ObjectData):

    def __init__(self):
        self.SetOptimizeCache(False)
        self.black = c4d.Vector(0, 0, 0)
        self.white = c4d.Vector(1, 1, 1)
        self.atmosphere_material_created = False
        self.bg_material_created = False
        self.has_camera = False
        self.has_active_objects = False
        self.active_obj_list = []
        self.has_background = False
        self.has_controls = False
        self.control_start = False
        self.control_end = False
        self.camera = None
        self.background = None

    def Init(self, node):

        # Set up checkboxes
        self.InitAttr(host=node, type=bool, id=[c4d.USE_CAMERA_SPACE])
        self.InitAttr(host=node, type=bool, id=[c4d.BOOL_BG_UNLINK])
        self.InitAttr(host=node, type=float, id=[c4d.ATMOSPHERE_STRENGTH])
        self.InitAttr(host=node, type=float, id=[c4d.ATMOSPHERE_DISTANCE])
        node[c4d.USE_CAMERA_SPACE] = True
        node[c4d.BOOL_BG_UNLINK] = True
        node[c4d.ATMOSPHERE_STRENGTH] = 100
        node[c4d.ATMOSPHERE_DISTANCE] = 0

        # set up the color gradients
        gradient = c4d.Gradient()
        gradient.InsertKnot(col=self.black, pos=0)
        gradient.InsertKnot(col=self.white, pos=1)

        alpha_gradient = c4d.Gradient()
        alpha_gradient.InsertKnot(col=self.white, pos=0)
        alpha_gradient.InsertKnot(col=self.white, pos=1)

        data = node.GetDataInstance()
        data.SetData(c4d.ATMOSPHERE_COLOR, gradient)
        data.SetData(c4d.BG_GRAD_BG_COLOR, gradient)
        data.SetData(c4d.ATMOSPHERE_ALPHA_GRAD, alpha_gradient)

        # check for an active object(s) and store it if so
        active_objects = CRUtils.get_active_objects()
        if len(active_objects) > 0:
            self.has_active_objects = True
            self.active_obj_list = active_objects

        return True

    def add_atmosphere_material_to_objects(self):
        atmosphere_mat = self.get_atmosphere_material()
        atmosphere_bg_mat = self.get_atmosphere_material("Atmosphere Background")
        all_objects = CRUtils.get_all_objects()
        ignored_objects = []

        for o in all_objects:
            tags = o.GetTags()
            has_texture = False
            has_atmosphere_texture = False
            is_atmosphere_background = False
            if len(tags) > 0:
                for tag in tags:
                    if tag.GetType() == c4d.BaseTag(c4d.Ttexture).GetType():
                        has_texture = True
                        if tag[c4d.TEXTURETAG_MATERIAL] == atmosphere_mat:
                            has_atmosphere_texture = True
                        if tag[c4d.TEXTURETAG_MATERIAL] == atmosphere_bg_mat:
                            is_atmosphere_background = True

            if has_texture:
                if has_atmosphere_texture is False and is_atmosphere_background is False:
                    assign_tag = CRUtils.assign_atmosphere_texture_tag(c4d.BaseTag(c4d.Ttexture).GetType(),
                                                                       atmosphere_mat, o, "Atmosphere Texture")

        return True

    def add_material_override(self, active_renderdata=None):
        if active_renderdata is None:
            active_renderdata = CRUtils.get_activedoc().GetActiveRenderData()
        # get the atmosphere material
        atmosphere_material = self.get_atmosphere_material("Atmosphere")
        bg_atmosphere_material = self.get_atmosphere_material("Atmosphere Background")
        print("get bh material::: ", bg_atmosphere_material)

        active_renderdata[c4d.RDATA_MATERIAL_OVERRIDE] = True
        active_renderdata[c4d.RDATA_MATERIAL_OVERRIDE_LINK] = atmosphere_material
        active_renderdata[c4d.RDATA_MATERIAL_OVERRIDE_ALPHA] = False

        material_exclude_list = active_renderdata[c4d.RDATA_MATERIAL_OVERRIDE_EXCLUSION_LIST]

        if material_exclude_list.GetObjectCount() == 0:
            material_exclude_list.InsertObject(bg_atmosphere_material, 0)
            active_renderdata[c4d.RDATA_MATERIAL_OVERRIDE_EXCLUSION_LIST] = material_exclude_list
            c4d.EventAdd()

        return True

    def add_renderdata_preset(self):
        active_renderdata = CRUtils.get_activedoc().GetActiveRenderData()
        rd = CRUtils.get_activedoc().GetFirstRenderData()

        while rd is not None:
            if rd.GetName() == "Atmosphere":
                return rd
            else:
                rd = rd.GetNext()

        if rd is None:
            # we got through the list and its not there. lets make it.
            atmosphere_rd = c4d.documents.RenderData()
            atmosphere_rd.SetName("Atmosphere")
            atmosphere_rd[c4d.RDATA_ANTIALIASING] = c4d.RDATA_ANTIALIASING_NONE
            atmosphere_rd[c4d.RDATA_MULTIPASS_ENABLE] = False
            atmosphere_rd[c4d.RDATA_RENDERENGINE] = active_renderdata[c4d.RDATA_RENDERENGINE]
            atmosphere_rd[c4d.RDATA_XRES_VIRTUAL] = active_renderdata[c4d.RDATA_XRES_VIRTUAL]
            atmosphere_rd[c4d.RDATA_YRES_VIRTUAL] = active_renderdata[c4d.RDATA_YRES_VIRTUAL]
            atmosphere_rd[c4d.RDATA_LOCKRATIO] = active_renderdata[c4d.RDATA_LOCKRATIO]
            atmosphere_rd[c4d.RDATA_PIXELRESOLUTION_VIRTUAL] = active_renderdata[c4d.RDATA_PIXELRESOLUTION_VIRTUAL]
            atmosphere_rd[c4d.RDATA_RENDERREGION] = active_renderdata[c4d.RDATA_RENDERREGION]
            atmosphere_rd[c4d.RDATA_FILMASPECT] = active_renderdata[c4d.RDATA_FILMASPECT]
            atmosphere_rd[c4d.RDATA_PIXELASPECT] = active_renderdata[c4d.RDATA_PIXELASPECT]
            atmosphere_rd[c4d.RDATA_FRAMERATE] = active_renderdata[c4d.RDATA_FRAMERATE]
            atmosphere_rd[c4d.RDATA_FRAMESEQUENCE] = active_renderdata[c4d.RDATA_FRAMESEQUENCE]
            atmosphere_rd[c4d.RDATA_FRAMEFROM] = active_renderdata[c4d.RDATA_FRAMEFROM]
            atmosphere_rd[c4d.RDATA_FRAMETO] = active_renderdata[c4d.RDATA_FRAMETO]
            atmosphere_rd[c4d.RDATA_FRAMESTEP] = active_renderdata[c4d.RDATA_FRAMESTEP]
            atmosphere_rd[c4d.RDATA_FIELD] = active_renderdata[c4d.RDATA_FIELD]
            atmosphere_rd[c4d.RDATA_HELPTEXT] = active_renderdata[c4d.RDATA_HELPTEXT]
            atmosphere_rd[c4d.RDATA_SAVEIMAGE] = active_renderdata[c4d.RDATA_SAVEIMAGE]
            atmosphere_rd[c4d.RDATA_PATH] = active_renderdata[c4d.RDATA_PATH]
            atmosphere_rd[c4d.RDATA_FORMAT] = active_renderdata[c4d.RDATA_FORMAT]
            atmosphere_rd[c4d.RDATA_FORMATDEPTH] = active_renderdata[c4d.RDATA_FORMATDEPTH]
            atmosphere_rd[c4d.RDATA_NAMEFORMAT] = active_renderdata[c4d.RDATA_NAMEFORMAT]
            atmosphere_rd[c4d.RDATA_IMAGECOLORPROFILE] = active_renderdata[c4d.RDATA_IMAGECOLORPROFILE]
            atmosphere_rd[c4d.RDATA_ALPHACHANNEL] = active_renderdata[c4d.RDATA_ALPHACHANNEL]
            atmosphere_rd[c4d.RDATA_STRAIGHTALPHA] = active_renderdata[c4d.RDATA_STRAIGHTALPHA]
            atmosphere_rd[c4d.RDATA_SEPARATEALPHA] = active_renderdata[c4d.RDATA_SEPARATEALPHA]
            atmosphere_rd[c4d.RDATA_TRUECOLORDITHERING] = active_renderdata[c4d.RDATA_TRUECOLORDITHERING]
            atmosphere_rd[c4d.RDATA_INCLUDESOUND] = active_renderdata[c4d.RDATA_INCLUDESOUND]
            atmosphere_rd[c4d.RDATA_PROJECTFILE] = active_renderdata[c4d.RDATA_PROJECTFILE]
            atmosphere_rd[c4d.RDATA_PROJECTFILETYPE] = active_renderdata[c4d.RDATA_PROJECTFILETYPE]
            atmosphere_rd[c4d.RDATA_PROJECTFILELOCAL] = active_renderdata[c4d.RDATA_PROJECTFILELOCAL]
            atmosphere_rd[c4d.RDATA_PROJECTFILEMARKER] = active_renderdata[c4d.RDATA_PROJECTFILEMARKER]
            atmosphere_rd[c4d.RDATA_PROJECTFILEDATA] = active_renderdata[c4d.RDATA_PROJECTFILEDATA]
            atmosphere_rd[c4d.RDATA_PROJECTFILEFBX] = active_renderdata[c4d.RDATA_PROJECTFILEFBX]

            if C4DVNUM > 16:
                # this version of cinema is higher than 16 so it hsa material override
                self.add_material_override(atmosphere_rd)

            CRUtils.get_activedoc().InsertRenderDataLast(atmosphere_rd)
            CRUtils.get_activedoc().SetActiveRenderData(atmosphere_rd)

        return True

    def atmosphere_background(self, op):
        scene_objects = CRUtils.get_all_objects()

        if scene_objects is None:
            # the hell you trying to pull here? You got no objects yo!
            self.has_background = False
            return False

        if scene_objects is not None:
            if self.has_active_objects:
                for obj in self.active_obj_list:
                    if obj.GetType() == c4d.BaseObject(c4d.Obackground).GetType():
                        op[c4d.BG_OBJECT_LINK] = obj
                        self.has_background = True
                        self.camera = op[c4d.BG_OBJECT_LINK]
                        return True

            for o in scene_objects:
                if o.GetType() == c4d.BaseObject(c4d.Obackground).GetType():
                    self.has_background = True
                    return True

        if not self.has_background:
            background_object = c4d.BaseObject(c4d.Obackground)
            background_object.SetName("Atmosphere Background")
            doc = CRUtils.get_activedoc()
            doc.InsertObject(background_object)
            op[c4d.BG_OBJECT_LINK] = background_object
            self.has_background = True
            self.background = background_object
            return True

        # if we got this far, we are fucked
        return False

    def atmosphere_camera(self, op):
        scene_objects = CRUtils.get_all_objects()

        if scene_objects is None:
            # the hell you trying to pull here? You got no objects yo!
            self.has_camera = False
            return False

        object_types = CRUtils.get_all_objects_types()
        camera_list = []

        for i in object_types:
            if i == c4d.BaseObject(c4d.Ocamera).GetType():
                camera_list.append(i)

        # check for a camera. if there is one, and it is selected, set it as the link.
        if self.has_active_objects:
            for o in self.active_obj_list:
                if o.GetType() == c4d.BaseObject(c4d.Ocamera).GetType():
                    op[c4d.CAMERA_LINK] = o
                    self.has_camera = True
                    self.camera = op[c4d.CAMERA_LINK]
                    self.distance_null(op, CRUtils.get_activedoc())
                    return True

        for obj in scene_objects:
            if obj.GetType() == c4d.BaseObject(c4d.Ocamera).GetType():
                self.has_camera = True

                # there is only 1 camera in the scene so set it as the atmosphere camera.
                if len(camera_list) == 1:
                    op[c4d.CAMERA_LINK] = obj
                    self.camera = obj

                return True

        # if there is no camera in the scene at all, make one and set it as the link
        if not self.has_camera:
            camera = c4d.BaseObject(c4d.Ocamera)
            doc = CRUtils.get_activedoc()
            doc.InsertObject(camera)

            # set the atmosphere axis to match the camera axis
            op[c4d.CAMERA_LINK] = camera
            self.has_camera = True
            self.camera = op[c4d.CAMERA_LINK]
            self.distance_null(op, CRUtils.get_activedoc())
            return True

        # if we got this far, we are fucked
        return False

    def check_atmosphere_material(self):
        # check the material manager
        atmosphere_material = self.get_atmosphere_material("Atmosphere")

        if atmosphere_material is False or atmosphere_material is None:
            self.atmosphere_material_created = False
            return False
        else:
            self.atmosphere_material_created = True
            return True

    def check_background_material(self):
        atmosphere_material = self.get_atmosphere_material("Atmosphere Background")

        if atmosphere_material is False or atmosphere_material is None:
            return False
        else:
            return True

    def create_atmosphere_control_null(self, node):
        doc = CRUtils.get_activedoc()
        start_check = CRUtils.get_object_by_name("Atmosphere Start")
        end_check = CRUtils.get_object_by_name("Atmosphere End")

        if not start_check:
            atmosphere_start_null = c4d.BaseObject(c4d.Onull)
            atmosphere_start_null.SetName("Atmosphere Start")
            atmosphere_start_null[c4d.NULLOBJECT_DISPLAY] = c4d.NULLOBJECT_DISPLAY_STAR
            atmosphere_start_null[c4d.NULLOBJECT_RADIUS] = 300
            atmosphere_start_null[c4d.NULLOBJECT_ORIENTATION] = c4d.NULLOBJECT_ORIENTATION_XZ
            atmosphere_start_null[c4d.NULLOBJECT_ICONCOL] = True
            atmosphere_start_null[c4d.ID_BASEOBJECT_USECOLOR] = c4d.ID_BASEOBJECT_USECOLOR_ALWAYS
            atmosphere_start_null[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(1, 0, 0)
            self.control_start = atmosphere_start_null

            if node[c4d.CAMERA_LINK]:
                camera = node[c4d.CAMERA_LINK]
                camera_matrix = camera.GetMg()
                atmosphere_start_null.SetMg(camera_matrix)

            doc.InsertObject(atmosphere_start_null, parent=node, checknames=True)

        if not end_check:
            atmosphere_end_null = c4d.BaseObject(c4d.Onull)
            atmosphere_end_null.SetName("Atmosphere End")
            atmosphere_end_null[c4d.NULLOBJECT_DISPLAY] = c4d.NULLOBJECT_DISPLAY_STAR
            atmosphere_end_null[c4d.NULLOBJECT_RADIUS] = 300
            atmosphere_end_null[c4d.NULLOBJECT_ORIENTATION] = c4d.NULLOBJECT_ORIENTATION_XZ
            atmosphere_end_null[c4d.NULLOBJECT_ICONCOL] = True
            atmosphere_end_null[c4d.ID_BASEOBJECT_USECOLOR] = c4d.ID_BASEOBJECT_USECOLOR_ALWAYS
            atmosphere_end_null[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(0, 1, 0)
            doc.InsertObject(atmosphere_end_null, parent=node, checknames=True)
            self.control_end = atmosphere_end_null

            if node[c4d.CAMERA_LINK]:
                camera = node[c4d.CAMERA_LINK]
                camera_rot = camera.GetAbsRot()
                atmosphere_end_null.SetAbsRot(camera_rot)

        # shut off the camera space boole
        if node[c4d.USE_CAMERA_SPACE] is True or node[c4d.USE_CAMERA_SPACE] == 1:
            node[c4d.USE_CAMERA_SPACE] = False

        # set the controls variable
        self.has_controls = True

        c4d.EventAdd()

    def create_atmosphere_material(self, op):
        doc = CRUtils.get_activedoc()

        mat = c4d.BaseMaterial(c4d.Mmaterial)

        # set the name
        mat.SetName("Atmosphere")

        # shut off the color and reflectance
        mat[c4d.MATERIAL_USE_COLOR] = 0
        mat[c4d.MATERIAL_USE_REFLECTION] = 0

        # turn on the luminance channel
        mat[c4d.MATERIAL_USE_LUMINANCE] = True
        mat[c4d.MATERIAL_USE_ALPHA] = True

        # luminance channel
        shd_color = c4d.BaseList2D(c4d.Xgradient)
        shd_color[c4d.SLA_GRADIENT_TYPE] = c4d.SLA_GRADIENT_TYPE_3D_LINEAR
        shd_color[c4d.SLA_GRADIENT_CYCLE] = False
        shd_color[c4d.SLA_GRADIENT_SPACE] = c4d.SLA_GRADIENT_SPACE_WORLD
        mat[c4d.MATERIAL_LUMINANCE_SHADER] = shd_color
        shd_color[c4d.SLA_GRADIENT_GRADIENT] = op[c4d.ATMOSPHERE_COLOR]
        mat.InsertShader(shd_color)

        # alpha channel
        shd_alpha = c4d.BaseList2D(c4d.Xgradient)
        shd_alpha[c4d.SLA_GRADIENT_TYPE] = c4d.SLA_GRADIENT_TYPE_3D_LINEAR
        shd_alpha[c4d.SLA_GRADIENT_CYCLE] = False
        shd_alpha[c4d.SLA_GRADIENT_SPACE] = c4d.SLA_GRADIENT_SPACE_WORLD
        mat[c4d.MATERIAL_ALPHA_SHADER] = shd_alpha
        shd_alpha[c4d.SLA_GRADIENT_GRADIENT] = op[c4d.ATMOSPHERE_ALPHA_GRAD]
        mat.InsertShader(shd_alpha)

        # update and insert the material
        mat.Message(c4d.MSG_UPDATE)
        mat.Update(True, True)
        doc.InsertMaterial(mat)

        self.atmosphere_material_created = True

        c4d.EventAdd()

        return True

    def create_background_material(self, data):
        doc = CRUtils.get_activedoc()

        mat = c4d.BaseMaterial(c4d.Mmaterial)
        mat.SetName("Atmosphere Background")

        # shut off the color and reflectance
        mat[c4d.MATERIAL_USE_COLOR] = 0
        mat[c4d.MATERIAL_USE_REFLECTION] = 0

        # turn on the luminance channel
        mat[c4d.MATERIAL_USE_LUMINANCE] = True
        mat[c4d.MATERIAL_USE_ALPHA] = True

        # luminance channel
        shd_color = c4d.BaseList2D(c4d.Xgradient)
        shd_color[c4d.SLA_GRADIENT_TYPE] = c4d.SLA_GRADIENT_TYPE_2D_V
        mat[c4d.MATERIAL_LUMINANCE_SHADER] = shd_color
        shd_color[c4d.SLA_GRADIENT_GRADIENT] = data[c4d.ATMOSPHERE_COLOR]
        mat.InsertShader(shd_color)

        # alpha channel
        shd_alpha = c4d.BaseList2D(c4d.Xgradient)
        shd_alpha[c4d.SLA_GRADIENT_TYPE] = c4d.SLA_GRADIENT_TYPE_2D_V
        mat[c4d.MATERIAL_ALPHA_SHADER] = shd_alpha
        shd_alpha[c4d.SLA_GRADIENT_GRADIENT] = data[c4d.ATMOSPHERE_ALPHA_GRAD]
        mat.InsertShader(shd_alpha)

        # update and insert the material
        mat.Message(c4d.MSG_UPDATE)
        mat.Update(True, True)
        doc.InsertMaterial(mat)

        self.bg_material_created = True

        c4d.EventAdd()
        return True

    def distance_null(self, op, doc):
        # check to see if there is a camera in the slot. IF SO, check for the
        # camera distance null. if it doesnt exist, make it and add it as a child of the camera in the slot
        if op[c4d.CAMERA_LINK]:
            atmosphere_camera = op[c4d.CAMERA_LINK]
            self.camera = op[c4d.CAMERA_LINK]
            distance_null = CRUtils.get_object_by_name("Atmosphere_Distance_Controller")

            # set up the distance null
            if distance_null is not None:
                # there is one, lets check to see if its the child of the linked camera
                has_parent = distance_null.GetUp()

                if has_parent:
                    if has_parent != atmosphere_camera:
                        # move the distance null to THIS camera
                        doc.InsertObject(distance_null, atmosphere_camera)
                else:
                    # this should never happen but lets make sure anyway
                    doc.InsertObject(distance_null, atmosphere_camera)
            else:
                # the distance null does not exist, make it,
                distance_null = c4d.BaseObject(c4d.Onull)
                distance_null.SetName("Atmosphere_Distance_Controller")

                # hide the distance null from the user. hahahahahahaha
                distance_null.ChangeNBit(c4d.NBIT_OHIDE, True)

                # make it a child of the camera
                doc.InsertObject(distance_null, atmosphere_camera)

                # reset the PSR so it's inline with the camera
                CRUtils.reset_psr(distance_null)
        return True

    def get_atmosphere_material(self, name="Atmosphere"):
        mat = CRUtils.get_activedoc().SearchMaterial(name)

        if mat is None:
            self.atmosphere_material_created = False
            return False
        else:
            self.atmosphere_material_created = True
            return mat

    def GetVirtualObjects(self, op, hh):
        child_one = op.GetDown()

        if child_one:
            child_two = child_one.GetNext()

        start_control = CRUtils.get_object_by_name("Atmosphere Start")
        end_control = CRUtils.get_object_by_name("Atmosphere End")

        if start_control is not None and end_control is not None:
            dirty = op.CheckCache(hh) or op.IsDirty(c4d.DIRTY_DATA) or op.IsDirty(c4d.DIRTYFLAGS_MATRIX) or \
                    op.IsDirty(c4d.DIRTYFLAGS_CHILDREN) or start_control.IsDirty(c4d.DIRTYFLAGS_MATRIX) or \
                    end_control(c4d.DIRTYFLAGS_MATRIX)
        else:
            dirty = op.CheckCache(hh) or op.IsDirty(c4d.DIRTY_DATA) or op.IsDirty(c4d.DIRTYFLAGS_MATRIX) or \
                    op.IsDirty(c4d.DIRTYFLAGS_CHILDREN)

        if dirty is False: return op.GetCache(hh)

        # look for null controls
        start_check = CRUtils.get_object_by_name("Atmosphere Start")
        end_check = CRUtils.get_object_by_name("Atmosphere End")

        if start_check is not None:
            self.control_start = start_check

        if end_check is not None:
            self.control_end = end_check

        if self.control_start and self.control_end:
            self.has_controls = True

        # camera stuff
        if op[c4d.CAMERA_LINK] is None:
            self.atmosphere_camera(op)
        else:
            # camera is in slot, check for the distance null
            self.camera = op[c4d.CAMERA_LINK]
            dn = CRUtils.get_object_by_name("Atmosphere_Distance_Controller")
            if dn is None:
                self.distance_null(op, CRUtils.get_activedoc())

        # check for a background object
        if op[c4d.BG_OBJECT_LINK] is None:
            # currently background is not set. Fetch a BG object
            self.atmosphere_background(op)
        else:
            self.background = op[c4d.BG_OBJECT_LINK]

        # material for the atmosphere object
        mat_check = self.check_atmosphere_material()
        bg_mat_check = self.check_background_material()

        if not mat_check:
            self.create_atmosphere_material(op)
        atmosphere_mat = self.get_atmosphere_material("Atmosphere")

        if not bg_mat_check:
            self.create_background_material(op)
            if C4DVNUM < 17:
                self.add_atmosphere_material_to_objects()
            else:
                self.add_material_override()

        bg_material = self.get_atmosphere_material("Atmosphere Background")

        # check for the atmosphere texture tag
        texture_tag_check = CRUtils.check_for_tag_by_name(op, "Atmosphere Texture", c4d.BaseTag(c4d.Ttexture).GetType())
        if not texture_tag_check:
            # tag does not exists
            if atmosphere_mat is not False:
                # atmosphere material does exist so we can assign a tag and link the material
                assign_tag = CRUtils.assign_atmosphere_texture_tag(c4d.BaseTag(c4d.Ttexture).GetType(),
                                                                   atmosphere_mat, op, "Atmosphere Texture")

        if self.background is not None:
            bg_texture_tag_check = CRUtils.check_for_tag_by_name(self.background, "Atmosphere Background Texture",
                                                                 c4d.BaseTag(c4d.Ttexture).GetType())
            if not bg_texture_tag_check:
                # tag does not exist
                if bg_material is not False:
                    assign_tag = CRUtils.assign_atmosphere_texture_tag(c4d.BaseTag(c4d.Ttexture).GetType(), bg_material,
                                                                       self.background, "Atmosphere Background Texture")

        # lets start working with the gradients
        color_gradient = op[c4d.ATMOSPHERE_COLOR]
        alpha_gradient = op[c4d.ATMOSPHERE_ALPHA_GRAD]
        bg_color_grad = op[c4d.BG_GRAD_BG_COLOR]
        atmosphere_grad = CRUtils.get_material_gradient(atmosphere_mat, "luminance", "gradient_object")
        atmosphere_alpha_grad = CRUtils.get_material_gradient(atmosphere_mat, "alpha", "gradient_object")
        atmosphere_bg_luma_grad = CRUtils.get_material_gradient(bg_material, "luminance", "gradient_object")
        atmosphere_bg_alpha_grad = CRUtils.get_material_gradient(bg_material, "alpha", "gradient_object")

        if atmosphere_grad != color_gradient:
            atmosphere_grad[c4d.SLA_GRADIENT_GRADIENT] = color_gradient

        if atmosphere_alpha_grad != alpha_gradient:
            # alpha channels for both materials
            atmosphere_alpha_grad[c4d.SLA_GRADIENT_GRADIENT] = alpha_gradient
            # atmosphere_bg_alpha_grad[c4d.SLA_GRADIENT_GRADIENT] = alpha_gradient

        # get the Unlink BG bool
        unlink_bg = op[c4d.BOOL_BG_UNLINK]
        if unlink_bg is False or unlink_bg == 0:
            # If Unlink Background Color is FALSE all of the gradient chips on the background will match the
            # last color chip on the Atmosphere color so that the atmosphere gradient blends into the background
            self.sync_2d_gradient(op)

        if bg_color_grad != atmosphere_bg_luma_grad:
            atmosphere_bg_luma_grad[c4d.SLA_GRADIENT_GRADIENT] = bg_color_grad

        # get the camera space bool so we know wtf we are doing
        use_camera_space = op[c4d.USE_CAMERA_SPACE]
        if self.camera is not None:
            if use_camera_space is True or use_camera_space == 1:
                # we are using the camera for start and distance for end
                # get the distance null
                distance_null = CRUtils.get_object_by_name("Atmosphere_Distance_Controller")

                if distance_null:
                    distance_null[c4d.ID_BASEOBJECT_REL_POSITION, c4d.VECTOR_Z] = op[c4d.ATMOSPHERE_DISTANCE]
                    distance_m = distance_null.GetMg().off
                    camera_m = self.camera.GetMg().off
                    self.sync_3d_gradient(atmosphere_grad, camera_m, distance_m)
                    self.sync_3d_gradient(atmosphere_alpha_grad, camera_m, distance_m)
            else:
                # we are using control nodes
                if self.has_controls:
                    # we have null controls, link them up
                    control_start_pos = self.control_start.GetMg().off
                    control_end_pos = self.control_end.GetMg().off

                    if self.control_end.IsDirty(c4d.DIRTYFLAGS_MATRIX):
                        control_end_pos = self.control_end.GetMg().off
                    if self.control_start.IsDirty(c4d.DIRTYFLAGS_MATRIX):
                        control_start_pos = self.control_start.GetMg().off

                    self.sync_3d_gradient(atmosphere_grad, control_start_pos, control_end_pos)
                    self.sync_3d_gradient(atmosphere_alpha_grad, control_start_pos, control_end_pos)

        # alpha strength stuff
        """
        strength = op[c4d.ATMOSPHERE_STRENGTH]
        gradient_list = list(atmosphere_alpha_grad, atmosphere_bg_alpha_grad)
        materials_list = list(atmosphere_mat, bg_material)
        self.sync_alpha_strength(op, gradient_list, materials_list, strength)
        """

        return c4d.BaseObject(c4d.Onull)

    def Message(self, node, type, data):
        if type == c4d.MSG_DESCRIPTION_COMMAND:
            if data['id'][0].id == c4d.CREATE_GRAD_CONTROLS:
                # we can now add two nulls to the scene for use as controls.
                # disable the gradient if so?
                self.create_atmosphere_control_null(node)

                return True

            if data['id'][0].id == c4d.CREATE_DEPTH_MATTE_RS:
                # we can setup the render settings and stuff for the depth matte
                self.add_renderdata_preset()
                return True

            if data['id'][0].id == c4d.ADD_DEPTH_MATERIAL:
                if C4DVNUM < 17:
                    self.add_atmosphere_material_to_objects()
                else:
                    self.add_material_override()
                return True

            if data['id'][0].id == c4d.REMOVE_DEPTH_MATERIAL:
                self.remove_atmosphere_material()
                return True

        return True

    def remove_atmosphere_material(self):
        atmosphere_mat = self.get_atmosphere_material()
        all_objects = CRUtils.get_all_objects()

        for o in all_objects:
            tags = o.GetTags()
            if len(tags) > 0:
                for tag in tags:
                    if tag.GetType() == c4d.BaseTag(c4d.Ttexture).GetType():
                        if tag[c4d.TEXTURETAG_MATERIAL] == atmosphere_mat:
                            tag.Remove()

        return True

    @staticmethod
    def sync_2d_gradient(op):
        atmosphere_color_grad = op[c4d.ATMOSPHERE_COLOR]
        background_color_grad = op[c4d.BG_GRAD_BG_COLOR]
        knots_list_at_color = list(range(0, atmosphere_color_grad.GetKnotCount()))
        knots_list_bg_color = list(range(0, background_color_grad.GetKnotCount()))

        new_color = None

        for i in knots_list_at_color:
            if atmosphere_color_grad.GetKnot(i)['pos'] == 0:
                new_color = atmosphere_color_grad.GetKnot(i)['col']

        for i in knots_list_bg_color:
            bias = background_color_grad.GetKnot(i)['bias']
            pos = background_color_grad.GetKnot(i)['pos']
            color = new_color
            brightness = background_color_grad.GetKnot(i)['brightness']

            background_color_grad.SetKnot(i, color, brightness, pos, bias)

        d = op.GetDataInstance()
        d.SetData(c4d.BG_GRAD_BG_COLOR, background_color_grad)

        return True

    @staticmethod
    def sync_3d_gradient(gradient, start_pos, end_pos):
        gradient[c4d.SLA_GRADIENT_END] = c4d.Vector(start_pos.x, start_pos.y, start_pos.z)
        gradient[c4d.SLA_GRADIENT_START] = c4d.Vector(end_pos.x, end_pos.y, end_pos.z)

        return True

    @staticmethod
    def sync_alpha_strength(op, gradient_list, material_list, strength):
        # alpha channels
        for m in material_list:
            alpha_channel = m[c4d.MATERIAL_USE_ALPHA]
            # what the fuck is the strength?

        return True

if __name__ == "__main__":
    bmp = c4d.bitmaps.BaseBitmap()
    dir, file = os.path.split(__file__)
    fn = os.path.join(dir, "res", "icon.tif")
    bmp.InitWith(fn)
    result = plugins.RegisterObjectPlugin(id=PLUGIN_ID, str="Atmosphere",
                                          g=Atmosphere,
                                          description="Oatmosphere",
                                          info=c4d.OBJECT_GENERATOR | c4d.OBJECT_HIERARCHYMODIFIER | c4d.OBJECT_INPUT | c4d.OBJECT_MODIFIER,
                                          icon=bmp)
    if result:
        print("****************************** SYMBOLIC LINK")
        print("Atmosphere v{0} copyright {1} Eyedesyn http:www.eyedesn.com, written by Charles Rowland http:www.wickedsword.com".format(VERSION, YEAR))
