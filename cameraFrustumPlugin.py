'''
Created on Jul 9, 2013

@author: volodymyrkazantsev
'''

import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaRender as OpenMayaRender
import maya.OpenMayaUI as OpenMayaUI
 
import pymel.core as pm
 
glRenderer = OpenMayaRender.MHardwareRenderer.theRenderer()
glFT = glRenderer.glFunctionTable()



# -------------------------------------------------------------------------------- 
# Custom locator node that draws the camera frustum using openGL
class camFrustumNode(OpenMayaMPx.MPxLocatorNode):
    """
    A locator node that draws camera frustum using Maya OpenGL
    """
    nodeTypeName = "cameraFrustum"
    nodeTypeId = OpenMaya.MTypeId(0x0002920)

    def __init__(self):
        OpenMayaMPx.MPxLocatorNode.__init__(self)
        
    def getAttributeData(self):
        "[self] -> {'attr1',val1,'attr2',val2,..}. Evaluates input attribute"
        thisNode = self.thisMObject()
        attributeData = {}
        attributeData['horizontalFilmAperture'] = \
            OpenMaya.MPlug(thisNode, self.horizontalFilmAperture).asDouble()
        attributeData['verticalFilmAperture'] = \
            OpenMaya.MPlug(thisNode, self.verticalFilmAperture).asDouble()
        attributeData['nearClipPlane'] = \
            OpenMaya.MPlug(thisNode, self.nearClipPlane).asDouble()
        attributeData['farClipPlane'] = \
            OpenMaya.MPlug(thisNode, self.farClipPlane).asDouble()
        attributeData['focalLength'] = \
            OpenMaya.MPlug(thisNode, self.focalLength).asDouble()            
        attributeData['shaded'] = \
            OpenMaya.MPlug(thisNode, self.shaded).asBool()    
        dataHandle = OpenMaya.MPlug(thisNode, self.color).asMDataHandle()       
        attributeData['color'] = dataHandle.asFloatVector()

        return attributeData
    
    def calculateFrustumCorners(self,aData):
        "This method calculates eight corners of camera frustum"
        corners = {}
        
        horizontalFov = aData['horizontalFilmAperture'] * 0.5 / ( aData['focalLength'] * 0.03937 )
        verticalFov = aData['verticalFilmAperture'] * 0.5 / ( aData['focalLength'] * 0.03937 )
    
        farRight = aData['farClipPlane'] * horizontalFov
        farTop = aData['farClipPlane'] * verticalFov
    
        nearRight = aData['nearClipPlane'] * horizontalFov
        nearTop = aData['nearClipPlane'] * verticalFov

        corners['farTopRight']  = [farRight,farTop,-aData['farClipPlane']]
        corners['farTopLeft']   = [-farRight,farTop,-aData['farClipPlane']]
        corners['farLowLeft']   = [-farRight,-farTop,-aData['farClipPlane']]
        corners['farLowRight']  = [farRight,-farTop,-aData['farClipPlane']]
        
        corners['nearTopRight'] = [nearRight,nearTop,-aData['nearClipPlane']]   
        corners['nearTopLeft']  = [-nearRight,nearTop,-aData['nearClipPlane']]  
        corners['nearLowLeft']  = [-nearRight,-nearTop,-aData['nearClipPlane']] 
        corners['nearLowRight'] = [nearRight,-nearTop,-aData['nearClipPlane']]  
        
        return corners
        
    def drawBoundingLines(self, corners,view,status):
        
        
        glFT.glBegin( OpenMayaRender.MGL_LINES );
        
        if status == OpenMayaUI.M3dView.kDormant:
            glFT.glColor3f(0.0, 0.25, 0.05)
        #draw far frame
        glFT.glVertex3f( *corners['farTopRight'] )
        glFT.glVertex3f( *corners['farTopLeft'] )
        
        glFT.glVertex3f( *corners['farTopLeft'] )
        glFT.glVertex3f( *corners['farLowLeft'] )
        
        glFT.glVertex3f( *corners['farLowLeft'] )
        glFT.glVertex3f( *corners['farLowRight'] )
        
        glFT.glVertex3f( *corners['farLowRight'] )
        glFT.glVertex3f( *corners['farTopRight'] )
        
        #draw edges from far to near
        glFT.glVertex3f( *corners['farTopRight'] )
        glFT.glVertex3f( *corners['nearTopRight'] )

        glFT.glVertex3f( *corners['farTopLeft'] )
        glFT.glVertex3f( *corners['nearTopLeft'] )

        glFT.glVertex3f( *corners['farLowLeft'] )
        glFT.glVertex3f( *corners['nearLowLeft'] )

        glFT.glVertex3f( *corners['farLowRight'] )
        glFT.glVertex3f( *corners['nearLowRight'] )      
          
        #draw near frame
        glFT.glVertex3f( *corners['nearTopRight'] )
        glFT.glVertex3f( *corners['nearTopLeft'] )
        
        glFT.glVertex3f( *corners['nearTopLeft'] )
        glFT.glVertex3f( *corners['nearLowLeft'] )
        
        glFT.glVertex3f( *corners['nearLowLeft'] )
        glFT.glVertex3f( *corners['nearLowRight'] )
        
        glFT.glVertex3f( *corners['nearLowRight'] )
        glFT.glVertex3f( *corners['nearTopRight'] )
      
        glFT.glEnd();
        

                   
    def drawFrustumSides(self, corners, shadeColor):
        "renders four quads on the sides of the frustum"
        
        glFT.glClearDepth(1.0)        
        glFT.glEnable(OpenMayaRender.MGL_BLEND)
        glFT.glEnable(OpenMayaRender.MGL_DEPTH_TEST)
        glFT.glDepthFunc(OpenMayaRender.MGL_LEQUAL)
        glFT.glShadeModel(OpenMayaRender.MGL_SMOOTH)
        glFT.glBlendFunc(OpenMayaRender.MGL_SRC_ALPHA, OpenMayaRender.MGL_ONE_MINUS_SRC_ALPHA)
        glFT.glDepthMask( OpenMayaRender.MGL_FALSE )
        glFT.glColor4f(shadeColor.x, shadeColor.y, shadeColor.z, 0.1)
        
        #let's start drawing quads
        glFT.glBegin(OpenMayaRender.MGL_QUADS)
        #Right side
        glFT.glVertex3f(*corners['farTopRight'])
        glFT.glVertex3f(*corners['farLowRight'])
        glFT.glVertex3f(*corners['nearLowRight'])
        glFT.glVertex3f(*corners['nearTopRight'])
        
        #Top side
        glFT.glVertex3f(*corners['farTopRight'])
        glFT.glVertex3f(*corners['nearTopRight'])
        glFT.glVertex3f(*corners['nearTopLeft'])
        glFT.glVertex3f(*corners['farTopLeft'])
        
        #Left side
        glFT.glVertex3f(*corners['farTopLeft'])
        glFT.glVertex3f(*corners['nearTopLeft'])
        glFT.glVertex3f(*corners['nearLowLeft'])
        glFT.glVertex3f(*corners['farLowLeft'])
        
        #Low side
        glFT.glVertex3f(*corners['farLowRight'])
        glFT.glVertex3f(*corners['farLowLeft'])
        glFT.glVertex3f(*corners['nearLowLeft'])
        glFT.glVertex3f(*corners['nearLowRight'])
                
        glFT.glEnd()
        
        
    def draw(self, view, path, style, status):
        "This is the main draw method called by Maya's viewport renderer"
        glFT.glPushAttrib(OpenMayaRender.MGL_ALL_ATTRIB_BITS)
        attributeValues = self.getAttributeData()
        frustumCorners = self.calculateFrustumCorners(attributeValues)
        
        view.beginGL()
        self.drawBoundingLines(frustumCorners,view,status)
        if attributeValues['shaded'] and (style == OpenMayaUI.M3dView.kFlatShaded or 
                                          style == OpenMayaUI.M3dView.kGouraudShaded):
            self.drawFrustumSides(frustumCorners,attributeValues['color'])
        glFT.glPopAttrib()
        view.endGL()
        
     

    @classmethod
    def nodeCreator(cls):
        return OpenMayaMPx.asMPxPtr(cls())
  
    @classmethod
    def nodeInitializer(cls):
        "Adding all node attributes here"
        #unitAttr = OpenMaya.MFnUnitAttribute()
        #typedAttr = OpenMaya.MFnTypedAttribute()
        numAttr = OpenMaya.MFnNumericAttribute()

        cls.horizontalFilmAperture = numAttr.create(
                                           "horizontalFilmAperture", 
                                           "hfa", 
                                           OpenMaya.MFnNumericData.kDouble, 
                                           1.0)
        cls.addAttribute(cls.horizontalFilmAperture)
        
        cls.verticalFilmAperture = numAttr.create(
                                           "verticalFilmAperture", 
                                           "vfa", 
                                           OpenMaya.MFnNumericData.kDouble, 
                                           0.5625)        
        cls.addAttribute(cls.verticalFilmAperture)
        
        cls.nearClipPlane = numAttr.create(
                                           "nearClipPlane", 
                                           "ncp", 
                                           OpenMaya.MFnNumericData.kDouble, 
                                           0.01)
        cls.addAttribute(cls.nearClipPlane)
        
        cls.farClipPlane = numAttr.create(
                                           "farClipPlane", 
                                           "fcp", 
                                           OpenMaya.MFnNumericData.kDouble, 
                                           100.0)
        cls.addAttribute(cls.farClipPlane)
        
        cls.focalLength = numAttr.create(
                                           "focalLength", 
                                           "fl", 
                                           OpenMaya.MFnNumericData.kDouble, 
                                           35.0)
        cls.addAttribute(cls.focalLength)
        
        cls.shaded = numAttr.create(
                                           "shaded", 
                                           "sh", 
                                           OpenMaya.MFnNumericData.kBoolean, 
                                           True)
        cls.addAttribute(cls.shaded)
        
        cls.color = numAttr.createColor( "color", "cl" )
        numAttr.setDefault(0.2, 0.8, 0.7)
        numAttr.setUsedAsColor(1)
        cls.addAttribute(cls.color)
        
        
# --------------------------------------------------------------------------------
class AEcameraFrustumTemplate(pm.uitypes.AETemplate):
    _nodeType = 'cameraFrustum' 
    def __init__(self, nodeName):
        self.beginScrollLayout()

        self.beginLayout("Frustum Display",collapse=0)
        self.addControl("horizontalFilmAperture")
        self.addControl("verticalFilmAperture")
        self.addControl("nearClipPlane")
        self.addControl("farClipPlane")
        self.addControl("focalLength")
        self.addControl("shaded")
        self.addControl("color")
        self.endLayout()
    
        self.addExtraControls()
        self.endScrollLayout()


# --------------------------------------------------------------------------------
# Maya command to create camFrustumNode with Undo/Redo support
class createCameraFrustum(OpenMayaMPx.MPxCommand):
    @staticmethod
    def commandName():
        return "createCameraFrustum"

    @staticmethod
    def commandCreator():
        return OpenMayaMPx.asMPxPtr( createCameraFrustum() )

    def findCameraInSelection(self):
        selection = pm.ls(sl=True)
        assert len(selection)>0, "Nothing is selected. Select a camera"
        assert len(selection)<2, "Multiple objects selected. Select camera only"
        
        if pm.nodeType(selection[0])=='transform':
            camShapeLst = pm.listRelatives(selection[0], type='camera')
            assert len(camShapeLst)>0, "No camera selected"
            return (selection[0], camShapeLst[0])
        
        elif pm.nodeType(selection[0])=='camera':
            parentTransform = pm.listRelatives(selection[0], parent=True)
            return (parentTransform,selection[0])
        
        raise StandardError("No camera is selected")
    
    def isUndoable(self):
        return True

    def doIt(self, args = OpenMaya.MArgList() ):
        self.camera = self.findCameraInSelection()
        self.cameraFrustumNodeName = self.camera[0].name()+"frustum"
        self.redoIt()        
        
    
    def redoIt(self):
        self.frustumNode = pm.createNode('cameraFrustum',name=self.cameraFrustumNodeName, parent=self.camera[0])
        self.camera[1].horizontalFilmAperture.connect(self.frustumNode.horizontalFilmAperture)
        self.camera[1].verticalFilmAperture.connect(self.frustumNode.verticalFilmAperture)
        self.camera[1].nearClipPlane.connect(self.frustumNode.nearClipPlane)
        self.camera[1].farClipPlane.connect(self.frustumNode.farClipPlane)
        self.camera[1].focalLength.connect(self.frustumNode.focalLength)        
         
    def undoIt(self):
        if self.frustumNode:
            pm.delete(self.frustumNode)
            self.frustumNode = None
    
# --------------------------------------------------------------------------------
# def maya_useNewAPI():
#     """
#     The presence of this function tells Maya that the plugin produces, and
#     expects to be passed, objects created using Maya Python API 2.0.
#     """
#     pass


def initializePlugin(plugin):
    pluginFn = OpenMayaMPx.MFnPlugin(plugin)
    try:
        pluginFn.registerNode(camFrustumNode.nodeTypeName, 
                            camFrustumNode.nodeTypeId, 
                            camFrustumNode.nodeCreator, 
                            camFrustumNode.nodeInitializer, 
                            OpenMayaMPx.MPxNode.kLocatorNode)
        
        pluginFn.registerCommand(createCameraFrustum.commandName(), createCameraFrustum.commandCreator )
    except:
        sys.stderr.write( "Failed to register node: %s" % camFrustumNode.nodeTypeName)
 
def uninitializePlugin(plugin):
    pluginFn = OpenMayaMPx.MFnPlugin(plugin)
    try:
        pluginFn.deregisterNode(camFrustumNode.nodeTypeId)
        pluginFn.deregisterCommand(createCameraFrustum.commandName())
    except:
        sys.stderr.write( "Failed to deregister plugin: %s" % camFrustumNode.nodeTypeName)