from DOMParser import *

# libraries from python
from xml.dom.minidom import parse, parseString
import os

def GenerateTestDataMultiScene():
    inputFile = '..\\..\\StandardDataSets\\collada\\scene\\animation\\multi_visualscene\\multi_visualscene_blessed.dae'
    
    testIO = COLLADAIO(inputFile)
        
    try:
        testIO.Init()
    except Exception, info:
        print 'Exception is thrown at line %d in DOMParserTest.py' %sys.exc_traceback.tb_lineno
        print ''
        print info
        
    testIO.Init()
    
    colladaRoot = testIO.GetRoot()
    
    tagVisuLst = ['library_visual_scenes', 'visual_scene']        
    resVisuLst  = GetElementsByHierTags(colladaRoot, tagVisuLst)
    
    # generate the multiple scene
    totalDegree = 180
    numFrame = 15
    eachDegree = totalDegree / numFrame
    testCameraCon = 'testCamera'
    visualSceneLst = []
    visualSceneLst.append( resVisuLst[0].cloneNode(True) )

    for index in range (0, numFrame): 
        if GenerateMultiScene(visualSceneLst[index], index) == True:            
            # Add rotation data as well
            visualSceneNode = visualSceneLst[index]
            for eachChild in visualSceneNode.childNodes:
                # search for camera node: it comes with id testCamera
                idValue = GetAttriByEle(eachChild, 'id')
                if idValue != None:
                    if idValue.find( testCameraCon ) != -1:
                        # check the rotation part
                        rotateYElem = GetElementBySID( eachChild, 'rotateY' )
                        # change last number
                        rot = rotateYElem.childNodes[0].nodeValue.split()
                        if len(rot) == 4: #Too many or too less number there
                            initV = vec3(float(rot[0]), float(rot[1]), float(rot[2]))
                        else:
                            print 'Error, it is not a rotation data.\n'
                        
                        currDegree = index * eachDegree
                        
                        rotateYElem.childNodes[0].nodeValue = rot[0] + ' ' + rot[1] + ' ' + rot[2] + ' ' + str( currDegree )
                    
            # Add original one for next iteration
            visualSceneLst.append( resVisuLst[0].cloneNode(True) )            
        else:
            print 'Error: can not find visual_scene'
    
    # remove the original one at very last
    visualSceneLst.pop()
    
    write_docs_to_file(visualSceneLst, 'scene.xml')
    
    testIO.Delink()

GenerateTestDataMultiScene()