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
        


# with open('Networking/DEVICE_INFO.txt') as f:
#     lines = f.read()
#     lines2 = lines.replace('\n','')
#     print(lines2)
#     new: dict
#     new = json.loads(lines)
#     # new.update({"test2":"me"})
#     dumper = json.dumps(new)

#     with open("Networking/DEVICE_INFO.json", "w") as outfile:
#         json.dump(dumper, outfile)

# with open('Networking/DEVICE_INFO.json', 'r') as openfile:
#     meh = json.loads(json.load(openfile))
#     print(type(meh))
