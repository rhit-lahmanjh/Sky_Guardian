import json

def read_device_data() -> dict:
    with open('main\DEVICE_INFO.json') as device_info:
        info = json.load(device_info)
        return info

def edit_device_data(newData:dict):
    with open('main\DEVICE_INFO.json') as device_info:
        info:dict
        info = json.load(device_info)
        info.update(newData)
        with open('main\DEVICE_INFO.json','w') as new_device_info:
            json.dump(info,new_device_info)
            new_device_info.close()
        
