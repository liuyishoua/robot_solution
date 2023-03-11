#!/bin/bash
import sys
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

    robots = []
    for i in range(4):
        if_station, if_product, time_factor, break_factor, angle_speed, x_line_speed, y_line_speed, direction, x, y = input().split()
        if_station, if_product, time_factor, break_factor, angle_speed, x_line_speed, y_line_speed, direction, x, y = int(if_station), int(if_product), float(time_factor), float(break_factor), float(angle_speed), float(x_line_speed), float(y_line_speed), float(direction), float(x), float(y)
        robot_dict = dict({"if_station":if_station, "if_product":if_product, "time_factor":time_factor, "break_factor":break_factor, "angle_speed":angle_speed, "x_line_speed":x_line_speed, "y_line_speed":y_line_speed, "direction":direction, "x":x, "y":y})
        robots.append(robot_dict)

    return workstations, robots, frame_num, money

def find_indices(num):
    # Convert the number to a binary string
    binary_string = bin(num)[1:][::-1]
    # Create a list of the non-zero indices using a list comprehension
    nonzero_indices = [i for i, bit in enumerate(binary_string) if bit == '1']
    return nonzero_indices

def find_null_materials_id(station_type, num):
    materials_list = find_indices(num)
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
    
    return id_list

def check_action(workstations, robots):
    # Check for buy, sell, destroy for each robot.
    for robot_id in range(len(robots)):
        target_station = r_next[robot_id]
        # If robot arrive the target station
        if robots[robot_id]["if_station"] == target_station:
            # Check buy or sell. If robot have something, then sell. Otherwise buy.
            if robots[robot_id]["if_product"] != -1:
                product_id = robots[robot_id]["if_product"]
                station_type = workstations[target_station]['type']
                m_state = workstations[target_station]['m_state']
                # Robot sell, station buy
                # If station not full material, then sell. otherwise do what
                if product_id in find_null_materials_id(station_type, m_state):
                    r_action[robot_id][3] = target_station
                    workstations[target_station]['m_state'] = m_state + int(pow(2, product_id))
                else:
                    # Robot sell, but station full, do what
                    pass
            else:
                # Robot buy, station sell
                if workstations[target_station]['p_state']:
                    r_action[robot_id][2] = target_station
                    if workstations[target_station]["rest_frame"] != 0:
                        workstations[target_station]['p_state'] = 0
                else:
                    # Robot buy, but station dont have, do what
                    pass

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

def find_target(r_distance, workstations, robots):
    for robot_id in range(len(robots)):
        r_distance_with_index = [[distance, index] for index, distance in enumerate(r_distance[robot_id])]
        r_distance_with_index_sorted = sorted(r_distance_with_index, key=lambda x: x[0])

        # Check current robot if have product.
        if robots[robot_id]['if_product'] == 0:
            temp_list = [a or b or c for a, b, c in zip(np.array(s_type)==1, np.array(s_type)==2, np.array(s_type)==3)]
            index_list = [i for i in range(len(temp_list)) if temp_list[i]]
            # Current robot not take the product
            for _, index in r_distance_with_index_sorted:
                if index in index_list and index not in r_next:
                    r_next[robot_id] = index
                    break
        else:
            # Current robot take the product
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

def move_target(r_distance, workstations, robots):
    # Setting the angle and speed for each robot.
    # Only ensure the + or - for angle
    for robot_id in range(len(robots)):
        # If station target = -1, how to do ???
        station_target = r_next[robot_id]
        delta_x = workstations[station_target]["x"] - robots[robot_id]['x']
        delta_y = workstations[station_target]["y"] - robots[robot_id]['y']
        direction = np.arctan2(delta_y, delta_x)
        delta_direction = (direction - robots[robot_id]['direction'])
        r_action[robot_id][1] = delta_direction
        # Always the maximum speed in positive
        r_action[robot_id][0] = 3

def handle_module(workstations, robots, frame_id, money):
    # Maintain the distance for each robot and s_type for stations.
    r_distance = maintain_varible(workstations, robots)

    # Check and update buy, sell, destroy action for each robot.
    check_action(workstations, robots)

    # Update r_next for each robot.
    # And speed and angle speed for each robot.
    find_target(r_distance, workstations, robots)
    move_target(r_distance, workstations, robots)
    check_action(workstations, robots)

def respond_module():
    sys.stdout.write('%d\n' % frame_id)
    # line_speed, angle_speed = 3, 1.5
    for robot_id in range(4):
        line_speed, angle_speed, buy, sell, destroy = r_action[robot_id]
        sys.stdout.write('forward %d %d\n' % (robot_id, line_speed))
        sys.stdout.write('rotate %d %f\n' % (robot_id, angle_speed))
        if buy != -1:
            sys.stdout.write('buy %d %d\n' % (robot_id, buy))
        if sell != -1:
            sys.stdout.write('sell %d %d\n' % (robot_id, sell))

# Different material buy and sell money. 
m_price = [[3000, 6000], [4400, 7600], [5800, 9200], [15400, 22500], [17200, 25000], [19200, 27500], [76000, 105000]]
station_work_time = [50, 50, 50, 500, 500, 500, 1000, 1, 1]
# Action mapping
action_list = ["forward", "rotate", "buy", "sell", "destroy"]
# The distance robot to each station. Type list[list[]]
r_distance = []
# K station type
s_type = []
# The next target station for robot i. Length 4.
r_next = [5, 2 ,3 ,4]
# The next action for robot i. For a given robot i, [forward_value, rotate_value, buy_value, sell_value, destroy_value],
# The last three equal to -1, means no buy, sell and destroy action. list[list[]] shape 4*4
r_action = [[-1]*5, [-1]*5, [-1]*5, [-1]*5]

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
