import cv2
import time
import numpy as np
import serial

ser = serial.Serial(port='COM9', baudrate=9600)

        
        
capture = cv2.VideoCapture(1)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
Lo=[]
loc_pr=[]


def density(den,v): #새로운 농도를 넘파이로 리턴
    lo_den=[]
    new_lo=[]                         
    x_den,y_den=[],[]
    new_den=[]
    for i in range(24): #새로운 농도 확산
        new_den.append([0 for j in range(32)])  
    
    #print(den)
    for i in range(len(den)): #기존 농도의 0이 아닌 값의 좌표 찾아서 lo_den 에 넣기
        for j in range(len(den[i])):
            if den[i][j]!=0:
                lo_den.append([i,j])
    #print(lo_den)                     
    for i in range(len(lo_den)):#lo_den의 길이만큼 xy좌표를 대입하고..?
        x_den.append(lo_den[i][0])
        y_den.append(lo_den[i][1])
    #print(x_den,y_den)                     
    for i in range(len(lo_den)): #속도의 m/s에 맞게 조정해야한다!!!->a와 b 그후 now_lo에 새로운 비말의 좌표값을 집어넣음
        a=float(v)/20*0.7
        #print(a)
        #print(x_den[i]-int(a), y_den[i]-int(a), y_den[i]+int(a))
        if x_den[i]-int(a)>=0 and y_den[i]-int(a)>=0 and y_den[i]+int(a)<=31:
            #print('okay')
            new_lo.append([x_den[i]-int(a), y_den[i]-int(a), den[x_den[i]][y_den[i]]])
            
            new_lo.append([x_den[i]-int(a), y_den[i]+int(a), den[x_den[i]][y_den[i]]])
            
            new_lo.append([x_den[i]-int(a), y_den[i], den[x_den[i]][y_den[i]]])
            
    #print(new_lo)
    
    for i in range(len(new_lo)):#new_den(새로운 비말 농도)에 값 추가 c는 최저한계
        x_new,y_new=new_lo[i][0],new_lo[i][1]
        if new_lo[i][2]/3<0.00010: pass
        elif new_lo[i][2]==0.017: new_den[x_new][y_new]+=float("{0:.5f}".format(new_lo[i][2]/3))-0.00400
        else: new_den[x_new][y_new]+=float("{0:.5f}".format(new_lo[i][2]/3)) #여기에 자신의 비말농도 빼기
    for i in range(len(new_den)):
        print(new_den[i])
    return np.array(new_den)

def over(den):
    danger_loc=[]
    for i in range(len(den)):
        for j in range(len(den[i])):
            if den[i][j]>=0.081:
                danger_loc.append([i,j])
    return danger_loc

den_list=[]

for i in range(24):
    Lo.append([0 for j in range(32)])   
while True:
    
    if ser.readable():
        res = ser.readline()
        v=res.decode()[:len(res)-1] #시리얼 모니터 (mL/sec) 
    
    time.sleep(1)
    den_=density(den_list,v)
    dan_den=den_.tolist()
    dan_loc=over(dan_den)
    ret, frame = capture.read()
    if cv2.waitKey(1) > 0: break
    #print(frame)

    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    binary = cv2.bitwise_not(binary)
    contours, he = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for i in range(len(contours)):
        cv2.drawContours(frame, [contours[i]], 0, (0, 0, 255), 2)
        mmt=cv2.moments(contours[i])
        try:
            cx=int(mmt['m10']/mmt['m00'])
            cy=int(mmt['m01']/mmt['m00'])
            loc_pr.append([int(cx/32),int(cy/24)])
            cv2.line(frame,(cx,cy),(cx,cy),(255,0,0),5)
        except:
            pass
        
    if len(dan_loc)==0: ser.write('0'.encode('utf-8')) #시리얼 모니터에 on/off상태 출력
    else: ser.write('1'.encode('utf-8'))



    for i in range(len(dan_loc)):
        dan_x,dan_y=dan_loc[i][0],dan_loc[i][1]
        cv2.rectangle(frame,(dan_x,dan_y),(dan_x+20,dan_y+20),(0,0,255),-1)
    #여기까지 사람위치 알아내기
    
                         
    #사람의 위치를 파악한 후, 리스트에 비말 값 담기
    for i in range(len(loc_pr)):
        x,y =loc_pr[i][1],loc_pr[i][0]
        Lo[x][y]=0.017  
    

        const=den_+np.array(Lo)
        den_list=const.tolist()
                
    
    
    #타인의 비말농도 파악하여 위험위치의 좌표 구하기
    #비말농도 opencv에 표시
    #위험 반경 표시
    
    
    
    
    cv2.imshow("window", frame)
    #print('\n')
    #cv2.imshow("canny",gray)

capture.release()
cv2.destroyAllWindows()
