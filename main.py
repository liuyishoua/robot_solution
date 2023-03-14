import sys
from utils import have_material_type, find_materials_id, stationtype_index, have_product_index, have_material_index
import numpy as np

# 本地图跑 ，图一，二，三，四，分别为55w，45w, 18w, 44w
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
    # log.write_string(f"{frame_num}")
    workstations = []
    for i in range(K):
        station_type, x, y, rest_frame, material_state, product_state = input().split()
        station_type, x, y, rest_frame, material_state, product_state = int(station_type), float(x), float(y), int(
            rest_frame), int(material_state), int(product_state)
        stration_dict = dict({"type": station_type, "x": x, "y": y, "rest_frame": rest_frame, "m_state": material_state,
                              "p_state": product_state})
        workstations.append(stration_dict)
    # log.write_string(f"9: {workstations[9]['x']}, {workstations[9]['y']}; 4: {workstations[4]['x']}, {workstations[4]['y']}")
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

    r_priority = []
    # Compute priority from station
    for station_id in range(len(workstations)):
        priority = 10

        # 补2缺1
        if is_materials_2only1_rest(workstations[station_id]['type']):
            priority = 20
        # 补3缺2
        if is_materials_3only2_rest(workstations[station_id]['type']):
            priority = 15
        # 补3缺1
        if is_materials_3only1_rest(workstations[station_id]['type']):
            priority = 30

        if workstations[station_id]['type'] in [4, 5, 6]:
            priority = 40

        if workstations[station_id]['type'] in [7]:
            priority = 50

        # for robot_id in range(len(robots)):
        #     if robots[robot_id]['if_product'] == workstations[station_id]['type']:
        #         priority -= 1

        if is_station_rest(station_id) == 0:
            priority = 0
        if workstations[station_id]['p_state'] == 0:
            priority = 0
        r_priority.append(priority)

    # log.write_string(f'second: {frame_id / 50},  r_priority: {r_priority}\n ')

    if frame_id == 1:  # 只在刚开始的时候，维护工作站的类型
        for station_id in range(len(workstations)):
            s_type.append(workstations[station_id]['type'])

    return r_distance, r_priority


# 给一个产品，判断当前是否存在两个空一个的空格
def is_materials_2only1_rest(m_type):
    res = 0
    for station_id in range(len(workstations)):
        type = workstations[station_id]['type']
        if type in [4, 5, 6]:
            rest_materials = find_materials_id(type, workstations[station_id]['m_state'])
            if m_type in rest_materials and len(rest_materials) == 1:
                res = 1
    return res


# 给一个产品，判断当前是否存在三个空一个的空格
def is_materials_3only1_rest(m_type):
    res = 0
    for station_id in range(len(workstations)):
        type = workstations[station_id]['type']
        if type == 7:
            rest_materials = find_materials_id(type, workstations[station_id]['m_state'])
            if m_type in rest_materials and len(rest_materials) == 1:
                res = 1
    return res


# 给一个产品，判断当前是否存在三个空两个的空格
def is_materials_3only2_rest(m_type):
    res = 0
    for station_id in range(len(workstations)):
        type = workstations[station_id]['type']
        if type == 7:
            rest_materials = find_materials_id(type, workstations[station_id]['m_state'])
            if m_type in rest_materials and len(rest_materials) == 2:
                res = 1
    return res


# 给一个产品，判断当前是否有空格
def is_materials_rest(m_type):
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
def is_station_rest(station_id):
    return is_materials_rest(workstations[station_id]['type'])


def check_action(workstations, robots):
    # Check for buy, sell, destroy for each robot.
    for robot_id in range(len(robots)):
        target_station = r_next[robot_id]
        robot_in_station = robots[robot_id]["if_station"]
        if robots[robot_id]["if_station"] == target_station:
            # 这里处理完订单后r_order设置为0，寻找下一个订单
            # 检查买卖，都是直接行为。机器人有产品就卖，没产品就买。
            if robots[robot_id]["if_product"] != 0:
                # 可做判断。能否卖。
                station_type = workstations[target_station]['type']
                # 进一步判断靶工作站,空缺材料位的list
                material_id = find_materials_id(station_type, workstations[target_station]['m_state'])
                if robots[robot_id]["if_product"] in material_id:
                    # 可卖成功
                    r_action[robot_id][3] = target_station
                    r_order[robot_id] = 0
                else:
                    for station_id in range(len(workstations)):
                        rest_materials = find_materials_id(workstations[station_id]['type'], workstations[station_id]['m_state'])
                        if robots[robot_id]["if_product"] in rest_materials:
                            r_next[robot_id] = station_id
                            break

                    # destory非 -1 都能执行
                    # 销毁操作，只在当前帧进行。
                    # r_action[robot_id][4] = 2
                    pass
            else:
                # 能否成功买，不用判断
                r_action[robot_id][2] = target_station
                r_order[robot_id] = 0



def find_target(r_distance, r_priority, workstations, robots):
    for robot_id in range(len(robots)):
        if r_order[robot_id] == 0:  # 如果当前机器人没有靶订单，则设置靶订单
            r_order[robot_id] = 1
            r_distance_with_index = [[distance, index] for index, distance in enumerate(r_distance[robot_id])]
            r_distance_with_index_sorted = sorted(r_distance_with_index, key=lambda x: x[0])


            # 当前机器人无货物在手，要向工作台买
            # if robots[robot_id]['if_product'] == 0:
            #     # log.write_object(workstations)
            #     # log.write_list(s_type)
            #     index_list = stationtype_index(s_type, [4, 5, 6, 7])  # 获取工作站类型的 index
            #     index_list_with_product = have_product_index(workstations, index_list)  # 获取有产品的工作站的 index
            #     # 4，5，6，7 工作台是否有货，有则买；否则买 1，2，3 工作台。//如果工作台都没货，之后考虑（基本不存在这种情况，因为1，2，3工作台更新很快）
            #     flag = 0
            #     for _, index in r_distance_with_index_sorted:
            #         if index in index_list_with_product and index not in r_next:
            #             r_next[robot_id] = index
            #             flag = 1
            #             break
            #     if flag == 0:
            #         index_list = stationtype_index(s_type, [1, 2, 3])
            #         index_list_with_product = have_product_index(workstations, index_list)
            #         for _, index in r_distance_with_index_sorted:
            #             if index in index_list_with_product and index not in r_next:
            #                 r_next[robot_id] = index
            #                 break
            # else:
            #     # 当前机器人有货物在手，要卖给工作台
            #     product_id = robots[robot_id]['if_product']  # 机器人手中产品的类型
            #     # 产品类别为1，卖给 4，5，9 工作台
            #     # 产品类别为2，卖给 4，6，9 工作台
            #     # 产品类别为3，卖给 5，6，9 工作台
            #     # 产品类别为4，卖给 7，9 工作台
            #     # 产品类别为5，卖给 7，9 工作台
            #     # 产品类别为6，卖给 7，9 工作台
            #     # 产品类别为7，卖给 8，9 工作台
            #     # 要求，卖给的工作台要有材料空位，//且含有优先级数组index，之后考虑//如果不存在有空位的工作台，之后考虑
            #     if product_id == 1:
            #         index_list = stationtype_index(s_type, [4, 5, 9])  # 获取工作站类型的 index
            #         # 获取有材料为空缺的工作站的 index。当然,空缺的材料类型与机器人运送物品的类型相同
            #         index_list_with_material = have_material_index(workstations, index_list, product_id)
            #         for _, index in r_distance_with_index_sorted:  # 这部分代码速度可以提升
            #             if index in index_list_with_material and index not in r_next:
            #                 r_next[robot_id] = index
            #                 break
            #     elif product_id == 2:
            #         index_list = stationtype_index(s_type, [4, 6, 9])
            #         index_list_with_material = have_material_index(workstations, index_list, product_id)
            #         for _, index in r_distance_with_index_sorted:
            #             if index in index_list_with_material and index not in r_next:
            #                 r_next[robot_id] = index
            #                 break
            #     elif product_id == 3:
            #         index_list = stationtype_index(s_type, [5, 6, 9])
            #         index_list_with_material = have_material_index(workstations, index_list, product_id)
            #         for _, index in r_distance_with_index_sorted:
            #             if index in index_list_with_material and index not in r_next:
            #                 r_next[robot_id] = index
            #                 break
            #     elif product_id == 4 or product_id == 5 or product_id == 6:
            #         index_list = stationtype_index(s_type, [7, 9])
            #         index_list_with_material = have_material_index(workstations, index_list, product_id)
            #         for _, index in r_distance_with_index_sorted:
            #             if index in index_list_with_material and index not in r_next:
            #                 r_next[robot_id] = index
            #                 break
            #     elif product_id == 7:
            #         index_list = stationtype_index(s_type, [8, 9])
            #         index_list_with_material = have_material_index(workstations, index_list, product_id)
            #         for _, index in r_distance_with_index_sorted:
            #             if index in index_list_with_material and index not in r_next:
            #                 r_next[robot_id] = index
            #                 break

            # r_priority_with_index = [[priority, index] for index, priority in enumerate(r_priority)]
            # r_priority_with_index_sorted = np.argsort(-np.array(r_priority))

            r_priority = np.array(r_priority)
            if robots[robot_id]['if_product'] == 0:
                # log.write_object(workstations)
                # log.write_list(s_type)
                index_list = stationtype_index(s_type, [1, 2, 3, 4, 5, 6, 7])  # 获取工作站类型的 index
                index_list_with_product = have_product_index(workstations, index_list)  # 获取有产品的工作站的 index
                # 4，5，6，7 工作台是否有货，有则买；否则买 1，2，3 工作台。//如果工作台都没货，之后考虑（基本不存在这种情况，因为1，2，3工作台更新很快）
                index_list = []
                max_priority = np.max(r_priority)
                min_distance = 9999
                r_next_cur = -1
                for i in range(len(r_priority)):
                    if r_priority[i] == max_priority:
                        if r_distance[robot_id][i] < min_distance and i not in r_next:
                            min_distance = r_distance[robot_id][i]
                            r_next[robot_id] = i
                # r_next[robot_id] = r_next_cur

                # r_priority_with_index_sorted = np.argsort(-np.array(r_priority))
                # index_list = stationtype_index(s_type, [1, 2, 3, 4, 5, 6, 7])  # 获取工作站类型的 index
                # index_list_with_product = have_product_index(workstations, index_list)  # 获取有产品的工作站的 index
                # for index in r_priority_with_index_sorted:
                #     if index in index_list_with_product and index not in r_next:
                #         r_next[robot_id] = index
                #         break

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
                # 要求，卖给的工作台要有材料空位，//且含有优先级数组index，之后考虑//如果不存在有空位的工作台，之后考虑
                if product_id == 1:
                    index_list = stationtype_index(s_type, [4, 5, 9])  # 获取工作站类型的 index
                    # 获取有材料为空缺的工作站的 index。当然,空缺的材料类型与机器人运送物品的类型相同
                    index_list_with_material = have_material_index(workstations, index_list, product_id)
                    for _, index in r_distance_with_index_sorted:  # 这部分代码速度可以提升
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


def dis_wall(robot_id):
    dis = [robots[robot_id]['x'], 50 - robots[robot_id]['x'], robots[robot_id]['y'], 50 - robots[robot_id]['y']]
    dis = np.array(dis)
    return dis.min()


def move_target(r_distance, workstations, robots):
    for robot_id in range(len(robots)):
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

    for robot_id in range(len(robots)):
        for robot_j in range(len(robots)):
            if robot_j > robot_id:
                    # 如果两机器人之间的距离小于碰撞距离阈值，则进一步检测是否会发生碰撞
                    # if r_r_distance[robot_id][robot_j] <= (crash_distance * crash_distance):
                        # # 判断 机器人 i，j 之间是否 即将 发生碰撞，如果发生碰撞，则进行规避；不发生，则不做任何行为
                if if_crash(robots, robot_id, robot_j):
                            # 对机器人i与j进行躲避碰撞, 函数内调整角速度。
                    evade_crash(robots, robot_id, robot_j)
                    # pass
def evade_crash(robots, robot_i, robot_j):
    r_action[robot_j][0] = -2
    r_action[robot_j][1] = - np.sign(r_action[robot_j][1]) * np.pi
    # if r_action[robot_i][0] > r_action[robot_j][0]:
    #     pass
    # else:
    #     r_action[robot_i][0] = 3
    #     r_action[robot_i][1] = 0.5 * np.pi
    #     r_action[robot_j][1] = - 0.5 * np.pi

    # # 碰撞物理模拟, robot i 1帧后，是顺时针的方向还是逆时针的方向离robot j更近。我们想要更远的时针，作为i的角速度方向
    # during_frame = 1
    # second = (during_frame) * 0.02
    # # 判断机器人 i 向哪个时针旋转，以躲避 j
    # robot_i_shun = robots[robot_i]['direction'] + delta_theta
    # robot_i_ni = robots[robot_i]['direction'] - delta_theta

    # v1 = np.sqrt(np.square(robots[robot_i]['x_line_speed']) + np.square(robots[robot_i]['y_line_speed']))

    # x_shun = robots[robot_i]['x'] + v1 * np.cos(robot_i_shun) * second
    # y_shun = robots[robot_i]['y'] + v1 * np.sin(robot_i_shun) * second
    # x_ni = robots[robot_i]['x'] + v1 * np.cos(robot_i_ni) * second
    # y_ni = robots[robot_i]['y'] + v1 * np.sin(robot_i_ni) * second

    # delta_distance_shun = np.square(x_shun - robots[robot_j]['x']) + np.square(y_shun - robots[robot_j]['y'])
    # delta_distance_ni = np.square(x_ni - robots[robot_j]['x']) + np.square(y_ni - robots[robot_j]['y'])
    # if delta_distance_shun > delta_distance_ni:
    #     r_action[robot_i][1] = robot_i_shun
    # elif delta_distance_shun < delta_distance_ni:
    #     r_action[robot_i][1] = robot_i_ni


    # # 判断机器人 i 向哪个时针旋转，以躲避 j
    # robot_j_shun = robots[robot_j]['direction'] + delta_theta
    # robot_j_ni = robots[robot_j]['direction'] - delta_theta

    # v2 = np.sqrt(np.square(robots[robot_j]['x_line_speed']) + np.square(robots[robot_j]['y_line_speed']))

    # x_shun = robots[robot_j]['x'] + v2 * np.cos(robot_j_shun) * second
    # y_shun = robots[robot_j]['y'] + v2 * np.sin(robot_j_shun) * second
    # x_ni = robots[robot_j]['x'] + v2 * np.cos(robot_j_ni) * second
    # y_ni = robots[robot_j]['y'] + v2 * np.sin(robot_j_ni) * second

    # delta_distance_shun = np.square(x_shun - robots[robot_i]['x']) + np.square(y_shun - robots[robot_i]['y'])
    # delta_distance_ni = np.square(x_ni - robots[robot_i]['x']) + np.square(y_ni - robots[robot_i]['y'])
    # if delta_distance_shun > delta_distance_ni:
    #     r_action[robot_j][1] = robot_j_shun
    # elif delta_distance_shun < delta_distance_ni:
    #     r_action[robot_j][1] = robot_j_ni

    # r_action[robot_i][0] = 0 
    # r_action[robot_i][1] = 0
    # r_action[robot_j][0] = 0
    # r_action[robot_j][1] = 0

def if_crash(robots, robot_i, robot_j, frame=100):
    ''' 将会发生碰撞返回true, 否则返回false
    '''
    # 5帧，也就是 0.1s 进行一次，未来距离运算.一直到frame的帧数截止
    # 机器人i与j的半径 0.53或0.45
    # if abs(robots[robot_i]['direction'] - robots[robot_j]['direction']) < np.pi / 2:
    #     return False
    radius_i = 0.53 if robots[robot_i]['if_product'] else 0.45
    radius_j = 0.53 if robots[robot_j]['if_product'] else 0.45
    distance = radius_i + radius_j
    during_frame = 1
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

def get_material_locked(workstations):
    '''获取所有工作站的信息,获取被死锁了的材料。(即该材料类被没有工作站能接收去放)
    '''
    # 材料有1-7个类别。设立空的set集合，遍历station，找到所有空缺的材料类别添加到set里面。
    # set集合中没有1-7的哪个类别，哪个类别就被锁住了。
    have_material = set()
    for i, station in enumerate(workstations):
        # 输入的工作台类别只能是4,5,6,7,8,9, 这种收购类型的工作台
        if station["type"] in [4,5,6,7,8,9]:
            material_list = find_materials_id(station["type"], station['m_state'])
            for material in material_list:
                have_material.add(material)
    
    # have material中没有的元素
    result = set([1,2,3,4,5,6,7]) - have_material
    return list(result)

def get_locked_station(workstations, product_list):
    '''输入类别,获取锁住的所有工作台id。并按找优先级排序 (只要一个材料就能解锁的无疑拥有更高的优先级)。
    输入产品类别数组，获取锁住的所有工作台
    '''
    locked_station = []

    for i, station in enumerate(workstations):
        if 1 in product_list and station['type'] in [4,5,9]:
            locked_station.append(i)
        elif 2 in product_list and station['type'] in [4,6,9]:
            locked_station.append(i)
        elif 3 in product_list and station['type'] in [5,6,9]:
            locked_station.append(i)
        elif (4 in product_list or 5 in product_list or 6 in product_list) and station['type'] in [7,9]:
            locked_station.append(i)
        elif 7 in product_list and station['type'] in [8,9]:
            locked_station.append(i)
        
    return locked_station

def get_material_class(workstations, locked_station):
    # 获取锁住的工作站，完成解锁（或者说完成合成），所需材料类别。
    material_class = set()
    for index in locked_station:
        material_list = find_materials_id(workstations[index]["type"], workstations[index]['m_state'])
        for material in material_list:
            material_class.add(material)
    return list(material_class)

def lock_remove(workstations, robots):
    # 解除死锁。给非死锁的空闲机器人以及非死锁的有材料的机器人，更新靶工作站。
    # 1. 机器人判断：哪几个机器人死锁（手上有材料，但是没地方卖）。如果没死锁，分为空闲的机器人和手上有材料的机器人。
    # 2. 根据死锁的机器人手上拿的材料找到 需要解锁的工作站，获取index list。
    # 3. 获取待解锁的工作站，所需解锁的材料 list。
    # 4. 空闲机器人去找解除 “死锁工作站所需的材料”；非空闲机器人则判断自己手上的材料是否能用于解除死锁工作站，如果能，则改方向去死锁工作站
    locked_robot_index = []
    free_robot_index = []
    material_robot_index = []

    locked_station_index = [] # 锁住的工作站
    locked_station_need_material = [] # 解锁，锁住的工作站所需的材料

    # 获取每一帧，物品 1-7, 哪个类别物品锁住了。
    material_locked_list = get_material_locked(workstations)
    robot_material_locked_list = []
    for robot_id in range(len(robots)):
        product = robots[robot_id]["if_product"]
        if product == 0:
            free_robot_index.append(robot_id)
        elif product in material_locked_list:
            # 判断机器人的产品是否有材料位，可以接收。
            # 如果没有材料位可以接收，则找到那些材料位置满，所以锁住了的工作站，获取index list。
            # 并获取锁住的工作站，解锁所需的材料
            locked_robot_index.append(robot_id)
            robot_material_locked_list.append(product)
        else:
            # 如果有材料位可以接收
            material_robot_index.append(robot_id)

    # log.write_string(f"当前时间：{frame_id/50} 秒，被锁住的机器人的index：{locked_robot_index}; 它相应的被锁住的材料位置：{robot_material_locked_list}")
    # log.write_string(f"空闲机器人的index：{free_robot_index}")
    # log.write_string(f"有材料但是没被锁住的机器人：{material_robot_index}；")   
    
    # 输入索住物品类别，获取相应锁住了的工作站 index list。
    # 并获取锁住了工作台的优先级，到时候for循环优先解锁。
    locked_station_index = get_locked_station(workstations, robot_material_locked_list)
    # 获取锁住的工作站，完成解锁（或者说完成合成），所需材料类别。
    locked_station_need_material = get_material_class(workstations, locked_station_index)
    # log.write_string(f"被锁住工作站所需的解锁材料，{locked_station_need_material}；")
    
    # 输入机器人所需材料类别 list，获取相应的工作台 list
    station_index = stationtype_index(s_type, locked_station_need_material)
    # log.write_string(f"被锁住工作站所需的解锁材料，能生产解锁材料的工作站index，{station_index}；")
    index_list_with_product = have_product_index(workstations, station_index)  # 获取有产品的工作站的 index
    # log.write_string(f"被锁住工作站所需的解锁材料，能供应解锁材料的工作站index，{index_list_with_product}；")

    # 空闲的机器人和不空闲但有材料的机器人要开始解锁了。解锁工作台
    # 空闲的机器人下一个target节点，是解锁工作站所需材料。材料也需要有优先级。
    for free_robot in free_robot_index:
        # r_distance_with_index = [[distance, index] for index, distance in enumerate(r_distance[robot_id])]
        # r_distance_with_index_sorted = sorted(r_distance_with_index, key=lambda x: x[0])

        # 如果空手的机器人没单，则找能解锁工作台的新单
        if r_order[free_robot] == 0:
            for index in index_list_with_product:
                if index not in r_next:
                    r_next[free_robot] = index
                    r_order[free_robot] = 1
                    break
        elif r_order[free_robot] == 1:
            # 如果空闲机器手里有单，则判断是不是去找解锁工作站所需材料单
            # 如果不是，则换单；如果是，则不执行行为
            if workstations[r_next[free_robot]]['type'] not in locked_station_need_material:
                for index in index_list_with_product:
                    if index not in r_next:
                        r_next[free_robot] = index
                        break

    # 有材料的机器人且没死锁的，如果材料对的上，就去解锁指定工作站。否则不执行任何操作。
    for material_robot in material_robot_index:
        product = robots[material_robot]['if_product']
        
        # 如果有材料的机器人没单，则看看该材料能不能解锁被锁住的工作站
        # 如果能解锁，则派单。不能解锁，则继续完成当前订单。
        if r_order[material_robot] == 0:
            for station_index in locked_station_index: # 遍历锁住了的工作站
                # 如果有材料机器人拿着的材料，能被锁住了的工作站收购，那就让有材料的机器人去那个工作站。
                if product in find_materials_id(workstations[station_index]["type"], workstations[station_index]['m_state']) and station_index not in r_next:
                    r_next[material_robot] = station_index
                    r_order[material_robot] = 1
                    break
        elif r_order[material_robot] == 1:
            # 如果有材料的机器人有单，则看该材料能不能解锁被锁住的工作站
            # 如果能，则判断它的去是不是锁住的工作站，是则不进行操作；不是则，改变派单
            # 如果不能，则不进行任何操作
            if product in locked_station_need_material:
                if r_next[material_robot] not in locked_station_index:
                    for station_index in locked_station_index: 
                        if product in find_materials_id(workstations[station_index]["type"], workstations[station_index]['m_state']) and station_index not in r_next:
                            r_next[material_robot] = station_index
                            break
    # log.write_string(f"\n")

def handle_module(workstations, robots, frame_id, money):
    # Maintain the distance for each robot and s_type for stations.
    r_distance, r_priority = maintain_varible(workstations, robots)

    # Update r_next for each robot.
    # And speed and angle speed for each robot.
    find_target(r_distance, r_priority, workstations, robots)
    move_target(r_distance, workstations, robots)

    # 解除死锁
    lock_remove(workstations, robots)

    # Check and update buy, sell, destroy action for each robot.
    check_action(workstations, robots)


def respond_module():
    sys.stdout.write('%d\n' % frame_id)
    # line_speed, angle_speed = 3, 1.5
    for robot_id in range(4):
        line_speed, angle_speed, buy, sell, destroy = r_action[robot_id]
        if frame_id > 8650:
            buy = -1
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
# 每个机器人与工作台之间的距离. 类型 list[list[]]，shape是（4，工作台的个数）
r_distance = []
# 两两机器人之间的距离
r_r_distance = []
# 执行碰撞检测的最小距离
crash_distance = 2
# 工作台的类型list
s_type = []
# The next target station for robot i. Length 4.
r_next = [-1, -1, -1, -1]
# The next action for robot i. For a given robot i, [forward_value, rotate_value, buy_value, sell_value, destroy_value],
# The last three equal to -1, means no buy, sell and destroy action. list[list[]] shape 4*4
# 销毁操作初始为-1， 销毁则为2.
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
