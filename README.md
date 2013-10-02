Camera Frustum Plugin
---------

This plugin adds a new locator node to maya- "cameraFrustum"
and a new undoable command - "createCameraFrustum"

How to use
--------
1. place "cameraFrustumPlugin.py" in your MAYA_PLUG_IN_PATH folder
2. select a perspective camera that you wish to add a frustum to
3. run "createCameraFrustum" in MEL ( "import maya.cmds as cmds; cmds.createCameraFrustum" - python)
