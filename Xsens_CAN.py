import can
import struct
import time
import matplotlib.pyplot as plt

# 리눅스 상에서 candlelight 펌웨어 사용 시
bus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=500000)

# 리눅스 상에서 slcan 펌웨어 사용 시

#bus = can.interface.Bus(bustype='slcan', channel='/dev/ttyACM0', bitrate=500000)

# 윈도우 상에서 slcan 펌웨어 사용 시
#bus = can.interface.Bus(bustype='slcan', channel='COM18', bitrate=500000)

msg = can.Message(arbitration_id=0xE6,
                  data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  is_extended_id=False)

prim_time = time.time()  
count = 0
prev_time = prim_time
Ptime = []
Euler_roll = []
Euler_pitch = []
Euler_yaw = []

try:
    while (time.time() - prim_time) < 1:
        
        #bus.send(msg)   #CAN 메세지 보내기
        msg=bus.recv(1)
        #bus.flush()
        if msg is not None:

            #---------------- Sample time -----------------
            if msg.arbitration_id == 5: 
                sampletime = 0
                for i in range (4):
                    sampletime += msg.data[i]
                print("---------------------")
                print("Sampletime :",sampletime)
                print("Program timestamp :",msg.timestamp-prim_time)
                print("time difference :",msg.timestamp-prev_time)
                prev_time = msg.timestamp
                if count<400:
                    Ptime.append(msg.timestamp-prim_time)
                count = count + 1

            #---------------- Can frame -----------------
            elif msg.arbitration_id == 6:
                canframe = 0
                for i in range (2):
                    canframe += msg.data[i]
                print("Canframe :",canframe)

            #---------------- Quaternion -----------------
            elif msg.arbitration_id == 33:
                (Qua0,Qua1,Qua2,Qua3) = struct.unpack(">hhhh", msg.data)
                enu_Qua0 = Qua0 * (3.0517578125e-05)
                enu_Qua1 = Qua1 * (3.0517578125e-05)
                enu_Qua2 = Qua2 * (3.0517578125e-05)
                enu_Qua3 = Qua3 * (3.0517578125e-05)
                print("Q0 :",enu_Qua0,"Q1 :",enu_Qua1,"Q2 :",enu_Qua2,"Q3 :",enu_Qua3)
            
            #---------------- Euler Angle -----------------
            elif msg.arbitration_id == 34:
                #Angle = [0,0,0]
                (roll, pitch, yaw) = struct.unpack(">hhh", msg.data)
                enu_roll = roll * 0.0078
                enu_pitch = pitch * 0.0078
                enu_yaw = yaw * 0.0078

                #for i in range(3):
                #    Angle[i] = ( msg.data[2*i]*256 + msg.data[1+2*i] ) * 0.0078125
                print("X :",enu_roll,"Y :",enu_pitch,"Z :",enu_yaw)
                Euler_roll.append(enu_roll)
                Euler_pitch.append(enu_pitch)
                Euler_yaw.append(enu_yaw)

            
            #---------------- Acceleration -----------------
            elif msg.arbitration_id == 52:
                Acc = [0,0,0]
                for i in range(3):
                    Acc[i] = msg.data[2*i] + msg.data[1+2*i]
                print("accX :",Acc[0],"accY :",Acc[0],"accZ :",Acc[0])


            
except can.CanError:
    print("Receiving message is unavailable")

print("---------------------")
print("제어 주파수 :",str(count)+"Hz")

plt.plot(Ptime,Euler_roll,'r',label='roll')
plt.plot(Ptime,Euler_pitch,'g',label='pitch')
plt.plot(Ptime,Euler_yaw,'b',label='yaw')
plt.axis([0,1,-180,180])
plt.xlabel('time(sec)')
plt.ylabel('Angle(deg)')
plt.title('Euler Angle')
plt.legend(loc='upper right')
plt.show()
#print("Message sent on {}".format(bus.channel_info))