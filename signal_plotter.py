import matplotlib.pyplot as plt
import csv

def plot_signal(signal, sample_rate=None, title="Signal", xlabel=None, ylabel="Amplitude"):
    """
    Plot the signal using matplotlib.
    :param signal: List or array of signal values.
    :param sample_rate: (Optional) Sample rate in Hz. If provided, x-axis will be time in seconds.
    :param title: Plot title.
    :param xlabel: X-axis label. If not provided, uses 'Sample' or 'Time (s)'.
    :param ylabel: Y-axis label.
    """
    if sample_rate:
        x = [i / sample_rate for i in range(len(signal))]
        xlabel = xlabel or "Time (s)"
    else:
        x = list(range(len(signal)))
        xlabel = xlabel or "Sample"
    plt.figure(figsize=(10, 4))
    plt.plot(x, signal)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def save_signal_to_csv(path, signal):
    """
    Save the signal to a CSV file at the given path.
    :param path: File path to save the CSV.
    :param signal: List or array of signal values.
    """
    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for value in signal:
            writer.writerow([value])
