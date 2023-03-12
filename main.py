#!/bin/bash
import sys
from log import Log
from utils import have_material_type, find_materials_id, stationtype_index, have_product_index, have_material_index
import numpy as np

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
    # log.write_string(f"{frame_num}")
    workstations = []
    for i in range(K):
        station_type, x, y, rest_frame, material_state, product_state = input().split()
        station_type, x, y, rest_frame, material_state, product_state = int(station_type), float(x), float(y), int(rest_frame), int(material_state), int(product_state)
        stration_dict = dict({"type":station_type, "x":x, "y":y, "rest_frame":rest_frame, "m_state":material_state, "p_state":product_state})
        workstations.append(stration_dict)
    # log.write_string(f"9: {workstations[9]['x']}, {workstations[9]['y']}; 4: {workstations[4]['x']}, {workstations[4]['y']}")
    robots = []
    for i in range(4):
        if_station, if_product, time_factor, break_factor, angle_speed, x_line_speed, y_line_speed, direction, x, y = input().split()
        if_station, if_product, time_factor, break_factor, angle_speed, x_line_speed, y_line_speed, direction, x, y = int(if_station), int(if_product), float(time_factor), float(break_factor), float(angle_speed), float(x_line_speed), float(y_line_speed), float(direction), float(x), float(y)
        robot_dict = dict({"if_station":if_station, "if_product":if_product, "time_factor":time_factor, "break_factor":break_factor, "angle_speed":angle_speed, "x_line_speed":x_line_speed, "y_line_speed":y_line_speed, "direction":direction, "x":x, "y":y})
        robots.append(robot_dict)
        r_action[i][4] = -1
    
    return workstations, robots, frame_num, money

def maintain_varible(workstations, robots):
    # Compute distance between robot and station
    for robot_id in range(len(robots)):
        robot_i = []
        for station_id in range(len(workstations)):
            distance = np.square(robots[robot_id]['x'] - workstations[station_id]['x']) + np.square(robots[robot_id]['y'] - workstations[station_id]['y'])
            robot_i.append(distance)
        r_distance.append(robot_i)
        robot_i = []
        # 机器人之间的距离
        for j in range(len(robots)):
            distance = np.square((robots[robot_id]['x']-robots[j]['x'])) + np.square((robots[robot_id]['y']-robots[j]['y']))
            robot_i.append(distance)
        r_r_distance.append(robot_i)
    
    if frame_id == 1: # 只在刚开始的时候，维护工作站的类型 
        for station_id in range(len(workstations)):
            s_type.append(workstations[station_id]['type'])
    
    return r_distance

def check_action(workstations, robots):
    # Check for buy, sell, destroy for each robot.
    for robot_id in range(len(robots)):
        target_station = r_next[robot_id]
        # If robot arrive the target station
        robot_in_station = robots[robot_id]["if_station"]
        if robots[robot_id]["if_station"] == target_station:
            r_order[robot_id] = 0 # 这里处理完订单后r_order设置为0，寻找下一个订单
            # 检查买卖，都是直接行为。机器人有产品就卖，没产品就买。
            if robots[robot_id]["if_product"] != 0:
                # 可做判断。能否卖。
                station_type = workstations[target_station]['type']
                # 进一步判断靶工作站,空缺材料位的list
                material_id = find_materials_id(station_type, workstations[target_station]['m_state'])
                if robots[robot_id]["if_product"] in material_id:
                    # 可卖成功
                    r_action[robot_id][3] = target_station
                else:
                    # destory非 -1 都能执行
                    # 销毁操作，只在当前帧进行。
                    # r_action[robot_id][4] = 2
                    pass
            else:
                # 能否成功买，不用判断
                r_action[robot_id][2] = target_station

def find_target(r_distance, workstations, robots):
    for robot_id in range(len(robots)):
        if r_order[robot_id] == 0: # 如果当前机器人没有靶订单，则设置靶订单
            r_distance_with_index = [[distance, index] for index, distance in enumerate(r_distance[robot_id])]
            r_distance_with_index_sorted = sorted(r_distance_with_index, key=lambda x: x[0])

            # 当前机器人无货物在手，要向工作台买
            if robots[robot_id]['if_product'] == 0:
                # log.write_object(workstations)
                # log.write_list(s_type)
                index_list = stationtype_index(s_type, [4, 5, 6, 7]) # 获取工作站类型的 index
                index_list_with_product = have_product_index(workstations, index_list) # 获取有产品的工作站的 index
                # 4，5，6，7 工作台是否有货，有则买；否则买 1，2，3 工作台。//如果工作台都没货，之后考虑（基本不存在这种情况，因为1，2，3工作台更新很快）
                flag = 0
                for _, index in r_distance_with_index_sorted:
                    if index in index_list_with_product and index not in r_next:
                        r_next[robot_id] = index
                        flag = 1
                        break
                if flag == 0:
                    index_list = stationtype_index(s_type, [1, 2, 3])
                    index_list_with_product = have_product_index(workstations, index_list)
                    for _, index in r_distance_with_index_sorted:
                        if index in index_list_with_product and index not in r_next:
                            r_next[robot_id] = index
                            break
            else:
                # 当前机器人有货物在手，要卖给工作台
                product_id = robots[robot_id]['if_product'] # 机器人手中产品的类型
                # 产品类别为1，卖给 4，5，9 工作台
                # 产品类别为2，卖给 4，6，9 工作台
                # 产品类别为3，卖给 5，6，9 工作台
                # 产品类别为4，卖给 7，9 工作台
                # 产品类别为5，卖给 7，9 工作台
                # 产品类别为6，卖给 7，9 工作台
                # 产品类别为7，卖给 8，9 工作台
                # 要求，卖给的工作台要有材料空位，//且含有优先级数组index，之后考虑//如果不存在有空位的工作台，之后考虑
                if product_id == 1:
                    index_list = stationtype_index(s_type, [4, 5, 9]) # 获取工作站类型的 index
                    # 获取有材料为空缺的工作站的 index。当然,空缺的材料类型与机器人运送物品的类型相同
                    index_list_with_material = have_material_index(workstations, index_list, product_id)
                    for _, index in r_distance_with_index_sorted: # 这部分代码速度可以提升
                        if index in index_list_with_material and index not in r_next:
                            r_next[robot_id] = index
                            break
                elif product_id == 2:
                    index_list = stationtype_index(s_type, [4, 6, 9])
                    index_list_with_material = have_material_index(workstations, index_list, product_id)
                    for _, index in r_distance_with_index_sorted:
                        if index in index_list_with_material and index not in r_next:
                            r_next[robot_id] = index
                            break
                elif product_id == 3:
                    index_list = stationtype_index(s_type, [5, 6, 9])
                    index_list_with_material = have_material_index(workstations, index_list, product_id)
                    for _, index in r_distance_with_index_sorted:
                        if index in index_list_with_material and index not in r_next:
                            r_next[robot_id] = index
                            break
                elif product_id == 4 or product_id == 5 or product_id == 6:
                    index_list = stationtype_index(s_type, [7, 9])
                    index_list_with_material = have_material_index(workstations, index_list, product_id)
                    for _, index in r_distance_with_index_sorted:
                        if index in index_list_with_material and index not in r_next:
                            r_next[robot_id] = index
                            break
                elif product_id == 7:
                    index_list = stationtype_index(s_type, [8, 9])
                    index_list_with_material = have_material_index(workstations, index_list, product_id)
                    for _, index in r_distance_with_index_sorted:
                        if index in index_list_with_material and index not in r_next:
                            r_next[robot_id] = index
                            break
            r_order[robot_id] = 1
            # if robot_id == 3:
            #     log.write_string(f'second: {frame_id/50}, r_next: {r_next[3]}\n')

def dis_wall(robot_id):
    dis = [robots[robot_id]['x'], 50 - robots[robot_id]['x'], robots[robot_id]['y'], 50 - robots[robot_id]['y']]
    dis = np.array(dis)
    return dis.min()

def move_target(r_distance, workstations, robots):
    # Setting the angle and speed for each robot.
    # Only ensure the + or - for angle
    for robot_id in range(len(robots)):
        # If station target = -1, how to do ???
        station_target = r_next[robot_id]
        delta_x = workstations[station_target]["x"] - robots[robot_id]['x']
        delta_y = workstations[station_target]["y"] - robots[robot_id]['y']
        direction = np.arctan2(delta_y, delta_x)
        delta_direction = direction - robots[robot_id]['direction']
        # tanh映射角速度
        ex = np.exp(delta_direction)
        ex2 = np.exp(-delta_direction)
        r_action[robot_id][1] = np.pi * (ex - ex2) / (ex + ex2)
        # r_action[robot_id][1] = delta_direction
        # Always the maximum speed in positive
        eps = 2
        if abs(delta_direction) > 0.1:
            r_action[robot_id][0] = 0
        else:
            if dis_wall(robot_id) < eps:
                if abs(delta_direction) > 0.01:
                    r_action[robot_id][0] = 0
                else:
                    r_action[robot_id][0] = 3
            else:
                r_action[robot_id][0] = 6
        # 是否靠近墙壁
        # if dis_wall(robot_id) > eps:
        #     if abs(delta_direction) > 0.1:
        #         r_action[robot_id][0] = 0
        #     else:
        #         r_action[robot_id][0] = 6
        # else:
        #     # 是否对准
        #     if abs(delta_direction) > 0.001:
        #         #没对准，则慢慢减速
        #         r_action[robot_id][0] = 0
        #     else:
        #         #对准，则匀速
        #         r_action[robot_id][0] = 6
    
    # 找到会发生碰撞的机器人i与j，进行碰撞躲避
    detect_robot_list = []
    for robot_i in range(len(robots)):
        for robot_j in range(len(robots)):
            if robot_j > robot_i:
                # 如果两机器人之间的距离小于碰撞距离阈值，则进一步检测是否会发生碰撞
                if r_r_distance[robot_i][robot_j] <= (crash_distance * crash_distance):
                    # detect_robot_list.append([robot_id, j])
                    # 判断 机器人 i，j 之间是否 即将 发生碰撞，如果发生碰撞，则进行规避；不发生，则不做任何行为
                    if if_crash(robots, robot_i, robot_j):
                        # 对机器人i与j进行躲避碰撞, 函数内调整角速度。
                        evade_crash(robots, robot_i, robot_j)

def evade_crash(robots, robot_i, robot_j):
    # angle_speedi =  
    # angle_speedi = if robots[robot_j]['direction']
    r_action[robot_i][1] = - np.pi
    r_action[robot_j][1] = np.pi
    r_action[robot_i][0] = -2

def if_crash(robots, robot_i, robot_j, frame = 50):
    ''' 将会发生碰撞返回true, 否则返回false
    '''
    # 5帧，也就是 0.1s 进行一次，未来距离运算.一直到frame的帧数截止
    # 机器人i与j的半径 0.53或0.45
    radius_i = 0.53 if robots[robot_i]['if_product'] else 0.45
    radius_j = 0.53 if robots[robot_j]['if_product'] else 0.45
    distance = radius_i + radius_j
    during_frame = 5
    for i in range(int (frame/during_frame)):
        second = ((i+1) * during_frame) * 0.02
        v1 = np.sqrt(np.square(robots[robot_i]['x_line_speed']) + np.square(robots[robot_i]['y_line_speed']))
        v2 = np.sqrt(np.square(robots[robot_j]['x_line_speed']) + np.square(robots[robot_j]['y_line_speed']))
        x1 = robots[robot_i]['x'] + v1 * np.cos(robots[robot_i]['direction']) * second
        y1 = robots[robot_i]['y'] + v1 * np.sin(robots[robot_i]['direction']) * second
        x2 = robots[robot_j]['x'] + v2 * np.cos(robots[robot_j]['direction']) * second
        y2 = robots[robot_j]['y'] + v2 * np.cos(robots[robot_j]['direction']) * second
        if np.square(x1 - x2) + np.square(y1 - y2) <= np.square(distance):
            return True
    return False

def handle_module(workstations, robots, frame_id, money):
    # Maintain the distance for each robot and s_type for stations.
    r_distance = maintain_varible(workstations, robots)

    # Update r_next for each robot.
    # And speed and angle speed for each robot.
    find_target(r_distance, workstations, robots)
    move_target(r_distance, workstations, robots)

    # Check and update buy, sell, destroy action for each robot.
    check_action(workstations, robots)

def respond_module():
    sys.stdout.write('%d\n' % frame_id)
    # line_speed, angle_speed = 3, 1.5
    for robot_id in range(4):
        line_speed, angle_speed, buy, sell, destroy = r_action[robot_id]
        sys.stdout.write('forward %d %d\n' % (robot_id, line_speed))
        sys.stdout.write('rotate %d %f\n' % (robot_id, angle_speed))
        if buy != -1:
            sys.stdout.write('buy %d\n' % (robot_id))
        if sell != -1:
            sys.stdout.write('sell %d\n' % (robot_id))
        if destroy != -1:
            sys.stdout.write('destroy %d\n' % (robot_id))
    # log.write_string(f"{r_action[1][4]}")
        # log.write_string('forward %d %d\n' % (robot_id, line_speed))
        # log.write_string('rotate %d %f\n' % (robot_id, angle_speed))
        # log.write_string('buy %d %d\n' % (robot_id, buy))
        # log.write_string('sell %d %d\n' % (robot_id, sell))

# Different material buy and sell money. 
# m_price = [[3000, 6000], [4400, 7600], [5800, 9200], [15400, 22500], [17200, 25000], [19200, 27500], [76000, 105000]]
# station_work_time = [50, 50, 50, 500, 500, 500, 1000, 1, 1]
# Action mapping
# action_list = ["forward", "rotate", "buy", "sell", "destroy"]
# The distance robot to each station. Type list[list[]]
r_distance = []
# 两两机器人之间的距离
r_r_distance = []
# 执行碰撞检测的最小距离
crash_distance = 2
# K station type
s_type = []
# The next target station for robot i. Length 4.
r_next = [-1, -1, -1, -1]
# The next action for robot i. For a given robot i, [forward_value, rotate_value, buy_value, sell_value, destroy_value],
# The last three equal to -1, means no buy, sell and destroy action. list[list[]] shape 4*4
# 销毁操作初始为-1， 销毁则为2.
r_action = [[-1]*5, [-1]*5, [-1]*5, [-1]*5]

frame_id = 0

# Set an order for each robot, there are orders for 1 and no for 0.
r_order = [0, 0, 0, 0]
log = Log()

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
