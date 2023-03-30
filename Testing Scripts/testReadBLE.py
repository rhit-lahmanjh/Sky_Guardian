from ble_serial.bluetooth.ble_interface import BLE_interface
import cv2

while cv2.waitKey(1) != 27:
    ADAPTER = "hci0"
    SERVICE_UUID = None
    WRITE_UUID = None
    READ_UUID = None
    DEVICE = "20:91:48:4C:4C:54"

    ble = BLE_interface(ADAPTER, SERVICE_UUID)
    ble.set_receiver(receive_callback)

        
    ble.disconnect()