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
        h = int( (self.BlockSize)/2 + 1)
        assert r >= 1
        return ['s['+str(r-1)+']['+str(i)+']' for i in range(h)]
        
        
    
    def threeForkConstraints(self, p0, p1, p2, q0, q1, q2, r) :
        h = int(self.BlockSize)
        d = ['d['+str(r-1)+']['+str(i)+']' for i in range(h)]
        constraints = list([])
        for i in range(h/2) :  
            constraints = constraints + [d[i]+' >= '+p0[i]]
            constraints = constraints + [d[i]+' >= '+p1[i]]
            constraints = constraints + [d[i]+' >= '+p2[i]]
            constraints = constraints + [p0[i]+'+'+p1[i]+'+'+p2[i]+ '>=2*' +d[i]] 
            constraints = constraints + [p0[i]+'+'+p1[i]+'+'+p2[i]+ '<=2'] 
             
        for i in range(h/2) :  
            constraints = constraints + [d[i+h/2]+' >= '+q0[i]]
            constraints = constraints + [d[i+h/2]+' >= '+q1[i]]
            constraints = constraints + [d[i+h/2]+' >= '+q2[i]]
            constraints = constraints + [q0[i]+'+'+q1[i]+'+'+q2[i]+ '>=2*' +d[i+h/2]] 
            constraints = constraints + [q0[i]+'+'+q1[i]+'+'+q2[i]+ '<=2'] 
        
        return constraints
        
    def genConstraints_of_Round(self, r):
        assert r>=1
        constraints = list()
        X = self.genVars_InVars_at_Round(r)
        Y = self.genVars_InVars_at_Round(r+1)
        h = self.BlockSize
        n = int(h/2)

        x0 = X[0 : n]
        x1 = X[n: 2*n]
        
        y0 = Y[0 : n]
        y1 = Y[n: 2*n]
        
        
        if n == 16 :
            x2 = self.rotr(x0, n, 7)
        else :
            x2 = self.rotr(x0, n, 8)
            
            
        xf = ['xf['+str(r-1)+']['+str(i)+']' for i in range(h)]
        xf1 = xf[0 : n]
        xf2 =xf[n : 2*n] 
        
        if n == 16 :
            y2 = self.rotr(y1, n, 2)
        else :
            y2 = self.rotr(y1, n, 3)
            
        constraints = self.threeForkConstraints(x1, y2, xf1, xf2, y1, y0, r)
        #constraints = self.threeForkConstraints(r)
               
        d = self.genVars_Objective(r)
        for i in range(n) :
            a = [xf2[i],x2[i],xf1[i]]
            constraints = constraints + [d[i]+' - '+a[0]+' - '+a[1]+' + '+a[2]+' + '+d[i+1]+' >= 0']
            constraints = constraints + [d[i]+' + '+a[0]+' + '+a[1]+' - '+a[2]+' - '+d[i+1]+' >= 0']
            constraints = constraints + [d[i]+' + '+a[0]+' - '+a[1]+' - '+a[2]+' + '+d[i+1]+' >= 0']
            constraints = constraints + [d[i]+' - '+a[0]+' + '+a[1]+' - '+a[2]+' + '+d[i+1]+' >= 0']
            constraints = constraints + [d[i]+' + '+a[0]+' - '+a[1]+' + '+a[2]+' - '+d[i+1]+' >= 0']
            constraints = constraints + [d[i]+' - '+a[0]+' + '+a[1]+' + '+a[2]+' - '+d[i+1]+' >= 0']
            constraints = constraints + [a[0]+' - '+d[i]+' + '+a[1]+' + '+a[2]+' + '+d[i+1]+' >= 0']
            constraints = constraints + [d[i]+' + '+a[0]+' + '+a[1]+' + '+a[2]+' + '+d[i+1]+' <= 4']
            
        return constraints
    

    def genModel(self, r):

        C = list([]) 
        
        for i in range(1, r+1):
            C = C + self.genConstraints_of_Round(i)
        
        filename='speck('+str(self.BlockSize)+')_linearModelForCplex_round'+str(r)+'.txt'
        o=open(filename,'w')
        o.write('int r = '+str(r)+';')
        o.write('\n')
        o.write('int h = '+str(self.BlockSize-1)+';')
        o.write('\n')
        o.write('\n')
        
        o.write('range i = 0..h;')
        o.write('\n')
        o.write('range j = 0..'+str(self.BlockSize/2)+';')
        o.write('\n')
        o.write('range r1 = 0..r-1;')
        o.write('\n')
        o.write('range r2 = 0..r;')
        o.write('\n')
        o.write('\n')
        
        o.write('dvar boolean x[r2][i];')
        o.write('\n')
        o.write('dvar boolean xf[r1][i];')
        o.write('\n')
        o.write('dvar boolean d[r1][i];')
        o.write('\n')
        o.write('dvar boolean s[r1][j];')
        o.write('\n')
        o.write('dvar int A[r1];')
        o.write('\n')
        o.write('dvar int total;')
        o.write('\n')
        o.write('\n')        
        
        o.write('minimize')
        o.write('\n')
        o.write('sum (m in r1) sum(n in j) s[m,n];')
        o.write('\n')
        o.write('\n')
    
        o.write('subject to  {')
        o.write('\n')
        
        for i in range(r) :
            o.write('s['+str(i)+'][0] == 0;')
            o.write('\n')
        o.write('\n')
                      
        o.write('sum (m in i) x[0,m]>=1;'+'\n')
        for c in C:
            o.write(c+';')
            o.write('\n')
        
        
        o.write('\n')
        for i in range(r):
            o.write('A['+str(i)+'] == sum (m in j) s['+str(i)+',m];\n')
        o.write('total == sum (m in r1) A[m];')
        
        o.write('\n')
        o.write('}')
        o.close()   
        
        
        
Speck32 = speck(32)
Speck32.genModel(4)
print('Initialized...')
    
    
