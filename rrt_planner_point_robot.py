import time
import random
import drawSample
import math
import _tkinter
import sys
import imageToRects
import utils
import numpy as np

#display = drawSample.SelectRect(imfile=im2Small,keepcontrol=0,quitLabel="")
args = utils.get_args()
visualize = utils.get_args()
drawInterval = 100 # 10 is good for normal real-time drawing

prompt_before_next=1  # ask before re-running sonce solved
SMALLSTEP = args.step_size # what our "local planner" can handle.
map_size,obstacles = imageToRects.imageToRects(args.world)
#Note the obstacles are the two corner points of a rectangle
#Each obstacle is (x1,y1), (x2,y2), making for 4 points
XMAX = map_size[0]
YMAX = map_size[1]

G = [  [ 0 ]  , [] ]   # nodes, edges
vertices = [ [args.start_pos_x, args.start_pos_y], [args.start_pos_x, args.start_pos_y + 10]]

# goal/target
tx = args.target_pos_x
ty = args.target_pos_y

# start
sigmax_for_randgen = XMAX/2.0
sigmay_for_randgen = YMAX/2.0
nodes=0
edges=1

def redraw(canvas):
    canvas.clear()
    canvas.markit( tx, ty, r=SMALLSTEP )
    drawGraph(G, canvas)
    for o in obstacles: canvas.showRect(o, outline='blue', fill='blue')
    canvas.delete("debug")


def drawGraph(G, canvas):
    global vertices,nodes,edges
    if not visualize: return
    for i in G[edges]:
       canvas.polyline(  [vertices[i[0]], vertices[i[1]] ]  )


def genPoint():
    if args.rrt_sampling_policy == "uniform":
        # Uniform distribution
        x = random.random()*XMAX
        y = random.random()*YMAX
    elif args.rrt_sampling_policy == "gaussian":
        # Gaussian with mean at the goal
        x = random.gauss(tx, sigmax_for_randgen)
        y = random.gauss(ty, sigmay_for_randgen)
    else:
        print "Not yet implemented"
        quit(1)

    bad = 1
    while bad:
        bad = 0
        if args.rrt_sampling_policy == "uniform":
            # Uniform distribution
            x = random.random()*XMAX
            y = random.random()*YMAX
        elif args.rrt_sampling_policy == "gaussian":
            # Gaussian with mean at the goal
            x = random.gauss(tx, sigmax_for_randgen)
            y = random.gauss(ty, sigmay_for_randgen)
        else:
            print "Not yet implemented"
            quit(1)
        # range check for gaussian
        if x<0: bad = 1
        if y<0: bad = 1
        if x>XMAX: bad = 1
        if y>YMAX: bad = 1
    return [x,y]

def returnParent(k, canvas, G):
    """ Return parent note for input node k. """
    for e in G[edges]:
        if e[1]==k:
            canvas.polyline(  [vertices[e[0]], vertices[e[1]] ], style=3  )
            return e[0]

def genvertex():
    vertices.append( genPoint() )
    return len(vertices)-1

def pointToVertex(p):
    vertices.append( p )
    return len(vertices)-1

def pickvertex():
    return random.choice( range(len(vertices) ))

def pointPointDistance(p1,p2):
    #TODO
    return math.sqrt(np.power((p1[0] - p2[0]), 2) + np.power((p1[1] - p2[1]), 2))

def closestPointToPoint(G,p2):
    #TODO
    #return vertex index
    min = float('inf')
    idx = -1
    for node in G[nodes]:
        dist = pointPointDistance(vertices[node], p2)
        if  dist < min:
            min = dist
            idx = node
    return idx

def lineHitsRect(p1,p2,r):
    #TODO
    # check that line p1,p2 doesn't intersect any of the 4 sides of the rectangle 
    r1 = [r[0],r[1]]
    r2 = [r[0],r[3]]
    r3 = [r[2],r[3]]
    r4 = [r[2],r[1]]
    return linesIntersect(p1,p2,r1,r2) or  linesIntersect(p1,p2,r2,r3) or linesIntersect(p1,p2,r3,r4) or linesIntersect(p1,p2,r4,r1)

def linesIntersect(p1,p2,p3,p4):
    #TODO
    # inspired from https://stackoverflow.com/questions/3838329/how-can-i-check-if-two-segments-intersect

    # 1st test to see if both line segments are on top of each other
    if lineFromPoints(p1,p2) == lineFromPoints(p3,p4):
        return True
    
    # test see both line segments intersect 
    def ccw(p1,p2,p3):
        return (p3[1]-p1[1]) * (p2[0]-p1[0]) > (p2[1]-p1[1]) * (p3[0]-p1[0])

    return ccw(p1,p3,p4) != ccw(p2,p3,p4) and ccw(p1,p2,p3) != ccw(p1,p2,p4)

def lineFromPoints(p1,p2):
    #TODO
    # return line equation y=mx+b
    if p1[0] == p2[0]:
        return "x={}".format(p1[0])

    m = (p2[1] - p1[1]) / (p2[0] - p1[0])
    b = p1[1] - m * p1[0]
    return "y={}x+{}".format(m,b)

def inRect(p,rect,dilation):
    #TODO
   if p[0]<rect[0]-dilation: return 0
   if p[1]<rect[1]-dilation: return 0
   if p[0]>rect[2]+dilation: return 0
   if p[1]>rect[3]+dilation: return 0
   return 1

def steer(cur, target):
    dist = pointPointDistance(cur, target)
    newX = cur[0]+SMALLSTEP/dist*(target[0]-cur[0])
    newY = cur[1]+SMALLSTEP/dist*(target[1]-cur[1])
    return [newX, newY]

def printPoint(p, canvas, size, color):
    # helper to print a point at runtime
    x1, y1 = (p[0] - size), (p[1] - size)
    x2, y2 = (p[0] + size), (p[1] + size)
    canvas.showRect([x1,y1,x2,y2], outline=color, fill=color)

def rrt_search(G, tx, ty, canvas):
    #TODO
    #Fill this function as needed to work ...

    global sigmax_for_randgen, sigmay_for_randgen
    n=0
    numIterations=0
    while 1:
        numIterations = numIterations + 1  # count steps
        p = genPoint()
        v = closestPointToPoint(G,p)

        if pointPointDistance(p, vertices[v]) > SMALLSTEP:
            p = steer(vertices[v], p)

        if visualize:
            # if nsteps%500 == 0: redraw()  # erase generated points now and then or it gets too cluttered
            n=n+1
            if n>10:
                canvas.events()
                n=0

        reject = 0
        for o in obstacles:
            if lineHitsRect(vertices[v],p,o) or inRect(p,o,1):
                reject = 1
                break
        if reject:
            continue

        k = pointToVertex( p )   # is the new vertex ID
        G[nodes].append(k)
        G[edges].append( (v,k) )
        if visualize:
            canvas.polyline(  [vertices[v], vertices[k] ]  )
            
        if pointPointDistance( p, [tx,ty] ) < SMALLSTEP :
            print "Target achieved in ", numIterations, " iterations.", len(G[nodes]), "nodes in entire tree, "
            if visualize:
                t = pointToVertex([tx, ty])  # is the new vertex ID
                G[edges].append((k, t))
                if visualize:
                    canvas.polyline([p, vertices[t]], 1)
                # while 1:
                #     # backtrace and show the solution ...
                #     canvas.events()
                nsteps = 0
                totaldist = 0
                while 1:
                    oldp = vertices[k]  # remember point to compute distance
                    k = returnParent(k, canvas, G)  # follow links back to root.
                    canvas.events()
                    if k <= 1: break  # have we arrived?
                    nsteps = nsteps + 1  # count steps
                    totaldist = totaldist + pointPointDistance(vertices[k], oldp)  # sum lengths
                print "Path length", totaldist, "using", nsteps, "nodes."

                global prompt_before_next
                if prompt_before_next:
                    canvas.events()
                    print "More [c,q,g,Y]>",
                    d = sys.stdin.readline().strip().lstrip()
                    print "[" + d + "]"
                    if d == "c": canvas.delete()
                    if d == "q": return
                    if d == "g": prompt_before_next = 0
                break

def main():
    #seed
    random.seed(args.seed)
    if visualize:
        canvas = drawSample.SelectRect(xmin=0,ymin=0,xmax=XMAX ,ymax=YMAX, nrects=0, keepcontrol=0)#, rescale=800/1800.)
        for o in obstacles: canvas.showRect(o, outline='red', fill='blue')
    while 1:
        # graph G
        G = [  [ 0 ]  , [] ]   # nodes, edges
        redraw(canvas)
        G[edges].append( (0,1) )
        G[nodes].append(1)
        if visualize: canvas.markit( tx, ty, r=SMALLSTEP )

        drawGraph(G, canvas)
        rrt_search(G, tx, ty, canvas)

    if visualize:
        canvas.mainloop()

if __name__ == '__main__':
    main()