import sys
from utils import *
import numpy as np
# 跑分203w，表现比较稳定均在50w左右。改动寻路模块，曲线寻路。
# from log import Log
# log = Log()


def read_util_ok():
    while input() != "OK":
        pass


def finish():
    sys.stdout.write('OK\n')
    sys.stdout.flush()


def read_info():
    '''Read the stdin data, including workstations and robots.
    workstations and robots in list(dict{}) format.
    Output: workstations, robots, frame_num, money
    '''
    frame_num, money = input().split()
    frame_num, money = int(frame_num), int(money)
    K = int(input())
    workstations = []
    for i in range(K):
        station_type, x, y, rest_frame, material_state, product_state = input().split()
        station_type, x, y, rest_frame, material_state, product_state = int(station_type), float(x), float(y), int(
            rest_frame), int(material_state), int(product_state)
        stration_dict = dict({"type": station_type, "x": x, "y": y, "rest_frame": rest_frame, "m_state": material_state,
                              "p_state": product_state})
        workstations.append(stration_dict)
    robots = []
    for i in range(4):
        if_station, if_product, time_factor, break_factor, angle_speed, x_line_speed, y_line_speed, direction, x, y = input().split()
        if_station, if_product, time_factor, break_factor, angle_speed, x_line_speed, y_line_speed, direction, x, y = int(
            if_station), int(if_product), float(time_factor), float(break_factor), float(angle_speed), float(
            x_line_speed), float(y_line_speed), float(direction), float(x), float(y)
        robot_dict = dict({"if_station": if_station, "if_product": if_product, "time_factor": time_factor,
                           "break_factor": break_factor, "angle_speed": angle_speed, "x_line_speed": x_line_speed,
                           "y_line_speed": y_line_speed, "direction": direction, "x": x, "y": y})
        robots.append(robot_dict)
        r_action[i][4] = -1

    return workstations, robots, frame_num, money


def maintain_varible(workstations, robots):
    # Compute distance between robot and station
    for robot_id in range(len(robots)):
        robot_i = []
        for station_id in range(len(workstations)):
            distance = np.square(robots[robot_id]['x'] - workstations[station_id]['x']) + np.square(
                robots[robot_id]['y'] - workstations[station_id]['y'])
            robot_i.append(distance)
        r_distance.append(robot_i)
        robot_i = []
        # 机器人之间的距离
        for j in range(len(robots)):
            distance = np.square((robots[robot_id]['x'] - robots[j]['x'])) + np.square(
                (robots[robot_id]['y'] - robots[j]['y']))
            robot_i.append(distance)
        r_r_distance.append(robot_i)

    global locked_robots
    # 获取每一帧，物品 1-7, 哪个类别物品锁住了。
    material_locked_list = get_material_locked(workstations)
    for robot_id in range(len(robots)):
        product = robots[robot_id]["if_product"]
        if product != 0 and product in material_locked_list:
            # 机器人有材料，且没地方放
            locked_robots.append(robot_id)

    r_priority = []
    # Compute priority from station
    for station_id in range(len(workstations)):
        priority = 10

        if workstations[station_id]['type'] in [4, 5, 6]:
            priority = 20

        if workstations[station_id]['type'] in [7]:
            priority = 30
        # 补2缺1
        if is_materials_2only1_rest(workstations[station_id]['type'], workstations):
            priority += 10
        # 补3缺2
        if is_materials_3only2_rest(workstations[station_id]['type'], workstations):
            priority += 5
        # 补3缺1
        if is_materials_3only1_rest(workstations[station_id]['type'], workstations):
            priority += 20

        for robot_id in range(len(robots)):
            if robots[robot_id]['if_product'] == workstations[station_id]['type']:
                priority -= 20

        if is_station_rest(station_id, workstations, robots) == 0:
            priority = 0
        if workstations[station_id]['p_state'] == 0:
            priority = 0

        # 帧数0，1-7都没有产品。因此开局有可能会去 4-7 拿产品
        if frame_id <= 50:
            if workstations[station_id]['type'] in [1, 2, 3]:
                priority = 10
            else:
                priority = 0
        r_priority.append(priority)

    sell_priority = []
    lock_type_list = [[], [4, 5], [4, 6], [5, 6], [7], [7], [7], [8]]
    # 卖的优先级
    for station_id in range(len(workstations)):
        # 7只能到8去卖，因此8的优先值可随意设定。
        # 9优先级最低，仅当没地方卖了才去找9卖
        priority = 10
        
        if workstations[station_id]['type'] in [4, 5, 6]:
            priority = 20

        if workstations[station_id]['type'] in [7]:
            priority = 30
        
        # 当前工作站空缺的材料位
        material_num = len(find_materials_id(workstations[station_id]['type'], workstations[station_id]['m_state']))
        # 补3缺2
        if workstations[station_id]['type'] in [7] and material_num == 2:
            priority += 5
        # 补3缺1
        if workstations[station_id]['type'] in [7] and material_num == 1:
            priority += 20
        # 补2缺1
        if workstations[station_id]['type'] in [4, 5, 6] and material_num == 1:
            priority += 10
        

        for robot_id in range(len(robots)):
            if robots[robot_id]["if_product"] != 0:
                if r_next[robot_id] == station_id:
                    priority -= 10

        # 提前解锁材料。1-6类别。7类别可以被工作台8接收，不会死锁。
        for material_type in material_locked_list:
            if workstations[station_id]["type"] in lock_type_list[material_type]:
                priority += 30

        sell_priority.append(priority)

    if frame_id == 1:  # 只在刚开始的时候，维护工作站的类型
        for station_id in range(len(workstations)):
            s_type.append(workstations[station_id]['type'])

    return r_distance, r_priority, sell_priority

def check_action(workstations, robots):
    # Check for buy, sell, destroy for each robot.
    for robot_id in range(len(robots)):
        target_station = r_next[robot_id]
        robot_in_station = robots[robot_id]["if_station"]
        if robots[robot_id]["if_station"] == target_station:  # 如果机器人到达了指定的靶工作站，则进行交易
            # 检查买卖。机器人有产品就卖，没产品就买。
            if robots[robot_id]["if_product"] != 0:
                station_type = workstations[target_station]['type']
                # 进一步判断靶工作站,空缺材料位的list
                material_id = find_materials_id(station_type, workstations[target_station]['m_state'])
                if robots[robot_id]["if_product"] in material_id:
                    # 可卖成功
                    r_action[robot_id][3] = target_station  # 成功卖，则设置下一个靶订单
                    r_order[robot_id] = 0
                else:
                    # 不可卖成功，找其他可以卖的点。
                    for station_id in range(len(workstations)):
                        rest_materials = find_materials_id(workstations[station_id]['type'],
                                                           workstations[station_id]['m_state'])
                        if robots[robot_id]["if_product"] in rest_materials and r_next_pass(r_next, robots, workstations, robot_id, station_id, flag=1):
                            r_next[robot_id] = station_id
                            break
            else:
                r_action[robot_id][2] = target_station
                r_order[robot_id] = 0  # 成功买，则设置下一个靶订单

def find_target(r_distance, r_priority, sell_priority, workstations, robots):
    for robot_id in range(len(robots)):
        if r_order[robot_id] == 0:  # 如果当前机器人没有靶订单，则设置靶订单
            r_order[robot_id] = 1
            r_distance_with_index = [[distance, index] for index, distance in enumerate(r_distance[robot_id])]
            r_distance_with_index_sorted = sorted(r_distance_with_index, key=lambda x: x[0])

            r_priority = np.array(r_priority)
            sell_priority = np.array(sell_priority)
            if robots[robot_id]['if_product'] == 0:
                index_list = []
                max_priority = np.max(r_priority)
                min_distance = 9999
                for i in range(len(r_priority)):
                    if r_priority[i] == max_priority:
                        if r_distance[robot_id][i] < min_distance and r_next_pass(r_next, robots, workstations, robot_id, i, flag=0):
                            min_distance = r_distance[robot_id][i]
                            r_next[robot_id] = i

            else:
                # 当前机器人有货物在手，要卖给工作台
                product_id = robots[robot_id]['if_product']  # 机器人手中产品的类型
                # 产品类别为1，卖给 4，5，9 工作台
                # 产品类别为2，卖给 4，6，9 工作台
                # 产品类别为3，卖给 5，6，9 工作台
                # 产品类别为4，卖给 7，9 工作台
                # 产品类别为5，卖给 7，9 工作台
                # 产品类别为6，卖给 7，9 工作台
                # 产品类别为7，卖给 8，9 工作台
                if product_id == 1:
                    sell_priority_copy = sell_priority.copy()
                    bool_list = np.array(stationtype_index(s_type, [4, 5, 9], bool_flag=True))
                    sell_priority_copy[~bool_list] = 0 # 非4，5，9设置为0

                    max_priority = np.max(sell_priority_copy)
                    min_distance = 9999
                    if max_priority != 0: # 最大优先值为0，说明没有可卖的工作台
                        for i in range(len(sell_priority_copy)):
                            if sell_priority_copy[i] == max_priority:
                                if r_distance[robot_id][i] < min_distance and product_id in find_materials_id(workstations[i]['type'], workstations[i]['m_state']) and r_next_pass(r_next, robots, workstations, robot_id, i, flag=1):
                                    min_distance = r_distance[robot_id][i]
                                    r_next[robot_id] = i
                elif product_id == 2:
                    sell_priority_copy = sell_priority.copy()
                    bool_list = np.array(stationtype_index(s_type, [4, 6, 9], bool_flag=True))
                    sell_priority_copy[~bool_list] = 0

                    max_priority = np.max(sell_priority_copy)
                    min_distance = 9999
                    if max_priority != 0:
                        for i in range(len(sell_priority_copy)):
                            if sell_priority_copy[i] == max_priority:
                                if r_distance[robot_id][i] < min_distance and product_id in find_materials_id(workstations[i]['type'], workstations[i]['m_state']) and r_next_pass(r_next, robots, workstations, robot_id, i, flag=1):
                                    min_distance = r_distance[robot_id][i]
                                    r_next[robot_id] = i
                elif product_id == 3:
                    sell_priority_copy = sell_priority.copy()
                    bool_list = np.array(stationtype_index(s_type, [5, 6, 9], bool_flag=True))
                    sell_priority_copy[~bool_list] = 0

                    max_priority = np.max(sell_priority_copy)
                    min_distance = 9999
                    if max_priority != 0:
                        for i in range(len(sell_priority_copy)):
                            if sell_priority_copy[i] == max_priority:
                                if r_distance[robot_id][i] < min_distance and product_id in find_materials_id(workstations[i]['type'], workstations[i]['m_state']) and r_next_pass(r_next, robots, workstations, robot_id, i, flag=1):
                                    min_distance = r_distance[robot_id][i]
                                    r_next[robot_id] = i
                elif product_id == 4 or product_id == 5 or product_id == 6:
                    sell_priority_copy = sell_priority.copy()
                    bool_list = np.array(stationtype_index(s_type, [7, 9], bool_flag=True))
                    sell_priority_copy[~bool_list] = 0

                    max_priority = np.max(sell_priority_copy)
                    min_distance = 9999
                    if max_priority != 0:
                        for i in range(len(sell_priority_copy)):
                            if sell_priority_copy[i] == max_priority:
                                if r_distance[robot_id][i] < min_distance and product_id in find_materials_id(workstations[i]['type'], workstations[i]['m_state']) and r_next_pass(r_next, robots, workstations, robot_id, i, flag=1):
                                    min_distance = r_distance[robot_id][i]
                                    r_next[robot_id] = i
                elif product_id == 7:
                    sell_priority_copy = sell_priority.copy()
                    bool_list = np.array(stationtype_index(s_type, [8, 9], bool_flag=True))
                    sell_priority_copy[~bool_list] = 0

                    max_priority = np.max(sell_priority_copy)
                    min_distance = 9999
                    if max_priority != 0:
                        for i in range(len(sell_priority_copy)):
                            if sell_priority_copy[i] == max_priority:
                                if r_distance[robot_id][i] < min_distance and product_id in find_materials_id(workstations[i]['type'], workstations[i]['m_state']) and r_next_pass(r_next, robots, workstations, robot_id, i, flag=1):
                                    min_distance = r_distance[robot_id][i]
                                    r_next[robot_id] = i

def move_target(r_distance, workstations, robots):
    global locked_robots
    global r_next
    global r_action
    global r_order
    global s_type
    global r_r_distance
    for robot_id in range(len(robots)):
        # 前进加速度，角加速度
        station_target = r_next[robot_id]
        
        delta_x = workstations[station_target]["x"] - robots[robot_id]['x']
        delta_y = workstations[station_target]["y"] - robots[robot_id]['y']
        delta_dis = np.sqrt(np.square(delta_x) + np.square(delta_y))
        direction = np.arctan2(np.abs(delta_y), np.abs(delta_x))
        robot_direction = robots[robot_id]['direction']
        # 角度换算为 0 - 2pi
        if delta_x <= 0 and delta_y > 0:
            direction = np.pi - direction
        elif delta_x < 0 and delta_y <= 0:
            direction = direction + np.pi
        elif delta_x >= 0 and delta_y < 0:
            direction = 2 * np.pi - direction
        
        if robot_direction < 0:
            robot_direction = 2 * np.pi + robot_direction

        delta_direction = robot_direction - direction
        real_delta_direction = 0
        # 区分象限，以机器人的坐标为 (0,0)
        if delta_y > 0:
            if delta_direction > 0 and delta_direction < np.pi:
                real_delta_direction = - delta_direction
            elif delta_direction >= np.pi:
                real_delta_direction = 2 * np.pi - delta_direction
            elif delta_direction <= 0:
                real_delta_direction = -delta_direction
        elif delta_y < 0:
            if delta_direction > -np.pi and delta_direction < 0:
                real_delta_direction = - delta_direction
            elif delta_direction >= 0:
                real_delta_direction = - delta_direction
            elif delta_direction <= - np.pi:
                real_delta_direction = -(2 * np.pi + delta_direction)
        else:
            real_delta_direction = np.abs(delta_direction)

        if delta_dis > 1.5:
            # tanh映射前进速度
            ex = np.exp(delta_dis)
            ex2 = np.exp(-delta_dis)
            r_action[robot_id][0] = 6 
            # tanh映射角速度
            ex = np.exp(real_delta_direction)
            ex2 = np.exp(-real_delta_direction)
            if abs(real_delta_direction) > 0.1:
                r_action[robot_id][1] = np.pi if real_delta_direction >= 0 else -np.pi
            else:
                r_action[robot_id][1] = np.pi * (ex - ex2) / (ex + ex2)
        else:
            r_action[robot_id][0] = 1
            r_action[robot_id][1] = np.pi if real_delta_direction >= 0 else -np.pi
    
        eps = 0.5
        if dis_wall(robot_id) < eps:
            r_action[robot_id][0] = 2

    for robot_id in range(len(robots)):
        for robot_j in range(len(robots)):
            if robot_j > robot_id:
                if if_crash(robots, robot_id, robot_j):
                    # 对机器人i与j进行躲避碰撞, 函数内调整角速度。
                    evade_crash(robots, robot_id, robot_j)
                    # pass


def evade_crash(robots, robot_i, robot_j):
    r_action[robot_j][0] = -2
    r_action[robot_j][1] = - np.sign(r_action[robot_j][1]) * np.pi


def get_material_locked(workstations):
    '''获取所有工作站的信息,获取被死锁了的材料。(即该材料类被没有工作站能接收去放)
    '''
    # 材料有1-7个类别。设立空的set集合，遍历station，找到所有空缺的材料类别添加到set里面。
    # set集合中没有1-7的哪个类别，哪个类别就被锁住了。
    have_material = set()
    for i, station in enumerate(workstations):
        # 输入的工作台类别只能是4,5,6,7,8,9, 这种收购类型的工作台
        if station["type"] in [4, 5, 6, 7, 8, 9]:
            material_list = find_materials_id(station["type"], station['m_state'])
            for material in material_list:
                have_material.add(material)

    # have material中没有的元素
    result = set([1, 2, 3, 4, 5, 6, 7]) - have_material
    return list(result)

def r_next_pass(r_next, robots, workstations, robot_i, station_i, flag=0):
    """判断机器人 i 能够去工作台 station_i。买或者卖
    flag=0 表示机器人 i 能否去工作台买
    flag=1 表示机器人 i 能否去工作台卖
    返回是否成功进行买卖
    """
    global locked_robots
    not_locked_robots = [i for i in range(4) if i != robot_i]
    not_locked_robots_buy = [i for i in range(len(not_locked_robots)) if robots[i]["if_product"] == 0]
    not_locked_robots_sell = [i for i in range(len(not_locked_robots)) if robots[i]["if_product"]]
    not_locked_robots_station = np.array(r_next)[np.array(not_locked_robots)]

    if flag == 0:
        buy_times = 0
        for station_id in not_locked_robots_station[not_locked_robots_buy]:
            if station_id == station_i:
                # 机器人去相同工作站买。最多两个去同一个工作台买。工作站1，2，3，1s即可生产出产品。如果4，5，6，7因生产输出格满而阻塞，则可以同一个
                if workstations[station_id]['type'] in [1,2,3] and workstations[station_id]['rest_frame'] == 0 and buy_times==0:
                    pass
                elif workstations[station_id]['type'] in [4,5,6,7] and workstations[station_id]['rest_frame'] == 0 and buy_times==0:
                    buy_times += 1
                    pass
                else:
                    return False
    elif flag == 1:
        for i, station_id in enumerate(not_locked_robots_station[not_locked_robots_sell]):
            if station_id == station_i:
                # 机器人去同一个工作站，不能卖同样的东西。8,9不用考虑
                if robots[not_locked_robots_sell[i]]['if_product'] == robots[robot_i]["if_product"] and workstations[station_i]['type'] not in [8,9]:
                    return False
    return True

def dis_wall(robot_id):
    dis = [robots[robot_id]['x'], 50 - robots[robot_id]['x'], robots[robot_id]['y'], 50 - robots[robot_id]['y']]
    dis = np.array(dis)
    return dis.min()

def handle_module(workstations, robots, frame_id, money):
    global r_action
    global locked_robots
    r_action = [[-1] * 5, [-1] * 5, [-1] * 5, [-1] * 5]
    locked_robots = []
    # Maintain the distance for each robot and s_type for stations.
    r_distance, r_priority, sell_priority = maintain_varible(workstations, robots)

    # Update r_next for each robot.
    find_target(r_distance, r_priority, sell_priority, workstations, robots)
    move_target(r_distance, workstations, robots)

    # Check and update buy, sell, destroy action for each robot.
    check_action(workstations, robots)

def respond_module():
    sys.stdout.write('%d\n' % frame_id)
    for robot_id in range(4):
        line_speed, angle_speed, buy, sell, destroy = r_action[robot_id]
        if frame_id > 8650:
            buy = -1
        # 如果检测到了机器人死锁，则进行原地打转操作。直到死锁解除。
        if robot_id in locked_robots:
            sys.stdout.write('forward %d %d\n' % (robot_id, 3))
            # sys.stdout.write('rotate %d %f\n' % (robot_id, np.pi - robots[robot_id]['direction']))
            sys.stdout.write('rotate %d %f\n' % (robot_id, 1.5))

        else:
            sys.stdout.write('forward %d %d\n' % (robot_id, line_speed))
            sys.stdout.write('rotate %d %f\n' % (robot_id, angle_speed))
        if buy != -1:
            sys.stdout.write('buy %d\n' % (robot_id))
        if sell != -1:
            sys.stdout.write('sell %d\n' % (robot_id))
        if destroy != -1:
            sys.stdout.write('destroy %d\n' % (robot_id))

# 被锁住的机器人
locked_robots = []
# 每个机器人与工作台之间的距离. 类型 list[list[]]，shape是（4，工作台的个数）
r_distance = []
# 两两机器人之间的距离
r_r_distance = []
# 工作台的类型list
s_type = []
# The next target station for robot i. Length 4.
r_next = [-1, -1, -1, -1]
# The next action for robot i. For a given robot i, [forward_value, rotate_value, buy_value, sell_value, destroy_value],
r_action = [[-1] * 5, [-1] * 5, [-1] * 5, [-1] * 5]
frame_id = 0
# Set an order for each robot, there are orders for 1 and no for 0.
r_order = [0, 0, 0, 0]

if __name__ == '__main__':
    read_util_ok()
    finish()
    while True:
        # Read the input stdin
        workstations, robots, frame_id, money = read_info()
        read_util_ok()

        # The core logical handle module
        handle_module(workstations, robots, frame_id, money)

        # The respond to each frame. Action for each robot.
        respond_module()
        finish()
