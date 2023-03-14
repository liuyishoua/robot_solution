import numpy as np
# from log import Log
# log = Log()

def have_material_type(num):
    '''例如48 (110000) 表示拥有物品 4 和 5。
    输入48, 返回数组 [4,5]
    '''
    # Convert the number to a binary string
    binary_string = bin(num)[1:][::-1]
    # Create a list of the non-zero indices using a list comprehension
    have_material_type = [i for i, bit in enumerate(binary_string) if bit == '1']
    return have_material_type

def find_materials_id(station_type, num):
    '''输入的工作台类别只能是4,5,6,7,8,9, 这种收购类型的工作台
    例如48 (110000) 表示拥有物品 4 和 5。
    根据工作台的类型, 返回工作台当前空缺的材料类别
    如果是工作台 4, 只拥有 1 类别的物品, 那么工作台 4, 还有 2 类别的物品是空缺的
    返回 list
    '''
    materials_list = have_material_type(num)
    id_list = []
    if station_type == 4:
        if 1 not in materials_list:
            id_list.append(1)
        if 2 not in materials_list:
            id_list.append(2)
    elif station_type == 5:
        if 1 not in materials_list:
            id_list.append(1)
        if 3 not in materials_list:
            id_list.append(3)
    elif station_type == 6:
        if 2 not in materials_list:
            id_list.append(2)
        if 3 not in materials_list:
            id_list.append(3)
    elif station_type == 7:
        if 4 not in materials_list:
            id_list.append(4)
        if 5 not in materials_list:
            id_list.append(5)
        if 6 not in materials_list:
            id_list.append(6)
    elif station_type == 8:
        id_list.append(7)
    elif station_type == 9:
        id_list = [1,2,3,4,5,6,7]
    
    return id_list

def stationtype_index(s_type, type_index):
    '''给定工作台的类型，获取相应的 index
    '''
    # 如果产品类型数组为空，则返回空数组
    if len(type_index) == 0:
        return []

    result_index = (np.array(s_type) == type_index[0])
    for type_i in type_index:
        result_index = result_index | (np.array(s_type)==type_i)    
    
    # log.write_list(result_index)
    
    result_index = [i for i in range(len(result_index)) if result_index[i]]
    
    # log.write_list(result_index)
    return result_index

def have_product_index(workstations, index_list):
    result_index = []
    for i, station in enumerate(np.array(workstations)[index_list]):
        if station['p_state'] == 1:
            result_index.append(index_list[i])
    return result_index

def have_material_index(workstations, index_list, product_id):
    result_index = []
    for i, station in enumerate(np.array(workstations)[index_list]):
        material_list = find_materials_id(station['type'], station['m_state']) # 当前工作站还剩下的材料类别的空位
        if product_id in material_list: # 如果机器人运送的物品，当前工作站刚好有空位
            result_index.append(index_list[i])
    return result_index

    

