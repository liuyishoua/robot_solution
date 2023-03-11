#!/bin/bash
import sys
# from log import Log
from utils import find_indices, find_null_materials_id
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

    return workstations, robots, frame_num, money

def maintain_varible(workstations, robots):
    # Compute distance between robot and station
    for robot_id in range(len(robots)):
        robot_i = []
        for station_id in range(len(workstations)):
            distance = np.square(robots[robot_id]['x'] - workstations[station_id]['x']) + np.square(robots[robot_id]['y'] - workstations[station_id]['y'])
            robot_i.append(distance)
        r_distance.append(robot_i)

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
            # 如果出现材料放不下的情况，就不能算处理完订单。
            
            # Check buy or sell. If robot have something, then sell. Otherwise buy.
            if robots[robot_id]["if_product"] != 0:
                r_action[robot_id][3] = target_station

                # product_id = robots[robot_id]["if_product"]
                # station_type = workstations[target_station]['type']
                # m_state = workstations[target_station]['m_state']
                # Robot sell, station buy
                # If station not full material, then sell. otherwise do what
                
                # if product_id in find_null_materials_id(station_type, m_state):    
                #     workstations[target_station]['m_state'] = m_state + int(pow(2, product_id))
                # else:
                #     # Robot sell, but station full, do what
                #     pass
            else:
                # log.write_string(f"target_station: {target_station}, robot_in_station: {robot_in_station}")
                # log.write_string(f"product: {workstations[target_station]['p_state']}")
                # Robot buy, station sell
                if workstations[target_station]['p_state']:
                    r_action[robot_id][2] = target_station
                    # if workstations[target_station]["rest_frame"] != 0:
                    #     workstations[target_station]['p_state'] = 0
                # else:
                #     # Robot buy, but station dont have, do what
                #     pass

def find_target(r_distance, workstations, robots):
    for robot_id in range(len(robots)):
        if r_order[robot_id] == 1:
            pass
        else:
            r_distance_with_index = [[distance, index] for index, distance in enumerate(r_distance[robot_id])]
            r_distance_with_index_sorted = sorted(r_distance_with_index, key=lambda x: x[0])

            # Current robot dont have product.
            if robots[robot_id]['if_product'] == 0:
                temp_list = [a or b or c for a, b, c in zip(np.array(s_type)==1, np.array(s_type)==2, np.array(s_type)==3)]
                index_list = [i for i in range(len(temp_list)) if temp_list[i]]
                for _, index in r_distance_with_index_sorted:
                    if index in index_list and index not in r_next:
                        r_next[robot_id] = index
                        break
            else:
                # Current robot have the product
                robot_product_id = robots[robot_id]['if_product']
                if robot_product_id == 1:
                    temp_list = [a or b or c for a, b, c in zip(np.array(s_type)==4, np.array(s_type)==5, np.array(s_type)==9)]
                    index_list = [i for i in range(len(temp_list)) if temp_list[i]]
                    for _, index in r_distance_with_index_sorted:
                        if index in index_list and index not in r_next:
                            r_next[robot_id] = index
                            break
                elif robot_product_id == 2:
                    temp_list = [a or b or c for a, b, c in zip(np.array(s_type)==4, np.array(s_type)==6, np.array(s_type)==9)]
                    index_list = [i for i in range(len(temp_list)) if temp_list[i]]
                    for _, index in r_distance_with_index_sorted:
                        if index in index_list and index not in r_next:
                            r_next[robot_id] = index
                            break
                elif robot_product_id == 3:
                    temp_list = [a or b or c for a, b, c in zip(np.array(s_type)==5, np.array(s_type)==6, np.array(s_type)==9)]
                    index_list = [i for i in range(len(temp_list)) if temp_list[i]]
                    for _, index in r_distance_with_index_sorted:
                        if index in index_list and index not in r_next:
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
        # if robot_id == 1:
        #     log.write_string(f'second: {frame_id / 50}, r_next: {r_next[3]}\n')


def handle_module(workstations, robots, frame_id, money):
    # Maintain the distance for each robot and s_type for stations.
    r_distance = maintain_varible(workstations, robots)

    # Check and update buy, sell, destroy action for each robot.
    check_action(workstations, robots)

    # Update r_next for each robot.
    # And speed and angle speed for each robot.
    find_target(r_distance, workstations, robots)
    move_target(r_distance, workstations, robots)

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
# K station type
s_type = []
# The next target station for robot i. Length 4.
r_next = [-1, -1, -1, -1]
# The next action for robot i. For a given robot i, [forward_value, rotate_value, buy_value, sell_value, destroy_value],
# The last three equal to -1, means no buy, sell and destroy action. list[list[]] shape 4*4
r_action = [[-1]*5, [-1]*5, [-1]*5, [-1]*5]

frame_id = 0

# Set an order for each robot, there are orders for 1 and no for 0.
r_order = [0, 0, 0, 0]
# log = Log()

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
