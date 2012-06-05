# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.
from math import *

class vec3:
    def __init__(self, x_ = 0.0, y_ = 0.0, z_ = 0.0):
        self.x = x_
        self.y = y_
        self.z = z_
    
    # for operator []: float xTmp = v1[0]
    def __getitem__(self, i):
        if ( i == 0 ):
            return self.x
        elif ( i == 1 ):
            return self.y
        elif ( i == 2 ):
            return self.z
        else:
            return None
    
    # for operator []: v1[0] = 0.0
    def __setitem__(self, i, f):
        if i == 0:
            self.x = f
        elif i == 1:
            self.y = f
        elif i == 2:
            self.z = f
        else:
            return None
    
    # define for * float
    def __mul__(self, f):
        res = vec3(self.x * f, self.y * f, self.z * f)
        return res
    
    # define for -
    def __sub__(self, other):
        res = vec3()
        res.x = self.x - other.x
        res.y = self.y - other.y
        res.z = self.z - other.z
        return res
        
    # define for ==
    def __eq__( self, other):
        
        if other == None:
            return False
        else:
            if (abs( self.x - other.x ) < 1e-6 ) and  (abs( self.y - other.y ) < 1e-6 ) and (abs( self.z - other.z ) < 1e-6 ):
                return True
            else:
                return False
    
    def IsXAxis(self, epsilon):
        if (abs( self.x ) - 1.0 < epsilon and abs(self.y) < epsilon and abs(self.z) < epsilon ):
            return True
        else:
            return False
    
    def IsYAxis(self, epsilon):
        if (abs( self.x ) < epsilon and abs(self.y) - 1.0 < epsilon and abs(self.z) < epsilon ):
            return True
        else:
            return False
    
    def IsZAxis(self, epsilon):
        if (abs( self.x ) < epsilon and abs(self.y) < epsilon and abs(self.z) - 1.0 < epsilon ):
            return True
        else:
            return False
    
    # find length
    def length(self):
        return sqrt( self.x * self.x + self.y * self.y + self.z * self.z )

    # change vector
    def normalize(self):
        lenV = self.length()
        
        if abs(lenV) > 1e-6:
            self.x = self.x / lenV
            self.y = self.y / lenV
            self.z = self.z / lenV
        
        return
        
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def crossproduct(self, other):
        res = vec3()
        res.x = self.y * other.z - self.z * other.y
        res.y = self.z * other.x - self.x * other.z
        res.z = self.x * other.y - self.y * other.x
        return res
    
    def orthorand(self):
        res = vec3()
        
        ax = abs(self.x)
        ay = abs(self.y)
        az = abs(self.z)
        
        # is x the smallest component?
        if (ax < ay and ax < az):
            # (0, -z, y)
            res.x = 0.0
            res.y = -1.0 * self.z
            res.z = self.y
            return res
        # is y the smallest?
        elif (ax < az):
            # (-z, 0, x)
            res.x = -1.0 * self.z
            res.y = 0.0
            res.z = self.x
        else:
            # (-y, x, 0)
            res.x = -1.0 * self.y
            res.y = self.x
            res.z = 0.0
        
        return res
        
    def printout(self):
        print [self.x, self.y, self.z]

class mat4:
    def __init__(self, m0 = 0.0, m1 = 0.0, m2 = 0.0, m3 = 0.0, m4 = 0.0, m5 = 0.0, m6 = 0.0, m7 = 0.0, m8 = 0.0, m9 = 0.0, m10 = 0.0, m11 = 0.0, m12 = 0.0, m13 = 0.0, m14 = 0.0, m15 = 0.0):
        self.rowLst = []
        self.rowLst.append( [m0, m1, m2, m3] )
        self.rowLst.append( [m4, m5, m6, m7] )
        self.rowLst.append( [m8, m9, m10, m11] )
        self.rowLst.append( [m12, m13, m14, m15] )
    
    def __getitem__(self, index):
        if index <= 3 and index >= 0:
            return self.rowLst[index]
        else:
            return None
    
    def __eq__(self, other):
        
        if other == None:
            return False
        else:
            for indexRow in range(4):
                for indexCol in range(4):
                    if abs( self.rowLst[indexRow][indexCol] - other.rowLst[indexRow][indexCol] ) > 1e-6:
                        return False
        
        return True
    
    def SetIdentity(self):
        self.rowLst[0][0] = 1.0
        self.rowLst[1][1] = 1.0
        self.rowLst[2][2] = 1.0
        self.rowLst[3][3] = 1.0
        
    # a static function call for translation
    def translation( self, traV = vec3() ):
        tranM = mat4()
        tranM.SetIdentity()
        
        tranM.rowLst[0][3] = traV.x
        tranM.rowLst[1][3] = traV.y
        tranM.rowLst[2][3] = traV.z
        
        return tranM       
    
    # a static function call for rotation
    def rotation( self, rad, rotV_ =vec3() ):
        rotaM = mat4()
        rotaM.SetIdentity()
        
        rotV = rotV_
        
        # cos(theta) and sin(theta)
        c_t = cos( rad )
        s_t = sin( rad )
        
        x_ = rotV.x
        y_ = rotV.y
        z_ = rotV.z
        
        # only tale along x , y, z axis
        if ( rotV.IsXAxis(1e-6) == True ): # rotate along X
            # change [1, 2] * [1, 2]
            rotaM[1][1] = c_t
            rotaM[1][2] = -1.0 * s_t
            rotaM[2][1] = s_t
            rotaM[2][2] = c_t
        elif rotV.IsYAxis(1e-6) == True: # rotate along Y
            # change (0,0), (0,2), (2,0) and (2,2)
            rotaM[0][0] = c_t
            rotaM[0][2] = s_t
            rotaM[2][0] = -1.0 * s_t
            rotaM[2][2] = c_t
        elif rotV.IsZAxis(1e-6) == True: # rotate along Z
            # change [0, 1] * [0, 1]
            rotaM[0][0] = c_t
            rotaM[0][1] = -1.0 * s_t
            rotaM[1][0] = s_t
            rotaM[1][1] = c_t
        else: # rotate along any axis
            # get unit vector:
            len = sqrt( x_ * x_ + y_ * y_ + z_ * z_ )
            if ( abs( len ) < 1e-6 ):
                return None
            else:
                x = x_ / len
                y = y_ / len
                z = z_ / len
                rotaM[0][0] = x * x * (1.0  - c_t) + c_t
                rotaM[0][1] = x * y * (1.0  - c_t) - z * s_t
                rotaM[0][2] = x * z * (1.0  - c_t) + y * s_t
                
                rotaM[1][0] = x * y * (1.0 - c_t) + z * s_t
                rotaM[1][1] = y * y * (1.0 - c_t) + c_t
                rotaM[1][2] = y * z * (1.0 - c_t) - x * s_t
                
                rotaM[2][0] = x * z * (1.0 - c_t) - y * s_t
                rotaM[2][1] = y * z * (1.0 - c_t) + x * s_t
                rotaM[2][2] = z * z * (1.0 - c_t) + c_t
        
        return rotaM
    
    def scaling( self, scaleV = vec3() ):
        scalM = mat4()
        scalM.SetIdentity()
        
        scalM[0][0] = scaleV.x
        scalM[1][1] = scaleV.y
        scalM[2][2] = scaleV.z
        
        return scalM
    
    def lookAt(self, pos_, target_, up_):
        pos = pos_
        target = target_
        up = up_
        
        # find direction 
        dir = target - pos
        
        # normalize dir
        dir.normalize()
        
        # normalize up vector
        up.normalize()
        
        # find coefficient of projection of  up vector to dir
        coePro = up.dot(dir)
        
        # find vector perpendicular to dir
        vup = up - dir * coePro
        
        # judge whether dir vector is along up vector
        if abs( abs( coePro )  - 1 )< 1e-6:
            # pick up anything that is perpendicular to this vector
            vup = dir.orthorand()
        else:
            vup.normalize()
        
        # find binormal
        right = vup.crossproduct( dir )
        
        right.normalize()
        
        # matrix : transpose is the inverse for orthgonal matrix
        res =  mat4( right.x, vup.x, dir.x, pos.x, right.y, vup.y, dir.y, pos.y, right.z, vup.z, dir.z, pos.z, 0.0, 0.0, 0.0, 1.0)
        
        return res
    
    # self * other
    def __mul__(self, other):
        mulM = mat4(
        self[0][0] * other[0][0] + self[0][1] * other[1][0] + self[0][2] * other[2][0] + self[0][3] * other[3][0],
        self[0][0] * other[0][1] + self[0][1] * other[1][1] + self[0][2] * other[2][1] + self[0][3] * other[3][1],
        self[0][0] * other[0][2] + self[0][1] * other[1][2] + self[0][2] * other[2][2] + self[0][3] * other[3][2],
        self[0][0] * other[0][3] + self[0][1] * other[1][3] + self[0][2] * other[2][3] + self[0][3] * other[3][3],
        
        # computer 2 nd row of matrix        
        self[1][0] * other[0][0] + self[1][1] * other[1][0] + self[1][2] * other[2][0] + self[1][3] * other[3][0],
        self[1][0] * other[0][1] + self[1][1] * other[1][1] + self[1][2] * other[2][1] + self[1][3] * other[3][1],
        self[1][0] * other[0][2] + self[1][1] * other[1][2] + self[1][2] * other[2][2] + self[1][3] * other[3][2],
        self[1][0] * other[0][3] + self[1][1] * other[1][3] + self[1][2] * other[2][3] + self[1][3] * other[3][3],
        
        # computer 3 rd row of matrix        
        self[2][0] * other[0][0] + self[2][1] * other[1][0] + self[2][2] * other[2][0] + self[2][3] * other[3][0],
        self[2][0] * other[0][1] + self[2][1] * other[1][1] + self[2][2] * other[2][1] + self[2][3] * other[3][1],
        self[2][0] * other[0][2] + self[2][1] * other[1][2] + self[2][2] * other[2][2] + self[2][3] * other[3][2],
        self[2][0] * other[0][3] + self[2][1] * other[1][3] + self[2][2] * other[2][3] + self[2][3] * other[3][3],
        
        # computer 4 th row of matrix        
        self[3][0] * other[0][0] + self[3][1] * other[1][0] + self[3][2] * other[2][0] + self[3][3] * other[3][0],
        self[3][0] * other[0][1] + self[3][1] * other[1][1] + self[3][2] * other[2][1] + self[3][3] * other[3][1],
        self[3][0] * other[0][2] + self[3][1] * other[1][2] + self[3][2] * other[2][2] + self[3][3] * other[3][2],
        self[3][0] * other[0][3] + self[3][1] * other[1][3] + self[3][2] * other[2][3] + self[3][3] * other[3][3],        
        )
        
        return mulM
        
    def printout(self):
        for indexRow in range(4):
            print [ self[indexRow][0], self[indexRow][1], self[indexRow][2], self[indexRow][3] ]
    