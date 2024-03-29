import sys
from utils import *
import numpy as np


# 跑分279w，表现比较稳定均在70w左右。加入融合距离优先级建模，修改BUG。
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
    # # Compute distance between robot and station
    # for robot_id in range(len(robots)):
    #     robot_i = []
    #     for station_id in range(len(workstations)):
    #         distance = np.square(robots[robot_id]['x'] - workstations[station_id]['x']) + np.square(
    #             robots[robot_id]['y'] - workstations[station_id]['y'])
    #         robot_i.append(distance)
    #     r_distance.append(robot_i)
    #     robot_i = []
    #     # 机器人之间的距离
    #     for j in range(len(robots)):
    #         distance = np.square((robots[robot_id]['x'] - robots[j]['x'])) + np.square(
    #             (robots[robot_id]['y'] - robots[j]['y']))
    #         robot_i.append(distance)
    #     r_r_distance.append(robot_i)
    r_distance = None
    r_r_distance = None
    global locked_robots
    # 获取每一帧，物品 1-7, 哪个类别物品锁住了。
    material_locked_list = get_material_locked(workstations)
    for robot_id in range(len(robots)):
        product = robots[robot_id]["if_product"]
        if product != 0 and product in material_locked_list:
            # 机器人有材料，且没地方放
            locked_robots.append(robot_id)

    index_7 = stationtype_index(s_type, [7])
    count_456 = [0, 0, 0]
    for station in np.array(workstations)[index_7]:
        if 4 in find_materials_id(7, station['m_state']):
            count_456[0] += 1
        if 5 in find_materials_id(7, station['m_state']):
            count_456[1] += 1
        if 6 in find_materials_id(7, station['m_state']):
            count_456[2] += 1
    # 还可添加调节因子进行优化，max_456 - min_456
    max_456 = 0 if count_456[0] == count_456[1] and count_456[1] == count_456[2] else np.argmax(count_456) + 4

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

        if max_456 == 4 and workstations[station_id]['type'] in [1,2]:
            priority += 5
        elif max_456 == 5 and workstations[station_id]['type'] in [1,3]:
            priority += 5
        elif max_456 == 6 and workstations[station_id]['type'] in [2,3]:
            priority += 10
            

        if max_456 == workstations[station_id]['type']:
            priority += 10

        if is_station_rest(station_id, workstations, robots) == 0:
            priority = -9999

        if workstations[station_id]['p_state'] == 0:
            priority = -9999

        # 帧数0，1-7都没有产品。因此开局有可能会去 4-7 拿产品
        if frame_id <= 50:
            if workstations[station_id]['type'] in [1, 2, 3]:
                priority = 10
            else:
                priority = -9999
        elif frame_id > 8300 and workstations[station_id]["type"] in [1,2,3]:
            priority = -9999
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
            priority += 20
        # 补3缺1
        if workstations[station_id]['type'] in [7] and material_num == 1:
            priority += 40
        # 补2缺1
        if workstations[station_id]['type'] in [4, 5, 6] and material_num == 1:
            priority += 15

        # 地图中 7 工作台越少，解4，5，6锁的权重越大。添加后总计能提升3w。
        if max_456 == workstations[station_id]['type']:
            priority += 20

        sell_priority.append(priority)

    if frame_id == 1:  # 只在刚开始的时候，维护工作站的类型
        for station_id in range(len(workstations)):
            s_type.append(workstations[station_id]['type'])

    return r_distance, r_priority, sell_priority

def distance_buy_sell(workstations, station_id):
    # 输入买的station id，判断到其最近可卖的点的距离
    # 买的 station id 的类别是 1-7
    current_type = workstations[station_id]["type"]
    buy_sell_list = [[], [4,5,9], [4,6,9], [5,6,9], [7,9], [7,9], [7,9], [8,9]]
    sell_station_type = buy_sell_list[current_type]
    station_list = stationtype_index(s_type, sell_station_type)
    distance = 9999
    for station_index in station_list:
        if current_type in find_materials_id(workstations[station_index]["type"], workstations[station_index]["m_state"]):
            between_distance = np.sqrt(np.square(workstations[station_index]['x'] - workstations[station_id]['x']) + np.square(workstations[station_index]['y'] - workstations[station_id]['y']))
            if between_distance < distance:
                distance = between_distance
    return distance
        

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
                    r_order[robot_id] = 0
                    # 不可卖成功，找其他可以卖的点。
                    # for station_id in range(len(workstations)):
                    #     rest_materials = find_materials_id(workstations[station_id]['type'],
                    #                                        workstations[station_id]['m_state'])
                    #     if robots[robot_id]["if_product"] in rest_materials and r_next_pass(r_next, robots,
                    #                                                                         workstations, robot_id,
                    #                                                                         station_id, flag=1):
                    #         r_next[robot_id] = station_id
                    #         break
            else:
                r_action[robot_id][2] = target_station
                r_order[robot_id] = 0  # 成功买，则设置下一个靶订单


def find_target(r_distance, r_priority, sell_priority, workstations, robots):
    alphamai = 0
    alpha = 0
    # alpha = 50
    for robot_id in range(len(robots)):
        if r_order[robot_id] == 0:  # 如果当前机器人没有靶订单，则设置靶订单
            r_priority = np.array(r_priority)
            sell_priority = np.array(sell_priority)
            if robots[robot_id]['if_product'] == 0:
                max_priority = -np.inf
                # log.write_string(f"prior: {r_priority}")
                for i in range(len(r_priority)):
                    prior = r_priority[i]
                    if prior > max_priority and r_next_pass(r_next, robots, workstations,
                                                            robot_id, i, flag=0):
                        max_priority = prior
                        r_next[robot_id] = i
                        r_order[robot_id] = 1

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
                    sell_priority_copy[~bool_list] = 0  # 非4，5，9设置为0

                    max_priority = -np.inf
                    for i in range(len(sell_priority_copy)):
                        prior = sell_priority_copy[i]
                        if prior > max_priority and product_id in find_materials_id(
                                workstations[i]['type'], workstations[i]['m_state']) and r_next_pass(r_next, robots,
                                                                                                     workstations,
                                                                                                     robot_id, i,
                                                                                                     flag=1):
                            max_priority = prior
                            r_next[robot_id] = i
                            r_order[robot_id] = 1

                elif product_id == 2:
                    sell_priority_copy = sell_priority.copy()
                    bool_list = np.array(stationtype_index(s_type, [4, 6, 9], bool_flag=True))
                    sell_priority_copy[~bool_list] = 0

                    max_priority = -np.inf
                    for i in range(len(sell_priority_copy)):
                        prior = sell_priority_copy[i]
                        if prior > max_priority and product_id in find_materials_id(
                                workstations[i]['type'], workstations[i]['m_state']) and r_next_pass(r_next, robots,
                                                                                                     workstations,
                                                                                                     robot_id, i,
                                                                                                     flag=1):
                            max_priority = prior
                            r_next[robot_id] = i
                            r_order[robot_id] = 1
                elif product_id == 3:
                    sell_priority_copy = sell_priority.copy()
                    bool_list = np.array(stationtype_index(s_type, [5, 6, 9], bool_flag=True))
                    sell_priority_copy[~bool_list] = 0

                    max_priority = -np.inf
                    for i in range(len(sell_priority_copy)):
                        prior = sell_priority_copy[i]
                        if prior > max_priority and product_id in find_materials_id(
                                workstations[i]['type'], workstations[i]['m_state']) and r_next_pass(r_next, robots,
                                                                                                     workstations,
                                                                                                     robot_id, i,
                                                                                                     flag=1):
                            max_priority = prior
                            r_next[robot_id] = i
                            r_order[robot_id] = 1
                elif product_id == 4 or product_id == 5 or product_id == 6:
                    sell_priority_copy = sell_priority.copy()
                    bool_list = np.array(stationtype_index(s_type, [7, 9], bool_flag=True))
                    sell_priority_copy[~bool_list] = 0

                    max_priority = -np.inf
                    for i in range(len(sell_priority_copy)):
                        prior = sell_priority_copy[i]
                        if prior > max_priority and product_id in find_materials_id(
                                workstations[i]['type'], workstations[i]['m_state']) and r_next_pass(r_next, robots,
                                                                                                     workstations,
                                                                                                     robot_id, i,
                                                                                                     flag=1):
                            max_priority = prior
                            r_next[robot_id] = i
                            r_order[robot_id] = 1
                elif product_id == 7:
                    sell_priority_copy = sell_priority.copy()
                    bool_list = np.array(stationtype_index(s_type, [8, 9], bool_flag=True))
                    sell_priority_copy[~bool_list] = 0

                    max_priority = -np.inf
                    for i in range(len(sell_priority_copy)):
                        prior = sell_priority_copy[i]
                        if prior > max_priority and product_id in find_materials_id(
                                workstations[i]['type'], workstations[i]['m_state']) and r_next_pass(r_next, robots,
                                                                                                     workstations,
                                                                                                     robot_id, i,
                                                                                                     flag=1):
                            max_priority = prior
                            r_next[robot_id] = i
                            r_order[robot_id] = 1
        elif r_order[robot_id] == 1:  # 如果当前机器人有靶订单
            station_id = r_next[robot_id]
            if robots[robot_id]['if_product'] == 0:
                # 机器人去买的时候，有可能买的没位置放。要做判断，机器按优先级换个工作站买
                if is_station_rest(station_id, workstations, robots) == 0:  # 如果发现没地方放了（当前物品类型被锁了），则按照优先级换单。
                    r_order[robot_id] = 0
            else: # 机器人去卖的时候，如果没位置放，则按照优先级换个工作站卖
                product_type = robots[robot_id]["if_product"]
                if product_type not in find_materials_id(workstations[station_id]["type"], workstations[station_id]["m_state"]):
                    r_order[robot_id] = 0


def compute_real_direction(delta_direction, delta_y):
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
    return real_delta_direction


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
        real_delta_direction = compute_real_direction(delta_direction, delta_y)

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

        # tanh映射角速度
        ex = np.exp(real_delta_direction)
        ex2 = np.exp(-real_delta_direction)

        # 距离大于1.5，全程加速，角度微调
        # 距离小于1.5，角度对准进行微调并加速，不准进行减速并大调角度
        eps = 2
        if delta_dis > eps:
            r_action[robot_id][0] = 6
            if abs(real_delta_direction) > 0.1:
                r_action[robot_id][1] = np.pi if real_delta_direction >= 0 else -np.pi
            else:
                r_action[robot_id][1] = np.pi * (ex - ex2) / (ex + ex2)
        else:
            if abs(real_delta_direction) > 0.1:
                # r_action[robot_id][0] = delta_dis * (6 / eps)
                r_action[robot_id][0] = 0
                r_action[robot_id][1] = np.pi if real_delta_direction >= 0 else -np.pi
            else:
                r_action[robot_id][0] = 6
                r_action[robot_id][1] = np.pi * (ex - ex2) / (ex + ex2)
        
        if workstations[station_target]["type"] in [1,2,3]:
            distance = np.sqrt(np.square(robots[robot_id]["x"] - workstations[station_target]["x"]) + np.square(robots[robot_id]["y"] - workstations[station_target]["y"]))
            if distance < 2:
                r_action[robot_id][0] = 3

        if workstations[station_target]["type"] in [4,5,6,7,8,9]:
            if abs(real_delta_direction) > 0.7:
                # r_action[robot_id][0] = delta_dis * (6 / eps)
                r_action[robot_id][0] = 0
                r_action[robot_id][1] = np.pi if real_delta_direction >= 0 else -np.pi
            else:
                r_action[robot_id][0] = 6
                r_action[robot_id][1] = np.pi * (ex - ex2) / (ex + ex2)

    for robot_id in range(len(robots)):
        for robot_j in range(len(robots)):
            if robot_j > robot_id:
                if if_crash(robots, robot_id, robot_j):
                    if frame_id % 2 == 0:
                        evade_crash(robots, robot_id, robot_j)
                    elif frame_id % 2 == 1:
                        evade_crash_simple(robots, robot_id, robot_j)
                    # elif frame_id % 3 == 2:
                    #     evade_crash_back(robots, robot_id, robot_j)

def evade_crash_back(robots, robot_i, robot_j):
    r_action[robot_j][0] = -2
    r_action[robot_j][1] = - np.sign(r_action[robot_j][1]) * np.pi


def evade_crash_simple(robots, robot_i, robot_j):
    second = 0.1
    v1 = np.sqrt(np.square(robots[robot_i]['x_line_speed']) + np.square(robots[robot_i]['y_line_speed']))
    x1 = robots[robot_i]['x'] + v1 * np.cos(robots[robot_i]['direction']) * second
    y1 = robots[robot_i]['y'] + v1 * np.sin(robots[robot_i]['direction']) * second

    delta_x = x1 - robots[robot_j]['x']
    delta_y = y1 - robots[robot_j]['y']
    delta_dis = np.sqrt(np.square(delta_x) + np.square(delta_y))
    direction = np.arctan2(np.abs(delta_y), np.abs(delta_x))
    robot_direction = robots[robot_j]['direction']
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

    # tanh映射角速度
    ex = np.exp(real_delta_direction)
    ex2 = np.exp(-real_delta_direction)

    # 距离大于1.5，全程加速，角度微调
    # 距离小于1.5，角度对准进行微调并加速，不准进行减速并大调角度
    eps = 3
    if delta_dis > eps:
        r_action[robot_j][0] = 6
        r_action[robot_j][1] = -np.pi if real_delta_direction >= 0 else np.pi
    else:
        r_action[robot_j][0] = delta_dis * (6 / eps)
        r_action[robot_j][1] = -np.pi if real_delta_direction >= 0 else np.pi


def evade_crash(robots, robot_i, robot_j):
    agents = [-1, -1, -1, -1]
    max_speed = 6
    dt = 1/50
    tau = 5
    for robot_id in range(len(robots)):
        station_target = r_next[robot_id]
        delta_x = workstations[station_target]["x"] - robots[robot_id]['x']
        delta_y = workstations[station_target]["y"] - robots[robot_id]['y']
        dis = np.sqrt(np.square(delta_x) + np.square(delta_y))
        agents[robot_id] = Agent([robots[robot_id]["x"], robots[robot_id]["y"]], [robots[robot_id]["x_line_speed"], robots[robot_id]["y_line_speed"]], \
        0.53 if robots[robot_id]["if_product"] else 0.45, max_speed, [max_speed * delta_x/dis, max_speed * delta_y/dis])
    
    for i, agent in enumerate(agents):
        candidates = agents[:i] + agents[i + 1:]
        new_vels, all_lines = orca(agent, candidates, tau, dt)
        agent.velocity = new_vels

    for i, agent in enumerate(agents):
        new_speed = agent.velocity
        if new_speed != []: 
            new_speed_direction = np.arctan2(np.abs(new_speed[1]), np.abs(new_speed[0]))
            robot_direction = robots[i]['direction']

            # 角度换算为 0 - 2pi
            if new_speed[0] <= 0 and new_speed[1] > 0:
                new_speed_direction = np.pi - new_speed_direction
            elif new_speed[0] < 0 and new_speed[1] <= 0:
                new_speed_direction = new_speed_direction + np.pi
            elif new_speed[0] >= 0 and new_speed[1] < 0:
                new_speed_direction = 2 * np.pi - new_speed_direction

            if robot_direction < 0:
                robot_direction = 2 * np.pi + robot_direction
            
            delta_direction = robot_direction - new_speed_direction
            real_delta_direction = compute_real_direction(delta_direction, new_speed[1])

            ex = np.exp(real_delta_direction)
            ex2 = np.exp(-real_delta_direction)

            # r_action[i][0] = np.sqrt(np.square(new_speed[0]) + np.square(new_speed[1]))
            if i == robot_i or i == robot_j:
                r_action[i][0] = np.sqrt(np.square(new_speed[0]) + np.square(new_speed[1]))
                r_action[i][1] = np.pi if real_delta_direction >= 0 else -np.pi
            # np.pi * (ex - ex2) / (ex + ex2)
        else:
            if i == robot_i or i == robot_j:
                r_action[i][0] = 0
                r_action[i][1] = 0


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
    robots_notself = [i for i in range(4) if i != robot_i]
    robots_buy = [i for i in robots_notself if robots[i]["if_product"] == 0]
    robots_sell = [i for i in robots_notself if robots[i]["if_product"]]

    if flag == 0:
        buy_times = 0
        for station_id in np.array(r_next)[robots_buy]:
            if station_id == station_i:
                # 机器人去相同工作站买。最多两个去同一个工作台买。工作站1，2，3，1s即可生产出产品。如果4，5，6，7因生产输出格满而阻塞，则可以同一个
                if workstations[station_id]['type'] in [1, 2, 3] and workstations[station_id][
                    'rest_frame'] == 0 and buy_times == 0 and frame_id < 200:
                    buy_times += 1
                    pass
                elif workstations[station_id]['type'] in [4, 5, 6, 7] and workstations[station_id][
                    'rest_frame'] == 0 and buy_times == 0:
                    # buy_times += 1
                    return False
                else:
                    return False
    elif flag == 1:
        for i, station_id in zip(robots_sell, np.array(r_next)[robots_sell]):
            if station_id == station_i:
                # 机器人去同一个工作站，不能卖同样的东西。8,9不用考虑
                if robots[i]['if_product'] == robots[robot_i]["if_product"] and \
                        workstations[station_i]['type'] not in [8, 9]:
                    return False
    return True
    

def dis_wall(robot_id, eps):
    # 判断那堵墙与机器人的距离小于eps，返回墙壁数组
    # 左墙为1，下墙为2，右墙为3，上墙为4
    dis = [robots[robot_id]['x'], 50 - robots[robot_id]['x'], robots[robot_id]['y'], 50 - robots[robot_id]['y']]

    dis = [i + 1 for i in range(4) if np.array(dis)[i] < eps]
    return dis


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
        if frame_id > 8850:
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

