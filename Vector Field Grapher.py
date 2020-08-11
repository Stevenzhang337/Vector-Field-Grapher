from cmu_112_graphics import*
import math
import string

def sqrt(x):
    return x**.5
def log(x):
    try: return math.log(x,10)
    except: return 1j
def ln(x):
    try: return math.log(x)
    except: return 1j
def sin(x):
    return math.sin(x)
def cos(x):
    return math.cos(x)
def tan(x):
    return math.tan(x)

def getHex(x):
    hexRep = hex(x)
    i = hexRep.index('x')
    hexRep = hexRep[i+1:]
    if len(hexRep) == 1:
        return '0' + hexRep
    else:
        return hexRep

def getCircularHex(x):
    #ff0000
    corner = x//256%6
    if corner == 0: #(ff,00,00) -> (ff,ff,00)
        return 'ff' + str(getHex(x%256)) + '00'
    elif corner == 1: #(ff,ff,00) -> (00,ff,00)
        return str(getHex(255-x%256)) + 'ff' + '00'
    elif corner == 2: #(00,ff,00) -> (00,ff,ff)
        return '00' + 'ff' + str(getHex(x%256))
    elif corner == 3: #(00,ff,ff) -> (00,00,ff)
        return '00' + str(getHex(255-x%256)) + 'ff'
    elif corner == 4: #(00,00,ff) -> (ff,00,ff)
        return str(getHex(x%256)) + '00' + 'ff'
    elif corner == 5: #(ff,00,ff) -> (ff,00,00)
        return str(getHex(x%256)) + '00' + 'ff'


class Vector(object):
    def __init__(self, xPos, yPos, xComp, yComp):
        self.xPos = xPos
        self.yPos = yPos
        self.xComp = xComp
        self.yComp = yComp
    
    def getMagnitude(self):
        return (self.xComp**2 + self.yComp**2)**.5

    def getUnitVector(self):
        magnitude = self.getMagnitude()
        if magnitude == 0:
            magnitude = 1
        return (self.xComp/magnitude, self.yComp/magnitude)
    
    def getVectorHead(self):
        return (self.xPos+self.xComp, self.yPos+self.yComp)
    def getUnitVectorHead(self):
        unitX, unitY = self.getUnitVector()
        return(self.xPos+unitX,self.yPos+unitY)
    def __eq__(self,other):
        return isinstance(other,Vector) and self.xPos == other.xPos and self.yPos == other.yPos

class Function(object):
    def __init__(self, M, N):
        #F(x,y) = <M(x,y),N(x,y)>
        self.M = M
        self.N = N
        self.constants = ['0','1','2','3','4','5','6','7','8','9','e','pi']
        self.variables = ['x','y']
        self.newNotation = ['^','e','pi']
        self.oldNotation = ['**','math.e','math.pi']

    def evaluate(self,f,x,y):
        if f == 0:
            F = self.M
        else:
            F = self.N
        if F == '':
            return 0
        
        for i in range(len(self.newNotation)):
            F = F.replace(self.newNotation[i],self.oldNotation[i])
        temp = F
        for i in range(len(F)):
            if F[i] == 'x':
                if ((not (i == 0 or i == len(F) - 1)) and 
                    (F[i-1] in self.constants and F[i+1] in self.constants+self.variables)):
                    temp = temp.replace('x','*'+str(x)+'*',1)
                elif not i == 0 and F[i-1] in self.constants:
                    temp = temp.replace('x','*'+str(x),1)
                elif not i == len(F) - 1 and F[i+1] in self.constants+self.variables:
                    temp = temp.replace('x',str(x)+'*',1)
            elif F[i] == 'y':
                if ((not (i == 0 or i == len(F) - 1)) and 
                    (F[i-1] in self.constants and F[i+1] in self.constants+self.variables)):
                    temp = temp.replace('y','*'+str(y)+'*',1)
                elif not i == 0 and F[i-1] in self.constants:
                    temp = temp.replace('y','*'+str(y),1)
                elif not i == len(F) - 1 and F[i+1] in self.constants+self.variables:
                    temp = temp.replace('y',str(y)+'*',1)
            if F[i] == 'x':
                temp = temp.replace('x',str(x),1)
            elif F[i] == 'y':
                temp = temp.replace('y',str(y),1)
        try: return eval(temp)
        except: return 1j
    
    def partialDelX(self,f,x,y):
        delX = .0000001
        return (self.evaluate(f,x+delX,y) - self.evaluate(f,x,y))/delX
    
    def partialDelY(self,f,x,y):
        delY = .0000001
        return (self.evaluate(f,x,y+delY) - self.evaluate(f,x,y))/delY
    
    def divF(self,x,y):
        return self.partialDelX(0,x,y) + self.partialDelY(1,x,y)
    
    def curlF(self,x,y):
        return self.partialDelX(1,x,y) - self.partialDelY(0,x,y)
        

    
class VectorFieldGrapher(Mode):
    def appStarted(mode):
        #function
        mode.viewFunctionScreen = True
        mode.fM = ''    #0
        mode.fN = ''    #1
        mode.f = Function(mode.fM,mode.fN)
        mode.indicator = ' '
        mode.moveIndicator = 0
        mode.timer = 0

        #buttons
        mode.currF = 0
        mode.row = 3
        mode.col = 10
        mode.margin = mode.height//25
        mode.boxWidth = (mode.width-(mode.col+1)*mode.margin)//mode.col
        mode.boxHeight = ((mode.height//3)-(mode.row+1)*mode.margin)//mode.row
        mode.buttons = [['0','1','2','3','4','5','6','7','8','9',],
                        ['+','-','*','/','^','sqrt()','.','e','pi','Delete'],
                        ['log()','ln()','sin()','cos()','tan()','e^','()','x','y','Graph']]
        
        #graph
        mode.shiftX = 0
        mode.shiftY = 0
        mode.mouseCoordinates = (0,0)
        mode.origin = (mode.width//2,mode.height//2)
        mode.tickMarks = 10
        mode.tickIntervalX = mode.width//(2*mode.tickMarks)
        mode.tickIntervalY = mode.height//(2*mode.tickMarks)
        mode.vectors = []
    
    def sizeChanged(mode):
        mode.appStarted()
    
    def getGraphCoordinates(mode,canvasX,canvasY):
        origX,origY = mode.origin
        graphX = (canvasX - origX)/mode.tickIntervalX
        graphY = (origY - canvasY)/mode.tickIntervalY
        return (graphX,graphY)

    def mousePressed(mode,event):
        if mode.viewFunctionScreen:
            (i,j) = mode.checkForButtonPressed(event)
            if mode.currF == 0:
                mode.fM = mode.writeFunction(i,j,mode.fM)
            else:
                mode.fN = mode.writeFunction(i,j,mode.fN)
        mode.mouseCoordinates = (event.x,event.y)
        x,y = mode.getGraphCoordinates(event.x,event.y)
    def mouseDragged(mode,event):
        initX, initY = mode.mouseCoordinates
        mode.shiftX += (event.x - initX)
        mode.shiftY += (event.y - initY)
        mode.origin = mode.width//2+mode.shiftX,mode.height//2+mode.shiftY
        mode.getDomain()
        mode.mouseCoordinates = (event.x,event.y)

    
    def keyPressed(mode,event):
        if not mode.viewFunctionScreen and event.key == 'r':
            mode.shiftX = mode.shiftY = 0
            mode.origin = (mode.width//2,mode.height//2)
            mode.getDomain()
        elif event.key == 'Tab':
            mode.viewFunctionScreen = not mode.viewFunctionScreen
        elif event.key == 'Enter':
            mode.currF = (mode.currF + 1)%2
            mode.moveIndicator = 0
        elif event.key == 'Right':
            mode.moveIndicator -= 1
        elif event.key == 'Left':
            mode.moveIndicator += 1
            
    def getDomain(mode):
        origX,origY = mode.origin
        mode.vectors = []
        pointsLeft = origX//mode.tickIntervalX
        pointsRight = (mode.width-origX)//mode.tickIntervalX
        pointsAbove = origY//mode.tickIntervalY
        pointsBelow = (mode.height-origY)//mode.tickIntervalY
        for i in range(-pointsLeft,pointsRight+1):
            for j in range(-pointsBelow,pointsAbove+1):
                x,y = mode.f.evaluate(0,i,j),mode.f.evaluate(1,i,j)
                mode.vectors.append(Vector(i,j,x,y))
    def checkForButtonPressed(mode,event):
        for i in range(mode.row):
            for j in range(mode.col):
                if (event.x in range(j*(mode.margin+mode.boxWidth)+mode.margin,
                                    (j+1)*(mode.margin+mode.boxWidth)) and
                   event.y in range(2*mode.height//3+i*(mode.margin+mode.boxHeight)+mode.margin,
                                    2*mode.height//3+(i+1)*(mode.margin+mode.boxHeight))):
                    return(i,j)
        return (-1,-1)
    def writeFunction(mode,i,j,fComponent):
        if i == j == -1:
            return fComponent
        else: inputSymbol = mode.buttons[i][j]

        if inputSymbol == 'Graph':
            mode.f = Function(mode.fM,mode.fN)
            mode.vectors = []
            for i in range(-10,11):
                for j in range(-10,11):
                    x,y = mode.f.evaluate(0,i,j),mode.f.evaluate(1,i,j)
                    mode.vectors.append(Vector(i,j,x,y))
        elif inputSymbol == 'Delete':
            if mode.moveIndicator == len(fComponent):
                pass
            else:
                fComponent = (fComponent[:len(fComponent)-mode.moveIndicator-1]+
                            fComponent[len(fComponent)-mode.moveIndicator:])
        else:
            fComponent = (fComponent[:len(fComponent)-mode.moveIndicator]+
                            inputSymbol+
                            fComponent[len(fComponent)-mode.moveIndicator:])
            if inputSymbol == '()':
                mode.moveIndicator += 1
        return fComponent

                                       
 
    def drawAxis(mode,canvas):
        #axis lines
        canvas.create_line(0,mode.height//2+mode.shiftY,
                           mode.width,mode.height//2+mode.shiftY,width=2)
        canvas.create_line(mode.width//2+mode.shiftX,0,
                           mode.width//2+mode.shiftX,mode.height,width=2)
    
    def drawLabeledAxis(mode,canvas):
        (origX, origY) = mode.origin
        tickWidth = 5
        
        #x-axis
        pointsLeft = origX//mode.tickIntervalX
        pointsRight = (mode.width-origX)//mode.tickIntervalX
        for i in range(-pointsLeft, pointsRight+1):
            tickX = origX + i*mode.tickIntervalX
            tickY = origY
            canvas.create_line(tickX,tickY+tickWidth,tickX,tickY-tickWidth)

        #y-axis
        pointsAbove = origY//mode.tickIntervalY
        pointsBelow = (mode.height-origY)//mode.tickIntervalY
        for j in range(-pointsBelow, pointsAbove+1):
            tickX = origX
            tickY = origY - j*mode.tickIntervalY
            canvas.create_line(tickX+tickWidth,tickY,tickX-tickWidth,tickY)

        #origin
        r = 5
        canvas.create_oval(origX-r,origY-r,origX+r,origY+r)

    def getCanvasCoordinates(mode,x,y):
        origX,origY = mode.origin
        xCanvas = origX + x*mode.tickIntervalX
        yCanvas = origY - y*mode.tickIntervalY
        return(xCanvas,yCanvas)
    
    def drawVector(mode,canvas,vector):
        #if one of the component is imaginery, dont draw anything
        if isinstance(vector.xComp,complex) or isinstance(vector.yComp,complex):
            return
        vectorTailX,vectorTailY = mode.getCanvasCoordinates(vector.xPos,vector.yPos)
        vectorXPosHead,vectorYPosHead = vector.getUnitVectorHead()
        vectorHeadX,vectorHeadY = mode.getCanvasCoordinates(vectorXPosHead,vectorYPosHead)
        color = '#' + getCircularHex(int(vector.getMagnitude()))
        canvas.create_line(vectorTailX,vectorTailY,vectorHeadX,vectorHeadY,width = 2,fill=color)
        #arrowhead
        unitX,unitY = vector.getUnitVector()
        x1,y1 = vectorHeadX - 5*unitY, vectorHeadY - 5*unitX
        x2,y2 = vectorHeadX + 5*unitY, vectorHeadY + 5*unitX
        x3,y3 = vectorHeadX + 5*(3**.5)*unitX, vectorHeadY - 5*(3**.5)*unitY
        canvas.create_polygon(x1,y1,x2,y2,x3,y3)
    
    def timerFired(mode):
        mode.timer += 1
        if mode.timer % 4 == 0:
            mode.indicator = ' '
        else:
            mode.indicator = '|'
    
    def drawFunctionScreen(mode,canvas):
        #top
        canvas.create_rectangle(0,0,mode.width,mode.height//10,fill='beige')
        #writing function
        if mode.currF == 0:
            if len(mode.fM) == 0:
                indicatorPosition = 0
            else:
                if mode.moveIndicator < 0:
                    mode.moveIndicator = 0
                elif mode.moveIndicator > len(mode.fM):
                    mode.moveIndicator = len(mode.fM)
            fM = mode.fM[:len(mode.fM)-mode.moveIndicator] + mode.indicator + mode.fM[len(mode.fM)-mode.moveIndicator:]
            fN = mode.fN
        else:
            if len(mode.fN) == 0:
                indicatorPosition = 0
            else:
                if mode.moveIndicator < 0:
                    mode.moveIndicator = 0
                elif mode.moveIndicator > len(mode.fN):
                    mode.moveIndicator = len(mode.fN)
            fM = mode.fM
            fN = mode.fN[:len(mode.fN)-mode.moveIndicator] + mode.indicator + mode.fN[len(mode.fN)-mode.moveIndicator:]
        canvas.create_text(mode.width//2,mode.height//20,text=f'F(x,y) = <{fM},{fN}>', font = 'Ariel 30')

        #bottom
        canvas.create_rectangle(0,2*mode.height//3,mode.width,mode.height,fill='beige')
        #boxes
        for i in range(mode.row):
            for j in range(mode.col):
                canvas.create_rectangle(mode.margin+j*(mode.margin+mode.boxWidth),
                                        2*mode.height//3+mode.margin+i*(mode.margin+mode.boxHeight),
                                        (j+1)*(mode.margin+mode.boxWidth),
                                        2*mode.height//3+(i+1)*(mode.margin+mode.boxHeight))
                button = mode.buttons[i][j]
                canvas.create_text(mode.margin+mode.boxWidth//2 + j*(mode.margin+mode.boxWidth),
                                   2*mode.height//3+mode.margin+mode.boxHeight//2+i*(mode.margin+mode.boxHeight),
                                   text=button)
        
    def drawPointData(mode,canvas):
        canvas.create_rectangle(0,14*mode.height//15,mode.width,mode.height,fill='beige')
        canvasX,canvasY = mode.mouseCoordinates
        x,y = mode.getGraphCoordinates(canvasX,canvasY)
        canvas.create_text(mode.margin,29*mode.height//30,text=f'Point: ({x}, {y})',anchor='w')
        canvas.create_text(mode.margin+mode.width//3,29*mode.height//30,text=f'Div: {mode.f.divF(x,y)}',anchor='w')
        canvas.create_text(mode.margin+2*mode.width//3,29*mode.height//30,text=f'Curl: {mode.f.curlF(x,y)}',anchor='w')

    


    def redrawAll(mode,canvas):
        mode.drawAxis(canvas)
        mode.drawLabeledAxis(canvas)
        for vector in mode.vectors:
            mode.drawVector(canvas,vector)
        mode.drawPointData(canvas)
        if mode.viewFunctionScreen:
            mode.drawFunctionScreen(canvas)


class VectorGrapherProgram(ModalApp):
    def appStarted(app):
        app.VectorFieldGrapher = VectorFieldGrapher()
        app.setActiveMode(app.VectorFieldGrapher)

VectorGrapherProgram(width=800,height=800)