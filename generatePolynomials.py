import numpy as np
import importlib
import matplotlib.pyplot as plt
import sys
import os

def polynomial(x, y, num_segments):

    x_segments = np.array_split(x, num_segments)
    y_segments = np.array_split(y, num_segments)

    t_curve_segments = []
    x_curve_segments = []
    y_curve_segments = []

    coefficients=[]
    segments=[]
    coefficients_y=np.array([])
    coefficients_z=np.array([])

    for x_seg, y_seg in zip(x_segments, y_segments):
        t_values_seg = np.linspace(0, 2*np.pi, x_seg.size)
        coefficients_x_seg = np.polyfit(t_values_seg, x_seg, 7)
        coefficients_y_seg = np.polyfit(t_values_seg, y_seg, 7)
        t_curve_seg = np.linspace(min(t_values_seg), max(t_values_seg), 100)
        x_curve_seg = np.polyval(coefficients_x_seg, t_curve_seg)
        y_curve_seg = np.polyval(coefficients_y_seg, t_curve_seg)
        t_curve_segments.append(t_curve_seg)
        x_curve_segments.append(x_curve_seg)
        y_curve_segments.append(y_curve_seg)
        segment=np.array([])
        segment=np.concatenate((segment, np.flip(coefficients_x_seg), np.flip(coefficients_y_seg), np.zeros(16)))
        segments.append(list(segment))
    segments.append(segments[0])

    x_curve = np.concatenate(x_curve_segments)
    y_curve = np.concatenate(y_curve_segments)
    return segments, x_curve, y_curve

def plot_trajectory(x, y, x_curve, y_curve):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(x, y, label='Trajectory Points')
    ax.plot(x_curve, y_curve, label='Trajectory Curve', color='red')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('7th Degree Polynomial Fit')
    plt.legend()
    plt.grid(True)
    plt.show()

def write_to_file(file_path, segments, num_segments, duration):
    with open(file_path, 'w') as file:
        for segment in segments:
            file.write(str('{:.6f}'.format(duration/num_segments))+','+','.join(str('{:.6f}'.format(coeff)) for coeff in segment) + '\n')
        
if __name__ == "__main__":
    if len(sys.argv) !=5:
        print("Usage: python3 generatePolynomials.py [input_coordinates.py] [total_duration] [number_of_polynomials] [output_polynomials.csv]")
        exit()
    inputPath=sys.argv[1]
    duration=int(sys.argv[2])
    num_segments = int(sys.argv[3])
    output=sys.argv[4]

    sys.path.append(os.path.dirname(inputPath))
    module_name = os.path.splitext(os.path.basename(inputPath))[0]
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        print(f"Error: Could not import module '{module_name}'")

    data=np.array(module.trajectory_points)
    x = data[:, 0]
    y = data[:, 1]
    segments, x_curve, y_curve=polynomial(x, y, num_segments)
    plot_trajectory(x, y, x_curve, y_curve)
    write_to_file(output, segments, num_segments, duration)
