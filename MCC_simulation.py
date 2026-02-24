import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import constants as c
from numpy import random
from tqdm import tqdm

pos_x_db = []
pos_y_db = []
pos_z_db = []

b_max = 49 * (4 * c.pi * c.epsilon_0 * np.square(c.hbar)) / (c.electron_mass * np.square(c.elementary_charge)) # m
dt = 1e-10 # s
max_time = 1e-5 # s
thickness = 5e-02 # m
reverse_bias = 2
lowest_trans_energy = 4.89 * c.elementary_charge # J
min_y = -2e-02 # m
max_y = 2e-02 # m
min_z = -2e-02 # m
max_z = 2e-02 # m
det_min_y = -1e-02 # m
det_max_y = 1e-02 # m
det_min_z = -1e-02 # m
det_max_z = 1e-02 # m

runs = 1

voltages = np.linspace(20, 50, 100) # V

sigma = np.square(b_max) * np.pi
n = 2.6e20 # 1 / m^3

electrons_per_sim = 200

def kinetic_energy(vel:np.ndarray):
    return 0.5 * c.electron_mass * np.square(np.linalg.norm(vel))

def mc_collision(vel:np.ndarray):
    propability = 1 - np.e**(- n * sigma * np.linalg.norm(vel) * dt)

    random_val = random.random()
    b = b_max * np.sqrt(random.random())

    if propability > random_val:
        if kinetic_energy(vel) > lowest_trans_energy:
            direction_vector = vel / np.linalg.norm(vel)
            vel -= direction_vector * np.sqrt((2 * lowest_trans_energy) / (c.electron_mass))
            return vel
        else:
            
            n_q = int(np.sqrt((b * c.electron_mass * np.square(c.elementary_charge)) / (4 * np.pi * c.epsilon_0 * np.square(c.hbar))))
            sigma_n_l = {
                0 : 0,
                1 : 0.6,
                2 : 2.8,
                3 : 8.85,
                4 : 21.4,
                5 : 49.4,
                6 : 70.2,
            }
            alpha = (80 - sigma_n_l[n_q]) * np.square(c.elementary_charge) / (4 * np.pi * c.epsilon_0)
            chi = np.pi - 2 * np.arccos((alpha / (c.electron_mass * np.square(np.linalg.norm(vel)) * b)) / np.sqrt(1 + (alpha) / np.square(c.electron_mass * np.square(np.linalg.norm(vel)) * b)))
            #vel_new = np.sqrt(np.square(np.linalg.norm(vel)) - ((80 - sigma_n_l[n_q]) * np.square(c.elementary_charge)) / (2 * np.pi * c.electron_mass * c.epsilon_0 * b))
            phi = random.uniform(0, 2 * np.pi)
            
            direction_vector = vel / np.linalg.norm(vel)

            vel[0] = direction_vector[0] * np.linalg.norm(vel) * np.sin(chi) * np.cos(phi)
            vel[1] = direction_vector[1] * np.linalg.norm(vel) * np.sin(chi) * np.sin(phi)
            vel[2] = direction_vector[2] * np.linalg.norm(vel) * np.cos(chi)
            #print("Elastic Collision occured (EC)")
            return vel
    return vel

def field_acc(voltage:float, thickness:float):
    return np.array([c.elementary_charge * voltage / (thickness * c.electron_mass), 0, 0])

def single_particle_verlet(voltage:float, counter:int):
    time = 0
    pos = np.array([0, random.uniform(min_y / 4, max_z / 4), random.uniform(min_z / 4, max_z / 4)])
    vel = np.array([random.normal(0, 1e05), random.normal(0, 1e05), random.normal(0, 1e05)]) # 0, random.uniform(-1, 1) * 5e06, random.uniform(-1, 1) * 5e06])

    acc = field_acc(voltage, thickness)

    datax = []
    datay = []
    dataz = []

    res = 0

    while res == 0:
        time += dt
        pos += vel * dt + 0.5 * acc * dt * dt
        vel += acc * dt
        
        vel = mc_collision(vel)

        datax.append(pos[0])
        datay.append(pos[1])
        dataz.append(pos[2])
        if not(-1 <= pos[0] < thickness):
            res = 1
            #print("Left x")
            #print(pos)
        elif not(min_y <= pos[1] <= max_y):
            res = 1
            #print("Left y")
        elif not(min_z <= pos[2] <= max_z):
            res = 1
            #print("Left z")
        elif not(time < max_time):
            res = 1
            #print("Timeout")

    pos_x_db.append(datax)
    pos_y_db.append(datay)
    pos_z_db.append(dataz)
    
    if kinetic_energy(vel) >= c.elementary_charge * reverse_bias and pos[0] >= thickness and det_min_y <= pos[1] <= det_max_y and det_min_z <= pos[2] <= det_max_z:
        counter += 1

    return counter
    
def sweep(num:int):
    currents = []
    for voltage in tqdm(voltages, colour = "#20C20E"):
        counter = 0
        for i in tqdm(range(electrons_per_sim), colour = "#20C20E"):
            counter = single_particle_verlet(voltage, counter)
            #print(counter)
        currents.append(counter)
    #plt.plot(voltages, currents)
    df = pd.DataFrame({"voltages": voltages, "currents": currents})
    df.to_csv(fr"C:\Programmieren\Praktikum\L3\Data\Sim\Messung_rev_bias_{reverse_bias}_{num}.csv", sep = ";")

def main():
    for i in range(runs):
        sweep(i)

    """ax = plt.figure().add_subplot(projection='3d')

    for i in range(len(pos_x_db)):
        ax.plot(pos_x_db[i], pos_y_db[i], pos_z_db[i])

    ax.set_xbound(0, thickness)
    ax.set_ybound(min_y, max_y)
    ax.set_zbound(min_z, max_z)

    ax.set_xlim(0, thickness)
    ax.set_ylim(min_y, max_y)
    ax.set_zlim(min_z, max_z)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")"""

if __name__ == "__main__":
    main()
    plt.show()