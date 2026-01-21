import locale
import scipy.constants as constants
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.interpolate import make_smoothing_spline
from os import listdir
from os.path import isfile, join

# enable latex in plots
mpl.rcParams['text.usetex'] = True
mpl.rcParams.update(mpl.rcParamsDefault)

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

num = 11
test_phase = True

path = r"C:\Programmieren\Praktikum\L3\Data"

u_current = 10

def u_voltage(volt):
    return volt * 0.001 + 0.05

def csv_read(filename):
    df = pd.read_csv(path + r"\\" + filename, sep = ";")
    voltages = list(df["voltages"])
    currents = list(df["currents"])
    return voltages, currents

def single_evaluation(voltages, currents, axs, rev_bias, ax_3d):
    spl = make_smoothing_spline(voltages, currents)

    u_volt = [u_voltage(i) for i in voltages]

    x = np.linspace(voltages[0], voltages[-1], 10000)
    
    smoothed_data = spl(x)

    valley_find_data = smoothed_data.copy()
    valley_find_data *= -1

    valleys, props = find_peaks(valley_find_data, prominence = 6)

    volt_valleys = [x[i] for i in valleys]
    curr_valleys = [smoothed_data[i] for i in valleys]

    axs.errorbar(voltages, currents, xerr = u_volt, yerr = u_current, capsize= 3, label = f"Roh {round(rev_bias,2)}")
    axs.plot(x, smoothed_data, label = f"Spline {round(rev_bias,2)}")
    ax_3d.plot(x, smoothed_data, zs=rev_bias, zdir='z')

    peaks, props = find_peaks(smoothed_data, prominence = 6)

    volt_peaks = [x[i] for i in peaks]
    curr_peaks = [smoothed_data[i] for i in peaks]

    u_volt_peak = [u_voltage(i) for i in volt_peaks]

    v0 = 0
    diff = []

    if len(volt_peaks) >= 5:
        for i in volt_peaks:
            if i == volt_peaks[0]:
                v0 = i
            else:
                diff.append(i - v0)
                v0 = i

        energy = [np.mean(diff), np.std(diff)]

        print(energy)
        axs.errorbar(volt_peaks, curr_peaks, xerr = u_volt_peak, yerr = u_current, capsize = 3, fmt = "o", label = f"Peaks {round(rev_bias,2)}")
        axs.errorbar(volt_valleys, curr_valleys, fmt = "o", label = f"Valleys {round(rev_bias,2)}")

        if len(peaks) == len(valleys):
            contrast = [(curr_peaks[i] - curr_valleys[i]) / (curr_peaks[i] + curr_valleys[i]) for i in range(len(peaks))]
            contrast = [np.mean(contrast), np.std(contrast)]
            return energy, contrast
        return energy, "Nan"
    return "Nan", "Nan"

def main():
    # get all files in the directory
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]

    onlyfiles.sort()

    fig, axs = plt.subplots()
    fig_diff, axs_diff = plt.subplots()
    fig_contrast, axs_contrast = plt.subplots()
    ax_3d = plt.figure().add_subplot(projection='3d')

    rev_bias_contrast_li = []
    contrast_li = []
    u_contrast_li = []
    energy_li = []

    for i in onlyfiles:
        # get the rev bias from one of the filenames
        split = i.split("_")
        rev_bias = float(split[-2])
        voltages, currents = csv_read(i)
        energy, contrast = single_evaluation(voltages, currents, axs, rev_bias, ax_3d)
        if energy != "Nan":
            energy_li.append(energy[0])
            axs_diff.errorbar(rev_bias, energy[0], yerr = energy[1], capsize = 3, fmt = "o", label = f"{round(rev_bias,2)} A") #xerr = 0.5 * (2 * np.sqrt(6)),
        if contrast != "Nan":
            rev_bias_contrast_li.append(rev_bias)
            contrast_li.append(contrast[0])
            u_contrast_li.append(contrast[1])
    
    energy_li.pop(0)
    energy_li.pop(2)

    print(np.mean(energy_li))
    print(np.std(energy_li))

    axs_contrast.errorbar(rev_bias_contrast_li, contrast_li, yerr = u_contrast_li, fmt = "o", capsize = 3)

    # edit style for plots
    axs.legend(loc = 2, ncol = 3, fontsize = 6)
    axs.grid()
    axs.set_xlabel(r'Kinetische Energie $E$ [eV]')
    axs.set_ylabel(r'Spannung $U$ [mV]')
    axs.set_title(rf'Alle Messungen')
    if test_phase == False: # save figure
        fig.savefig(fname = rf"Alle_Messungen_v1.pdf", format = "pdf")

    axs_contrast.legend(loc = 4, ncol = 2)
    axs_contrast.grid()
    axs_contrast.set_xlabel(r'Gegenspannung $U_G$ [V]')
    axs_contrast.set_ylabel(r'Kontrast $K$ [mV]')
    axs_contrast.set_title(rf'Kontrast gegen Gegenspannung')
    plt.show()
    if test_phase == False: # save figure
        fig_contrast.savefig(fname = rf"Messung_contrast_v1.pdf", format = "pdf")

    axs_diff.legend(loc = 4, ncol = 2)
    axs_diff.grid()
    axs_diff.set_xlabel(r'Gegenspannung $U_G$ [V]')
    axs_diff.set_ylabel(r'Kinetische Energie $E$ [eV]')
    axs_diff.set_title(rf'Energie gegen Gegenspannung')
    plt.show()
    if test_phase == False: # save figure
        fig_diff.savefig(fname = rf"Messung_energy_v1.pdf", format = "pdf")
        
    plt.show()
    

if __name__ == "__main__":
    main()