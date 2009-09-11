import os
import sys
import traceback
from decimal import *
from xml.dom.minidom import parse, parseString
from DOMMatrix import *
from math import *
from types import *


# define a COLLADA class
class COLLADAIO:
    def __init__(self, inputFilename_):
        self.inputFilename = inputFilename_
        self.root = None
        
    def Init(self):
        # try to load COLLADA document
        try:
            domInput = parse(self.inputFilename)
        except Exception, info:
            print 'Error: in DOM parser I/O: Importing\n'
            print 'Exception is thrown at line %d in DOMParser.py' %sys.exc_traceback.tb_lineno
            print info[0]
            return False
        
        # get root
        rootLst = domInput.getElementsByTagName("COLLADA")
        
        if len( rootLst ) == 0:
            print "Error: No COLLADA information in imported file.\n"
            return False
        elif len( rootLst ) == 1:
            self.root = rootLst[0]
        else:
            print "Error: Too many COLLADA information in imported file.\n"
            return False
        
    def GetRoot(self):
        return self.root
    
    def Delink(self):
        self.root.unlink()

# An IO parser class which will provide parsing file to xml node and return root of input and output file.
class DOMParserIO:
    def __init__(self, inputFilename_, exportFilenameList_):
        self.inputFilename = inputFilename_
        self.exportFilenameList = exportFilenameList_
        self.dict = {} # dictionary for I/O loading
        self.status = 0
    
    def Init(self):        
        # Parse files and construct dictionary:
        try:            
            domInput = parse(self.inputFilename)            
        except Exception, info:            
            print 'Error: in DOM parser I/O: Importing\n'
            print 'Exception is thrown at line %d in DOMParser.py' %sys.exc_traceback.tb_lineno
            print info[0]
            return False # unsuccessful 
        
        # get the input of root
        rootInput = domInput.getElementsByTagName("COLLADA")
        
        if len(rootInput) == 0:
            print "Error: No COLLADA information in imported file.\n"
            return False
    
        self.dict[self.inputFilename] = [domInput, rootInput[0]]
        
        # get the exported files
        try:
            for eachFile in self.exportFilenameList:
                #print 'File is ' + eachFile
                domExp = parse(eachFile)
                rootExp = domExp.getElementsByTagName("COLLADA")
                if rootExp == None or len(rootExp) == 0:
                    print "No COLLADA information in exported file.\n"
                    return False
                self.dict[eachFile] = [domExp, rootExp[0]]

        except Exception, info: 
            print 'Error: in DOM parser I/O: Exporting\n'            
            print 'Exception is thrown at line %d in DOMParser.py' %sys.exc_traceback.tb_lineno
            print info[0]
            return False # Unsuccessfully initialization
            
        # set the status as ready
        self.status = 1
    
    def GetRoot(self, filename):
        if self.status != 1:
            print 'Error: You need to init Root first.\n'
            return None
        
        if self.dict.has_key(filename):
            return self.dict[filename][1]
        else:
            print 'Error: do not have such key for %s\n' %filename
            return None

    def Delink(self):
        # at the end of code, unlink the dom and DAE files
        for each in self.dict:
            self.dict[each][1] = None
            self.dict[each][0].unlink()
        
        self.dict.clear()   
    
# ########################################
# GET section
# ########################################

# define a file list object and root
# Find a daeElement by id under specified element, it is not an Element list!
def GetElementByID(daeElement, strId):
    
    # check if current element has id attribute
    #print daeElement.nodeName
    #print daeElement.attributes.keys()
    
    if daeElement.attributes != None: 
        # if there is attributes, check whether there is an attribute called id
        if daeElement.attributes.has_key('id'):            
            # check if current element matches the strId
            if daeElement.attributes['id'].value == strId:
                return daeElement
                
    # No match for current elements, check its children:
    for each in daeElement.childNodes:
        Result = GetElementByID(each, strId)
        
        if Result != None:            
            return  Result        
    
    return None

def GetElementBySID(daeElement, strSId):
    
    # check if current element has id attribute
    #print daeElement.nodeName
    #print daeElement.attributes.keys()
    
    if daeElement.attributes != None: 
        # if there is attributes, check whether there is an attribute called id
        if daeElement.attributes.has_key('sid'):            
            # check if current element matches the strId
            if daeElement.attributes['sid'].value == strSId:
                return daeElement
                
    # No match for current elements, check its children:
    for each in daeElement.childNodes:
        Result = GetElementBySID(each, strSId)
        
        if Result != None:            
            return  Result        
    
    return None

# define a function which will get elements by list of tags:
# Pre: all levels elements are unique until last one: user may have to use it by several times if any parent elements is not unique
def GetElementsByTags(daeElement, tagLst):
    if daeElement != None and len(tagLst) > 0:
        intermediate = daeElement
        for index in range( len(tagLst)-1 ):
            # get list of each
            Lst = intermediate.getElementsByTagName(tagLst[index])
            if len(Lst) == 1:
                intermediate = Lst[0]
            else:
                return []
        
        Lst = intermediate.getElementsByTagName( tagLst[len(tagLst)-1] )
        return Lst
    else:
        return []

# this only search tag match during direct child, no grandchildren
def GetElementsByHierTags(daeElement, tagLst):
    if daeElement != None and len(tagLst) > 0:
        intermediate = daeElement
        for index in range( len(tagLst)-1 ):
            # get list of each child
            Lst = []
            for eachChild in intermediate.childNodes:
                if eachChild.nodeName == tagLst[index]:
                    Lst.append( eachChild)
            
            if len(Lst) == 1:
                intermediate = Lst[0]
            else:
                return []
        
        Lst = intermediate.getElementsByTagName( tagLst[len(tagLst)-1] )
        return Lst
    else:
        return []

# find the occurances of a path search
def FindElement(daeElement, tagLst):
    if daeElement != None and len(tagLst) > 0:
        intermediate = [daeElement]
        for index in range( len(tagLst) ):
            Lst = []
            for x in range( len(intermediate) ):
                nLst = intermediate[x].getElementsByTagName( tagLst[index] )
                for y in range( len(nLst) ):
                    Lst.append( nLst[y] )

            if len(Lst) == 0:
                return []
            else:
                intermediate = Lst

        return intermediate
    else:
        return []

# define a function which will get attributes from a element
def GetAttriByEle(daeElement, attrName):
    # check whether element has that attributes
    if daeElement.attributes != None:
        #if there is attribute:
        if daeElement.attributes.has_key(attrName):
            # return the value:
            return daeElement.attributes[attrName].value
        else:
            return None
    else:
        return None

#define function which will judge whether an element have an attribute
def IsAttrExist(inputEle, attr):    
    if GetAttriByEle(inputEle, attr) != None:
        return [True, '']
    else:
        return [False, 'No attribute exist.']

# This function will return THE INTERNAL reference only reference element in url format: #nodeid
# For example, 'source' attribute in <input> and url in <instance_node>
def GetTargetElement(Root, inputEle, Attri):
    SourceStr = GetAttriByEle( inputEle, Attri)
    if SourceStr == None or SourceStr[0] != '#':
        print 'Error: This element doesn\'t have required attribute or try to get external target'
        return None
    else:
        # remove # at first letter
        idSource = SourceStr[1:len( SourceStr )]
        resEle = GetElementByID(Root, idSource)
        if resEle == None:
            print 'Error: This element doesn\'t have responding target related to id of source: '+idSource
            return None
        else:
            return resEle
    
#define function which will parse input and then access data in its resource.
def GetDataFromInput(Root, inputEle, dataTag):
    sourceEle = GetTargetElement(Root, inputEle, 'source')
    
    if sourceEle != None:
        # get this array to inputLsts
        resArrays = GetElementsByTags( sourceEle, [dataTag] )
        if len(resArrays) > 0:
            return resArrays[0]
        else:            
            print 'There is either no such data array or too many of those arrays.'
            return None
    else:
        return None

# Assume that Root is under COLLADA
def GetUnitValue(Root):
    if Root.nodeName != 'COLLADA':
        return None
    else:
        #print Root.nodeName
        for each in Root.childNodes:
            #print each.nodeName
            if each.nodeName == 'asset':
                # process and find unit
                if each.getElementsByTagName('unit') != None and len( each.getElementsByTagName('unit') ) > 0:
                    unitEle = each.getElementsByTagName('unit')[0]
                    if unitEle.attributes != None:
                        # check attribute meter
                        if unitEle.attributes.has_key('meter'):
                            # return the vale as float
                            return float( unitEle.attributes['meter'].value )
                        else:
                            print 'No meter find, assume default one\n' 
                            return float(1.0)
                    else:
                        print 'No attribute find, assume default one\n' 
                        return float(1.0)
                else:
                    print 'No unit find, assume default one\n' 
                    return float(1.0)
    
    print 'Error: no asset found.\n'
    return None
    
def GetUpAxisStr(Root):
    if Root.nodeName != 'COLLADA':
        return None
    else:
        for each in Root.childNodes:
            #print Root.nodeName
            #print each.nodeName
            if each.nodeName == 'asset':
                # process the up axis
                upaxisEleList = each.getElementsByTagName('up_axis')
                if upaxisEleList != None and len( upaxisEleList ) > 0:
                    upaxisEle = upaxisEleList[0]
                    # check nade value:
                    if upaxisEle.childNodes[0] != None:
                        return upaxisEle.childNodes[0].nodeValue.split()[0]
                    else:                           
                        print 'No value stored.\n'
                        return None
                else:
                    print 'Default Value'
                    return 'Y_UP'

    print 'Error: no asset found.\n'
    return None

# #################################
# Add section
# #################################

# This function will add attribute name and its value to specific element:
# return True if add successfully, otherwise, false
def AddAttribute(daeElement, attriName, attriValue, IsOverwriteable=False):
    if daeElement == None:
        return False
    else:
        if daeElement.attributes != None:
            if daeElement.attributes.has_key(attriName):
                if IsOverwriteable:
                    daeElement.setAttribute(attriName, attriValue)
                    return True
                else:
                    return False
            else:
                daeElement.setAttribute(attriName, attriValue)
        else:
            daeElement.setAttribute(attriName, attriValue)
        return True

# #################################
# Utility section
# #################################

def IsEleMatchType(daeElement, tagName):
    if daeElement == None:
        return False
    else:
        if daeElement.nodeName == tagName:
            return True
        else:
            return False

# This function can only convert simple url not exteral one
def InternalUrl2Id(urlStr):
    if (urlStr[0] != '#'):
        return ''
    else:
        return urlStr[1:len(urlStr)]

# #############################################
# MATRIX section
# #############################################

# This function will return all transformation information under specified node.
# Input: xml node of a node
# Output: list of transformations elements
def GetTransformationsOfNode(daeNodeEle, tranList =['lookat', 'matrix', 'rotate', 'scale',  'skew',  'translate']):
    listTrans = []
    if not IsEleMatchType(daeNodeEle, 'node'):
        return None
    else:
        for eachNode in daeNodeEle.childNodes:
            for eachTran in tranList:
                if eachNode.nodeName == eachTran:
                    listTrans.append(eachNode)

    return listTrans

def Degree2Rad(deg):
    degree = float(deg)
    return degree * pi / 180.0
    
# Adjust UpAxis for vector3 from X_UP, Z_UP to Y_UP
def AdjustUpAxisVec3(sourceV, up_axis):
    resV = vec3()
    
    if ( up_axis == 'X_UP' ):
        # X_UP to Y_UP: swtich the X -> Y and -Y -> X
        resV[0] = -sourceV[1]
        resV[1] = sourceV[0]
        resV[2] = sourceV[2]
        return resV
    elif ( up_axis == 'Z_UP' ):
        # Z_UP to Y_Up: swtich the Z -> Y and -Y -> Z
        resV[0] = sourceV[0]
        resV[1] = sourceV[2]
        resV[2] = -sourceV[1]       
        return resV
    elif ( up_axis == 'Y_UP' ):
        resV = sourceV
        return resV
    else:
        print 'Error: unknown type for UP_AXIS.\n'
        return None

# Revert will convert from Y_UP to Z_UP and X_UP
def RevertUpAxisVec3(sourceV, up_axis):
    resV = vec3()
    
    if up_axis == 'Y_UP':
        # Y_UP to Y_UP:
        resV = sourceV
        return resV
    elif up_axis == 'X_UP':
        # Y_UP to X_UP: Y -> X and -X -> Y
        resV[0] = sourceV[1]
        resV[1] = -sourceV[0]
        resV[2] = sourceV[2]
        return resV
    elif up_axis == 'Z_UP':
        # Y_UP to Z_UP: Y->Z and -Z->Y
        resV[0] = sourceV[0]
        resV[2] = sourceV[1]
        resV[1] = -sourceV[2]
        return resV
    else:
        print 'Error: unknown type for UP_AXIS'
        return None

def AdjustUnitVec3(sourceV, unit = 1.0):
    resV = sourceV * unit
    return resV

# this will tuning the vector through both unit and up_axis from source to target, if isMatrixChk is false, then just convert everything to standard axis and unit
def TunningVec3(sourceV, srcUnit='1.0', srcUp_axis='Y_UP', isMatrixChk=False, tgtUnit='1.0', tgtUp_axis='Y_UP'):
    # process up axis
    proUpdirV = TunningVec3UpAxis(sourceV, srcUp_axis, isMatrixChk, tgtUp_axis)
    
    # process unit
    # from src to standard
    proUnitV = AdjustUnitVec3(proUpdirV, float(srcUnit))
    if isMatrixChk == True:
        resV = AdjustUnitVec3(proUnitV, 1.0/float(tgtUnit))
    return resV
    
def TunningVec3UpAxis(sourceV, srcUp_axis='Y_UP', isMatrixChk=False, tgtUp_axis='Y_UP'):
    # convert from source up_axis to standar axis
    stdV = AdjustUpAxisVec3(sourceV, srcUp_axis)
    
    resV = vec3()
    
    # if need to check matrix, 
    if isMatrixChk == True:
        # we need to convert one axis to another
        resV = RevertUpAxisVec3(stdV, tgtUp_axis)
    else:
        resV = stdV
    
    return stdV
    
# This function will convert all matrix type to a 4 * 4 matrix in cgkit
# Need to know unit and axis_up as well for comparision between matrix stack
# convert every transformation in default mode and then compare
def ConvertXMLtoMat(daeTranEle, unit='1.0', up_axis='Y_UP'):
    
    name = daeTranEle.nodeName
        
    # local vector
    localV = vec3()
    
    if len(daeTranEle.childNodes) == 1: # The transformation is defined along schema
        if name == 'translate': # will be affected by unit and up_axis
            tra = daeTranEle.childNodes[0].nodeValue.split()            
            if len(tra) == 3:
                initV = vec3(float(tra[0]), float(tra[1]), float(tra[2]))
    
                # check up_axis:
                traV = AdjustUpAxisVec3(initV, up_axis)
                if traV == None:
                    return None
                
                # process unit
                traV = AdjustUnitVec3(traV, float(unit))
                    
                # generate translation matrix with static method
                resM = mat4().translation( traV )
                return resM
            else:
                print 'Error: More than or less than 3 numbers'
                return None                
    
        elif name == 'rotate': # will be affected by up_axis
        # for rotation, it is vect 3 and degree        
            # parse the number
            rot = daeTranEle.childNodes[0].nodeValue.split()
            if len(rot) == 4: #Too many or too less number there
                initV = vec3(float(rot[0]), float(rot[1]), float(rot[2]))
                
                # check up_axis:
                rotV = AdjustUpAxisVec3(initV, up_axis)
                if rotV == None:
                    return None
                
                # convert from degree (COLLADA) to rad                
                rad = Degree2Rad(rot[3])                
                # seperate as vec3 and degree
                resM = mat4().rotation(rad, rotV)                
                return resM
            else:
                print 'Error: Too many or too less number there\n'
                return None
        
        elif name == 'matrix': # It will be considered as a baked one so do not process it: too many possibility for this one. But myabe decomposed on some format?
            numbers = daeTranEle.childNodes[0].nodeValue.split()
            if len(numbers) == 16:
                
                # convert number to matrix
                resM = mat4(float(numbers[0]), float(numbers[1]), float(numbers[2]), float(numbers[3]), 
                float(numbers[4]), float(numbers[5]), float(numbers[6]), float(numbers[7]), 
                float(numbers[8]), float(numbers[9]), float(numbers[10]), float(numbers[11]), 
                float(numbers[12]), float(numbers[13]), float(numbers[14]), float(numbers[15]))
                
                return resM
            else:
                print 'Error: Too many or too less numbers for matrix.\n'
                return None
                
        elif name == 'scale': # will be affected by up_axis
            sca = daeTranEle.childNodes[0].nodeValue.split()
            if len (sca) == 3:
                initV = vec3(float(sca[0]), float(sca[1]), float(sca[2]))
                
                # check up axis;
                scaV = AdjustUpAxisVec3(initV, up_axis)                    
                if scaV == None:
                    return None
                    
                resM = mat4().scaling(scaV)
                return resM
            else:
                print 'Error: Incorrect number of elements for scale'
                return None
        
        elif name == 'lookat': # will be affected by unit and up_axis
            paramsLookat = daeTranEle.childNodes[0].nodeValue.split()
            if len(paramsLookat) == 9:                
                posInitV = vec3( float(paramsLookat[0]), float(paramsLookat[1]), float(paramsLookat[2]) )
                targetInitV = vec3( float(paramsLookat[3]), float(paramsLookat[4]), float(paramsLookat[5]) )
                upInitV = vec3( float(paramsLookat[6]), float(paramsLookat[7]), float(paramsLookat[8]) )
                
                # process UP_AXIS:
                posV = AdjustUpAxisVec3(posInitV, up_axis)
                if posV == None:
                    return None
                    
                targetV = AdjustUpAxisVec3(targetInitV, up_axis)
                if targetV == None:
                    return None
                        
                upV = AdjustUpAxisVec3(upInitV, up_axis)
                if upV == None:
                    return None
                
                # process unit
                posV      = AdjustUnitVec3(posV, float(unit))
                targetV  = AdjustUnitVec3(targetV, float(unit))
                # no unit needed for up vector upV       = AdjustUnitVec3(upV, float(unit))
                
                resM = mat4().lookAt(posV, targetV, upV)
                return resM
            else:
                print 'Error: Incorrect number of elements for lookat'
                return None
        elif name == 'skew':
            print 'Not supported yet.\n'
            return None
        else:
            print "Unknow type\n"
            return None
    else:
        print 'Error: number of children is not matched\n'
        return None
    
    return None
    
# Just bake matrix for only scale, rotate and traslate, take input as xml element
def BakeTransformations(xmlMatList, unit = '1.0', up_axis='Y_UP', nameList=['rotate', 'scale', 'translate']):
    resM = mat4(1.0)
    
    # post multiply in the order in which they are specified with the ,node>
    for eachEle in xmlMatList:
        flag = 0
        for eachName in nameList:
            if eachEle.nodeName == eachName:
                flag = 1
                break
        
        if flag == 0: # can find some element not in name list
            return None
        else:
            eachM = ConvertXMLtoMat(eachEle, unit, up_axis)
            if eachM == None:
                print 'Error: null matrix.\n'
                return None
            else:
                #print 'Each Matrix:\n'
                #print each
                resM = resM * eachM

    return resM

# This will judge whether a string is a float number or not
def isFloat(str):
   try:
       tmpF = float(str)
   except ValueError:
       return False
   return True

# Judge whether two value are equal
def IsValueEqual(value1, value2, type, epsilon = 1e-6):
    if type == 'string':
        return value1 == value2
    elif type == 'float':
        return abs(value1 - value2) < epsilon
    elif type == 'vector3':
        oldEpsilon = setEpsilon(epsilon)
        res = (value1 == value2)
        setEpsilon(oldEpsilon)
        return res

# Parse node value as string
def ParseEleAsString(daeElement):
    if len( daeElement.childNodes ) > 1:
        return [False, 'The elements have children elements so can not parse value at this step.\n']
    else:
        return [True,  daeElement.childNodes[0].nodeValue.split()]

# Parse node value as string
def ParseEleAsFloat(daeElement):
    strLst = []
    
    if len( daeElement.childNodes ) > 1:
        return [False, 'The elements have children elements so can not parse value at this step.\n']
    elif len( daeElement.childNodes ) == 0:
        return [False, 'The elements have no children elements so can not parse value at this step.\n']
    else:
        strLst = daeElement.childNodes[0].nodeValue.split()
    
    floatLst = []
    
    for eachStr in strLst:
        if isFloat( eachStr ):
            floatLst.append( float( eachStr ) )
        else:
            del floatLst[:]
            return [False, 'Error: some are not float number.\n']
    
    return [True, floatLst]

# Parse node value as vector
def ParseEleAsVec3(daeElement):
    strLst = []
    
    if len( daeElement.childNodes ) > 1:
        return [False, 'The elements have multiple children elements so can not parse value at this step.\n']
    elif len( daeElement.childNodes ) == 0:
        return [False, 'The elements have no children elements so can not parse value at this step.\n']
    else:
        strLst = daeElement.childNodes[0].nodeValue.split()
    
    vecLst = []
    
    count = len( strLst ) / 3
    if count * 3 != len( strLst ):
        return [False, 'Error: can not be list of vec3.\n']
    else:
        for i in range(count):
            if isFloat( strLst[ 3 * i + 0] ) and isFloat( strLst[ 3 * i + 1] ) and isFloat( strLst[ 3 * i + 2] ):
                v = vec3( float( strLst[ 3 * i + 0]), float( strLst[ 3 * i + 1] ), float( strLst[ 3 * i + 2] ) )
                vecLst.append(v)
            else:
                return [False, 'Error: some string can not be converted for float.\n']
        return [True, vecLst]

# #######################
# Converter
# #######################
def GetInNewUnit(data, ratio):
    resStr = ''
    for eachVal in data:
        valInMeter = eachVal * ratio
        
        if abs(valInMeter) < 1E-6:
            valDe = Decimal( '0.0' )
        else:
            valDe = Decimal( str(valInMeter) ) + Decimal( '0.0' )
        resStr = resStr +  str(valDe) + ' '
    return resStr

def ConvertCentimeterToInch(valueInInchLst):
    return GetInNewUnit(valueInInchLst, 0.393701)
    
def ConvertCentimeterToFoot(valueInInchLst):
    return GetInNewUnit(valueInInchLst, 0.032808)

def ConvertInchesToMeter(valueInInchLst):
    return GetInNewUnit(valueInInchLst, 0.0254)

def ConvertMetersToInch(valueInMeterLst):
    return GetInNewUnit(valueInMeterLst, 1.0/0.0254)

# #######################
# Generate multi scenes
# #######################

# Input should be a head of visual scene
# Pre: daeElement only has flat children
# This function will change id of all nodes
def GenerateMultiScene(daeVisualScene, Index, attriNameLst = ['id', 'name']):
    
    if daeVisualScene.nodeName != 'visual_scene':
        return False
    else:
        # add index to id of scene first
        idValue = GetAttriByEle(daeVisualScene, 'id')
        
        if idValue != None:
            daeVisualScene.setAttribute('id', idValue+str(Index))
        else:
            return False
        
        # need to change id of child node and attatch index to their id:
        for eachNode in daeVisualScene.childNodes:
            if eachNode.nodeName == 'node':
                
                for eachAttr in attriNameLst:
                    Value = GetAttriByEle(eachNode, eachAttr)
                    if Value != None:
                        eachNode.setAttribute(eachAttr, Value+str(Index))

    return True
        
# #######################
# Write file section
# #######################
def write_docs_to_file(docList, name="data.xml"):
    file_object = open(name, "w")
    for each in docList:
        file_object.write( each.toprettyxml() )
    file_object.close()
    
# #######################
# Data structure utility: not covered by python library or google result
# #######################
def DiffSortedList(LstLong, LstSht):
        # find different of two sorted list
        indexLong = 0
        indexSht = 0
        diffLst = []
        
        for index in range( len(LstLong) ):
            if indexSht == len( LstSht):
                break
            
            if LstLong[ indexLong ] < LstSht[ indexSht ]:
                # if found an element in longlist is bigger than in shorter, put it in diff and increase index of longlist                
                diffLst.append( LstLong[ indexLong ] )
                indexLong = indexLong + 1
            elif LstLong[ indexLong ] > LstSht[ indexSht ]:
                # if finally that element in longer list is bigger than the shorter one, put element of shortlist in diff and increase index of shortlist
                diffLst.append( LstSht[ indexSht ] )
                indexSht = indexSht + 1
            else:
                # when meet something same, increase both of them
                indexLong = indexLong + 1
                indexSht = indexSht + 1
        
        # put all left in longer list to difference list:
        diffLst.extend( LstLong[indexLong:len(LstLong)] )
        diffLst.extend( LstSht[indexSht:len(LstSht)] )
        
        return diffLst