import numpy as np


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
        id_list = [1, 2, 3, 4, 5, 6, 7]

    return id_list


def stationtype_index(s_type, type_index, bool_flag=False):
    '''给定工作台的类型，获取相应的 index
    '''
    # 如果产品类型数组为空，则返回空数组
    if len(type_index) == 0:
        return []

    result_index = (np.array(s_type) == type_index[0])
    for type_i in type_index:
        result_index = result_index | (np.array(s_type) == type_i)
    if bool_flag == False:
        result_index = [i for i in range(len(result_index)) if result_index[i]]

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
        material_list = find_materials_id(station['type'], station['m_state'])  # 当前工作站还剩下的材料类别的空位
        if product_id in material_list:  # 如果机器人运送的物品，当前工作站刚好有空位
            result_index.append(index_list[i])
    return result_index


# 给一个产品，判断当前是否存在两个空一个的空格
def is_materials_2only1_rest(m_type, workstations):
    res = 0
    for station_id in range(len(workstations)):
        type = workstations[station_id]['type']
        if type in [4, 5, 6]:
            rest_materials = find_materials_id(type, workstations[station_id]['m_state'])
            if m_type in rest_materials and len(rest_materials) == 1:
                res = 1
    return res


# 给一个产品，判断当前是否存在三个空一个的空格
def is_materials_3only1_rest(m_type, workstations):
    res = 0
    for station_id in range(len(workstations)):
        type = workstations[station_id]['type']
        if type == 7:
            rest_materials = find_materials_id(type, workstations[station_id]['m_state'])
            if m_type in rest_materials and len(rest_materials) == 1:
                res = 1
    return res


# 给一个产品，判断当前是否存在三个空两个的空格
def is_materials_3only2_rest(m_type, workstations):
    res = 0
    for station_id in range(len(workstations)):
        type = workstations[station_id]['type']
        if type == 7:
            rest_materials = find_materials_id(type, workstations[station_id]['m_state'])
            if m_type in rest_materials and len(rest_materials) == 2:
                res = 1
    return res


# 给一个产品，判断当前是否有空格
def is_materials_rest(m_type, workstations, robots):
    count = 0
    for station_id in range(len(workstations)):
        rest_materials = find_materials_id(workstations[station_id]['type'], workstations[station_id]['m_state'])
        if m_type in rest_materials:
            count += 1
    for robot_id in range(len(robots)):
        if robots[robot_id]['if_product'] == m_type:
            count -= 1
    if count >= 1:
        return 1
    else:
        return 0


# 给一个工作台id，判断他生产的产品当前是否卖得掉
def is_station_rest(station_id, workstations, robots):
    return is_materials_rest(workstations[station_id]['type'], workstations, robots)


def get_material_class(workstations, locked_station):
    # 获取锁住的工作站，完成解锁（或者说完成合成），所需材料类别。
    # 返回list[list]
    material_class = []
    for index in locked_station:
        material_list = find_materials_id(workstations[index]["type"], workstations[index]['m_state'])
        material_class.append(material_list)
    return material_class


def if_crash(robots, robot_i, robot_j, frame=100):
    ''' 将会发生碰撞返回true, 否则返回false
    '''
    # 5帧，也就是 0.1s 进行一次，未来距离运算.一直到frame的帧数截止
    # 机器人i与j的半径 0.53或0.45
    radius_i = 0.53 if robots[robot_i]['if_product'] else 0.45
    radius_j = 0.53 if robots[robot_j]['if_product'] else 0.45
    distance = radius_i + radius_j
    during_frame = 5
    for i in range(int(frame / during_frame)):
        second = ((i + 1) * during_frame) * 0.02
        v1 = np.sqrt(np.square(robots[robot_i]['x_line_speed']) + np.square(robots[robot_i]['y_line_speed']))
        v2 = np.sqrt(np.square(robots[robot_j]['x_line_speed']) + np.square(robots[robot_j]['y_line_speed']))
        x1 = robots[robot_i]['x'] + v1 * np.cos(robots[robot_i]['direction']) * second
        y1 = robots[robot_i]['y'] + v1 * np.sin(robots[robot_i]['direction']) * second
        x2 = robots[robot_j]['x'] + v2 * np.cos(robots[robot_j]['direction']) * second
        y2 = robots[robot_j]['y'] + v2 * np.sin(robots[robot_j]['direction']) * second
        if np.square(x1 - x2) + np.square(y1 - y2) <= np.square(distance):
            return True
    return False

def r_s_distance(robots, workstations):
    r_s_dis = []
    for robot_id in range(len(robots)):
        dis = []
        for station_id in range(len(workstations)):
            dis.append(np.sqrt(np.square(robots[robot_id]['x'] - workstations[station_id]['x']) + np.square(robots[robot_id]['y'] - workstations[station_id]['y'])))
        r_s_dis.append(dis)
    return r_s_dis
