import can
import time

# Candlelight firmware on Linux
#bus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=500000)

# Stock slcan firmware on Linux
# bus = can.interface.Bus(bustype='slcan', channel='/dev/ttyACM0', bitrate=500000)

# Stock slcan firmware on Windows
bus = can.interface.Bus(bustype='slcan', channel='COM18', bitrate=1000000)

msg = can.Message(arbitration_id=0x141,
                  data=[0xA1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  is_extended_id=False)

previous_time=time.time()
try:
    while True:
        
        bus.send(msg)
        time.sleep(0.005)
        msg=bus.recv(1)
        bus.flush()
        if msg is not None:
            duration=time.time()-previous_time
            angle=((msg.data[7]<<8)|(msg.data[6]))*360/16383
            print(duration,angle)
            previous_time=time.time()
            
except can.CanError:
    print("Message NOT sent")

# print("Message sent on {}".format(bus.channel_info))