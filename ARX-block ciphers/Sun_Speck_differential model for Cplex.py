from functools import reduce
import math
import random
from random import *

class speck():
    def __init__(self, blocksize):
        self.BlockSize = blocksize

    def genVars_InVars_at_Round(self, r):
        assert r >= 1      
        return ['x['+str(r-1)+']['+str(i)+']' for i in range(self.BlockSize)]
        
    def rotl(self, X, n, r):
        assert r >= 1
        temp = [None]*n
        for i in range(n-r) :
            temp[i] = X[i+r]
        for i in range(n-r,n) :
            temp[i] = X[i-n+r]
        return temp
    
    def rotr(self, X, n, r):
        assert r >= 1
        temp = [None]*n
        for i in range(r) :
            temp[i] = X[n-r+i]
        for i in range(r,n) :
            temp[i] = X[i-r]
        return temp
    
    def genVars_Objective(self, r) :
        h = self.BlockSize
        n = int(h/2)
        assert r >= 1
        return ['s['+str(r-1)+']['+str(i) +']' for i in range(n-1)]

    def xorConstraints(self, p0, p1, p2, r) :
        h = self.BlockSize
        n = int(h/2)
        d = ['d['+str(r-1)+']['+str(i)+']' for i in range(n)]
        constraints = list()
        for i in range(n) :  
            constraints = constraints + [d[i]+' >= '+p0[i]]
            constraints = constraints + [d[i]+' >= '+p1[i]]
            constraints = constraints + [d[i]+' >= '+p2[i]]
            constraints = constraints + [p0[i]+'+'+p1[i]+'+'+p2[i]+ '>=2*' +d[i]] 
            constraints = constraints + [p0[i]+'+'+p1[i]+'+'+p2[i]+ '<=2'] 

        return constraints
    
    def genConstraints_of_Round(self, r):
        assert r>=1
        constraints = list()
        X = self.genVars_InVars_at_Round(r)
        Y = self.genVars_InVars_at_Round(r+1)
        h = self.BlockSize
        n = int(h/2)
        x0 = X[0 :   n]
        x1 = X[n : 2*n]
        y0 = Y[0 :   n]
        y1 = Y[n : 2*n]
        
        if n == 16 :
            x2 = self.rotr(x0, 16, 7)
            x3 = self.rotl(x1, 16, 2)
        else :
            x2 = self.rotr(x0, n, 8)
            x3 = self.rotl(x1, n, 3)
            
        constraints = self.xorConstraints( x3, y1, y0, r)
        d = self.genVars_Objective(r)

        for i in range(n-1) :
            b = [x2[i],x1[i],y0[i]]
            a = [x2[i+1],x1[i+1],y0[i+1]]
            constraints = constraints + [a[1]+' - '+a[2]+' + '+d[i]+' >= 0 ']
            constraints = constraints + [a[0]+' - '+a[1]+' + '+d[i]+' >= 0 ']
            constraints = constraints + [a[2]+' - '+a[0]+' + '+d[i]+' >= 0 ']
            constraints = constraints + [a[0]+' + '+a[1]+' + '+a[2]+' + '+d[i]+' <= 3 ']
            constraints = constraints + [a[0]+' + '+a[1]+' + '+a[2]+' - '+d[i]+' >= 0 ']
            constraints = constraints + [b[0]+' + '+b[1]+' + '+b[2]+' + '+d[i]+' - '+a[1]+' >= 0 ']
            constraints = constraints + [a[1]+' + '+b[0]+' - '+b[1]+' + '+b[2]+' + '+d[i]+' >= 0 ']
            constraints = constraints + [a[1]+' - '+b[0]+' + '+b[1]+' + '+b[2]+' + '+d[i]+' >= 0 ']
            constraints = constraints + [a[0]+' + '+b[0]+' + '+b[1]+' - '+b[2]+' + '+d[i]+' >= 0 ']
            constraints = constraints + [a[2]+' - '+b[0]+' - '+b[1]+' - '+b[2]+' + '+d[i]+' >= -2 ']
            constraints = constraints + [b[0]+' - '+a[1]+' - '+b[1]+' - '+b[2]+' + '+d[i]+' >= -2 ']
            constraints = constraints + [b[1]+' - '+a[1]+' - '+b[0]+' - '+b[2]+' + '+d[i]+' >= -2 ']
            constraints = constraints + [b[2]+' - '+a[1]+' - '+b[0]+' - '+b[1]+' + '+d[i]+' >= -2 ']

        constraints = constraints + [x2[n-1]+' + '+x1[n-1]+' + '+y0[n-1]+' <= 2 ']
        constraints = constraints + [x2[n-1]+' + '+x1[n-1]+' + '+y0[n-1]+' - 2 *ss['+str(r-1)+'] >= 0 ']
        constraints = constraints + ['ss['+str(r-1)+'] - '+x2[n-1]+' >= 0 ']
        constraints = constraints + ['ss['+str(r-1)+'] - '+x1[n-1]+' >= 0 ']
        constraints = constraints + ['ss['+str(r-1)+'] - '+y0[n-1]+' >= 0 ']
        
        return constraints

    def genObjectiveFun_to_Round(self, r):
        assert (r >= 1)
        h = self.BlockSize
        n = int(h/2)
        f = list([])
        for i in range(1, r+1):
            for j in range(n-1):
                f.append(self.genVars_Objective(i)[j])

        f = ' + '.join(f)
        return f
    
    def genModel(self, r):
        
        C = list([])
        for i in range(1, r+1):
            C = C + self.genConstraints_of_Round(i)
        
        filename='speck('+str(self.BlockSize)+')_differenetialModelForCplex_round'+str(r)+'.txt'
        o=open(filename,'w')
        o.write('int r = '+str(r)+';')
        o.write('\n')
        o.write('int h = '+str(self.BlockSize-1)+';')
        o.write('\n')
        o.write('\n')

        o.write('range i = 0..h;')
        o.write('\n')
        #o.write('range j = 0..'+str(self.BlockSize/2)+';')
        #o.write('\n')
        o.write('range j = 0..'+str((self.BlockSize/2 )- 1)+';')
        o.write('\n')
        o.write('range k = 0..'+str((self.BlockSize/2 )- 2)+';')
        o.write('\n')
        o.write('range r1 = 0..r-1;')
        o.write('\n')
        o.write('range r2 = 0..r;')
        o.write('\n')
        o.write('\n')

        o.write('dvar boolean x[r2][i];')
        o.write('\n')
        o.write('dvar boolean d[r1][j];')
        o.write('\n')
        o.write('dvar boolean s[r1][k];')
        o.write('\n')
        o.write('dvar boolean ss[r1];')
        o.write('\n')
        o.write('dvar int A[r1];')
        o.write('\n')
        o.write('dvar int total;')
        o.write('\n')
        o.write('\n')

        o.write('minimize')
        o.write('\n')
        o.write('sum (m in r1) sum(n in k) s[m,n];')
        o.write('\n')
        o.write('\n')

        o.write('subject to  {')
        o.write('\n')

        o.write('sum (m in i) x[0,m]>=1;'+'\n')
        for c in C:
            o.write(c+';')
            o.write('\n')

        o.write('\n')
        for i in range(r):
            o.write('A['+str(i)+'] == sum (m in k) s['+str(i)+',m];\n')
        o.write('total == sum (m in r1) A[m];')
        
        o.write('\n')
        o.write('}')
        o.close()
        

def main():
    Speck32 = speck(32)
    Speck32.genModel(4)
    print('Initialized...')
    print("ssdsdsfsd")

if __name__ == '__main__':
    main()
