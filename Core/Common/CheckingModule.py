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

def chkAttri(inputEle, outputEle, attri):
    if inputEle.attributes.has_key(attri):
        # check whether there is attribute for input element
        if outputEle.attributes.has_key(attri):
            # check whether there is attribute for output element                
            if inputEle.attributes[attri].value == outputEle.attributes[attri].value:
                return [True, '']
            else:
                return [False, 'Two attributes are not same for attribute: ' + attri]
        else:
            return [False, 'output element doesn\'t have attribute: ' + attri]
    else:
        return [False, 'input element doesn\'t have attribute: ' + attri]
    
def chkAllAttri(inputEle, outputEle, attrLst=[], IsOrderReq=False):
    chkAttrLst = []
    
    if len( attrLst ) == 0:
        # need to check all attributes of two elements
        inputAttrKeys = inputEle.attributes.keys()
        outputAttrKeys = outputEle.attributes.keys()
        
        if IsOrderReq == False:
            inputAttrKeys.sort()
            outputAttrKeys.sort()
        
        if inputAttrKeys != outputAttrKeys:
            return [False, 'two elements has different set of attributes.\n']
        else:
            chkAttrLst = inputAttrKeys
    else:
        chkAttrLst = attrLst
    
    # check the attributes
    for eachAttr in chkAttrLst:
        res = chkAttri(inputEle, outputEle, eachAttr)
        if res[0] == False:
            return res
    
    return [True, '']
    
# Here the element can not have any child elements defined in COLLADA, i.e., elements without child elements. For example, IDREF_array
def chkEleValue(inputEle, outputEle, IsOrderReqInValue=False):
    
    # check whether there is no child under it
    if len ( inputEle.childNodes ) > 1 or len ( outputEle.childNodes ) >1:
        return [False, 'The elements have children elements. Considering use chkEleAndChildren instead\n']
    
    # check node value
    inputLst = inputEle.childNodes[0].nodeValue.split()
    outputLst = outputEle.childNodes[0].nodeValue.split()
    
    if len( inputLst ) != len( outputLst ):
        return [False, 'There are different number of string in value of elements.\n']
    elif IsOrderReqInValue == False:
        # decide whether we need order    
        inputLst.sort()
        outputLst.sort()
        
    # whether those two list are equal:
    if inputLst == outputLst:
        return [True, '']
    else:
        return [False, 'Value are not equal.\n']

def chkEleR( inputEle, outputEle, IsOrderReqAttr, IsOrderReqInValue):
    res = chkAllAttri(inputEle, outputEle, IsOrderReqAttr)
    if res[0] == False:
        return False
    else:
        # check all children under these two elements
        if len(inputEle.childNodes) != len(outputEle.childNodes):
            return False
        elif len(inputEle.childNodes) > 0: # if it is not leaf node
            for i in range( 0, len(inputEle.childNodes) ):
                # check each i
                res = chkEleR( inputEle.childNodes[i], outputEle.childNodes[i], IsOrderReqInValue )
                if res[0] == False: # do not need continue
                    return False
        else:
            res = chkEleValue(inputEle, outputEle, IsOrderReqInValue)
            if res[0] == False: # do not need continue
                return False
    return True
    
# check element and all elements under it recursively, for example, extra tag
def chkEleAndChildren(inputEle, outputEle):
    res = chkEleR( inputEle, outputEle, [], True, True)
    return res

# Preservation Checker: it will check attributes, simple element checking and recursively elements checking
class PresChecker: 
    def __init__(self, InputRoot_, OutputRoot_):
        self.inputRoot = InputRoot_
        self.outputRoot = OutputRoot_
        self.inputEles = []
        self.outputEles = []
        self.status = 0
    
    # Add elment to list if that element is availiable
    def SetEleById(self, id):
        # check whether inputRoot is valid or not
        if self.inputRoot == None:
            print 'Error'
            return [False, 'Input element doesn\'t have Root.\n']
        elif type(self.inputRoot) == str:
            return [False, 'Input should be a xml root. It is not a string.\n']
        
        # load input element
        inputEle = GetElementByID(self.inputRoot, id)
        
        if inputEle != None:
            self.inputEles.append( inputEle )
        else:
            return [False, 'Can not retrive the element with id ' + id + ' in input file.\n']
            
       # check whether outputRoot is valid or not
        if self.outputRoot == None:
            print 'Error'
            return [False, 'Output element doesn\'t have Root.\n']
        elif type(self.outputRoot) == str:
            return [False, 'Output should be a xml root. It is not a string.\n']
            
        # load output element
        outputEle = GetElementByID(self.outputRoot, id)
        if outputEle != None:
            self.outputEles.append( outputEle )
        else:
            return [False, 'Can not retrive the element with id '  + id + ' in output file.\n']
        
        return [True, '']
        
    def ResetElesByIds(self, idLst):
        # clear all elements in lists
        del self.inputEles[:]
        del self.outputEles[:]
        
        # append elements by id
        for eachId in idLst:
            resParseEle = self.SetEleById(eachId)
            if resParseEle[0] == False:
                self.status = -1
                return resParseEle
        
        # all elements has been added:
        self.status = 1
        return [True, '']

    # if tag is null, then it means that we only needs to search id, otherwise, it means that we will search id first and then find elements based on tag
    def ResetElementById(self, id):
        # clear all elements in lists
        del self.inputEles[:]
        del self.outputEles[:]
        
        # check whether inputRoot is valid or not
        if self.inputRoot == None:
            print 'Error'
            return [False, 'Input element doesn\'t have Root.\n']
        elif type(self.inputRoot) == str:
            return [False, 'Input should be a xml root. It is not a string.\n']
        
        # load input element
        inputEle = GetElementByID(self.inputRoot, id)
        
        if inputEle != None:
            self.inputEles.append( inputEle )
        else:
            self.status = -1
            return [False, 'Can not retrive the element with id ' + id + ' in input file.\n']
            
       # check whether outputRoot is valid or not
        if self.outputRoot == None:
            print 'Error'
            return [False, 'Output element doesn\'t have Root.\n']
        elif type(self.outputRoot) == str:
            return [False, 'Output should be a xml root. It is not a string.\n']
            
        # load output element
        outputEle = GetElementByID(self.outputRoot, id)
        if outputEle != None:
            self.outputEles.append( outputEle )
        else:
            self.status = -1
            return [False, 'Can not retrive the element with id '  + id + ' in output file.\n']        
        
        self.status = 1
        return [True, '']
        
    # if there is tag also, add all elements under same start with that tagname
    def ResetElementsByTag(self, idParent='', tagName = ''):
        # clear all elements in lists
        del self.inputEles[:]
        del self.outputEles[:]
        
        parentInEle =  GetElementByID(self.inputRoot, idParent) 
        parentOutEle = GetElementByID(self.outputRoot, idParent)
        
        if parentInEle == None or parentOutEle == None:
            self.status = -1
            return [False, 'Can not retrive the element with id ' + idParent + ' in input or output file.\n']
        else:
            self.inputEles.extend( parentInEle.getElementsByTagName(tagName) )
            self.outputEles.extend( parentOutEle.getElementsByTagName(tagName) )
            
            if len(self.inputEles) == 0 or len(self.outputEles) == 0:
                self.status = -1
                return [False, 'Can not retrive the element with tag ' + tagName + ' under id: ' + id + ' in input or output file.\n']
            elif len(self.inputEles) != len(self.outputEles):
                self.status = -1
                return [False, 'Different number of elements with tag name ' + tagName + ' under id: ' + id + ' in input and output file.\n']
            
        self.status = 1
        return [True, '']
    
    def ResetElements(self, inputEles, outputEles):
        # clear all elements in lists
        del self.inputEles[:]
        del self.outputEles[:]
        
        self.inputEles = inputEles
        self.outputEles = outputEles
        
        if len(self.inputEles) > 0 and len(self.inputEles) == len(self.outputEles):
            self.status = 1
            return [True, '']
        else:
            return [False, 'Error can not retrive elements.\n']
        
    # check attributes 
    # input id of element and attribute list: layer attribute for example
    # result: yes or no and error message as a list
    def checkElesAttribute(self, attri, IsOrderReq=False):
        
        # check whether the elements have been reset
        if self.status != 1:
            return [False, 'Not set element correctly.\n']
        
        attriInputValLst = []
        attriOutputValLst = []
        
        for i in range( 0, len(self.inputEles) ):
            # retrive two elements
            inputEle = self.inputEles[i]
            outputEle = self.outputEles[i]
            
            # check each attributes
            if inputEle.attributes.has_key(attri):
                attriInputValLst.append( inputEle.attributes[attri].value )
            else:
                return [False, 'Input element doesn\'t have attribute ' + attri + '\n']
            
            if outputEle.attributes.has_key(attri):
                attriOutputValLst.append( outputEle.attributes[attri].value )
            else:
                return [False, 'Output element doesn\'t have attribute.' + attri + '\n']
        
        if IsOrderReq == False:
            attriInputValLst.sort()
            attriOutputValLst.sort()
        
        for i in range(0, len( attriInputValLst ) ):
            if attriInputValLst[i] != attriInputValLst[i]:
                return [False, 'The attributes are not preserved.']
            
        return [True, '']
        
    def checkAttri(self, attr='', indexInput = 0, indexOutput = 0):
        
        if self.status != 1:
            return [False, 'Not set element correctly.\n']
        
        if indexInput > len( self.inputEles ) - 1:
            return [False, 'Index is out of range in inputEles']
        
        if indexOutput > len( self.outputEles ) - 1:
            return [False, 'Index is out of range in outputEles']

        inputEle = self.inputEles[indexInput]
        outputEle = self.outputEles[indexOutput]
        
        res = chkAttri(inputEle, outputEle, attr)
        
        return res
    
    def checkValue(self, IsValueOrdered=False, indexInput = 0, indexOutput = 0):
        if self.status != 1:
            return [False, 'Not set element correctly.\n']
        
        if indexInput > len( self.inputEles ) - 1:
            return [False, 'Index is out of range in inputEles']
        
        if indexOutput > len( self.outputEles ) - 1:
            return [False, 'Index is out of range in outputEles']

        inputEle = self.inputEles[indexInput]
        outputEle = self.outputEles[indexOutput]
        
        res = chkEleValue(inputEle, outputEle, IsValueOrdered)
        
        return res
        
    # check simple element, here means that there is only one child Node in it with string, i.e., no child nodes in COLLADA spec.
    # input id of element and attributes need to be preserved
    def checkSimpleEle(self, attrLst=[], IsAttriOrdered = False, IsValueOrdered = False, indexInput = 0, indexOutput = 0):
        
        if self.status != 1:
            return [False, 'Not set element correctly.\n']
        
        if indexInput > len( self.inputEles ) - 1:
            return [False, 'Index is out of range in inputEles']
        
        if indexOutput > len( self.outputEles ) - 1:
            return [False, 'Index is out of range in outputEles']

        inputEle = self.inputEles[indexInput]
        outputEle = self.outputEles[indexOutput]
        
        resAttr = chkAttri(inputEle, outputEle, attrLst)
        
        if resAttr[0] == False:
            return [False, 'Attribute is not same.\n']            
        
        resValue = chkEleValue(inputEle, outputEle, IsValueOrdered)
        
        if resValue[0] == False:
            return [False, 'The attribute is same but Value is not same.\n']            
        
        return res
    
    # This function will only check linkage between 2 elements
    def checkLinkage(self, pairType = ['string', 'string'], startIndexInput = 0, startIndexOutput = 0):
        if self.status != 1:
            return [False, 'Not set element correctly.\n']
        
        if startIndexInput + 1 > len( self.inputEles ) - 1:
            return [False, 'Index is out of range in inputEles']
        
        if startIndexOutput + 1 > len( self.outputEles ) - 1:
            return [False, 'Index is out of range in outputEles']
        
        # use dictionary to check the whether linkage is preserved
        
        # Build dictionary for input
        # Check number of elements from node value
        inputEleValuesLst = []
        dicInput = dict()
        
        # split value of element of key        
        # split value of element of value:
        
        for i in range(2):
            resParser = []
            if pairType[i] == 'string':
                resParse = ParseEleAsString( self.inputEles[ startIndexInput + i ] )            
            elif pairType[i] == 'float':
                resParse = ParseEleAsFloat( self.inputEles[ startIndexInput + i ] )
            elif pairType[i] == 'vector3':
                resParse = ParseEleAsVec3( self.inputEles[ startIndexInput + i] )
            else:
                return [False, 'Error: unsupported data type.\n']
            
            if resParse[0] == True:
                inputEleValuesLst.append( resParse[1] )
            else:
                return [False, 'Error: can not parse string correctly.\n']

        # check whether length of those two are equal
        if len( inputEleValuesLst[ 0 ] ) == len( inputEleValuesLst[ 1 ] ):
            for i in range( len( inputEleValuesLst[ 0 ] ) ):
                dicInput[ inputEleValuesLst[ 0 ][ i ]  ] = inputEleValuesLst[ 1 ][ i ]
        else:
            return [False, 'Error: not same number of value in two elements for input.']
        
        # Build dictionary for output
        outputEleValuesLst = []
        dicOutput = dict()
        
        #split value of element
        for i in range(2):
            resParser = []
            if pairType[i] == 'string':
                resParse = ParseEleAsString( self.outputEles[ startIndexOutput + i ] )            
            elif pairType[i] == 'float':
                resParse = ParseEleAsFloat( self.outputEles[ startIndexOutput + i ] )
            elif pairType[i] == 'vector3':
                resParse = ParseEleAsVec3( self.outputEles[ startIndexOutput + i] )
            else:
                return [False, 'Error: unsupported data type.\n']
            
            if resParse[0] == True:
                outputEleValuesLst.append( resParse[1] )
            else:
                return [False, 'Error: can not parse string correctly.\n']
            
        # check whether length of those two are equal
        if len( outputEleValuesLst[ 0 ] ) == len( outputEleValuesLst[1] ):
            for i in range( len( outputEleValuesLst[ 0 ] ) ):
                dicOutput[ outputEleValuesLst[ 0 ][ i ] ] = outputEleValuesLst[ 1 ][ i ]
        else:
            return [False, 'Error: not same number of value in two elements for output.']
        
        # compare two dictionary:
        if len( dicInput ) == len( dicOutput ):
            # went through the element:
            for eachKey in dicInput.keys():
                IsFind = False
                for eachOutputKey in dicOutput.keys():
                    if IsValueEqual( eachKey, eachOutputKey, pairType[0] ): # key type
                        IsFind = True
                        if (IsValueEqual( dicInput[ eachKey ], dicOutput[ eachOutputKey ], pairType[1] ) != True): # value type
                            return [False, 'Value are not same under' + str(eachKey) + ' ' + str(eachOutputKey) ]
                        break
                        
                if IsFind == False: 
                    return [False, 'Key doesn\t match']
                
            return ['True', '']
        else:
            return [False, 'Error: two dictionary don\'t have same length.\n']

    # check elements recursively for extra
    def checkExtraEle(self, indexInput = 0, indexOutput = 0):
        if self.status != 1:
            return [False, 'Not set element correctly.\n']
        
        if indexInput > len( self.inputEles ) - 1:
            return [False, 'Index is out of range in inputEles']
        
        if indexOutput > len( self.outputEles ) - 1:
            return [False, 'Index is out of range in outputEles']

        inputEle = self.inputEles[indexInput]
        outputEle = self.outputEles[indexOutput]
        
        res = chkEleAndChildren(inputEle, outputEle)
        
        return res