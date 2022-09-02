import c4d
from c4d import documents, gui, plugins, bitmaps

import time, sys, os, subprocess
import logging

__plugin_id__ = 1031677
__version__ = "1.0"
__plugin_title__ = "Volumatic"

DUMMY = 1000
INPUT_THICKNESS = 1001

# String shown in status bar
HELP_TEXT = "Volumatic for TFD"



logging.basicConfig(level=logging.DEBUG)



class MainDialog(gui.GeDialog):
    '''Main Dialog Class'''

    def InitValues(self):
        ''' Called when the dialog is initialized by the GUI. True if successful, or False to signalize an error. '''

        print("{0} loaded.".format(__plugin_title__))
        return True

    def CreateLayout(self):
        '''Override - Called when C4D is about to display the dialog. True if successful, or False to signalize an error. '''

        self.SetTitle("Thickness")

        #input box
        self.GroupBegin(0, c4d.BFH_SCALEFIT, 1)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(5, 5, 5, 5)
        thickness = self.AddEditText(INPUT_THICKNESS, c4d.BFH_SCALEFIT, 100, 15)
        self.GroupEnd()

        #buttons
        self.GroupBegin(10000, c4d.BFH_SCALEFIT, 2)
        self.GroupBorderNoTitle(0)
        self.GroupBorderSpace(20, 5, 20, 5)
        self.AddDlgGroup(3)
        self.GroupEnd()
  
        return True


    def Message(self, msg, result):
        '''
        Override - Use to react to more messages.
        The return value depends on the message.
        '''

        pass

        return c4d.gui.GeDialog.Message(self, msg, result)

    
    def CoreMessage(self, id, msg):
        ''' Override this function if you want to react to C4D core messages. The original message is stored in msg. '''

        pass

        return c4d.gui.GeDialog.CoreMessage(self, id, msg)


    def Command(self, id, msg):
        doc = c4d.documents.GetActiveDocument()
        op = doc.GetActiveObject()

        #function to determin if the user entered a string or a float. returns a bool
        def CheckFloat(s):
            try:
                float(s)
                return True
            except ValueError:
                return False

        def ResetPSR():
            c4d.CallCommand(1019940)
            return True

        if id == 1:
            ''' constants '''
            #get the user input
            thickness = self.GetString(INPUT_THICKNESS)
            
            #check if the user entered a number or string. strings are punished with a popup.
            if CheckFloat(thickness):
                thickness = float(thickness)
            else:
                gui.MessageDialog("You need to enter a number")
                return False

            #get the objects radius
            boundingbox = op.GetRad()

            #make that full width
            full_width = boundingbox * 2
            
            #get the name of the original object for later use
            name = op.GetName()


            ''' clone object '''
            #make a clone of the object
            obj_clone = op.GetClone()

            #insert the clone as a child of op
            doc.InsertObject(obj_clone, parent = op, checknames = False)

            #scale the object down based on the user input
            obj_clone.Scale( (1-thickness/100) )

            #set the clone to be the active object
            doc.SetActiveObject(obj_clone,0)

            #reset the PRS of the clone
            reset = ResetPSR()

            #select both parent and child, connect and delte
            doc.SetActiveObject(op, 1)
            c4d.CallCommand(16768)
            op = doc.GetActiveObject()
            op.SetName(name)
            

            ''' collision tag '''
            #set the TFD tag on this object
            op.MakeTag(1023165)
            tfd_tag = op.GetTag(1023165)
            tfd_tag[c4d.ID_OBSTACLE] = True



            ''' turbulance fd container '''
            #add a new TDF container
            tfdc = c4d.BaseObject(1023131)
            
            #resize the containers grid size to match the parents
            tfdc[c4d.ID_VOLUME_DIM] = full_width

            #insert the container
            doc.InsertObject(tfdc, parent = op, checknames = False)

            #set the container as the active object
            doc.SetActiveObject(tfdc, 0)

            #reset the PSR of the container so its centered with the parent
            reset = ResetPSR()



            ''' emitter sphere '''
            #create the shpere
            emitter = c4d.BaseObject(5160)

            #set the radius to 50, so its a width of 100
            emitter[c4d.PRIM_SPHERE_RAD] = 50

            #insert the sphere
            doc.InsertObject(emitter, parent = tfdc, checknames = False)
            
            #set the sphere emitter as the active object
            doc.SetActiveObject(emitter,0)

            #make the sphere editable
            c4d.CallCommand(12236)



            ''' emitter sphere TFD emissions tag '''
            #make a tfd tag on the emitter
            emitter.MakeTag(1023165)

            #get the tag
            emitter_tag = emitter.GetTag(1023165)

            #set tag optioins
            emitter_tag[c4d.ID_TEMPERATURE] = 0.5
            emitter_tag[c4d.ID_DENSITY] = 0.3
            

            #close the dialog and force an update
            self.Close()
            c4d.EventAdd()

           
        if id == 2:
            self.Close()

        c4d.EventAdd()
        return True

    '''
    @staticmethod()
    def dowork(self):
        
        pass
    '''

    

class Volumatic(plugins.CommandData):

    dialog = None

    '''
    bc=c4d.BaseContainer()
    if c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD,c4d.BFM_INPUT_CHANNEL, bc):
        if bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QSHIFT:
        pass
    '''

    def Execute(self,doc):
        docMode = doc.IsEditMode()
        op = doc.GetActiveObject()

        #check to see if an object is selected
        if not(op):
            gui.MessageDialog("You need to select an object first")
            return False

        #check to see if the selected object is editable
        if op.GetType() != 5100:
            gui.MessageDialog("You need to select an editable object first")
            return False



        if self.dialog is None:
            self.dialog = MainDialog()

        return self.dialog.Open(dlgtype = c4d.DLG_TYPE_MODAL,
                                pluginid = __plugin_id__,
                                xpos = -1,
                                ypos = -1,
                                defaultw = 300,
                                defaulth = 0)




if __name__ == "__main__":
    icon = bitmaps.BaseBitmap()
    dir, file = os.path.split(__file__)
    iconPath = os.path.join(dir, "res", "icon.tif")
    icon.InitWith(iconPath)

    plugins.RegisterCommandPlugin(id = __plugin_id__,
                                  str = __plugin_title__,
                                  info = 0, 
                                  help = HELP_TEXT,
                                  dat = Volumatic(),
                                  icon = icon)