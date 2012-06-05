# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import os
import sys
from xml.dom.minidom import parse, parseString
from types import *

# local modules that checking modules depend on:
from DOMParser import *

# Assumption1 : all nodes are coming with id
# Assumption2 : no duplicate instance under same parent in test cases: for example, following are not accepted because they are providing redundant data and useless in applications:
# <node id='n1'>
#   <instance_node url="#nodes"/>
#   <instance_node url="#nodes"/>

_Error_Instance_RED_Msg_ = 'Error: redundant url found.'
_Error_Instance_NUL_Msg_ = 'Error: null url found.'

# This is child node structure container: it will contains two list, one is id list and another is url list
#class childNodeStr:
#    def __init__(self, idLst_, urlLst_):
#        self.__idLst = idLst_
#        self.__urlLst = urlLst_
    
#    def IsValidSingle
class NodeChecker:
    def __init__(self, InputRoot_, OutputRoot_):
        self.__inputRoot = InputRoot_
        self.__outputRoot = OutputRoot_
        self.__structId = 'structID'
        self.__numInstantiation = 0 
        self.__maxInstantiation = 1 # maxium is 1
        self.__tranLst = ['lookat', 'matrix',   'skew', 'rotate', 'scale', 'translate']
        self.__tranCode = 't' # matrix
        self.__childDict = {'asset':'a', 'instance_camera':'ic', 'instance_controller':'ico',  'instance_geometry':'ig', 'instance_light':'il', 'instance_node':'in', 'node':'n', 'extra':'e'}
        
        self.__inputVS = None
        self.__outputVS = None
        
        self.__inputLN = None
        self.__outputLN = None
        
        self.__ResetStructIdStatus = -1
        
        # Apply struct id for both input and output: visual scene and library of node
        tagVSLst = ['library_visual_scenes', 'visual_scene']
        inputVSLst = GetElementsByTags(self.__inputRoot, tagVSLst)
        outputVSLst = GetElementsByTags(self.__outputRoot, tagVSLst)
        
        # build visual scene
        if len( inputVSLst ) == 0 or len( outputVSLst ) == 0:
            print 'Error: can not load visual scene'
        else:
            self.__inputVS = inputVSLst[0]
            self.__outputVS = outputVSLst[0]
        
        # build library of node
        tagLNLst = ['library_nodes']
        
        inputLNLst = GetElementsByTags(self.__inputRoot, tagLNLst)
        outputLNLst = GetElementsByTags(self.__outputRoot, tagLNLst)
        
        if len( inputLNLst ) > 0:
            self.__inputLN = inputLNLst[0]
        
        if len( outputLNLst ) > 0:
            self.__outputLN = outputLNLst[0]

    # This function will add struct id to each node under rootNode
    # structId will be a list of children element representation.
    # Those struct id will solve problem when instanciation will result in reuse of id.
    def __AddStructIDRes(self, rootNode, rootCOLLADA):
        IsTrans = False
        strucId = ''
        
        for eachEle in rootNode.childNodes:
            # map elements as childDic
            name =  eachEle.nodeName
            
            if name in self.__tranLst:
                if IsTrans == False:
                    # add it to struct id
                    strucId = strucId + self.__tranCode + ' ' # seperator
                IsTrans = True
            else:
                if self.__childDict.has_key(name):
                    strucId = strucId + self.__childDict[name]
                    if name == 'node':
                        # get subnode structure id:
                        subNodeIdLst = self.__AddStructIDRes( eachEle, rootCOLLADA )
                        if subNodeIdLst[0] == False:
                            return [False, subNodeIdLst[1]]
                        else:
                            strucId = strucId + '_' + subNodeIdLst[1].replace(' ', '_')                    
                    elif name == 'instance_node':
                        # find ulr target:
                        nodeUrl = GetTargetElement( rootCOLLADA, eachEle, 'url' )
                        if nodeUrl == None:
                            return [False, 'missing url']
                        nodeUrlIdLst = self.__AddStructIDRes( nodeUrl, rootCOLLADA )
                        if nodeUrlIdLst[0] == False:
                            return [False, nodeUrlIdLst[1]]
                        else:
                            # add it to id
                            strucId = strucId + '_' + nodeUrlIdLst[1].replace(' ', '_')                       
                            AddAttribute(eachEle, self.__structId, nodeUrlIdLst[1].replace(' ', '_'))    
                    strucId = strucId + ' '
                else:
                    if name != '#text':
                        err_msg = 'Error: some element is not recognized.' + name
                        print err_msg
                        return [False, err_msg]
                    else:
                        continue
        
        AddAttribute(rootNode, self.__structId, strucId)
        
        return [True, strucId]

    # because order of transformation is fixed so need to change _ between them to * for correct processing    
    def __ResetTransInStructIDRes(self, rootNode):
        # check the structure id first:
        if rootNode.attributes != None:
            if rootNode.attributes.has_key(self.__structId):                
                # reset the sturcture id: originally, __childDict['instance_node'] = 'in', now we replace every 'in' as 'n'
                oldStrucId = rootNode.attributes[self.__structId].value
                # replace _ between m, r, t, s as *:
                newStrucIdLst = list( oldStrucId )
                
                # target list 
                kLst = ['m', 'r', 't', 's']
                for index in range( len(newStrucIdLst) ):
                    if newStrucIdLst[index] in kLst:
                        if ( newStrucIdLst[index + 1] == '_' or newStrucIdLst[index + 1] == ' ') and newStrucIdLst[index + 2] in kLst:
                            newStrucIdLst[index+1] = '*'
                
                newStrucId = ''.join(newStrucIdLst)
                
                # replace old struct id with new one
                rootNode.setAttribute(self.__structId, newStrucId)
                
        
        for eachEle in rootNode.childNodes:
            self.__ResetTransInStructIDRes(eachEle)

        return

    # root is COLLADA
    def AddStructID(self):
        
        if self.__inputVS != None:
            self.__AddStructIDRes(self.__inputVS, self.__inputRoot)
        
        if self.__outputVS != None:
            self.__AddStructIDRes(self.__outputVS, self.__outputRoot)
        
        if self.__inputLN != None:
            self.__AddStructIDRes(self.__inputLN, self.__inputRoot)
            
        if self.__outputLN != None:
            self.__AddStructIDRes(self.__outputLN, self.__outputRoot)

        # reset transformation order
        #self.__ResetTransInStructIDRes(self.__inputRoot)
        #self.__ResetTransInStructIDRes(self.__outputRoot)
        
        return True
    
    def SetNumInst(self, num):
        self.__numInstantiation = num
    
    def GetNumInst(self):
        return self.__numInstantiation
    
    def __GetIdofChdNodes(self, parentNode):
        childDict = dict()
        for each in parentNode.childNodes:
            name = each.nodeName
            if name == 'node':
                idStr = GetAttriByEle(each, 'id')
                if idStr != None:
                    # add those node and id to dictionary
                    if not childDict.has_key(idStr):
                        childDict[idStr] = each
                    else:
                        print 'Error: id redundant.'
                        return None
                else:
                    print 'Error: not support testing node without id.'
                    return None
        return childDict

    def __GetUrlofInstanceNodes(self, parentNode):
        lst = []
        for each in parentNode.childNodes:
            name = each.nodeName
            if name == 'instance_node':
                if each.attributes != None:
                    urlStr = GetAttriByEle(each, 'url')
                    if urlStr != None:
                        lst.append( urlStr )
                    else:
                        del lst[:]
                        print 'Error url can not be none'
                        return [_Error_Instance_NUL_Msg_]
        
        # check whether there are two same url in the instance:
        redudantChkDict = dict()
        
        for each in lst:
            if redudantChkDict.has_key( each ):
                del lst[:]            
                return [_Error_Instance_Msg_]
            else:
                redudantChkDict[each] = 1
        
        # return if redundant checking pass
        return lst
        
    def __IsValidUrlMsg(self, insLst):
        if ( len( insLst ) == 1 and ( insLst[0] ==  _Error_Instance_Msg_ or insLst[0] == _Error_Instance_NUL_Msg_) ):
            return False
        else:
            return True
    
    # In library of node, they must be the same under schema and no instance replacement in it. Recursively function call.
    # This is for intermediate badge checking
    def __CheckTwoLNRec(self, root1, root2):

        # check each child
        chdDict1 = self.__GetIdofChdNodes(root1)
        chdDict2 = self.__GetIdofChdNodes(root2)
        
        # sort id (i.e., key of dictionary)
        idChdLst1 = chdDict1.keys()
        idChdLst1.sort()
        idChdLst2 = chdDict2.keys()
        idChdLst2.sort()
        
        if idChdLst1 == idChdLst2:
            # check url of instance nodes
            insLst1 = self.__GetUrlofInstanceNodes(root1)
            insLst1.sort()
            insLst2 = self.__GetUrlofInstanceNodes(root2)
            insLst2.sort()
            
            # check if redundant case happends
            if ( not self.__IsValidUrlMsg(insLst1) ) or ( not self.__IsValidUrlMsg(insLst2) ): 
                print _Error_Instance_Msg_
                return False
            else:
                # check whether two instance list are the same
                if insLst1 == insLst2:
                    # when roots are leave of tree: no more node
                    if len( idChdLst1 ) == 0:
                        return True
                    else:
                        # start to compare children
                        for index in range( len( idChdLst1 ) ):
                            child1 = chdDict1[ idChdLst1[index] ]
                            child2 = chdDict2[ idChdLst2[index] ]
                            res = self.__CheckTwoLNRec(child1, child2)
                            if res == False:
                                return res
                        
                        # if all child node checking finished
                        return True
                else:
                    return False # two instance list are not the same
        else:
            return False # two child list are not same

    # Input are two document roots
    def CheckTwoLN(self):
        if self.__inputRoot == None or self.__outputRoot == None:
            print 'Error: root of dom is not ready.'
            return False
            
        if self.__inputLN == None or self.__outputLN == None:
            return False
        
        return self.__CheckTwoLNRec(self.__inputLN, self.__outputLN)
    
    # first element is always longer one: both are sorted, if there is more than one different item, return false
    def __DiffListsMaxOneDiff(self, LstLong, LstSht):
        
        diffLst = DiffSortedList(LstLong, LstSht)
        
        if len(diffLst) > self.__maxInstantiation:
            return [False, []]
        else:
            return [True, diffLst]
    
    # checking instance: we only allow single instantiation
    # PRE: all inputs should be sorted.
    def __ValidateIns(self, idLstInput, urlLstInput, idLstOutput, urlLstOutput):
        if self.__numInstantiation >= self.__maxInstantiation:
            return [False, '']
        
        # number of idLstInput should be just 1 more than
        if len( urlLstInput ) > len( urlLstOutput ) + self.__maxInstantiation:
            return [False, '']
        
        # This additional one should be in the id list after convert to id
        # Find url which is missing in both
        
        resCmp = [False, '']
        if urlLstInput != urlLstOutput:
            #print 'Debug: url ' + str(urlLstInput)
            #print 'Debug: url ' + str(urlLstOutput)
            resCmp = self.__DiffListsMaxOneDiff(urlLstInput, urlLstOutput)
            
            missingUrl = ''
            
            if resCmp[0] == True:
                missingUrl = resCmp[1][0]                
            else:
                return [False, '']
        else:
            # if two url list are the same, then it can not be correct because id list are different.
            return [False, '']
        
        #print 'missing url: ' + missingUrl
        # remove all # in url list and they should be the same after sorting        
        inputAllLst = []
        inputAllLst.extend( idLstInput )
        inputAllLst.extend( urlLstInput )
        #print 'Debug: input id: ' + str( idLstInput )
        #print 'Debug: input url: ' + str(urlLstInput )
        
        outputAllLst = []
        outputAllLst.extend( idLstOutput )
        outputAllLst.extend( urlLstOutput )
        #print 'Debug: output id:' + str(idLstOutput)
        #print 'Debug: output url:' + str(urlLstOutput)
        
        for eachStr in inputAllLst:
            if eachStr[0] == '#':
                eachStr = InternalUrl2Id( eachStr )
        
        for eachStr in outputAllLst:
            if eachStr[0] == '#':
                eachStr = InternalUrl2Id( eachStr )
        
        if inputAllLst.sort() != outputAllLst.sort():
            return [False, '']
        
        return [True, resCmp[1]]
    
    # PRE: struct id has been reset already
    # Given a url and a root, need to validate them as same:
    # This should be called only once for passing intermediate badge when application has a single instianciation.
    def __ValidateUrlWithSubTree(self, url, nodeIdOutput, rootInput, rootOutput):
        # check by id
        #print 'url is: ' + url
        id = InternalUrl2Id(url)
        
        # find node element from input
        nodeInput = GetElementByID( rootInput, id)
        
        #print 'id is: ' + nodeIdOutput
        # find node element in output dom
        nodeOutput = GetElementByID( rootOutput, nodeIdOutput)
        
        if nodeInput == None or nodeOutput == None:
            print 'Error: can not find start node.'
            return False
        
        # check reset or not
        if self.__ResetStructIdStatus == -1:
            print 'No structure id ready'
            return False
        
        # compare two node
        return self.__CheckTwoVSRes(nodeInput, nodeOutput)

    # will be used for check intermediate badge
    def __CheckNodesByIdRes(self, nodeRoot1, nodeRoot2):
        # treat instance_node and node seperately:
        # all instance_node should have same url based on sorted url
        # get url list:
        urlLst1 = []
        for eachEle in nodeRoot1.childNodes:
            if eachEle.nodeName == 'instance_node':
                urlLink = GetAttriByEle( eachEle, 'url')
                if urlLink != None:
                    urlLst1.append( urlLink )
                else:
                    print 'Invalid url in input instance_node'
                    return False

        urlLst2 = []
        for eachEle in nodeRoot2.childNodes:
            if eachEle.nodeName == 'instance_node':
                urlLink = GetAttriByEle( eachEle, 'url')
                if urlLink != None:
                    urlLst2.append( urlLink )
                else:
                    print 'Invalid url in output instance_node'
                    return False

        # all node should have same id (sorted)
        idDict1 = self.__GetIdofChdNodes( nodeRoot1 )
        idDict2 = self.__GetIdofChdNodes( nodeRoot2 )
        
        # sort those result because that we do not need the order to be exact the same:
        urlLst1.sort()
        urlLst2.sort()
        idLst1 = idDict1.keys()
        idLst1.sort()
        idLst2 = idDict2.keys()
        idLst2.sort()
        
        if urlLst1 == urlLst2 and idLst1 == idLst2:
            # check each node only:
            for eachId in idLst1:
                res = self.__CheckNodesByIdRes( idDict1[ eachId ], idDict2[ eachId ] )
                if res == False:
                    print 'Child Node with id ' + eachId + ' did not pass the test'
                    return False
        else:
                # first validtae whether there is only one instanciation happens at current level
                resDiffUrl = self.__ValidateIns( idLst1, urlLst1,  idLst2, urlLst2 )
                # if yes, 
                if resDiffUrl[0] ==True:
                    # update the number of __numInstantiation:
                    self.__numInstantiation = self.__numInstantiation + 1
                    # Find the id difference
                    #print 'Debug: before id diff: ' + str( idLst2 )
                    #print 'Debug: before id diff: ' + str( idLst1 )
                    
                    resDiffIds = self.__DiffListsMaxOneDiff( idLst2, idLst1 )
                    if resDiffIds[0] == True:
                        return self.__ValidateUrlWithSubTree(resDiffUrl[1][0], resDiffIds[1][0], self.__inputRoot, self.__outputRoot)
                    else:
                        print 'The instantiation is not valid'
                        return False
                else:
                    # can not be valid so exit
                    print 'The limit of instantiation is broken'
                    #print 'Debug: Input: ' + 'ids: ' + str( idLst1 ) + 'urls: ' + str( urlLst1 )
                    #print 'Debug: Output: ' + 'ids: ' + str( idLst2 ) + 'urls: ' + str( urlLst2 )
                    return False
        
        # scan children as well
        return True
    
    # This function will only be called when need to do basic badge test
    def __ResetStructIdRes(self, rootNode):
        # check the structure id first:
        if rootNode.attributes != None:
            if rootNode.attributes.has_key(self.__structId):
                # reset the sturcture id: originally, __childDict['instance_node'] = 'in', now we replace every 'in' as 'n'
                oldStrucId = rootNode.attributes[self.__structId].value
                # replace in as n
                newStrucId = oldStrucId.replace( self.__childDict['instance_node'], self.__childDict['node'] )
                # replace old struct id with new one
                rootNode.setAttribute(self.__structId, newStrucId)
        
        for eachEle in rootNode.childNodes:
            self.__ResetStructIdRes(eachEle)

        return

    # convert struct id to list of strings
    def __ConvertStruId(self, structId):
        # replace '_' with ' '
        strRes = structId.replace('_', ' ')
        
        # split the strings
        strLst = strRes.split()

        # sort the list of string
        strLst.sort()
        
        # debug
        #print structId
        #print strLst
        #print '========'
        
        return  strLst
    
    # define the same function: two struct id are the same is we find that they have same content which can be in different order
    def __IsStructIdEqual(self, structId1, structId2):
        if type( structId1) != str or type(structId2) != str:
            print 'Error: input are not string in __IsStructIdEqual'
            return False
        
        return self.__ConvertStruId(structId1) == self.__ConvertStruId(structId2)

    # Pre: all struct id are reset
    def __CheckTwoVSRes(self, rootNode1, rootNode2):        
        # if there is no similar structure id, return false
        if not rootNode1.attributes.has_key(self.__structId):
            print 'First Node doesn\'t have attribute' + self.__structId
            print rootNode1.nodeName
        elif not rootNode2.attributes.has_key(self.__structId):
            print 'Second Node doesn\'t have attribute' + self.__structId
        
        #print 'Info:'
        #print self.__IsStructIdEqual(rootNode1.attributes[self.__structId].value, rootNode2.attributes[self.__structId].value)
        
        if self.__IsStructIdEqual(rootNode1.attributes[self.__structId].value, rootNode2.attributes[self.__structId].value):
            
            numNodeAndIns1 = 0
            
            for eachEle in rootNode1.childNodes:
                if eachEle.nodeName == 'node' or eachEle.nodeName == 'instance_node':
                    numNodeAndIns1 = numNodeAndIns1 + 1
            
            numNodeAndIns2 = 0
            
            for eachEle in rootNode2.childNodes:
                if eachEle.nodeName == 'node' or eachEle.nodeName == 'instance_node':
                    numNodeAndIns2 = numNodeAndIns2 + 1
            
            if numNodeAndIns1 == numNodeAndIns2:
                
                # when compare, recursely visit instance_node as node as well
                for eachEle1 in rootNode1.childNodes:
                    
                    if eachEle1.nodeName == 'node' or eachEle1.nodeName == 'instance_node':
                        res = False
                        IsMatch = False
                        for eachEle2 in rootNode2.childNodes:
                            if eachEle2.nodeName == 'node' or eachEle2.nodeName == 'instance_node':
                                if self.__IsStructIdEqual( eachEle1.attributes[ self.__structId ].value, eachEle2.attributes[ self.__structId ].value ):
                                    IsMatch = True
                                    
                                    if eachEle1.nodeName == 'node' and eachEle1.nodeName == eachEle2.nodeName:
                                        res = self.__CheckTwoVSRes( eachEle1, eachEle2 )
                                        #print 'Both nodes ' + str(res)
                                    else:
                                        # replace instance_node with node
                                        eachEleTarget1 = None
                                        eachEleTarget2 = None
                                        
                                        if eachEle1.nodeName == 'instance_node':
                                            eachEleTarget1 = GetTargetElement(self.__inputRoot, eachEle1, 'url')
                                            if eachEleTarget1 == None:
                                                print _Error_Instance_NUL_Msg_
                                                return False
                                        else:
                                            eachEleTarget1 = eachEle1
                                        
                                        if eachEle2.nodeName == 'instance_node':
                                            eachEleTarget2 = GetTargetElement(self.__inputRoot, eachEle2, 'url')
                                            if eachEleTarget2 == None:
                                                print _Error_Instance_NUL_Msg_
                                                return False
                                        else:
                                            eachEleTarget2 = eachEle2
                                        
                                        res = self.__CheckTwoVSRes( eachEleTarget1, eachEleTarget2 )
                                        #print 'At least one instance_node ' + str(res)
                                    
                                    if res == True:
                                        break
                                    else:                                        
                                        return False
                        
                        if IsMatch == False:
                            print 'No match found between child of first and second.\n'
                            return IsMatch
                    
                # if all child node pass, return True
                return True
            else:
                print 'Number of nodes: ' + str(numNodeAndIns1) + ' ' + str(numNodeAndIns2)
                return False
        else:            
            print 'Error: Structure ID: ' + rootNode1.attributes[self.__structId].value + ' ' +  rootNode2.attributes[self.__structId].value
            return False
        
    # check Visual Scene, those will be allowed that any id in library has been changed.
    def CheckTwoVS(self):
        # treat each instance_node as node now: reset the sturcture id: originally, __childDict['instance_node'] = 'in', now we replace every 'in' as 'n'
        self.__ResetStructIdRes(self.__inputRoot)
        self.__ResetStructIdRes(self.__outputRoot)
        self.__ResetStructIdStatus = 1
        # 
        return self.__CheckTwoVSRes(self.__inputVS, self.__outputVS)
        
    # check whether the files fit requirement of intermediate badges
    def CheckVSLN(self):
        
        # library_nodes should be checked first
        if self.CheckTwoLN() == False:
            print 'The library_nodes are not same.'
            return False
        
        # check vs and ln now:
        return self.__CheckNodesByIdRes( self.__inputVS, self.__outputVS )

    # for test purpose
    def GetTwoRoots(self):
        return [self.__inputRoot, self.__outputRoot]