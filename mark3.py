import freenect
import cv2
import numpy as np
from functions import *

def nothing(x):
    pass

cv2.namedWindow('Video')
cv2.moveWindow('Video',5,5)
cv2.namedWindow('Navig',cv2.WINDOW_AUTOSIZE)
cv2.resizeWindow('Navig',400,100)
cv2.moveWindow('Navig',700,5)
cv2.namedWindow('Input')
cv2.moveWindow('Input',700,200)
'''cv2.namedWindow('edge')
cv2.moveWindow('edge',1300,5)
cv2.namedWindow('erode')
cv2.moveWindow('erode',1300,5)'''
kernel = np.ones((5, 5), np.uint8)
cv2.createTrackbar('epsilon', 'Video', 1, 100, nothing)#for approxPolyDP

print('Press \'q\' in window to stop')
imn=cv2.imread('blank.bmp')

def pretty_depth(depth):
    np.clip(depth, 0, 2**10 - 1, depth)
    depth >>= 2
    depth = depth.astype(np.uint8)
    return depth

while 1:
	imn=cv2.imread('blank.bmp')
	cv2.imshow('Navig',imn)
	flag120=[1, 1, 1, 1]
	flag140=[1, 1, 1, 1]
	f14=0
	f12=0
	f10=0
	f8=0

#get kinect input__________________________________________________________________________
	dst = pretty_depth(freenect.sync_get_depth()[0])#input from kinect
	orig = freenect.sync_get_video()[0]
	orig = cv2.cvtColor(orig,cv2.COLOR_BGR2RGB) #to get RGB image, which we don't want
    
#rectangular border (improved edge detection + closed contours)___________________________ 
	cv2.rectangle(dst,(0,0),(640,480),(40,100,0),2)
	   
#image binning (for distinct edges)________________________________________________________
	binn=20
	e=4
    	dst = (dst/binn)*binn
	#dst = (dst/20)*20 #after plenty of testing 
	dst=cv2.erode(dst, kernel, iterations=e)
        #cv2.imshow('erode',dst)
  
#Video detection___________________________________________________________________________
	v1 = 37
	v2 = 43
	edges = cv2.Canny(dst, v1, v2)
	#cv2.imshow('edge', edges)

#finding contours__________________________________________________________________________
	contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	cv2.drawContours(dst, contours, -1, (0, 0, 255), -1)
	#cv2.drawContours(orig, contours, -1, (0, 0, 255), -1)

#finding contour center of mass (moments)___________________________________________________
	'''cx=0
	cy=0
	try:
		for i in range(len(contours)):
			M = cv2.moments(contours[i])
			cx = int(M['m10']/M['m00'])
			cy = int(M['m01']/M['m00'])
			cv2.circle(dst, (cx, cy), 6, (0, 255, 0), 3)
		cx = cx/len(contours)
		cy = cy/len(contours)
	except:
		pass'''

#boundingRect approach_______________________________________________________________________
    	ep=cv2.getTrackbarPos('epsilon', 'Video') 
    	'''for i in range(len(contours)):
		if (cv2.contourArea(contours[i])>1):
    			x,y,w,h = cv2.boundingRect(contours[i])#upright rectangle
			cv2.rectangle(dst,(x,y),(x+w,y+h),(150,100,0),2)
			cv2.circle(dst, (x+w/2,y+h/2), 1, (0, 255, 0), 3)
			
			rect=cv2.minAreaRect(contours[i])#rotated rect
			box = cv2.cv.BoxPoints(rect)                    # Rotated Rect approach failed
			box = np.int0(box)
			cv2.drawContours(dst,[box],0,(50,0,255),2)'''

#approxPolyDP approach________________________________________________________________________
	#approx = cv2.approxPolyDP(contours[i],(ep/100)*cv2.arcLength(contours[i],True),True)
	#cv2.drawContours(dst, approx, -1, (0, 0, 2), 1)

#defined points approach (to check: runtime)________________________________________________
	spac=30
	(rows,cols)=dst.shape # 480 rows and 640 cols
	#print col

    	for i in range(rows/spac): #note the presence of colon
		for j in range(cols/spac):
			cv2.circle(dst, (spac*j,spac*i), 1, (0, 255, 0), 1)
			if (dst[spac*i,spac*j]==80):
				f8=1
				cv2.putText(dst,"0",(spac*j,spac*i),cv2.FONT_HERSHEY_PLAIN,1,(0,200,20),2)
				cv2.putText(dst,"Collision Alert!",(30,30),cv2.FONT_HERSHEY_TRIPLEX,1,(2),1)
				imn=cv2.imread("Collision Alert.bmp")
				cv2.imshow('Navig',imn)
			if (dst[spac*i,spac*j]==100):
				f10=1
				cv2.putText(dst,"1",(spac*j,spac*i),cv2.FONT_HERSHEY_PLAIN,1,(0,200,20),2)
				cv2.putText(dst,"Very Close proximity. Reverse",(30,60),cv2.FONT_HERSHEY_TRIPLEX,1,(2),1)
				if(f8==0):
					imn=cv2.imread("VCP Reverse.bmp")
					cv2.imshow('Navig',imn)
			if (dst[spac*i,spac*j]==120):
				f12=1
                		cv2.putText(dst, "2", (spac*j, spac*i), cv2.FONT_HERSHEY_PLAIN, 1, (0, 200, 20), 2)
                		flag120 = RegionCheck(spac*j, flag120)
				if(f8==0 and f10==0):
					imgshow(flag120,120,imn,'Navig')
			if (dst[spac*i,spac*j]==140):
				f14=1
				cv2.putText(dst,"3",(spac*j,spac*i),cv2.FONT_HERSHEY_PLAIN,1,(0,200,20),1)
				flag140 = RegionCheck(spac*j, flag140)
				if(f8==0 and f10==0 and f12==0):
					imgshow(flag140,140,imn,'Navig')
			if (dst[spac*i,spac*j]==160):
				cv2.putText(dst,"4",(spac*j,spac*i),cv2.FONT_HERSHEY_PLAIN,1,(0,200,20),1)
			if (dst[spac*i,spac*j]==180):
				cv2.putText(dst,"5",(spac*j,spac*i),cv2.FONT_HERSHEY_PLAIN,1,(0,200,20),1)
			if (dst[spac*i,spac*j]==200):
				cv2.putText(dst,"6",(spac*j,spac*i),cv2.FONT_HERSHEY_PLAIN,1,(0,200,20),1)
			if (dst[spac*i,spac*j]==220):
				cv2.putText(dst,"7",(spac*j,spac*i),cv2.FONT_HERSHEY_PLAIN,1,(0,200,20),1)
				
#imshow outputs______________________________________________________________________   
	cv2.imshow('Input',orig)
	
	if(flag120[1:3]==[1, 1] and f12==1):
		cv2.putText(dst," frwd",(325,90),cv2.FONT_HERSHEY_DUPLEX,1,(2),1)
	elif(flag120[2:4]==[1, 1] and f12==1):
		cv2.putText(dst," right",(325,90),cv2.FONT_HERSHEY_DUPLEX,1,(2),1)
	elif(flag120[0:2]==[1, 1] and f12==1):
		cv2.putText(dst," left",(325,90),cv2.FONT_HERSHEY_DUPLEX,1,(2),1)
	elif(f12==1):
		cv2.putText(dst," back",(325,90),cv2.FONT_HERSHEY_DUPLEX,1,(2),1)

	cv2.line(dst,(130,0),(130,480),(0),1)
	cv2.line(dst,(320,0),(320,480),(0),1)
	cv2.line(dst,(510,0),(510,480),(0),1)
	cv2.imshow('Video', dst)
    	
	if(cv2.waitKey(1) & 0xFF == ord('q')):
		 break
