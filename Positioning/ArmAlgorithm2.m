#Arm algorithm 2

import math
import pandas as pd
import numpy as np

def calculate_coordinates_and_base_distance(a, b):

    M = 8.255
    N = 19.685
    O = 19.05
    P = 22.86
    Result = False

    #P_Point
    x1=0

    y1=0

    #O_point
    x2=0
    y2= 22.70    #22.86

    #N_point
    x3 = x2 - 16.51*math.sin(math.radians(a))  #19.05
    y3 = y2 - 16.51*math.cos(math.radians(a))

    #M_point
    x4 = x3 - 20.32*math.sin(math.radians(b)) #19.685
    y4 = y3 + 20.32*math.cos(math.radians(b))

    #S_point
    x5 = x4 
    y5 = y4 - 8.255

    c = 360 - a - b

    #C angle
    if (-1 < y5 < 1):
        Result = True

    #real_a_angle = math.acos((((0 * -19.05*math.cos(math.radians(a))) + (-22.86 * -19.05*math.cos(math.radians(a))) / (math.sqrt(math.pow(0, 2) + math.pow(22.86, 2) * math.sqrt(math.pow(19.05, 2) + math.pow(19.05, 2)))))))
    #real_b_angle = math.acos((((19.05*math.cos(math.radians(a)) * 19.685*math.sin(math.radians(b))) + (-19.05*math.sin(math.radians(a)) * 19.685*math.cos(math.radians(b))) / (math.sqrt(math.pow(19.05, 2) + math.pow(19.05, 2) * math.sqrt(math.pow(19.685, 2) + math.pow(19.685, 2)))))))
    #real_c_angle = math.acos((((0 * 19.685*math.sin(math.radians(b))) + (-22.86 * 19.685*math.sin(math.radians(b))) / (math.sqrt(math.pow(0, 2) + math.pow(22.86, 2) * math.sqrt(math.pow(19.685, 2) + math.pow(19.685, 2)))))))
    
    # Compute real_a_angle
    #numerator_a = (0 * -19.05 * math.sin(math.radians(a))) + (-22.86 * -19.05 * math.cos(math.radians(a)))
    #denominator_a = (math.sqrt(math.pow(0, 2) + math.pow(22.86, 2)) * math.sqrt(math.pow(19.05*math.sin(math.radians(a)), 2) + math.pow(0, 2)))
    #result_a = numerator_a / denominator_a
    #clamped_a = max(-1, min(1, result_a))  # Clamp to [-1, 1]
    #real_a_angle = math.degrees(math.acos(clamped_a))

    # Compute real_b_angle
    #numerator_b = (19.05 * math.cos(math.radians(a)) * 19.685 * math.cos(math.radians(b))) + (19.05 * math.sin(math.radians(a)) * -19.685 * math.sin(math.radians(b)))
    #denominator_b = (math.sqrt(math.pow(19.05*math.sin(math.radians(a)), 2) + math.pow(19.05*math.cos(math.radians(a)), 2)) * math.sqrt(math.pow(19.685*math.cos(math.radians(b)), 2) + math.pow(19.685*math.cos(math.radians(b)), 2)))
    #result_b = numerator_b / denominator_b


    #if (result_b > 1) or (result_b < -1):
    #    clamped_b = result_b % (math.pi/4)
    #else:
    #    clamped_b = result_b
    #real_b_angle = math.degrees(math.acos(clamped_b))




    # Compute real_c_angle
    #numerator_c = (0 * 19.685 * math.sin(math.radians(b))) + (19.85*math.cos(math.radians(b)) * -8.255)
    #denominator_c = (math.sqrt(math.pow(0, 2) + math.pow(8.255, 2)) * math.sqrt(math.pow(19.685*math.sin(math.radians(b)), 2) + math.pow(19.685*math.cos(math.radians(b)), 2)))
    #result_c = numerator_c / denominator_c

    #if (result_c > 1) or (result_c < -1):
    #    clamped_c = result_c % (math.pi/4)
    #else:
    #    clamped_c = result_c
    #real_c_angle = math.degrees(math.acos(clamped_c))

    #distance = abs(x4)

    # Define the coordinates of the points
    x_coords = [x1, x2, x3, x4, x5]
    y_coords = [y1, y2, y3, y4, y5]

    # Define vectors between consecutive points
    vectors = [
        [x2 - x1, y2 - y1],  # Vector 1 (x1 to x2)
        [x3 - x2, y3 - y2],  # Vector 2 (x2 to x3)
        [x4 - x3, y4 - y3],  # Vector 3 (x3 to x4)
        [x5 - x4, y5 - y4]   # Vector 4 (x4 to x5)
        ]   

    # Calculate angles dynamically
    angles = []
    for i in range(len(vectors) - 1):  # Loop through pairs of vectors
        u = np.array(vectors[i])      # Vector u
        v = np.array(vectors[i + 1])  # Vector v
    
        # Compute dot product and magnitudes
        dot_product = np.dot(u, v)
        magnitude_u = np.linalg.norm(u)
        magnitude_v = np.linalg.norm(v)
    
        # Calculate the angle (in degrees)
        angle = np.degrees(np.arccos(dot_product / (magnitude_u * magnitude_v)))
        angles.append(angle)


    #return(a, real_a_angle, b, real_b_angle, c, real_c_angle, Result, distance, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, numerator_a, denominator_a, result_a, clamped_a, numerator_b, denominator_b, result_b, clamped_b, numerator_c, denominator_c, result_c, clamped_c)
    return(a, b, c, Result, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, angles)


angle_range_a = range(70, 120, 1)
angle_range_b = range(0, 270, 1)

results = []

#for a in angle_range:
#    for b in angle_range:
for a in angle_range_a:
    for b in angle_range_b:
        #angle_a, real_angle_a, angle_b, real_angle_b, angle_c, real_angle_c, result, distance, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, numerator_a, denominator_a, result_a, clamped_a, numerator_b, denominator_b, result_b, clamped_b, numerator_c, denominator_c, result_c, clamped_c= calculate_coordinates_and_base_distance(a, b)
        angle_a, angle_b, angle_c, result, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, angles = calculate_coordinates_and_base_distance(a, b)
        if result == True:
            #results.append({"a": angle_a, "Real a": real_angle_a, "b": angle_b, "Real b": real_angle_b, "c": angle_c, "Real c": real_angle_c, "result": result, "base_distance": distance, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "x3": x3, "y3": y3, "x4": x4, "y4": y4, "x5": x5, "y5": y5, "numerator_a": numerator_a, "denominator_a": denominator_a, "result_a": result_a, "clamped_a": clamped_a, "numerator_b": numerator_b, "denominator_b": denominator_b, "result_b": result_b, "clamped_b": clamped_b, "numerator_c": numerator_c, "denominator_c": denominator_c, "result_c": result_c, "clamped_c": clamped_c})
            if x3 < x4:
                angles[2] = 180 + angles[2]

            elif x3 > x4:
                angles[2] = 180 - angles[2]
            results.append({"a": angle_a, "b": angle_b, "c": angle_c, "result": result, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "x3": x3, "y3": y3, "x4": x4, "y4": y4, "x5": x5, "y5": y5, "angle_a": 180-angles[0], "angle_b": 180-angles[1], "angle_c": angles[2]})
print("Test completed")

# Create a DataFrame and save to Excel
resultstdata = pd.DataFrame(results)

datatoexcel = pd.ExcelWriter('ArmResults15.xlsx')

resultstdata.to_excel(datatoexcel)

datatoexcel.close()
