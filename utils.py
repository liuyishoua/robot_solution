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