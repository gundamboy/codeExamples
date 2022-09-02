'''
Hindsight v1.0

Copyright: Charles Rowland (www.wickedsword.com)
Written for CINEMA 4D R13-19

Name-US: Hindsight

Description-US: A plugin for creating and recalling viewport filter presets to
enable fast switching between filter options in any viewport.

Creation Date: 25/5/2015
'''
import c4d, datetime, time, sys, os, subprocess, itertools, webbrowser, re, string, random, collections, shutil, json
from c4d import documents, gui, plugins, bitmaps, storage as st
from datetime import datetime

# salt is used to mask the id's of c4d
salt = 666

prefpath = st.GeGetC4DPath(c4d.C4D_PATH_PREFS)
hindsight_dir = os.path.join(prefpath, "hindsight")
hindsight_pref_file_name = "presets.hnds"
hindsightfile = os.path.join(hindsight_dir,hindsight_pref_file_name)

# be sure to use a unique ID obtained from www.plugincafe.com
__plugin_id__ = 1056002
__version__ = "1.0"
__plugin_title__ = "Hindsight - Beta 1.0"

filters_r13 = {3001 : "Null", 3002 : "Polygon", 3003 : "Spline", 3004 : "Generator", 3005 : "HyperNURBS", 3007 : "Deformer", 3008 : "Camera", 3009 : "Light", 3010 : "Environment", 3011 : "Particle", 3012 : "Other", 3014 : "Grid", 3015 : "Horizon", 3016 : "World Axis", 3017 : "Bounding-Box", 3018 : "HUD", 3019 : "SDS Mesh", 3020 : "Component Highlighting", 3021 : "Multi-Select Axes", 3022 : "Axis", 3023 : "Axis Bands", 3024 : "SDS Cage", 3025 : "N-gon Lines", 3026 : "Highlight Handles", 3027 : "Joint", 3028 : "Ghosting", 3029 : "Axis Guidelines"}
filters_r14 = {3001 : "Null", 3002 : "Polygon", 3003 : "Spline", 3004 : "Generator", 3005 : "HyperNURBS", 3007 : "Deformer", 3008 : "Camera", 3009 : "Light", 3010 : "Environment", 3011 : "Particle", 3012 : "Other", 3014 : "Grid", 3015 : "Horizon", 3016 : "World Axis", 3017 : "Bounding Box", 3018 : "HUD", 3019 : "SDS Mesh", 3020 : "Component Highlighting", 3021 : "Multi-Select Axes", 3022 : "Axis", 3023 : "Axis Bands", 3024 : "SDS Cage", 3025 : "N-gon Lines", 3026 : "Highlight Handles", 3027 : "Joint", 3028 : "Ghosting", 3029 : "Guides", 3030 : "Gradient", 3031 : "Object Highlighting", 3032 : "Navigation Cross"}
filters_r15 = {3001 : "Null", 3002 : "Polygon", 3003 : "Spline", 3004 : "Generator", 3005 : "HyperNURBS", 3007 : "Deformer", 3008 : "Camera", 3009 : "Light", 3010 : "Environment", 3011 : "Particle", 3012 : "Other", 3014 : "Grid", 3015 : "Horizon", 3016 : "World Axis", 3017 : "Bounding Box", 3018 : "HUD", 3019 : "SDS Mesh", 3020 : "Component Highlighting", 3021 : "Multi-Select Axes", 3022 : "Axis", 3023 : "Axis Bands", 3024 : "SDS Cage", 3025 : "N-gon Lines", 3026 : "Highlight Handles", 3027 : "Joint", 3028 : "Ghosting", 3029 : "Guides", 3030 : "Gradient", 3031 : "Object Highlighting", 3032 : "Navigation Cross"}
filters_r16 = {3001 : "Null", 3002 : "Polygon", 3003 : "Spline", 3004 : "Generator", 3005 : "Subdivision Surface", 3007 : "Deformer", 3008 : "Camera", 3009 : "Light", 3010 : "Environment", 3011 : "Particle", 3012 : "Other", 3014 : "Grid", 3015 : "Horizon", 3016 : "World Axis", 3017 : "Bounding-Box", 3018 : "HUD", 3019 : "SDS Mesh", 3020 : "Component Highlighting", 3021 : "Multi-Select Axes", 3022 : "Axis", 3023 : "Axis Bands", 3024 : "SDS Cage", 3025 : "N-gon Lines", 3026 : "Highlight Handles", 3027 : "Joint", 3028 : "Ghosting", 3029 : "Guides", 3030 : "Gradient", 3031 : "Object Highlighting", 3032 : "Navigation Cross", 3033 : "Base Grid"}
filters_r17 = {3001 : "Null", 3002 : "Polygon", 3003 : "Spline", 3004 : "Generator", 3005 : "Subdivision Surface", 3007 : "Deformer", 3008 : "Camera", 3009 : "Light", 3010 : "Environment", 3011 : "Particle", 3012 : "Other", 3014 : "Grid", 3015 : "Horizon", 3016 : "World Axis", 3017 : "Bounding-Box", 3018 : "HUD", 3019 : "SDS Mesh", 3020 : "Component Highlighting", 3021 : "Multi-Select Axes", 3022 : "Axis", 3023 : "Axis Bands", 3024 : "SDS Cage", 3025 : "N-gon Lines", 3026 : "Highlight Handles", 3027 : "Joint", 3028 : "Ghosting", 3029 : "Guides", 3030 : "Gradient", 3031 : "Object Highlighting", 3032 : "Navigation Cross", 3033 : "Base Grid"}
filters_r18 = {3001 : "Null", 3002 : "Polygon", 3003 : "Spline", 3004 : "Generator", 3005 : "Subdivision Surface", 3007 : "Deformer", 3008 : "Camera", 3009 : "Light", 3010 : "Environment", 3011 : "Particle", 3012 : "Other", 3014 : "Grid", 3015 : "Horizon", 3016 : "World Axis", 3017 : "Bounding-Box", 3018 : "HUD", 3019 : "SDS Mesh", 3020 : "Component Highlighting", 3021 : "Multi-Select Axes", 3022 : "Axis", 3023 : "Axis Bands", 3024 : "SDS Cage", 3025 : "N-gon Lines", 3026 : "Highlight Handles", 3027 : "Joint", 3028 : "Ghosting", 3029 : "Guides", 3030 : "Gradient", 3031 : "Object Highlighting", 3032 : "Navigation Cross", 3033 : "Base Grid"}
filters_r19 = {3001 : "Null", 3002 : "Polygon", 3003 : "Spline", 3004 : "Generator", 3005 : "Subdivision Surface", 3007 : "Deformer", 3008 : "Camera", 3009 : "Light", 3010 : "Environment", 3011 : "Particle", 3012 : "Other", 3014 : "Grid", 3015 : "Horizon", 3016 : "World Axis", 3017 : "Bounding-Box", 3018 : "HUD", 3019 : "SDS Mesh", 3020 : "Component Highlighting", 3021 : "Multi-Select Axes", 3022 : "Axis", 3023 : "Axis Bands", 3024 : "SDS Cage", 3025 : "N-gon Lines", 3026 : "Highlight Handles", 3027 : "Joint", 3028 : "Ghosting", 3029 : "Guides", 3030 : "Gradient", 3031 : "Object Highlighting", 3032 : "Navigation Cross", 3033 : "Base Grid"}

c4dversion = str(c4d.GetC4DVersion())[:2]
c4dversion = int(c4dversion)

if c4dversion == 13:
    filters = filters_r13
elif c4dversion == 14:
    filters = filters_r14
elif c4dversion == 15:
    filters = filters_r15
elif c4dversion == 16:
    filters = filters_r16
elif c4dversion == 17:
    filters = filters_r17
elif c4dversion == 18:
    filters = filters_r18
elif c4dversion == 19:
    filters = filters_r19
else:
    filters = False
    c4dversion = False

if c4dversion is not False:
    fkeys = filters.keys()
    fvalues = filters.values()

currentYear = datetime.now().year

# Strings
HELP_TEXT = "Hindsight: Store and reuse viewport filter presets"

# the header bar background color for the section titles
header_color = c4d.Vector(0.2,0.2,0.2)

# stores the total number of presets
totalnumpresets = 0
activepreset = 0

# Group ID's (this is just for coloring the stupid backgrounds)
GROUP_A = 6000  # Presets and # of Presets Available
GROUP_B = 6001  # Filter Options
GROUP_C = 6002  # Save Options
GROUP_D = 6003  # Display and View Options:
GROUP_E = 6004  # NOT USED YET
GROUP_F = 6005  # NOT USED YET

DUMMYGROUPID = 1000
DUMMYTEXTID = 1001
TOTALPRESETS = 1002
SEPARATOR = 1003
PRESET_OPTIONS = 1004
PRESET_NAME_TEXT_FIELD = 1005
PRESETCHECKBOXGROUP = 1006
PRESET_COMBOBOX = 1009
TAB_BASIC_OPTIONS = 1010
TAB_ADVANCED_OPTIONS = 1011
TAB_GROUP = 1012
PRESETLISTGROUP = 1015
SHADING_GROUP = c4d.BASEDRAW_DATA_SDISPLAYACTIVE * 10
WIRE_GROUP = c4d.BASEDRAW_DATA_WDISPLAYACTIVE * 10
LOD_GROUP = 1018
MANAGEPRESETSGROUP = 1016
NOPRESETLISTGROUP = 1017
GEARICON = 1018

# ID's
BTN_ABOUT = 2001
BTN_WEB = 2002
BTN_LOAD_SAVED_PRESETS = 2003
BTN_LOAD_CUSTOM_PRESETS = 2004
BTN_EXPORT_SINGLE_PRESET = 2005
BTN_EXPORT_ALL_PRESETS = 2006
BTN_SAVE_PRESET = 2007
CHKBOX_ALL = 2008
CHKBOX_NONE = 2009
BTN_RESET_TO_DEFAULTS = 2010
CHKBOX_CROSSHAIR = 2011

# OPTIONS
CHKBOX_RENDERSAFE = c4d.BASEDRAW_DATA_RENDERSAFE * 10
CHKBOX_RENDERSAFE_CENTER = c4d.BASEDRAW_DATA_RENDERSAFE_CENTER * 10
CHKBOX_TITLESAFE = c4d.BASEDRAW_DATA_TITLESAFE * 10
CHKBOX_TITLESAFE_CENTER = c4d.BASEDRAW_DATA_TITLESAFE_CENTER * 10
CHKBOX_ACTIONSAFE = c4d.BASEDRAW_DATA_ACTIONSAFE * 10
CHKBOX_ACTIONSAFE_CENTER = c4d.BASEDRAW_DATA_ACTIONSAFE_CENTER * 10
CHKBOX_ENHANCEDOPENGL = c4d.BASEDRAW_DATA_HQ_OPENGL * 10
CHKBOX_SHADOWS = c4d.BASEDRAW_DATA_HQ_SHADOWS * 10
CHKBOX_NOISES = c4d.BASEDRAW_DATA_HQ_NOISES * 10
CHKBOX_TRANSPARENCY = c4d.BASEDRAW_DATA_HQ_TRANSPARENCY * 10
CHKBOX_POSTEFFECTS = c4d.BASEDRAW_DATA_HQ_POST_EFFECTS * 10
CHKBOX_STEREOSCOPIC = c4d.BASEDRAW_STEREO_ENABLE * 10
CHKBOX_LINEARWORKFLOR = c4d.BASEDRAW_DATA_ENABLE_LWF * 10
CHKBOX_BACKFACECULLING = c4d.BASEDRAW_DATA_BACKCULL * 10
CHKBOX_ISOLINE_EDITING = c4d.BASEDRAW_DATA_SDSEDIT * 10
CHKBOX_NORMALS = c4d.BASEDRAW_DATA_SHOWNORMALS * 10
CHKBOX_TAGS = c4d.BASEDRAW_DATA_USEPROPERTIESACTIVE * 10
CHKBOX_TEXTURES = c4d.BASEDRAW_DATA_TEXTURES * 10
CHKBOX_XRAY = c4d.BASEDRAW_DATA_XRAY * 10
CHKBOX_LAYERCOLOR = c4d.BASEDRAW_DATA_USE_LAYERCOLOR * 10
REAL_TITLESAFE_SIZE = c4d.BASEDRAW_DATA_TITLESAFE_SIZE * 10
REAL_ACTIONSAFE_SIZE = c4d.BASEDRAW_DATA_ACTIONSAFE_SIZE * 10
MY_BITMAP_BUTTON = 8989

# sub dialog stuff
SUBD_NAME = "Hindsight Preset Settings"
SUBD_HEADER = 6006
SUBD_MAINGROUP = 3000
SUBD_BTN_DELETESELECTED = 3010
SUBD_BTN_DELETEALL = 3011
subd_ids = list()


# if more options are added they need to get added to this list
# this is the list used to check for id's being sent to and from the system
checkbox_options_list = [CHKBOX_RENDERSAFE, CHKBOX_RENDERSAFE_CENTER, CHKBOX_TITLESAFE, CHKBOX_TITLESAFE_CENTER, CHKBOX_ACTIONSAFE, CHKBOX_ACTIONSAFE_CENTER, CHKBOX_ENHANCEDOPENGL, CHKBOX_SHADOWS, CHKBOX_NOISES, CHKBOX_TRANSPARENCY, CHKBOX_POSTEFFECTS, CHKBOX_LINEARWORKFLOR, CHKBOX_BACKFACECULLING, CHKBOX_ISOLINE_EDITING, CHKBOX_NORMALS, CHKBOX_TAGS, CHKBOX_TEXTURES, CHKBOX_XRAY, CHKBOX_LAYERCOLOR, CHKBOX_STEREOSCOPIC]


# my cypher class. encrypts the cinema IDS so that they dont make sense if someone opens the .hnds file and looks.
class Crypto(object):
    def __init__(self, arg, salt):
        self.arg = arg

    @staticmethod
    def generateSalt(id, salt):
        # take the ID that is passed in, multiply it by the salt, then instert 3 random letters at random spots
        strID = str(id*salt)
        letter1 = random.choice(string.letters)
        letter2 = random.choice(string.letters)
        letter3 = random.choice(string.letters)
        indx= random.randrange(len(strID)+1)
        strID = strID[:indx] + letter1 + strID[indx:]
        indx= random.randrange(len(strID)+1)
        strID = strID[:indx] + letter2 + strID[indx:]
        indx= random.randrange(len(strID)+1)
        strID = strID[:indx] + letter3 + strID[indx:]
        return strID

    @staticmethod
    def decodeSalt(id, salt):
        # take the ID and remove any alpha characters then divide by the salt
        stripchars = re.sub('[^0-9]','', id)
        subid = int(stripchars)
        sysid = subid/salt
        return sysid


class CRUtilities(object):

    def __init__(self, arg):
        super(CRUtilities, self).__init__()

    @staticmethod
    def get_display_filter_code(keyvalue):
        theid = keyvalue/10
        for k in fkeys:
            if theid in filters:
                filtercode = filters[k][0]
            else:
                filtercode = False
            return filtercode

    @staticmethod
    def es_open_website(website):
        """Open default web browser and route to plugin Website

        :param string website: the full url to the site
        """

        webbrowser.open(website)

    @staticmethod
    def es_about(plugin_title, version, currentYear, author, website):
        """Show About information dialog box

        :param string plugin_title: name of plugin
        :param string version: version
        :param string copyright_year: year created
        :param string author: author of plugin
        :param string website: the website url
        """

        gui.MessageDialog("{0} v{1}\nCopyright (C) {2} {3}.\nAll rights reserved.\n\n{4}\n\n".format(plugin_title, version, currentYear, author, website), c4d.GEMB_OK)

    @staticmethod
    def es_get_active_doc():
        """Returns doc object"""

        activeDoc = documents.GetActiveDocument()

        return(activeDoc)

    @staticmethod
    def es_get_active_doc_path():
        """Return the document path without scene name"""

        activeDoc = documents.GetActiveDocument()
        activeDocPath = activeDoc.GetDocumentPath()

        return(activeDocPath)

    @staticmethod
    def es_get_active_doc_name():
        """Return the document name without extension"""

        activeDoc = documents.GetActiveDocument()
        activeDocName = activeDoc.GetDocumentName()

        return(activeDocName)

    @staticmethod
    def es_get_full_active_doc_name():
        """Return the document name with extension"""

        activeDoc = documents.GetActiveDocument()
        activeDocName = activeDoc.GetDocumentName()

        fullActiveDocName = activeDocName + ".c4d"

        return(fullActiveDocName)


class WARNINGICON(c4d.gui.GeUserArea):
    def __init__(self):
        self.bmp = c4d.bitmaps.BaseBitmap()

    def GetMinSize(self):
        self.width = 21 ####WIDTH OF YOUR IMAGE FILE
        self.height = 21 ####HEIGHT OF YOUR IMAGE FILE
        return (self.width, self.height)

    def DrawMsg(self, x1, y1, x2, y2, msg):
        path = os.path.join(os.path.dirname(__file__), "res", "icons", "warning_icon.png")
        result, ismovie = self.bmp.InitWith(path)
        x1 = 0
        y1 = 0
        x2 = self.bmp.GetBw()
        y2 = self.bmp.GetBh()
        if result == c4d.IMAGERESULT_OK:
            self.DrawBitmap(self.bmp, 0, 0, self.bmp.GetBw(), self.bmp.GetBh(), x1, y1, x2, y2, c4d.BMP_NORMALSCALED | c4d.BMP_ALLOWALPHA)


class INFOICON(c4d.gui.GeUserArea):
    def __init__(self):
        self.bmp = c4d.bitmaps.BaseBitmap()

    def GetMinSize(self):
        self.width = 21 ####WIDTH OF YOUR IMAGE FILE
        self.height = 21 ####HEIGHT OF YOUR IMAGE FILE
        return (self.width, self.height)

    def DrawMsg(self, x1, y1, x2, y2, msg):
        path = os.path.join(os.path.dirname(__file__), "res", "icons", "info_icon.png")
        result, ismovie = self.bmp.InitWith(path)
        x1 = 0
        y1 = 0
        x2 = self.bmp.GetBw()
        y2 = self.bmp.GetBh()
        if result == c4d.IMAGERESULT_OK:
            self.DrawBitmap(self.bmp, 0, 0, self.bmp.GetBw(), self.bmp.GetBh(), x1, y1, x2, y2, c4d.BMP_NORMALSCALED | c4d.BMP_ALLOWALPHA)


class ALERTICON(c4d.gui.GeUserArea):
    def __init__(self):
        self.bmp = c4d.bitmaps.BaseBitmap()

    def GetMinSize(self):
        self.width = 21 ####WIDTH OF YOUR IMAGE FILE
        self.height = 21 ####HEIGHT OF YOUR IMAGE FILE
        return (self.width, self.height)

    def DrawMsg(self, x1, y1, x2, y2, msg):
        path = os.path.join(os.path.dirname(__file__), "res", "icons", "alert_icon.png")
        result, ismovie = self.bmp.InitWith(path)
        x1 = 0
        y1 = 0
        x2 = self.bmp.GetBw()
        y2 = self.bmp.GetBh()
        if result == c4d.IMAGERESULT_OK:
            self.DrawBitmap(self.bmp, 0, 0, self.bmp.GetBw(), self.bmp.GetBh(), x1, y1, x2, y2, c4d.BMP_NORMALSCALED | c4d.BMP_ALLOWALPHA)


class SubDialog(gui.SubDialog):
    global hindsightfile, totalnumpresets, filters, fkeys, fvalues, header_color, subd_ids

    def InitValues(self):
        self.Enable(SUBD_BTN_DELETESELECTED, False)

        return True

    def CreateLayout(self):
        self.SetTitle(__plugin_title__)

        self.GroupBegin(SUBD_HEADER, c4d.BFH_SCALEFIT, cols=1)
        self.SetDefaultColor(SUBD_HEADER, c4d.COLOR_BG, header_color)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 5)
        self.AddStaticText(DUMMYTEXTID, c4d.BFH_LEFT, 0,13, name="Preset Options")
        self.GroupEnd()

        self.GroupBegin(DUMMYGROUPID, c4d.BFH_SCALEFIT, cols=1)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 0)
        self.AddStaticText(DUMMYTEXTID, c4d.BFH_LEFT, 0,13, name="Select the presets you want to delete")
        self.GroupEnd()

        self.GroupBegin(DUMMYGROUPID, c4d.BFH_SCALEFIT, cols=1)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 0, 15, 5)
        self.AddSeparatorH(0, c4d.BFH_SCALEFIT)
        self.GroupEnd()

        with open(hindsightfile) as f:
            hdata = json.load(f)

        self.GroupBegin(SUBD_MAINGROUP, c4d.BFH_SCALEFIT, cols=1)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 5)
        for row in hdata['hindsight']:
            subid = int(row['id']) * 2400
            subd_ids.append(subid)
            self.AddCheckbox(subid, c4d.BFH_SCALEFIT, 200, 0, row["name"])
        self.GroupEnd()

        self.GroupBegin(DUMMYGROUPID, c4d.BFH_SCALEFIT, cols=1)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 5)
        self.AddSeparatorH(0, c4d.BFH_SCALEFIT)
        self.GroupEnd()

        self.GroupBegin(DUMMYGROUPID, c4d.BFH_SCALEFIT, cols=4)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 10)
        self.AddButton(SUBD_BTN_DELETESELECTED, c4d.BFH_RIGHT, 0,13, name="Delete Selected Presets")
        self.AddStaticText(DUMMYTEXTID, c4d.BFH_SCALEFIT, 20, 0, " ")
        self.GroupEnd()

        return True

    def all_same(items):
        return all(x == items[0] for x in items)

    def Command(self, id, msg):
        # this makes a list of the values from the presets
        # then, if any of them are not true, turn the button off
        value_check = list()
        if id in subd_ids:
            for i in subd_ids:
                val = self.GetBool(i)
                value_check.append(val)

            if True not in value_check:
                self.Enable(SUBD_BTN_DELETESELECTED, False)
            else:
                self.Enable(SUBD_BTN_DELETESELECTED, True)

        # Delete Selected
        # remember to divide the id by 2400 (because that is the random number i picked on like 357)
        # id/2400 = hindsite preset id of file
        if id == SUBD_BTN_DELETESELECTED:
            with open(hindsightfile) as f:
                hdata = json.load(f)

            # get the id of each selected
            for oldID in subd_ids:
                val = self.GetBool(oldID)

                if val == True:
                    theid = oldID/2400

                    for i in range(len(hdata['hindsight'])):
                        if hdata['hindsight'][i]['id'] == theid:
                            del hdata['hindsight'][i]
                            break

            with open(hindsightfile, 'w') as outfile:
                json.dump(hdata, outfile, indent=4, sort_keys=True)

            c4d.SpecialEventAdd(1035663)
            self.Close()


        return True


class MainDialog(gui.GeDialog):
    ALERTICON = ALERTICON()
    WARNINGICON = WARNINGICON()
    INFOICON = INFOICON()

    # make sure there is a preference folder
    def checkdir(self):
        global hindsight_dir
        if not os.path.exists(hindsight_dir):
            os.makedirs(hindsight_dir)

    def presetoptionsbutton(self):
        path = os.path.join(os.path.dirname(__file__), "res", "icons", "manage.png")
        gearicon = c4d.BaseContainer()

        gearicon.SetLong(c4d.BITMAPBUTTON_BORDER, c4d.BORDER_NONE)
        gearicon.SetLong(c4d.BITMAPBUTTON_OUTBORDER, c4d.BORDER_NONE)
        gearicon.SetBool(c4d.BITMAPBUTTON_BUTTON, True)
        gearicon.SetBool(c4d.BITMAPBUTTON_TOGGLE, False)
        gearicon.SetString(c4d.BITMAPBUTTON_TOOLTIP, "Manage Existing Presets")
        gearicon.SetBool(c4d.BITMAPBUTTON_NOBORDERDRAW, True)
        gearicon.SetLong(c4d.BITMAPBUTTON_BACKCOLOR, c4d.COLOR_BG)

        gear = self.AddCustomGui(MANAGEPRESETSGROUP, c4d.CUSTOMGUI_BITMAPBUTTON, "options", c4d.BFV_CENTER | c4d.BFV_CENTER, 21, 21, gearicon)
        gear.SetImage(path, False, False)

    def build_preset_list(self):
        global hindsightfile, totalnumpresets, header_color

        # first check for the directory, if its not there, build that
        self.checkdir()

        if os.path.isfile(hindsightfile):
            with open(hindsightfile) as f:
                hdata = json.load(f)

            if hdata and len(hdata['hindsight']) == 0:
                os.remove(hindsightfile)

        # the directory exists now for sure, check the presets.hnds file
        if not os.path.isfile(hindsightfile):
            # add user area that display a message saying there are no presets saved
            self.GroupBegin(PRESETLISTGROUP, c4d.BFH_SCALEFIT, cols=2)
            self.GroupBorderNoTitle(0)
            self.GroupBorderSpace(15, 5, 15, 5)
            self.AddUserArea(1, c4d.BFV_CENTER | c4d.BFV_CENTER)
            self.AttachUserArea(self.ALERTICON, 1)
            self.AddStaticText(DUMMYTEXTID, c4d.BFH_LEFT | c4d.BFV_CENTER, 0,13, name="You have no presets saved")
            self.GroupEnd()
        else:
            # make a dropdown
            self.GroupBegin(PRESETLISTGROUP, c4d.BFH_SCALEFIT, cols=3)
            self.GroupBorderNoTitle(0)
            self.GroupBorderSpace(15, 5, 15, 5)
            self.AddComboBox(PRESET_COMBOBOX, c4d.BFH_SCALEFIT, 600, 15, False)
            self.AddChild(PRESET_COMBOBOX, 0, 'Choose a Preset...')

            with open(hindsightfile) as f:
                hdata = json.load(f)

            for row in hdata['hindsight']:
                # started at 0 so add 1
                totalnumpresets = totalnumpresets + 1
                subid = int(row['id'])
                self.AddChild(PRESET_COMBOBOX, subid, row['name'])

            self.AddStaticText(DUMMYTEXTID, c4d.BFH_LEFT | c4d.BFV_CENTER, 10,13, name=" ")
            self.presetoptionsbutton()

            # flush the layout to update the number of presets text string
            pnum = str(totalnumpresets) + " Presets Available"

            self.LayoutFlushGroup(GROUP_A)
            self.LayoutChanged(GROUP_A)
            self.GroupBegin(GROUP_A, c4d.BFH_SCALEFIT, cols=3)
            self.SetDefaultColor(GROUP_A, c4d.COLOR_BG, header_color)
            self.GroupBorderNoTitle(0)
            self.GroupBorderSpace(15, 5, 15, 5)
            self.AddStaticText(DUMMYTEXTID, c4d.BFH_LEFT, 0,13, name="Presets")
            self.AddStaticText(DUMMYTEXTID, c4d.BFH_SCALEFIT, 0,13, name="")
            self.AddStaticText(TOTALPRESETS, c4d.BFH_RIGHT, 0,13, name=pnum)
            self.GroupEnd()
            self.GroupEnd()

            totalnumpresets = 0

    def reload_dropdown(self, setpresetid):
        self.LayoutFlushGroup(PRESETLISTGROUP)
        self.build_preset_list()
        self.LayoutChanged(PRESETLISTGROUP)
        self.SetLong(PRESET_COMBOBOX, setpresetid)
        self.Enable(BTN_EXPORT_ALL_PRESETS, True)

    def set_save_field(self):
        if len(self.GetString(PRESET_NAME_TEXT_FIELD)) > 0:
           self.Enable(BTN_SAVE_PRESET, True)
        else:
            self.Enable(BTN_SAVE_PRESET, False)

    def get_values_from_cinema(self):
        doc = CRUtilities.es_get_active_doc()
        draw = doc.GetActiveBaseDraw()

        # get all the filter values currently set inside cinema
        for k in filters:
            filterid = k * 10
            filtertodraw = draw[k]
            self.SetBool(filterid, filtertodraw)

        for i in checkbox_options_list:
            filterid = i/10
            filtertodraw = draw[filterid]

            if filtertodraw is None:
                filtertodraw = 0

            self.SetBool(i, filtertodraw)

        # cinema turns these off if openGL is off, do the same
        if draw[CHKBOX_ENHANCEDOPENGL/10] == 0:
            self.Enable(CHKBOX_NOISES, False)
            self.Enable(CHKBOX_POSTEFFECTS, False)
            self.Enable(CHKBOX_SHADOWS, False)
            self.Enable(CHKBOX_TRANSPARENCY, False)

        if not os.path.isfile(hindsightfile):
            self.Enable(BTN_EXPORT_ALL_PRESETS, False)

        self.set_save_field()

        self.SetPercent(REAL_ACTIONSAFE_SIZE, draw[c4d.BASEDRAW_DATA_ACTIONSAFE_SIZE], 0, 100, 1.0, False)
        self.SetPercent(REAL_TITLESAFE_SIZE, draw[c4d.BASEDRAW_DATA_TITLESAFE_SIZE], 0, 100, 1.0, False)

        # combobox shading groups
        self.SetLong(SHADING_GROUP, draw[SHADING_GROUP/10])
        self.SetLong(WIRE_GROUP, draw[WIRE_GROUP/10])

        if activepreset is not None:
            self.SetLong(PRESET_COMBOBOX, activepreset)

    """
    *******************************************************************
    Should get values from preset on start if there is one set and not 
    the initial cinema values
    *******************************************************************
    """

    def InitValues(self):
        self.get_values_from_cinema()
        return True

    def CreateLayout(self):
        global filters, fkeys, fvalues, header_color

        self.SetTitle(__plugin_title__)

        # Create the menu
        self.MenuFlushAll()

        # About/Help menu
        self.MenuSubBegin("Info")
        self.MenuAddString(BTN_ABOUT, "About")
        self.MenuAddString(BTN_WEB, "Website")
        # self.MenuAddSeparator()
        self.MenuSubEnd()
        self.MenuFinished()

        """ PRESET TEXT START """
        self.GroupBegin(GROUP_A, c4d.BFH_SCALEFIT, cols=3)
        self.SetDefaultColor(GROUP_A, c4d.COLOR_BG, header_color)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 5)
        self.AddStaticText(DUMMYTEXTID, c4d.BFH_LEFT, 0,13, name="Presets")
        self.AddStaticText(DUMMYTEXTID, c4d.BFH_SCALEFIT, 0,13, name="")
        self.AddStaticText(TOTALPRESETS, c4d.BFH_RIGHT, 0,13, name="# Presets Available")
        self.GroupEnd()

        # call the function that actually builds the list or error notice
        self.build_preset_list()

        # TAB WRAPPER START ===========================================================================================
        self.TabGroupBegin(TAB_GROUP, c4d.BFH_SCALEFIT, c4d.TAB_TABS)

        # BASIC OPTIONS TAB ================================================
        self.GroupBegin(TAB_BASIC_OPTIONS, c4d.BFH_SCALEFIT, cols=1, title="Basic Options")

        """ PRESET OPTIONS TEXT START """
        self.GroupBegin(GROUP_B, c4d.BFH_SCALEFIT, cols=1)
        self.SetDefaultColor(GROUP_B, c4d.COLOR_BG, header_color)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 5)
        self.AddStaticText(DUMMYTEXTID, c4d.BFH_LEFT, name="Filter Options:")
        self.GroupEnd()

        """ CHECKBOXES FOR PRESESTS """
        self.GroupBegin(PRESETCHECKBOXGROUP, c4d.BFH_SCALEFIT, cols=3, initw=0)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 10)
        self.AddCheckbox(CHKBOX_ALL, c4d.BFH_SCALEFIT, 0, 0, "All")
        self.AddCheckbox(CHKBOX_NONE, c4d.BFH_SCALEFIT, 0, 0, "None")

        for k in fkeys:
            filterid = k * 10
            filtername = fvalues[fkeys.index(k)]
            self.AddCheckbox(filterid, c4d.BFH_SCALEFIT, 0, 0, filtername)

        self.GroupEnd()

        self.GroupBegin(DUMMYGROUPID, c4d.BFH_SCALEFIT, cols=1)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 5)
        self.AddSeparatorH(0, c4d.BFH_SCALEFIT)
        self.GroupEnd()

        self.GroupBegin(DUMMYGROUPID, c4d.BFH_SCALEFIT, cols=5)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 10)
        self.AddButton(BTN_RESET_TO_DEFAULTS, c4d.BFH_RIGHT, 0, 13, name="Reset to C4d Defaults")
        # self.AddStaticText(DUMMYTEXTID, c4d.BFH_SCALEFIT, 20, 0, " ")
        # self.AddButton(BTN_LOAD_CUSTOM_PRESETS, c4d.BFH_CENTER, 0,13, name="Load custom presets")
        # self.AddStaticText(DUMMYTEXTID, c4d.BFH_SCALEFIT, 20, 0, " ")
        # self.AddButton(BTN_EXPORT_ALL_PRESETS, c4d.BFH_RIGHT, 0,13, name="Export all presets")
        self.GroupEnd()

        self.GroupEnd()
        # BASIC OPTIONS TAB END ================================================

        # ADVANCED OPTIONS TAB START ================================================
        self.GroupBegin(TAB_ADVANCED_OPTIONS, c4d.BFH_SCALEFIT, cols=1, title="Advanced Options")

        self.GroupBegin(GROUP_D, c4d.BFH_SCALEFIT, cols=1)
        self.SetDefaultColor(GROUP_D, c4d.COLOR_BG, header_color)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 5)
        self.AddStaticText(DUMMYTEXTID, c4d.BFH_LEFT, name="Display and View Options:")
        self.GroupEnd()

        self.GroupBegin(DUMMYGROUPID, c4d.BFH_LEFT, cols=2)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 0)
        self.AddCheckbox(CHKBOX_RENDERSAFE, c4d.BFH_SCALEFIT, 200, 0, "Render Safe")
        self.AddCheckbox(CHKBOX_RENDERSAFE_CENTER, c4d.BFH_SCALEFIT, 0, 0, "Render Safe Center")
        self.GroupEnd()

        self.GroupBegin(DUMMYGROUPID, c4d.BFH_LEFT, cols=3)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 0, 15, 0)
        self.AddCheckbox(CHKBOX_TITLESAFE, c4d.BFH_SCALEFIT, 200, 0, "Title Safe")
        self.AddCheckbox(CHKBOX_TITLESAFE_CENTER, c4d.BFH_SCALEFIT, 240, 0, "Action Safe Center")
        self.AddEditNumberArrows(REAL_TITLESAFE_SIZE, c4d.BFH_SCALEFIT, 70, 0)
        self.AddCheckbox(CHKBOX_ACTIONSAFE, c4d.BFH_SCALEFIT, 200, 0, "Action Safe")
        self.AddCheckbox(CHKBOX_ACTIONSAFE_CENTER, c4d.BFH_SCALEFIT, 240, 0, "Action Safe Center")
        self.AddEditNumberArrows(REAL_ACTIONSAFE_SIZE, c4d.BFH_SCALEFIT, 70, 0)
        self.GroupEnd()

        self.GroupBegin(DUMMYGROUPID, c4d.BFH_SCALEFIT, cols=1)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 5)
        self.AddSeparatorH(0, c4d.BFH_SCALEFIT)
        self.GroupEnd()

        self.GroupBegin(DUMMYGROUPID, c4d.BFH_LEFT, cols=3)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 5)
        self.AddCheckbox(CHKBOX_STEREOSCOPIC, c4d.BFH_SCALEFIT, 200, 0, "Sterescopic")
        self.AddCheckbox(CHKBOX_ENHANCEDOPENGL, c4d.BFH_SCALEFIT, 200, 0, "Enhanced OpenGL")
        self.AddCheckbox(CHKBOX_SHADOWS, c4d.BFH_SCALEFIT, 200, 0, "Shadows")
        self.AddCheckbox(CHKBOX_NOISES, c4d.BFH_SCALEFIT, 200, 0, "Noises")
        self.AddCheckbox(CHKBOX_TRANSPARENCY, c4d.BFH_SCALEFIT, 200, 0, "Transparency")
        self.AddCheckbox(CHKBOX_POSTEFFECTS, c4d.BFH_SCALEFIT, 200, 0, "Post Effects")
        self.AddCheckbox(CHKBOX_LINEARWORKFLOR, c4d.BFH_SCALEFIT, 260, 0, "Allow Linear Workflow")
        self.AddCheckbox(CHKBOX_BACKFACECULLING, c4d.BFH_SCALEFIT, 200, 0, "Backface Culling")
        self.AddCheckbox(CHKBOX_ISOLINE_EDITING, c4d.BFH_SCALEFIT, 200, 0, "Isoline Editing")
        self.AddCheckbox(CHKBOX_LAYERCOLOR, c4d.BFH_SCALEFIT, 200, 0, "Layer Colors")
        self.AddCheckbox(CHKBOX_NORMALS, c4d.BFH_SCALEFIT, 200, 0, "Normals")
        self.AddCheckbox(CHKBOX_TAGS, c4d.BFH_SCALEFIT, 200, 0, "Tags")
        self.AddCheckbox(CHKBOX_TEXTURES, c4d.BFH_SCALEFIT, 200, 0, "Textures")
        self.AddCheckbox(CHKBOX_XRAY, c4d.BFH_SCALEFIT, 200, 0, "X-Ray")
        self.GroupEnd()

        self.GroupBegin(DUMMYGROUPID, c4d.BFH_SCALEFIT, cols=1)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 5)
        self.AddSeparatorH(0, c4d.BFH_SCALEFIT)
        self.GroupEnd()

        self.GroupBegin(DUMMYGROUPID, c4d.BFH_SCALEFIT, cols=5)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 0, 15, 5)
        self.AddStaticText(DUMMYTEXTID, c4d.BFH_LEFT, name="Shading")
        self.AddComboBox(SHADING_GROUP, c4d.BFH_LEFT, 200, 15, False)
        self.AddChild(SHADING_GROUP, 0, 'Gouraud Shading')
        self.AddChild(SHADING_GROUP, 1, 'Gouraud Shading (Lines)')
        self.AddChild(SHADING_GROUP, 2, 'Quick Shading')
        self.AddChild(SHADING_GROUP, 3, 'Quick Shading (Lines)')
        self.AddChild(SHADING_GROUP, 7, 'Constant Shading')
        self.AddChild(SHADING_GROUP, 4, 'Constant Shading (Lines)')
        self.AddChild(SHADING_GROUP, 5, 'Hidden Lines')
        self.AddChild(SHADING_GROUP, 6, 'Lines')
        self.AddStaticText(DUMMYTEXTID, c4d.BFH_LEFT, 100, 0, name=" ")
        self.AddStaticText(DUMMYTEXTID, c4d.BFH_LEFT, name="Wire")
        self.AddComboBox(WIRE_GROUP, c4d.BFH_LEFT, 200, 15, False)
        self.AddChild(WIRE_GROUP, 0, 'Wireframe')
        self.AddChild(WIRE_GROUP, 1, 'Isoparms')
        self.AddChild(WIRE_GROUP, 2, 'Box')
        self.AddChild(WIRE_GROUP, 3, 'Skeleton')
        # self.AddStaticText(DUMMYTEXTID, c4d.BFH_LEFT, name="LOD")
        # self.AddComboBox(LOD_GROUP, c4d.BFH_LEFT, 200, 15, False)
        # self.AddChild(LOD_GROUP, 0, 'High')
        # self.AddChild(LOD_GROUP, 1, 'Medium')
        # self.AddChild(LOD_GROUP, 2, 'Low')
        self.GroupEnd()

        self.GroupEnd() # ADVANCED OPTIONS TAB END ================================================

        self.GroupEnd()
        # TAB WRAPPER END =============================================================================================

        """ PRESET OPTIONS TEXT START """
        #************************
        self.GroupBegin(GROUP_C, c4d.BFH_SCALEFIT, cols=1)
        self.SetDefaultColor(GROUP_C, c4d.COLOR_BG, header_color)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 5)
        self.AddStaticText(DUMMYTEXTID, c4d.BFH_LEFT, name="Save Options")
        self.GroupEnd()
        #************************

        """ SAVE PRESETS NAME AND BUTTON """
        #************************
        self.GroupBegin(DUMMYGROUPID, c4d.BFH_SCALEFIT, cols=3)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(15, 5, 15, 10)
        self.AddStaticText(DUMMYTEXTID, c4d.BFH_LEFT, name="Preset Name: ")
        self.AddEditText(PRESET_NAME_TEXT_FIELD, c4d.BFH_SCALEFIT, 260, 0)
        self.AddButton(BTN_SAVE_PRESET, c4d.BFH_RIGHT, 0, 13, name="Save Preset")
        self.GroupEnd()
        #************************
        return True

    def about_plugin(self):
        gui.MessageDialog("{0} Copyright (C) {1} Charles Rowland. All rights reserved.\n\nHindsight logo and icon Design by Mathew Sienzant, @mdsienzant on Twitter.".format(__plugin_title__,currentYear), c4d.GEMB_OK)

    def open_website(self):
        webbrowser.open('http://www.wickedsword.com/')

    def CoreMessage(self, id, msg):
        if id == c4d.EVMSG_CHANGE:
            # reload the interface if an option from cinema was changed
            self.get_values_from_cinema()
            c4d.EventAdd()

        if id == 1035663:
            self.reload_dropdown(0)

        return True

    def collect_filters_for_saving(self):
        doc = CRUtilities.es_get_active_doc()
        draw = doc.GetActiveBaseDraw()
        vpfilters = {}

        # get all the filter values currently set inside cinema
        for k in filters:
            filterid = Crypto.generateSalt(k,salt)
            filtertodraw = draw[k]

            # encrypt the ID's from pyring eyes
            vpfilters[filterid] = filtertodraw

        return vpfilters

    def collect_shading_longs(self):
        doc = CRUtilities.es_get_active_doc()
        draw = doc.GetActiveBaseDraw()

        shadinglongs = {}
        shadingid = SHADING_GROUP/10
        wire = WIRE_GROUP/10

        shadinglongs[Crypto.generateSalt(shadingid,salt)] = draw[shadingid]
        shadinglongs[Crypto.generateSalt(wire,salt)] = draw[wire]

        return shadinglongs

    def collect_shading(self):
        doc = CRUtilities.es_get_active_doc()
        draw = doc.GetActiveBaseDraw()

        shading = {}
        for item in checkbox_options_list:
            sysid = item/10

            val = draw[sysid]

            if not val:
                val = 0

            shading[Crypto.generateSalt(sysid,salt)] = val

        return shading

    def collect_reals(self):
        doc = CRUtilities.es_get_active_doc()
        draw = doc.GetActiveBaseDraw()

        reals = {}
        titlesafe = REAL_TITLESAFE_SIZE/10
        actionsafe = REAL_ACTIONSAFE_SIZE/10

        reals[Crypto.generateSalt(actionsafe, salt)] = "%.2f" % draw[actionsafe]
        reals[Crypto.generateSalt(titlesafe, salt)] = "%.2f" % draw[titlesafe]

        return reals

    def collect_custom(self):
        # this is for the All and None checkbox options
        doc = CRUtilities.es_get_active_doc()
        draw = doc.GetActiveBaseDraw()

        custom = {}
        chckall = draw[CHKBOX_ALL]
        chcknone = draw[CHKBOX_NONE]

        if chckall is None:
            chckall = 0

        if chcknone is None:
            chcknone = 0

        custom[Crypto.generateSalt(CHKBOX_ALL,salt)] = chckall
        custom[Crypto.generateSalt(CHKBOX_NONE,salt)] = chcknone

        return custom

    def Command(self, id, msg):
        global hindsightfile, activepreset
        doc = CRUtilities.es_get_active_doc()
        draw = doc.GetActiveBaseDraw()

        # only open if the file is there or it's going to be a bad time
        if os.path.isfile(hindsightfile):
            with open(hindsightfile) as f:
                hdata = json.load(f)
        else:
            hdata = {"hindsight":[]}

        if id == MANAGEPRESETSGROUP:
            self.dialog2 = SubDialog()
            self.dialog2.Open(dlgtype = c4d.DLG_TYPE_MODAL, defaultw = 1, defaulth = 1)

            return True

        # change all options when a preset is chosen
        if id == PRESET_COMBOBOX:
            presetid = self.GetLong(id)
            activepreset = presetid

            for row in hdata['hindsight']:
                if int(row['id']) == presetid:
                    filterkeys = row['filters'].keys()
                    filtervalues = row['filters'].values()
                    shading_longskeys = row['shading_longs'].keys()
                    shading_longsvalues = row['shading_longs'].values()
                    shadingkeys = row['shading'].keys()
                    shadingvalues = row['shading'].values()
                    realskeys = row['reals'].keys()
                    realsvalues = row['reals'].values()
                    customkeys = row['custom'].keys()
                    customvalues = row['custom'].values()

                    # filters
                    for f in filterkeys:
                        thekey = Crypto.decodeSalt(f,salt)
                        sysid = thekey
                        hindsightvalue = int(filtervalues[filterkeys.index(f)])
                        sysvalue = hindsightvalue
                        myid = thekey*10

                        hindsightvalue = False if hindsightvalue == 0 else True

                        draw[sysid] = sysvalue
                        self.SetBool(myid, hindsightvalue)

                    # all or none checkboxes
                    for f in customkeys:
                        thekey = Crypto.decodeSalt(f,salt)
                        hindsightvalue = int(customvalues[customkeys.index(f)])
                        setvalue = False if hindsightvalue == 0 else True

                        self.SetBool(thekey, setvalue)

                    # shading
                    for f in shadingkeys:
                        thekey = Crypto.decodeSalt(f,salt)
                        sysid = thekey
                        hindsightvalue = int(shadingvalues[shadingkeys.index(f)])
                        sysvalue = hindsightvalue
                        myid = thekey*10

                        hindsightvalue = False if hindsightvalue == 0 else True

                        draw[sysid] = sysvalue
                        self.SetBool(myid, hindsightvalue)

                    # shading longs (comboboxes)
                    for f in shading_longskeys:
                        thekey = Crypto.decodeSalt(f,salt)
                        sysid = thekey
                        hindsightvalue = int(shading_longsvalues[shading_longskeys.index(f)])
                        sysvalue = hindsightvalue
                        myid = thekey*10
                        draw[sysid] = sysvalue
                        self.SetLong(myid, draw[sysid])

                    # % values
                    for f in realskeys:
                        thekey = Crypto.decodeSalt(f,salt)
                        sysid = thekey
                        hindsightvalue = float(realsvalues[realskeys.index(f)])
                        sysvalue = hindsightvalue
                        myid = thekey*10
                        draw[sysid] = sysvalue
                        self.SetPercent(myid, draw[sysid], 0, 100, 1.0, False)

            c4d.EventAdd()

        if id == BTN_ABOUT: self.about_plugin()
        if id == BTN_WEB: self.open_website()

        if id == CHKBOX_ALL:
            if self.GetBool(CHKBOX_ALL) == True:
                self.SetBool(CHKBOX_ALL, True)
                self.SetBool(CHKBOX_NONE, False)

                for i in xrange(30010, 30330, 10):
                    self.SetBool(i, True)
                    draw[i/10] = 1

            c4d.EventAdd()

        if id == CHKBOX_NONE:
            if self.GetBool(CHKBOX_NONE) == True:
                self.SetBool(CHKBOX_ALL, False)
                self.SetBool(CHKBOX_NONE, True)

                for i in xrange(30010, 30330, 10):
                    self.SetBool(i, False)
                    draw[i/10] = 0

            c4d.EventAdd()

        # specific for the filters
        if id in xrange(30010, 30330, 10):
            if self.GetBool(id) is True:
                drawID = id/10
                draw[drawID] = 1
            else:
                drawID = id/10
                draw[drawID] = 0

            c4d.EventAdd()

        # specific for all the rest
        if id in checkbox_options_list:
            drawID = id/10
            if self.GetBool(id) is True:
                draw[drawID] = 1
            else:
                draw[drawID] = 0

            c4d.EventAdd()

        if id == CHKBOX_ENHANCEDOPENGL:
            if self.GetBool(id) is True:
                self.Enable(CHKBOX_NOISES, True)
                self.Enable(CHKBOX_POSTEFFECTS, True)
                self.Enable(CHKBOX_SHADOWS, True)
                self.Enable(CHKBOX_TRANSPARENCY, True)
            else:
                self.Enable(CHKBOX_NOISES, False)
                self.Enable(CHKBOX_POSTEFFECTS, False)
                self.Enable(CHKBOX_SHADOWS, False)
                self.Enable(CHKBOX_TRANSPARENCY, False)

        # shading and wire options
        if id == SHADING_GROUP:
            v = self.GetLong(SHADING_GROUP)
            sysid = SHADING_GROUP/10
            draw[sysid] = v
            c4d.EventAdd()

        if id == WIRE_GROUP:
            v = self.GetLong(WIRE_GROUP)
            sysid = WIRE_GROUP/10
            draw[sysid] = v
            c4d.EventAdd()

        if id == LOD_GROUP:
            v = self.GetLong(LOD_GROUP)
            self.set_lod(v)
            c4d.EventAdd()

        if id == REAL_TITLESAFE_SIZE:
            v = self.GetReal(id)
            sysid = id/10
            draw[sysid] = v
            c4d.EventAdd()

        if id == REAL_ACTIONSAFE_SIZE:
            v = self.GetReal(id)
            sysid = id/10
            draw[sysid] = v
            c4d.EventAdd()

        # only let the save button work if a name was typed in
        if id == PRESET_NAME_TEXT_FIELD:
            self.set_save_field()

        if id == BTN_SAVE_PRESET:
            preset_name = self.GetString(PRESET_NAME_TEXT_FIELD)
            presetID = False

            # only check for the duplicate if there was already a file
            if os.path.isfile(hindsightfile):
                for row in hdata['hindsight']:
                    pname = row['name']
                    if preset_name == pname:
                        # error, show dialog
                        errorcheck = gui.MessageDialog("There is currently a preset already named '{0}'\n\nPress OK to make changes to the existing preset or\npress Cancel to pick a new name.".format(preset_name), c4d.GEMB_OKCANCEL)

                        if errorcheck == 1:
                            # user says it is ok to replace: delete the preset named preset_name
                            for i in range(len(hdata['hindsight'])):
                                if hdata['hindsight'][i]['name'] == pname:
                                    presetID = hdata['hindsight'][i]['id']
                                    del hdata['hindsight'][i]
                                    break

                            okToSave = True
                    else:
                        # OK
                        okToSave = True
            else:
                okToSave = True

            if okToSave == True:
                newdata = hdata['hindsight']

                if presetID == False:
                    if len(hdata['hindsight']) == 0:
                        presetID = 1
                    else:
                        for row in hdata['hindsight']:
                            currentid = row['id']
                            presetID = int(currentid)+1

                # get filters
                vpfilters = self.collect_filters_for_saving()

                # get shading longs
                shadinglongs = self.collect_shading_longs()

                # get shading
                shading = self.collect_shading()

                # get reals
                reals = self.collect_reals()

                # get all and none checkboxes
                custom = self.collect_custom()

                newpreset = {"name" : preset_name, "id" : presetID, "filters" : vpfilters, "shading_longs" : shadinglongs, "shading" : shading, "reals" : reals, "custom": custom }
                hdata['hindsight'].append(newpreset)

                # SAVE THE FILE NOW

                with open(hindsightfile, 'w') as outfile:
                    json.dump(hdata, outfile, indent=4, sort_keys=True)

                    savestatus = True

                # reload the interface
                if savestatus == True:
                    self.SetString(PRESET_NAME_TEXT_FIELD,'')
                    self.reload_dropdown(presetID)

        if id == BTN_EXPORT_ALL_PRESETS:
            dir, file = os.path.split(__file__)
            exportpath = os.path.join(dir, "export")

            if not os.path.exists(exportpath):
                os.makedirs(exportpath)

            shutil.copy(hindsightfile, exportpath)

            newcopy = os.path.join(exportpath,hindsight_pref_file_name)
            st.ShowInFinder(newcopy)

        if id == BTN_LOAD_CUSTOM_PRESETS:
            altkey = c4d.BaseContainer()
            c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD,c4d.KEY_ALT,altkey)
            fn = st.LoadDialog(c4d.FILESELECTTYPE_ANYTHING, "Load custom .hnds Hindsight presets file")
            if fn is not None:
                ext = fn.rsplit('.',4)

                if ext[1] != "hnds":
                    error = gui.MessageDialog("The file you have chosen is not a Hindsight file. Please select a Hindsight presets file.", c4d.GEMB_OK)
                    return False
                else:
                    # load the file and build the list, using this as the build file

                    if altkey[c4d.BFM_INPUT_VALUE] == 1:
                        #replace presets:
                        os.remove(hindsightfile)
                        hdata = {"hindsight":[]}

                        with open(fn) as f:
                            newdata = json.load(f)

                        for row in newdata['hindsight']:
                            hdata['hindsight'].append(row)

                        # resave the file
                        with open(hindsightfile, 'w') as outfile:
                            json.dump(hdata, outfile, indent=4, sort_keys=True)

                        self.reload_dropdown(0)

                    else:
                        # merge presets:
                        with open(fn) as f:
                            newdata = json.load(f)

                        # hdata['hindsight'].append(newpreset)
                        oldIdList = list()
                        existingNames = list()

                        # get the last id, gonna need that so there are not duplicates
                        for row in hdata['hindsight']:
                            oldIdList.append(row['id'])
                            existingNames.append(row['name'])

                        # oldIdList not has all the ids, get the length + 1. thats the starting id.
                        newid = len(oldIdList) + 1

                        for row in newdata['hindsight']:
                            # take care of dubplicate ids
                            row['id'] = newid

                            # take care of dubplicate names
                            if row['name'] in existingNames:
                                row['name'] = row['name'] + ' 2'

                            newid = newid + 1

                            # add the row to the data
                            hdata['hindsight'].append(row)

                        # resave the file
                        with open(hindsightfile, 'w') as outfile:
                            json.dump(hdata, outfile, indent=4, sort_keys=True)


                        currentpresetid = self.GetLong(PRESET_COMBOBOX)
                        self.reload_dropdown(currentpresetid)

        if id == BTN_RESET_TO_DEFAULTS:
            # reset filters
            for i in xrange(30010, 30330, 10):
                self.SetBool(i, True)
                draw[i/10] = 1

            # reset display and view options
            self.SetBool(CHKBOX_RENDERSAFE/10, True)
            self.SetBool(CHKBOX_RENDERSAFE_CENTER/10, False)
            self.SetBool(CHKBOX_TITLESAFE/10, True)
            self.SetBool(CHKBOX_TITLESAFE_CENTER/10, False)
            self.SetBool(CHKBOX_ACTIONSAFE/10, False)
            self.SetBool(CHKBOX_ACTIONSAFE_CENTER/10, False)
            self.SetBool(CHKBOX_ENHANCEDOPENGL/10, True)
            self.SetBool(CHKBOX_SHADOWS/10, False)
            self.SetBool(CHKBOX_NOISES/10, False)
            self.SetBool(CHKBOX_TRANSPARENCY/10, False)
            self.SetBool(CHKBOX_POSTEFFECTS/10, False)
            self.SetBool(CHKBOX_LINEARWORKFLOR/10, True)
            self.SetBool(CHKBOX_BACKFACECULLING/10, False)
            self.SetBool(CHKBOX_ISOLINE_EDITING/10, False)
            self.SetBool(CHKBOX_NORMALS/10, True)
            self.SetBool(CHKBOX_TAGS/10, True)
            self.SetBool(CHKBOX_TEXTURES/10, True)
            self.SetBool(CHKBOX_XRAY/10, False)
            self.SetBool(CHKBOX_LAYERCOLOR/10, False)
            self.SetPercent(REAL_ACTIONSAFE_SIZE/10, 0.40, 0, 100, 1.0, False)
            self.SetPercent(REAL_TITLESAFE_SIZE/10, 1, 0, 100, 1.0, False)

        return True


class Hindsight(plugins.CommandData):
    dialog = None

    def Execute(self,doc):
        if datetime(2018, 6, 01) < datetime.now():
            gui.MessageDialog("The trial period for Hindsight has expired.", c4d.GEMB_OK)
            return False

        if self.dialog is None:
            self.dialog = MainDialog()
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=__plugin_id__, defaultw=1, defaulth=1)

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = MainDialog()
        return self.dialog.Restore(pluginid=__plugin_id__, secret=sec_ref)


if __name__ == '__main__':
    icon = bitmaps.BaseBitmap()
    dir, file = os.path.split(__file__)
    iconPath = os.path.join(dir, "res", "icons", "HindSight.png")
    icon.InitWith(iconPath)
    result = plugins.RegisterCommandPlugin(id = __plugin_id__,
                                  str = __plugin_title__,
                                  info = 0, 
                                  help = HELP_TEXT,
                                  dat = Hindsight(),
                                  icon = icon)

    if(result):
        print "{0} loaded. Copyright (C) {1} Charles Rowland. All rights reserved.".format(__plugin_title__,currentYear)