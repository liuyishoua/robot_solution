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

# 打印读取的数据以进行测试
print("Frame number:", frame_num)
print("Money:", money)
print("Number of workstations:", K)
print("Workstations:", workstations)
print("Robots:", robots)