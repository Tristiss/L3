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

num = 3
test_phase = True

u_current = 10

def u_voltage(volt):
    return volt * 0.001 + 0.05

def main(num):
    df = pd.read_csv(rf"C:\Programmieren\Praktikum\L3\Data\Messung_{num}.csv", sep = ";", names = ["voltages", "currents"])
    # remove names after num = 5

    voltages = list(df["voltages"][1:])
    currents = list(df["currents"][1:])

    spl = make_smoothing_spline(voltages, currents)

    x = np.linspace(voltages[0], voltages[-1], 10000)
    
    smoothed_data = spl(x)

    peaks, props = find_peaks(smoothed_data)

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

    print(np.mean(diff))
    print(np.std(diff))

    fig, axs = plt.subplots()

    axs.errorbar(voltages, currents, xerr = u_volt, yerr = u_current, capsize= 3, label = "Messdaten")
    axs.plot(x, smoothed_data, label = "Geglättete Messdaten")
    axs.errorbar(volt_peaks, curr_peaks, xerr = u_volt_peak, yerr = u_volt_peak, capsize = 3, fmt = "o", label = "Peaks")

    # edit style for plots
    axs.legend()
    axs.grid()
    axs.set_xlabel(r'Kinetische Energie $E$ [eV]')
    axs.set_ylabel(r'Spannung $U$ [mV]')
    axs.set_title(rf'Messung {num}')
    plt.show()
    if test_phase == False: # save figure
        fig.savefig(fname = rf"Messung_{num}_v1.pdf", format = "pdf")
        
    plt.show()

if __name__ == "__main__":
    main(num)