import asyncio
from datetime import datetime
import bleak
from bleak import BleakClient
import os

IMU_SENSOR_2D = 1
IMU_SENSOR_63 = 0
IMU_SENSOR_2F = 0

if IMU_SENSOR_2D == 1:
    address = "2D:6F:AB:3C:F5:F4" #_IMU_SENSOR_2D_
    notity_charcteristic_uuid_accel = "741c12b9-e13c-4992-8a5e-fce46dec0bff"
    # notity_charcteristic_uuid_gyro = "baad41b2-f12e-4322-9ba6-22cd9ce09832"
    # notity_charcteristic_uuid_mag = "5748a25d-1834-4c68-a49b-81bf3aeb2e50"
if IMU_SENSOR_63 == 1:
    address = "63:C2:8F:29:36:89"
    notity_charcteristic_uuid_accel = "9d539e99-115c-485b-951d-cbd263821db7"
    # notity_charcteristic_uuid_gyro = "9adda6b7-219a-412c-aeba-976da3e92f10"
    # notity_charcteristic_uuid_mag = "b06d628d-1889-457a-a1a8-5f7adeed4941"

if IMU_SENSOR_2F == 1:
    address = "2F:92:31:56:F4:C7" #_IMU_SENSOR_2D_
    notity_charcteristic_uuid_accel = "f3f014e9-e1c9-4ab4-9542-44ff558ceb95"

file_name = ""

# accel_ble_data = []
# gyro_ble_data = []
# mag_ble_data = []

# accel_ble_string = []
# gyro_ble_string = []
# mag_ble_string = []
count = 0
write_count = 0
cur_time = 0
pre_time = 0

def makeDataFile():
    global file_name
    time = datetime.now()
    file_name = f"C:/Users/IoT18/Desktop/dm_project/IMU_{time.hour:02d}{time.minute:02d}{time.second:02d}.csv"
    f= open(file_name,'w')
    f.write("sequenece,AccelX,AccelY,AccelZ,time\n") # GyroX,GyroY,GyroZ,MagnX,MagnY,MagnZ,
    f.close()

# def writeDataFile():
#     global file_name
#     IMU_data = ""
#     f= open(file_name,'a')
#     length = len(accel_ble_data) # min(len(accel_ble_string), len(gyro_ble_string))
#     # length = min(length, len(mag_ble_string))
#     for index in range(length):
#         IMU_data = f'{index},{accel_ble_data[index]}\n' #+ gyro_ble_string[index] + mag_ble_string[index] + '\n'
#         print(IMU_data)
#         f.write(IMU_data)
#     f.close()
#     accel_ble_data.clear()
#     #sendDataFile()

# def sendDataFile():
#     global file_name
#     time = datetime.now()
#     os.system(f'sshpass -p \'jetson\' scp -o StrictHostKeyChecking=no {file_name} jetson@10.10.141.198:/home/jetson/Desktop/data/{time.month:02d}{time.day:02d}/IMU')

def notify_callback_accel(sender: int, data: bytearray):
    global cur_time
    global pre_time
    global write_count
    now = datetime.now()
    str_data = str(data, 'utf-8')
    cur_time = now.minute
    IMU_data = f'{write_count},{str_data},{now.hour:02d}{now.minute:02d}{now.second:02d}\n'
    # accel_ble_data.append(f'{str_data},{now.hour:02d}{now.minute:02d}{now.second:02d}')
    write_count += 1
    f= open(file_name,'a')
    f.write(IMU_data)
    f.close()
    # print(f'\t\t\t\t\tpre_time : {pre_time}, cur_time : {cur_time}')

# def notify_callback_gyro(sender: int, data: bytearray):
#     str_data = str(data, 'utf-8')
#     gyro_ble_string.append(str_data)
    
# def notify_callback_mag(sender: int, data: bytearray):
#     str_data = str(data, 'utf-8')
#     mag_ble_string.append(str_data)

async def run(address):
    global cur_time
    global pre_time
    global write_count
    global count
    while True:
        client = BleakClient(address, timeout=10)
        print("try to connect...")
        if await client.connect() is True:
            break
    while True:
        try:
            services = await client.get_services()
            for service in services:
                for characteristic in service.characteristics:
                    if characteristic.uuid == notity_charcteristic_uuid_accel:
                        if 'notify' in characteristic.properties:
                            await client.start_notify(characteristic, notify_callback_accel)
                    # if characteristic.uuid == notity_charcteristic_uuid_gyro:
                    #     if 'notify' in characteristic.properties:
                    #         await client.start_notify(characteristic, notify_callback_gyro)
                    # if characteristic.uuid == notity_charcteristic_uuid_mag:
                    #     if 'notify' in characteristic.properties:
                    #         await client.start_notify(characteristic, notify_callback_mag)
                    if cur_time - pre_time >= 1:
                        print("makefile : ",cur_time) ##dl q
                        # writeDataFile()
                        write_count = 0
                        count += 1
                        pre_time = cur_time
                        print(f'\t\t\t\t\tnew_pre_time : {pre_time}')
                        #makeDataFile()
        except Exception as e:
            print(e)
            continue
        else:
            if client.is_connected:
                if count >= 10:
                    print("\t\t\t\t\t50sec, count :", count)
                    print('try to deactivate notify.')
                    await client.stop_notify(notity_charcteristic_uuid_accel)
                    # await client.stop_notify(notity_charcteristic_uuid_gyro)
                    # await client.stop_notify(notity_charcteristic_uuid_mag)
                    await client.disconnect()
                    count = 0
                    break
                else:
                    # await asyncio.sleep(1)
                    print("data collect...")
                    # await client.disconnect()
                    # print('\t\t\t\t\tdisconnect, count :', count)
                    pass

###################################################################################################
now = datetime.now()
pre_time = now.minute
#print(f'\t\t\t\t\tpre_time : {pre_time}')
makeDataFile()
# loop = asyncio.get_event_loop()
# loop.run_until_complete(run(address))
asyncio.run(run(address))
