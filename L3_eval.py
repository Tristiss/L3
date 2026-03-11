import locale
import math
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
from scipy.interpolate import make_smoothing_spline
from os import listdir
from os.path import isfile, join
from tqdm import tqdm

# enable latex in plots
mpl.rcParams['text.usetex'] = True
mpl.rcParams.update(mpl.rcParamsDefault)

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

test_phase = False

path = r"C:\Programmieren\Praktikum\L3\Data"

u_current = 10 / (2 * np.sqrt(6))

kwargs = {
            "fmt" : "x",
            "capsize" : 3,
            "elinewidth" : 0.8,
            "capthick" : 0.8,
            "c" : "black"
        }

kwargs_wo_fmt = {
            "fmt" : " ",
            "capsize" : 3,
            "elinewidth" : 0.8,
            "capthick" : 0.8,
            "c" : "black"
        }

k = {
    1   :   13.97,
    2   :   4.527,
    3   :   3.306,
    4   :   2.87,
    5   :   2.649,
    6   :   2.517,
    7   :   2.429,
    8   :   2.366,
    9   :   2.32,
    10  :   2.284,
    11  :   2.255,
    12  :   2.231,
    13  :   2.212,
    14  :   2.195,
    15  :   2.181,
    16  :   2.169,
    17  :   2.158,
    18  :   2.149,
    19  :   2.14,
    20  :   2.133,
    21  :   2.126,
    22  :   2.12,
    23  :   2.115,
    24  :   2.11,
    25  :   2.105,
    26  :   2.101,
    27  :   2.097,
    28  :   2.093,
    29  :   2.09,
    30  :   2.087,
    31  :   2.084,
    32  :   2.081,
    33  :   2.079,
    34  :   2.076,
    35  :   2.074,
    36  :   2.072,
    37  :   2.07,
    38  :   2.068,
    39  :   2.066,
    40  :   2.064
}

def u_voltage(volt):
    return volt * 0.001 + 0.05

def weighted_mean(values:list[float], uncertainties:list[float]) ->float:
    if len(values) != len(uncertainties):
        raise ArithmeticError("Miss match in val and unc length")
    upper = lower = 0
    for i in range(len(values)):
        upper += values[i] / np.square(uncertainties[i])
        lower += 1 / np.square(uncertainties[i])

    return upper / lower

def unc_sum(uncertainties:list[float]) -> float:
    lower = 0
    for i in uncertainties:
        lower += 1 / np.square(i)
    return lower

def internal_unc_type_a(uncertainties:list[float]) -> float:
    lower = unc_sum(uncertainties)
    n = len(uncertainties)
    return k[n - 1] * np.sqrt(1 / lower) / np.sqrt(n)

def external_unc_type_a(values:list[float], uncertainties:list[float], weighted_mean:float) -> float:
    n = len(uncertainties)
    if len(values) != n:
        raise ArithmeticError("Miss match in val and unc length")
    upper = 0
    lower = unc_sum(uncertainties)
    for i in range(len(values)):
        upper += np.square(values[i] - weighted_mean) / uncertainties[i]
    return k[n - 1] / np.sqrt(n) * np.sqrt(upper / ((len(values) - 1) * lower))

def weigted_type_a_unc(values:list[float], uncertainties:list[float]) -> list[float]:
    mean = weighted_mean(values, uncertainties)
    internal = internal_unc_type_a(uncertainties)
    external = external_unc_type_a(values, uncertainties, mean)
    return [mean, max(internal, external)]

def normal_type_a_unc(values:list[float]) -> float:
    n = len(values)
    return k[n - 1] * np.std(values) / np.sqrt(n)

# Source - https://realpython.com/python-rounding/#rounding-up
# By DevCademy Media Inc. DBA Real Python
# Retrieved 2026-01-14, usage is allowed only non commercially
#import math
# ...
#def round_up(n, decimals=0):
#   multiplier = 10**decimals
#   return math.ceil(n * multiplier) / multiplier

def round_up(n, decimals = 0):
    multiplier = 10**decimals
    return math.ceil(n * multiplier) / multiplier

def csv_read(filename:str) -> tuple[list, list]:
    df = pd.read_csv(path + r"\\" + filename, sep = ";")
    voltages = list(df["voltages"])
    currents = list(df["currents"])
    return voltages, currents

def single_evaluation(voltages:list[float], currents:list[float], axs, rev_bias:float, ax_3d):
    spl = make_smoothing_spline(voltages, currents)

    u_volt = [u_voltage(i) for i in voltages]

    x = np.linspace(voltages[0], voltages[-1], 10000)
    
    smoothed_data = spl(x)

    valley_find_data = smoothed_data.copy()
    valley_find_data *= -1

    valleys, props = find_peaks(valley_find_data, prominence = 6)

    volt_valleys = [x[i] for i in valleys]
    curr_valleys = [smoothed_data[i] for i in valleys]

    #fig_sing, axs_sing = plt.subplots()

    #axs.errorbar(voltages, currents, xerr = u_volt, yerr = u_current, capsize= 3, label = f"Roh {round(rev_bias,2)}")
    axs.plot(x, smoothed_data, label = f"Spline {round(rev_bias,2)}")
    #axs_sing.plot(x, smoothed_data, label = f"Spline {round(rev_bias,2)}")
    ax_3d.plot(x, smoothed_data, zs=rev_bias, zdir='z')

    peaks, props = find_peaks(smoothed_data, prominence = 6)

    volt_peaks = [x[i] for i in peaks]
    curr_peaks = [smoothed_data[i] for i in peaks]

    u_volt_peak = [u_voltage(i) for i in volt_peaks]

    v0 = 0
    u_v0 = 0
    diff = []
    u_diff = []

    #axs_sing.errorbar(volt_peaks, curr_peaks, xerr = u_volt_peak, yerr = u_current, capsize = 3, fmt = "o", label = f"Peaks {round(rev_bias,2)}")
    #axs_sing.errorbar(volt_valleys, curr_valleys, fmt = "o", label = f"Valleys {round(rev_bias,2)}")

    #axs_sing.grid()
    #axs_sing.set_xlabel(r'Kinetische Energie $E$ [eV]')
    #axs_sing.set_ylabel(r'Spannung $U$ [mV]')
    #axs_sing.set_title(rf'Messung bei Gegenspannung {round(rev_bias, 2):n} V')
    #axs_sing.ticklabel_format(style='sci', axis='y', scilimits=(0,0)) # credit below
    #if test_phase == False: # save figure
    #    fig_sing.savefig(fname = rf"Messung_single_{rev_bias}_v1.pdf", format = "pdf")

    if len(volt_peaks) >= 5:
        for i in volt_peaks:
            if i == volt_peaks[0]:
                v0 = i
                u_v0 = u_volt_peak[volt_peaks.index(i)]
            else:
                diff.append(i - v0)
                u_diff.append(np.sqrt(np.square(u_volt_peak[volt_peaks.index(i)]) + np.square(u_v0)))
                v0 = i
                u_v0 = u_volt_peak[volt_peaks.index(i)]

        n = len(diff)
        type_b = 0
        for i in u_diff: # this type of for loop could be replaced with np.sum
            type_b += np.square(i)
        u_diff_val = np.sqrt(np.square(normal_type_a_unc(diff)) + type_b / np.square(len(u_diff)))
        
        energy = [np.mean(diff), u_diff_val, diff]

        if len(peaks) == len(valleys):
            contrast = [(curr_peaks[i] - curr_valleys[i]) / (curr_peaks[i] + curr_valleys[i]) for i in range(len(peaks))]
            
            u_peak = np.square((2 * curr_valleys[-2]) / np.square(curr_peaks[-2] + curr_valleys[-2]) * u_current)
            u_valley = np.square((2 * curr_peaks[-2]) / np.square(curr_peaks[-2] + curr_valleys[-2]) * u_current)

            type_b = np.sqrt(u_peak + u_valley)

            contrast = [contrast[-2], type_b]
            return energy, contrast, curr_peaks[-2]
        return energy, "Nan", "Nan"
    return "Nan", "Nan", "Nan"

def main():
    # get all files in the directory
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]

    onlyfiles.sort()

    fig, axs = plt.subplots()
    fig_diff, axs_diff = plt.subplots()
    fig_contrast, axs_contrast = plt.subplots()
    fig_sig, axs_sig = plt.subplots()
    fig_sig_con, axs_sig_con = plt.subplots()
    fig_peaks, axs_peaks = plt.subplots()
    fig_3d = plt.figure()
    ax_3d = fig_3d.add_subplot(projection='3d')

    rev_bias_contrast_li = []
    rev_bias_energy_li = []
    contrast_li = []
    u_contrast_li = []
    energy_li = []
    u_energy_li = []
    curr_peaks_li = []
    diff_li = [[],[],[],[],[]]

    for i in tqdm(onlyfiles, colour = "#20C20E"):
        # get the rev bias from one of the filenames
        split = i.split("_")
        rev_bias = float(split[-2])
        voltages, currents = csv_read(i)
        energy, contrast, curr_peak = single_evaluation(voltages, currents, axs, rev_bias, ax_3d)
        if energy != "Nan":
            energy_li.append(energy[0])
            u_energy_li.append(energy[1])
            rev_bias_energy_li.append(rev_bias)
            for i in energy[2]:
                diff_li[energy[2].index(i)].append(i)
        if contrast != "Nan":
            rev_bias_contrast_li.append(rev_bias)
            contrast_li.append(contrast[0])
            u_contrast_li.append(contrast[1])
            curr_peaks_li.append(curr_peak)

    e_mean, u_e_mean = weigted_type_a_unc(energy_li, u_energy_li)
    print(f"mean energy:{e_mean}")
    print(f"unc mean energy:{u_e_mean}")

    diffs_li = []
    u_diffs_li = []

    for i in diff_li:
        unc = normal_type_a_unc(i)
        diffs_li.append(np.mean(i))
        u_diffs_li.append(unc)

    peaks = range(len(diffs_li))

    p = np.polyfit(peaks, diffs_li, 1)
    print(f"Lin Fit results (e peak): {p}")

    x = np.linspace(min(peaks), max(peaks), 10000)
    y = [p[1] + p[0] * i for i in x]

    axs_peaks.plot(x, y, c = "#6100B0", label = "Linearer Fit")
    axs_peaks.errorbar(peaks, diffs_li, yerr = u_diffs_li, label = "Messwerte", **kwargs)

    print(f"energies for peaks: {[float(round(i,4)) for i in diffs_li]}")
    print(f"energies for peaks: {[float(round_up(i,4)) for i in u_diffs_li]}")

    u_rev_bias_energy = [u_voltage(i) for i in rev_bias_energy_li]
    u_rev_bias_contrast = [u_voltage(i) for i in rev_bias_contrast_li]

    def falling_exp(x, a, b):
        return a * np.e**(-b * x)
    def rising_exp(x, a, b):
        return a * np.e**(b * x)

    x = np.linspace(min(rev_bias_contrast_li), max(rev_bias_contrast_li), 10000)

    p = np.polyfit(rev_bias_contrast_li, contrast_li, 1)
    print(f"Lin Fit results (e peak): {p}")

    y = [p[1] + p[0] * i for i in x]

    popt_sig, pcov = curve_fit(falling_exp, rev_bias_contrast_li, curr_peaks_li)

    yy = [falling_exp(i, popt_sig[0], popt_sig[1]) for i in x]

    axs_contrast.plot(x, y, c = "#6100B0", label = "Linearer Fit")
    axs_contrast.errorbar(rev_bias_contrast_li, contrast_li, xerr = u_rev_bias_contrast, yerr = u_contrast_li, label = "Messwerte",  **kwargs_wo_fmt)

    axs_sig.plot(x, yy, c = "#6100B0", label = "Exponetieller Fit")
    axs_sig.errorbar(rev_bias_contrast_li, curr_peaks_li, xerr = u_rev_bias_contrast, yerr = u_current, label = "Messwerte",  **kwargs)

    x = np.linspace(min(rev_bias_energy_li), max(rev_bias_energy_li), 10000)

    p = np.polyfit(rev_bias_energy_li, energy_li, 1)
    print(f"Lin Fit results (e peak): {p}")

    y = [p[1] + p[0] * i for i in x]

    axs_diff.errorbar(rev_bias_energy_li, energy_li, xerr = u_rev_bias_energy, yerr = u_energy_li, **kwargs_wo_fmt)
    axs_diff.plot(x, y, c = "#6100B0", label = "Linearer Fit")

    popt, pcov = curve_fit(falling_exp, contrast_li, curr_peaks_li)
    print(f"Exp Fit results (sig con): {popt}")

    x = np.linspace(min(contrast_li), max(contrast_li), 10000)
    y = [falling_exp(i, popt[0], popt[1]) for i in x]

    axs_sig_con.plot(x, y, c = "#6100B0", label = "Exponetieller Fit")
    axs_sig_con.errorbar(contrast_li, curr_peaks_li, xerr = u_contrast_li, yerr = u_current, label = "Messwerte", **kwargs_wo_fmt)

    if min(rev_bias_energy_li) == 0: u_rev_min = np.nan
    else: u_rev_min = round_up(100 * min(u_rev_bias_energy) / min(rev_bias_energy_li), 4)
    if max(rev_bias_energy_li) == 0: u_rev_max = np.nan
    else: u_rev_max = round_up(100 * max(u_rev_bias_energy) / max(rev_bias_energy_li), 4)

    print(rf"\(U_\text{{G}}\)& Gegenspannung & \(({round(min(rev_bias_energy_li), 4):n}\cdots{round(max(rev_bias_energy_li), 4):n})~\text{{V}}\)& GFG: Gl.~\ref{{eq:u_}} & \(({round_up(min(u_rev_bias_energy), 4):n}\cdots{round_up(max(u_rev_bias_energy), 4):n})~\text{{V}}\) & \(({u_rev_min:n}\cdots{u_rev_max:n})~\%\) \\")
    print(rf"\(E\)& Übergangsenergie & \({round(e_mean, 4):n}~\text{{eV}}\)& Typ A: \(n={len(energy_li)}\) & \({round_up(u_e_mean, 4):n}~\text{{eV}}\) & \({round_up(100 * u_e_mean / e_mean, 4):n}~\%\) \\")
    
    # edit style for plots
    axs.legend(ncol = 3, fontsize = 6)
    axs.grid()
    axs.set_xlabel(r'Kinetische Energie $E$ [eV]')
    axs.set_ylabel(r'Spannung $U$ [mV]')
    axs.set_title(rf'Alle Messungen')
    axs.ticklabel_format(style='sci', axis='y', scilimits=(0,0)) # credit below
    if test_phase == False: # save figure
        fig.savefig(fname = rf"Messung_alle_v1.pdf", format = "pdf")

    axs_peaks.grid()
    axs_peaks.legend()
    axs_peaks.set_xlabel(r'Peak')
    axs_peaks.set_ylabel(r'Übergangsenergie $E$ [eV]')
    axs_peaks.set_title(rf'Übergangsenergie für unterschiedliche Peaks')
    axs_peaks.xaxis.set_ticks(range(len(diffs_li)))
    if test_phase == False: # save figure
        fig_peaks.savefig(fname = rf"Messung_peak_E_v1.pdf", format = "pdf")

    axs_contrast.grid()
    axs_contrast.legend()
    axs_contrast.set_xlabel(r'Gegenspannung $U_G$ [V]')
    axs_contrast.set_ylabel(r'Kontrast $K$ []')
    axs_contrast.set_title(rf'Kontrast gegen Gegenspannung')
    if test_phase == False: # save figure
        fig_contrast.savefig(fname = rf"Messung_contrast_v1.pdf", format = "pdf")

    axs_sig.grid()
    axs_sig.legend()
    axs_sig.set_xlabel(r'Gegenspannung $U_G$ [V]')
    axs_sig.set_ylabel(r'Signalstärke $U_S$ [mV]')
    axs_sig.set_title(rf'Kontrast gegen Gegenspannung')
    axs_sig.ticklabel_format(style='sci', axis='y', scilimits=(0,0)) # credit below
    if test_phase == False: # save figure
        fig_sig.savefig(fname = rf"Messung_sig_v1.pdf", format = "pdf")

    # Source - https://stackoverflow.com/a/10129461
    # Posted by zgana, modified by community. See post 'Timeline' for change history
    # Retrieved 2026-02-17, License - CC BY-SA 4.0
    
    axs_sig_con.grid()
    axs_sig_con.legend()
    axs_sig_con.set_xlabel(r'Kontrast $K$ []')
    axs_sig_con.set_ylabel(r'Signalstärke $U_S$ [mV]')
    axs_sig_con.set_title(rf'Kontrast gegen Signalstärke')
    axs_sig_con.ticklabel_format(style='sci', axis='y', scilimits=(0,0)) # credit below
    axs_sig_con.set_yscale("log")
    if test_phase == False: # save figure
        fig_sig_con.savefig(fname = rf"Messung_signal_strength_contrast_v1.pdf", format = "pdf")

    axs_diff.grid()
    axs_diff.set_xlabel(r'Gegenspannung $U_G$ [V]')
    axs_diff.set_ylabel(r'Kinetische Energie $E$ [eV]')
    axs_diff.set_title(rf'Energie gegen Gegenspannung')
    if test_phase == False: # save figure
        fig_diff.savefig(fname = rf"Messung_energy_v1.pdf", format = "pdf")
        
    ax_3d.view_init(elev = 52, azim = 165, roll = -103)
    ax_3d.autoscale_view(tight = True)
    ax_3d.set_xlabel(r'Kinetische Energie $E$ [eV]')
    ax_3d.set_ylabel(r'Spannung $U$ [mV]')
    ax_3d.set_zlabel(r'Gegenspannung $U_G$ [V]')
    ax_3d.set_title(r'Kinetische Energie und Spannung gegen Gegenspannung')
    
    # Source - https://stackoverflow.com/a
    # Posted by Chris
    # Retrieved 2026-01-28, License - CC BY-SA 3.0

    # import matplotlib.pyplot as plt
    # ...
    # plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

    ax_3d.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    if test_phase == False: # save figure
        fig_3d.savefig(fname = rf"Messung_3d_v1.pdf", format = "pdf")
    plt.show()
    

if __name__ == "__main__":
    main()