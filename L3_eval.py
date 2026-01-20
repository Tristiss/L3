import locale
import scipy.constants as constants
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.interpolate import make_smoothing_spline

# enable latex in plots
mpl.rcParams['text.usetex'] = True
mpl.rcParams.update(mpl.rcParamsDefault)

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

num = 11
test_phase = True

u_current = 10

def u_voltage(volt):
    return volt * 0.001 + 0.05

def single_evaluation(num, axs, rev_bias, ax_3d):
    if num == 5:
        df = pd.read_csv(rf"C:\Programmieren\Praktikum\L3\Data\Messung_{num}.csv", names = ["voltages", "currents"], sep = ";")    
        voltages = list(df["voltages"][1:])
        currents = list(df["currents"][1:])
    else:
        df = pd.read_csv(rf"C:\Programmieren\Praktikum\L3\Data\Messung_{num}.csv", sep = ";")
        voltages = list(df["voltages"])
        currents = list(df["currents"])

    spl = make_smoothing_spline(voltages, currents)

    x = np.linspace(voltages[0], voltages[-1], 10000)
    
    smoothed_data = spl(x)

    peaks, props = find_peaks(smoothed_data, prominence = 6)

    volt_peaks = [x[i] for i in peaks]
    curr_peaks = [smoothed_data[i] for i in peaks]

    u_volt = [u_voltage(i) for i in voltages]

    u_volt_peak = [u_voltage(i) for i in volt_peaks]

    v0 = 0
    diff = []

    for i in volt_peaks:
        if i == volt_peaks[0]:
            v0 = i
        else:
            diff.append(i - v0)
            v0 = i

    energy = [np.mean(diff), np.std(diff)]

    print(energy)

    axs.errorbar(voltages, currents, xerr = u_volt, yerr = u_current, capsize= 3, label = f"Roh {rev_bias}")
    axs.plot(x, smoothed_data, label = f"Geglättet {rev_bias}")
    ax_3d.plot(x, smoothed_data, zs=rev_bias, zdir='z', label='curve in (x, y)')
    axs.errorbar(volt_peaks, curr_peaks, xerr = u_volt_peak, yerr = u_volt_peak, capsize = 3, fmt = "o", label = f"Peaks {rev_bias}")

    return energy

if __name__ == "__main__":
    reverse_bias_num = {
        0.5 : 6,
        1   : 7,
        1.5 : 8,
        2   : 9,
        2.5 : 5,
        3   : 10,
        3.5 : 11,
        4   : 12,
        4.5 : 13
    }

    differences = {}

    fig, axs = plt.subplots()
    fig_diff, axs_diff = plt.subplots()
    ax_3d = plt.figure().add_subplot(projection='3d')

    for i in reverse_bias_num.keys():
        energy = single_evaluation(reverse_bias_num[i], axs, i, ax_3d)
        axs_diff.errorbar(i, energy[0], yerr = energy[1], capsize = 3, fmt = "o", label = f"{i} A") #xerr = 0.5 * (2 * np.sqrt(6)),

    # edit style for plots
    axs.legend(loc = 2, ncol = 3)
    axs.grid()
    axs.set_xlabel(r'Kinetische Energie $E$ [eV]')
    axs.set_ylabel(r'Spannung $U$ [mV]')
    axs.set_title(rf'Alle Messungen')
    if test_phase == False: # save figure
        fig.savefig(fname = rf"Alle_Messungen_v1.pdf", format = "pdf")

    # edit style for plots
    axs_diff.legend(loc = 2, ncol = 2)
    axs_diff.grid()
    axs_diff.set_xlabel(r'Gegenspannung $U_G$ [V]')
    axs_diff.set_ylabel(r'Kinetische Energie $E$ [eV]')
    axs_diff.set_title(rf'Energie gegen Gegenspannung')
    plt.show()
    if test_phase == False: # save figure
        fig_diff.savefig(fname = rf"Messung_eval_v1.pdf", format = "pdf")
        
    plt.show()