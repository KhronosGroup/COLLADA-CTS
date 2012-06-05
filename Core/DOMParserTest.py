# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.
from Common.DOMParser import *
from Common.CheckingModule import *
from Common.NodeInsCheck import *

# libraries from python
from xml.dom.minidom import parse, parseString
import os

_files_lst = []


def getText(nodelist):
    count = 0
    for node in nodelist:
        print count
        print node.nodeName
        count = count + 1
    print '\n'

# this function will generate the file list with target file type recursively.
def fetch(path=None,ext='.dae'):
	if not path: 
		path=os.getcwd()
		#print path
	if os.path.isdir(path): 
		lst = os.listdir(path)   
		if lst: 
			for each in lst:  
				spath=path+'/'+each  
				if os.path.isfile(spath):   
					# file type must be exactly matched
					if spath.endswith(ext)  == True:												
						_files_lst.append(spath) 
				fetch(spath, ext)
	#print _files_lst


def testRetriveIDFromEle(daeElement, strID):
    tag = 'No such id\n'
    id = ''
    
    xmlNode = GetElementByID(daeElement, strID)
    
    if xmlNode != None:
        tag = xmlNode.nodeName
        id = xmlNode.attributes['id'].value
        print 'id is %s' % id
    return id
    
# Test file name
def testRetriveIDFromFile(fileName, strID):
    
    nodeTag = None

    dom1 = parse(fileName)
    
    if dom1 == None:
        return
        
    root = dom1.getElementsByTagName("COLLADA")
    
    # search from root
    nodeTag = testRetriveIDFromEle(root[0], strID)
    
    dom1.unlink()
    
    return nodeTag
    
def testRetriveID():
    fetch()
    for each in _files_lst:
        res = testRetriveIDFromFile(each, 'cube')
        print 'res is %s' %res
        if res != 'cube':
            print 'None of id called cube in file '
            print each
            print '\n'
        else:
            print 'One element with id cube in file '
            print each
            print '\n'


#testRetriveID()

#
def testGetElementsByTags():
    inputFile = 'C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\animation_morph.dae'    
    dom1 = parse(inputFile)
    
    if dom1 == None:
        return
        
    root = dom1.getElementsByTagName("COLLADA")
    
    tagLst = ['library_controllers', 'controller', 'morph']
    
    result = GetElementsByTags(root[0], tagLst)
    
    # 
    print GetAttriByEle(result[0], 'source')
    print result[0].attributes.has_key('source')
    
    if len( result ) == 1 and GetAttriByEle(result[0], 'source') == '#mouthShape':
        print 'GetElementsByTags is Correct'
    else:
        print result[0].nodeName
        print result[0].attributes['source'].value
        print GetAttriByEle(result[0], 'source') == None
        print 'Wrong'

    dom1.unlink()
    
    inputFile = 'C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\id_dash.dae'    
    dom1 = parse(inputFile)
    
    if dom1 == None:
        return
        
    root = dom1.getElementsByTagName("COLLADA")
    
    tagLst = ['library_cameras', 'camera']
    
    result = GetElementsByTags(root[0], tagLst)
    
    # 
    print GetAttriByEle(result[0], 'id')
    print result[0].attributes.has_key('id')
    
    if len( result ) == 1 and GetAttriByEle(result[0], 'id') == 'this-is-a-id-test':
        print 'GetElementsByTags is Correct'
    else:
        print result[0].nodeName
        print result[0].attributes['source'].value
        print GetAttriByEle(result[0], 'source') == None
        print 'Wrong'

    dom1.unlink()

#testGetElementsByTags()

def testGetElementsByHierTags():
    inputFile = 'C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\unit.dae'    
    dom1 = parse(inputFile)
    
    if dom1 == None:
        return
        
    root = dom1.getElementsByTagName("COLLADA")
    
    tagLst = ['asset', 'subject']
    
    resultLst = GetElementsByHierTags(root[0], tagLst)
    
    print 'Result should be ASSET_TESTING and test result is'
    
    for each in resultLst:
        print each.childNodes[0].nodeValue
    
    dom1.unlink()
    
#testGetElementsByHierTags()

def testGetDataFromInput():
    inputFile = 'C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\animation_morph.dae'    
    dom1 = parse(inputFile)
    
    if dom1 == None:
        return
        
    root = dom1.getElementsByTagName("COLLADA")
    
    tagGeometryLst = ['library_geometries', 'geometry']    
    geometryLst = GetElementsByTags( root[0],  tagGeometryLst )
    
    tagInputLst = ['mesh', 'polylist', 'input']    
    inputInputLst = GetElementsByTags( geometryLst[0], tagInputLst)
    
    print 'length should be 30, 36 and 20'
    for eachInput in inputInputLst:
        res = None
        if GetAttriByEle( eachInput, 'semantic') == 'VERTEX':
            resVer = GetTargetElement( root[0], eachInput, 'source' )
            if resVer != None:
                # reach vertices element
                inputInVerLst = GetElementsByTags( resVer, ['input'])
                
                if len( inputInVerLst ) != 0:
                    print GetAttriByEle(inputInVerLst[0], 'semantic')
                    resFloat_array = GetDataFromInput(root[0], inputInVerLst[0], 'float_array')
                    if resFloat_array == None:
                        print 'Error: this should return some value.\n'                                        
                    else:                    
                        print GetAttriByEle( resFloat_array, 'id')
                        print GetAttriByEle( resFloat_array, 'count')
                else:
                    print 'Error: can not find input element'                
            else:
                print 'Can not find id for souce of pos'                
        else:
            res = GetDataFromInput(root[0], eachInput, 'float_array')
            if res == None:
                print 'Error: this should return some value.\n'
            else:
                print GetAttriByEle( res, 'id')
                print GetAttriByEle( res, 'count')

#testGetDataFromInput()

# suppose X->Y and Y->X should return original data
def testUpAxisFunctions():
    
    sourceV = vec3(0.3, 0.6, 0.9)
    resAdjust = AdjustUpAxisVec3(sourceV, 'Z_UP')    
    resRevert = RevertUpAxisVec3(resAdjust, 'Z_UP')    
    
    if sourceV != resRevert:
        print 'Error: up axis doesn\'t work'
        print inputV
        print resRevert
        print inputV == resRevert        
    else:
        print 'UpAxis works on first input.\n'
    
#testUpAxisFunctions()

# test DOMParserIO
def testDOMParserIO():
    del _files_lst[:]
    
    fetch()
    
    # add first as input and next 2 and 3 as output
    testIO = DOMParserIO(_files_lst[0], [_files_lst[1], _files_lst[2]])
    
    if testIO.Init() == 0:
        print 'Error: can not parse files to get root element.\n'
    else:
        print 'Correct initialization.\n'
    
    if testIO.GetRoot(_files_lst[0]) == None:
        print 'Error: can not access the first file.\n'
    else:
        print 'Correct\n'
    
    print 'You should have message about \'Error: do not have such key for...\''
    if testIO.GetRoot(_files_lst[3]) == None:
        print 'Correct\n'
    else:
        print 'Error: should not have access to the third file.\n'
        
    testIO.Delink()
    
#testDOMParserIO()

# test Add function:
def testAddAttribute():
    inputFile = 'C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\node__pc_1.dae'
    outputFiles = ['C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\node_lookat_pc_2.dae']
    
    testIO = DOMParserIO(inputFile, outputFiles)
    
    try:
        testIO.Init()
    except Exception, info:
        print 'Exception is thrown at line %d in DOMParserTest.py' %sys.exc_traceback.tb_lineno
        print ''
        print info
    
    root = testIO.GetRoot(inputFile)
    
    tagNodeLst = ['library_visual_scenes', 'visual_scene', 'node']
    
    nodeLst = GetElementsByTags(root, tagNodeLst)
    
    # add the element to first node test camera
    print 'First should be True and result is ' + str( AddAttribute( nodeLst[0], 'structID', '@*') )
    print 'Second should be False and result is ' + str( AddAttribute( nodeLst[0], 'name', 'test_cam_1') )
    
    # release memory
    testIO.Delink()
    
#testAddAttribute()

# ###############################
# Matrix Library testing
# ###############################
def testVec3():
    v1 = vec3(1.0, 1.0, 1.0)
    print 'v1 should be: 1.0, 1.0, 1.0'
    print v1.x
    print v1.y
    print v1.z
    
    if v1[1] == 1.0:
        print 'get index operators works well.\n'
    else:
        print 'get index operators doesn\'t work well.\n'
    
    v1[1] = 2.0
    if v1.y == 2.0:
        print 'set index operators works well.\n'
    else:
        print 'set index operators doesn\'t work well.\n'
    
    v2 = v1 * 0.5
    vres = vec3(0.5, 1.0, 0.5)
    
    if v2 == vres:
        print 'Multiplication with float is correct'
    else:
        print 'Multiplication with float is not correct'
    
    v3 = vec3(0.5, 1.0, 0.5)
    vres = vec3()
    
    if (v2 - v3 == vres):
        print 'Minus is correct'
    else:
        print 'Minus is not correct'
    
    vX = vec3(1.0, 0.0, 0.0)
    vY = vec3(0.0, 1.0, 0.0)
    vZ = vec3(0.0, 0.0, 1.0)

    if vX.IsXAxis(1e-6) == True:
        print 'IsXAxis is correct'
    else:
        print 'IsXAxis is not correct'
    
    if vY.IsXAxis(1e-6) == False:
        print 'IsXAxis is correct'
    else:
        print 'IsXAxis is not correct'
    
    if vY.IsYAxis(1e-6) == True:
        print 'IsYAxis is correct.'
    else:
        print 'IsYAxis is not correct.'
        
    if vX.IsYAxis(1e-6) == False:
        print 'IsYAxis is correct'
    else:
        print 'IsYAxis is not correct' 
    
    if vZ.IsZAxis(1e-6) == True:
        print 'IsZAxis is correct.'
    else:
        print 'IsZAxis is not correct.'

    if vY.IsZAxis(1e-6) == False:
        print 'IsZAxis is correct'
    else:
        print 'IsZAxis is not correct' 
        
    if vX.length() == 1.0:
        print 'length is correct'
    else:
        print 'length is not correct' 
        
    v5 = vec3(1.0, 2.0, 3.0)
    if abs( v5.length() - 3.7416574 ) < 1e-6:        
        print 'length is correct'
    else:
        print v5.length()
        print 'length is not correct'
        
    
    v6 = vec3(1.0, 2.0, 3.0)
    v6.normalize()
    if abs( v6.length() - 1.0 ) < 1e-6:
        print 'length is correct'
    else:
        print 'length is not correct'

    v7 = vec3(1.0, 2.0, 3.0)
    v71 = vec3(4.0, 5.0, 6.0)
    if abs( v7.dot(v71) - 32.0) < 1e-6:
        print 'dot is correct'
    else:
        print 'dot is not correct'
        
    v8 = vec3(1.0, 2.0, 3.0)
    v81 = vec3(4.0, 5.0, 6.0)
    vres = v8.crossproduct(v81)
    vcor = vec3(-3.0, 6.0, -3.0) # from cgkit.cgtypes import *
    if vres == vcor:
        print 'crossproduct is correct'
    else:
        print 'crossproduct is not correct'
    
    v9 = vec3(9.0, 5.0, 8.0)
    vres = v9.orthorand()
    if abs( v9.dot(vres) ) < 1e-6:
        print 'orthorand is correct'
    else:
        print 'orthorand is not correct'

#testVec3()

def testMat4():
    M0 = mat4()
    
    for indexRow in range(4):
        print [ M0[indexRow][0], M0[indexRow][1], M0[indexRow][2], M0[indexRow][3] ]
        
    M0.SetIdentity()

    MIdentity = mat4( 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0 )
    
    if M0 == MIdentity:
        print 'SetIndentity is correct'
    else:
        print 'SetIndentity is not correct'
        for indexRow in range(4):
            print [ M0[indexRow][0], M0[indexRow][1], M0[indexRow][2], M0[indexRow][3] ]
        
    
    vecT = vec3(100, 100, 100)
    M1 = mat4().translation(vecT)
    MRes = mat4()
    MRes.SetIdentity()
    MRes[0][3] = 100.0
    MRes[1][3] = 100.0
    MRes[2][3] = 100.0
    
    if M1 == MRes:
        print 'translation is correct'
    else:
        print 'translation is not correct'
    
    vecR = vec3(1.0, 0.0, 0.0)
    M2 = mat4().rotation(pi/4.0, vecR)
    MRes = mat4()
    MRes.SetIdentity()
    MRes[1][1] = 0.707107
    MRes[1][2] = -0.707107
    MRes[2][1] = 0.707107
    MRes[2][2] = 0.707107
    
    if MRes == M2:
        print 'rotation works'
    else:
        print 'rotation doesn\'t work'
    
    vecR = vec3(1.0, 1.0, 1.0)
    M2 = mat4().rotation(pi/4.0, vecR)
    MRes = mat4()
    MRes.SetIdentity()
    MRes[0][0] = 0.804738
    MRes[0][1] = -0.310617
    MRes[0][2] = 0.505879
    
    MRes[1][0] = 0.505879
    MRes[1][1] = 0.804738
    MRes[1][2] = -0.310617
    
    MRes[2][0] = -0.310617
    MRes[2][1] = 0.505879
    MRes[2][2] =0.804738
    
    if MRes == M2:
        print 'rotation works'
    else:
        print 'rotation doesn\'t work'
        
    vecS = vec3(2.0, 5.0, 7.0)
    M3 = mat4().scaling(vecS)
    MRes = mat4()
    MRes.SetIdentity()
    MRes[0][0] = vecS.x
    MRes[1][1] = vecS.y
    MRes[2][2] = vecS.z
    
    if MRes == M3:
        print 'scale works'
    else:
        print 'scale doesn\'t work'
    
    pos = vec3(2.0, 3.0, 4.0)
    target = vec3(1.0, 9.0, 8.0)
    up = vec3(0.0, 1.0, 0.0)
    
    M4 = mat4().lookAt(pos, target, up)
    MRes = mat4( 0.970143, 0.199889, -0.137361, 2.0, 0.0, 0.566352, 0.824163, 3.0, 0.242536, -0.799556, 0.549442, 4.0, 0.0, 0.0, 0.0, 1.0) # from cgkit.cgtypes import *
    if M4 == MRes:
        print 'lookat works'
    else:
        print 'lookat doesn\'t work'
        M4.printout()
    
    M5 = mat4( 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0 )
    M6 = mat4(  1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0 )
    MRes = mat4( 90.0, 100.0, 110.0, 120.0, 202.0, 228.0, 254.0, 280.0, 314.0, 356.0, 398.0, 440.0, 426.0, 484.0, 542.0, 600.0 )
    
    if M5 * M6 == MRes:
        print 'Matrix multiplication works'
    else:
        print 'Matrix multiplication doesn\'t work'

#testMat4()

# Go through files exported by Max and Maya to check whether transformation are eqaulvlent.
def testGetTransformationsOfNode():
    del _files_lst[:]
    
    fetch()
    
    for each in _files_lst:
        dom1 = parse(each)
        
        if dom1 == None:
            return
            
        root = dom1.getElementsByTagName("COLLADA")[0]
        
        if root == None:
            print 'Error: this may not be COLLADA DAE document.\n'
        
        visualSceneList = root.getElementsByTagName("visual_scene")
        
        if len(visualSceneList) == 0:
            continue
        
        visualScene = visualSceneList[0]
        
        nodeList = visualScene.childNodes
        
        print '\n\n'
        print each
        print '\n'
        
         # find unit:
        print 'unit value is: '
        print GetUnitValue(root)
        
        # fine up_axis
        print GetUpAxisStr(root)
        
        for eachNode in nodeList:
            res = GetTransformationsOfNode(eachNode, ['lookat', 'matrix', 'rotate', 'scale',  'skew',  'translate'])
            
            if res != None:
                if len(res) > 0:
                    for each in res:                        
                        print each.nodeName
                        print '\n'
                        tM = ConvertXMLtoMat(each, GetUnitValue(root), GetUpAxisStr(root))  # temp value
                        tM.printout()

                    bakedM = BakeTransformations(res, GetUnitValue(root), GetUpAxisStr(root))
                    
                    if bakedM != None:
                        print '\n Baked Matrix:\n'
                        bakedM.printout()
                    else:
                        print 'Not supported Baked: only scale, translate and rotate\n'
        
        dom1.unlink()

testGetTransformationsOfNode()

def testParseElement():
    inputFile = 'C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\node_lookat_pc_1.dae'
    outputFiles = ['C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\node_lookat_pc_2.dae']
    
    testIO = DOMParserIO(inputFile, outputFiles)
    
    try:
        testIO.Init()
    except Exception, info:
        print 'Exception is thrown at line %d in DOMParserTest.py' %sys.exc_traceback.tb_lineno
        print ''
        print info
    
    root = testIO.GetRoot(inputFile)
    posArrayEle = GetElementByID(root, 'cube-positions-array')
    if posArrayEle != None:
        resParse = ParseEleAsString(posArrayEle)
        
        if resParse[0] == True:
            vecStrLst = resParse[1]
            print '# of elements in here should be 24. And result is %d.\n' %len(vecStrLst)
            
            testStr = ''
            # reconstruct strings:
            for i in range( len( vecStrLst ) - 1):
                testStr = testStr + vecStrLst[i] + ' '
            testStr = testStr + vecStrLst[len( vecStrLst ) - 1]
            
            if testStr == posArrayEle.childNodes[0].nodeValue:
                print 'Correct'
            else:
                print 'Wrong'
                print 'Result should be ' + posArrayEle.childNodes[0].nodeValue
                print 'but it is ' + testStr
                print '\n\n'
        else:
            print 'Error ' + resParse[1]
            
        # for vector
        resParse = ParseEleAsVec3(posArrayEle)
        
        if resParse[0] == True:
            vecV3Lst  = resParse[1]
            
            print 'There should be 8 elements and result is %d\n' %len(vecV3Lst)
            
            testStr = ''
            # reconstruct string
            for i in range( len( vecV3Lst ) - 1 ):
                testStr = testStr + str(vecV3Lst[i][0]) + ' ' + str(vecV3Lst[i][1]) + ' ' + str(vecV3Lst[i][2]) + ' '
            testStr = testStr + str(vecV3Lst[len( vecV3Lst ) - 1][0]) + ' ' + str(vecV3Lst[len( vecV3Lst ) - 1][1]) + ' ' + str(vecV3Lst[len( vecV3Lst ) - 1][2])
            
            if testStr == posArrayEle.childNodes[0].nodeValue:
                print 'Correct'
            else:
                print 'Wrong'
                print 'Result should be ' + posArrayEle.childNodes[0].nodeValue
                print 'but it is ' + testStr
                print '\n\n'
                
        else:
            print 'Error: ' + resParse[1]        
    else:
        print 'Can not retrive that element.\n'  

# Get parse element 
# testParseElement()

# test the unit converter
def testConvert():
    dataInCentimeterLst = [-100, -100, 100, 100, -100, 100, -100, 100, 100, 100, 100, 100, -100, 100, -100, 100, 100, -100, -100, -100, -100, 100, -100, -100]
    
    d = parseString('<float_array>' + ConvertCentimeterToInch(dataInCentimeterLst) + '</float_array>')
    write_docs_to_file([d], 'centimeter2inch.xml')

    d = parseString('<float_array>' + ConvertCentimeterToFoot(dataInCentimeterLst) + '</float_array>')
    write_docs_to_file([d], 'centimeter2foot.xml')

#testConvert()

def testGenerateMultiScene():
    inputFile = 'C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\multi_visualscene.dae'
    
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
    numAngle = 15
    visualSceneLst = []
    visualSceneLst.append( resVisuLst[0].cloneNode(True) )

    for index in range (0, numAngle): 
        if GenerateMultiScene(visualSceneLst[index], index) == True:            
            visualSceneLst.append( resVisuLst[0].cloneNode(True) )
        else:
            print 'Error: can not find visual_scene'
    
    # remove the original one at very last
    visualSceneLst.pop()
    
    write_docs_to_file(visualSceneLst, 'scene.xml')
    
    testIO.Delink()

#testGenerateMultiScene()

# test the data structure utility:
def testDiffSortedList():
    listLong1 = [1]
    listSht1 = []
    resLst = [1]
    resTestLst = DiffSortedList(listLong1, listSht1)
    
    if resLst != resTestLst:
        print 'False'
        print 'Diff between first case should be ' + str( resLst )
        print str( resTestLst )
    else:
        print 'Test1 pass'
    
    listLong1 = [1, 8, 10]
    listSht1 = [10, 12]
    resLst = [1, 8, 12]
    resTestLst = DiffSortedList(listLong1, listSht1)
    
    if resLst != resTestLst:
        print 'False'
        print 'Diff between first case should be ' + str( resLst )
        print str( resTestLst )
    else:
        print 'Test2 pass'
    
    listLong1 = [1, 8, 10, 15]
    listSht1 = [10, 12]
    resLst = [1,8, 12, 15]
    resTestLst = DiffSortedList(listLong1, listSht1)
    
    if resLst != resTestLst:
        print 'False'
        print 'Diff between first case should be ' + str( resLst )
        print str( resTestLst )
    else:
        print 'Test3 pass'
    
    listLong1 = [1, 8, 110]
    listSht1 = [1, 8]
    resLst = [110]
    resTestLst = DiffSortedList(listLong1, listSht1)
    
    if resLst != resTestLst:
        print 'False'
        print 'Diff between first case should be ' + str( resLst )
        print str( resTestLst )
    else:
        print 'Test4 pass'
    
#testDiffSortedList()

def testPresCheckerClass():
    inputFile = 'C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\node_lookat_pc_1.dae'
    outputFiles = ['C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\node_lookat_pc_2.dae']
    
    testIO = DOMParserIO(inputFile, outputFiles)
    
    try:
        testIO.Init()
    except Exception, info:
        print 'Exception is thrown at line %d in DOMParserTest.py' %sys.exc_traceback.tb_lineno
        print ''
        print info
    
    testPChecker = PresChecker(testIO.GetRoot(inputFile), testIO.GetRoot(outputFiles[0]))
    
    # use id for the element
    resSetEle = testPChecker.ResetElementById('mainCamera')
    
    print 'id preservation should be false. And test result is: \n'
    
    ErrorMsg = 'Preservation is false.\n'
    # id preservation should be true:
    if resSetEle[0] == True:
        resChkAttri = testPChecker.checkAttri(['id'])
        
        if len(resChkAttri) == 0:
            print 'Error: returned wrong type of result.\n'
        else:
            print 'List is: '
        for each in resChkAttri:
            print each
        print '\n'
        
        if resChkAttri[0] == True:
            print 'id preservation is true.\n'
        else:
            print ErrorMsg
            
    else:
        print resSetEle[1]
        print'Can not retrive that element.\n'
    
    # test count in normal array
    resSetEle = testPChecker.ResetElementById('cube-normals-array')
    
    print 'count preservation should be true. And test result is: \n'
    
    if resSetEle[0] == True:
        resChkAttri = testPChecker.checkAttri('count')
        
        if resChkAttri[0] == True:
            print 'count preservation is true.\n'
        else:
            print ErrorMsg
            print resChkAttri[1]            
    else:
        print resSetEle[1]
        print 'Can not retrive that element.\n'
        
    # test layter attributes for node
    resSetEle = testPChecker.ResetElementById('testCamera')
    
    print 'layter preservation should be false. And test result is:\n'
    
    if resSetEle[0] == True:
        resChkAttri = testPChecker.checkAttri('layer')
        
        if resChkAttri[0] == True:
            print 'layer preservation is true.\n'
        else:
            print 'layer preservation is false.\n'
            print resChkAttri[1]            
    else:
        print resSetEle[1]
        print 'Can not retrive that element.\n'
    
    print '************\n'
    
    # test whether get attribute function works
    cubeEle = GetElementByID( testIO.GetRoot(inputFile) , 'cube_node' )
    
    if cubeEle == None:
        print 'Error: can not get that element. Please check id.'
    else:        
        print 'For attribute name, it should be true and Result is: ' + str( IsAttrExist(cubeEle, 'name' ) )
        print 'For attribute sid, it should be false and Result is: ' + str( IsAttrExist(cubeEle, 'sid' ) )
        
    # test whether under source it works to find attributs name under para
    sourceEle = GetElementByID( testIO.GetRoot(inputFile) , 'cube-positions' )
    
    if sourceEle == None:
        print 'Error: can not get that element. Please check id.'
    else:
        paraLst = sourceEle.getElementsByTagName('param')
        for eachPara in paraLst:
            print 'For attribute name, it should be true and Result is: ' + str( IsAttrExist(cubeEle, 'name' ) )
            
    
    testIO.Delink()
#testPresCheckerClass()

# test linkage functions:
def testCheckLinkage():
    inputFile = 'C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\animation_morph.dae'
    outputFiles = ['C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\animation_morph_1.dae']
    
    testIO = DOMParserIO(inputFile, outputFiles)
    
    try:
        testIO.Init()
    except Exception, info:
        print 'Exception is thrown at line %d in DOMParserTest.py' %sys.exc_traceback.tb_lineno
        print ''
        print info
    
    testPChecker = PresChecker(testIO.GetRoot(inputFile), testIO.GetRoot(outputFiles[0]))
    
    # check linkage
    idLst = [ 'mouthShape-morph-targets-array',  'mouthShape-morph-morph_weights-array']
    resSetEle = testPChecker.ResetElesByIds(idLst)
    
    if resSetEle[0] == True:
        # 
        res = testPChecker.checkLinkage(['string', 'float'])
        
        print 'The result should be true.\n ' 
        print 'The result is '
        print res[0]
    
    testIO.Delink()
    
#testCheckLinkage()

# Ths will test node checking function
def testNodeChecker():
    # pass basic only
    inputFileLst = []
    outputFileLstLst = []
    resLst = []
    
    inputFile1 = 'C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\cube_in_LNVS.dae'
    outputFiles1 = ['C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\cube_out_LNVS_Maya_NetAllied.dae']
    res1 = [True, False]
    inputFileLst.append(inputFile1)
    outputFileLstLst.append(outputFiles1)
    resLst.append(res1)
    
    inputFile2 = 'C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\cube_in_2insts.dae'
    outputFiles2 = ['C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\cube_in_2insts_Maya_NetAllied.dae']
    res2 = [True, False]
    inputFileLst.append(inputFile2)
    outputFileLstLst.append(outputFiles2)
    resLst.append(res2)
    
    inputFile3 = 'C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\cube_LN.dae'
    outputFiles3 = ['C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\cube_LN_Out1.dae']
    res3 = [True, True]
    inputFileLst.append(inputFile3)
    outputFileLstLst.append(outputFiles3)
    resLst.append(res3)

    inputFile4 = 'C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\cube_LN.dae'
    outputFiles4 = ['C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\cube_LN_Out2.dae']
    res4 = [True, True]
    inputFileLst.append(inputFile4)
    outputFileLstLst.append(outputFiles4)
    resLst.append(res4)

    # not pass intermediate: over limitation of instanciation
    inputFile5 = 'C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\cube_LN.dae'
    outputFiles5 = ['C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\cube_LN_Out3.dae']
    res5 = [True, False]
    inputFileLst.append(inputFile5)
    outputFileLstLst.append(outputFiles5)
    resLst.append(res5)
    
    # not pass intermediate: over limitation of instanciation
    inputFile6 = 'C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\cube_3insts.dae'
    outputFiles6 = ['C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\DOMParserTestCases\\cube_3insts_output.dae']
    res5 = [True, False]
    inputFileLst.append(inputFile5)
    outputFileLstLst.append(outputFiles5)
    resLst.append(res5)
    
    for index in range( len( inputFileLst ) ):
        
        inputFile = inputFileLst[index]
        outputFiles = outputFileLstLst[index]
        
        testIO = DOMParserIO(inputFile, outputFiles)
        
        try:
            testIO.Init()
        except Exception, info:
            print 'Exception is thrown at line %d in DOMParserTest.py' %sys.exc_traceback.tb_lineno
            print ''
            print info
        
        # DOM Root 
        testNodeChker = NodeChecker( testIO.GetRoot(inputFile), testIO.GetRoot(outputFiles[0]))
        
        testNodeChker.AddStructID()
        
        resCOLLADARootLst = testNodeChker.GetTwoRoots()
        
        # Find visual secne and library nodes then output
        # Apply struct id for both input and output: visual scene and library of node
        tagVSLst = ['library_visual_scenes', 'visual_scene']
        inputVSRootLst = GetElementsByTags(resCOLLADARootLst[0], tagVSLst)
        outputVSRootLst = GetElementsByTags(resCOLLADARootLst[1], tagVSLst)
        
        # build structure id for two visual scene
        if len( inputVSRootLst ) == 0 or len( outputVSRootLst ) == 0:
            print 'Error: can not load visual scene'
            return False

        tagLNLst = ['library_nodes']
        inputLNRootLst = GetElementsByTags(resCOLLADARootLst[0], tagLNLst)
        outputLNRootLst = GetElementsByTags(resCOLLADARootLst[1], tagLNLst)
        
        # build structure id for two library nodes
        if len( inputLNRootLst ) == 0: 
            print 'Error: can not load library node in input file.'
            write_docs_to_file([ inputVSRootLst[0] ] , 'cube_input.xml')
        else:
            write_docs_to_file([ inputVSRootLst[0],  inputLNRootLst[0] ] , 'cube_input.xml')

        if len( outputLNRootLst ) == 0:
            print 'Error: can not load library node in output file.'
            write_docs_to_file([ outputVSRootLst[0] ] , 'cube_output.xml')        
        else:        
            write_docs_to_file([ outputVSRootLst[0],  outputLNRootLst[0] ] , 'cube_output.xml')        
        
        # validate equaliveny
        resBasic = testNodeChker.CheckTwoVS()
        
        # build structure id for two library nodes
        if len( inputLNRootLst ) == 0: 
            print 'Error: can not load library node in input file.'
            write_docs_to_file([ inputVSRootLst[0] ] , 'cube_input_resetStrucId.xml')
        else:
            write_docs_to_file([ inputVSRootLst[0],  inputLNRootLst[0] ] , 'cube_input_resetStrucId.xml')

        if len( outputLNRootLst ) == 0:
            print 'Error: can not load library node in output file.'
            write_docs_to_file([ outputVSRootLst[0] ] , 'cube_output_resetStrucId.xml')        
        else:        
            write_docs_to_file([ outputVSRootLst[0],  outputLNRootLst[0] ] , 'cube_output_resetStrucId.xml')
        
        # test intermediate badge
        #print 'Check library_nodes'
        #print testNodeChker.CheckTwoLN()
        # print 'Check LN and VS'
        resIntermediate = testNodeChker.CheckVSLN()
        
        print '-----------------------'
        if resBasic == resLst[index][0] and resIntermediate == resLst[index][1]:            
            print 'Test ' + str( index ) + ' passed.'
        else:
            print 'Test ' + str( index ) + ' failded.'
        print '-----------------------'
        
        testIO.Delink()
    
#testNodeChecker()