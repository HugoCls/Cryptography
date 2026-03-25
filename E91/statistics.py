from e91_simulation import *
import matplotlib.pyplot as plt
import numpy as np

def save_results():
    p = E91(N=500)

    p.prepare_entangled_qubits()
    p.alice_generate_measurement_choices()
    p.bob_generate_measurement_choices()

    p.apply_measures()

    p.publicly_choose_common_bases()
    p.alice_create_key()
    p.bob_create_key()

    data_str = f"{''.join(['1' if b==1 else '0' for b in p.alice_key])}::{''.join(['1' if b==1 else '0' for b in p.bob_key])}::{len(p.alice_key)}::{p.check_random_bits_of_key(percent_to_check=1)}::{p.compute_chsh_correlation()}\n"

    with open('results.txt','a',encoding='utf-8') as f:
        f.write(data_str)


def analyse_and_plot(file):
    lengths = []
    chsh_correlations = []

    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            # Split the line into its components
            parts = line.strip().split('::')
            if len(parts) < 5:
                continue  # Skip malformed lines
            key_length = int(parts[2])
            chsh_correlation = float(parts[4])

            lengths.append(key_length)
            chsh_correlations.append(chsh_correlation)

    # Calculate statistics for key lengths
    mean_length = np.mean(lengths)
    std_length = np.std(lengths)
    median_length = np.median(lengths)
    
    # Calculate statistics for CHSH correlations
    mean_chsh = np.mean(chsh_correlations)
    std_chsh = np.std(chsh_correlations)
    median_chsh = np.median(chsh_correlations)

    # Plot the graphs
    fig, ax = plt.subplots(2, 1, figsize=(10, 10))

    # Graph for key length
    ax[0].plot(lengths, label='Key Length')
    ax[0].axhline(mean_length, color='r', linestyle='--', label=f'Mean: {mean_length:.2f}')
    ax[0].axhline(median_length, color='g', linestyle='--', label=f'Median: {median_length:.2f}')
    ax[0].fill_between(range(len(lengths)), mean_length - std_length, mean_length + std_length, color='r', alpha=0.2, label=f'Standard Deviation: {std_length:.2f}')
    ax[0].set_title('Key Length')
    ax[0].set_xlabel('Sample')
    ax[0].set_ylabel('Length')
    ax[0].legend()

    # Graph for CHSH correlation
    ax[1].plot(chsh_correlations, label='CHSH Correlation')
    ax[1].axhline(mean_chsh, color='r', linestyle='--', label=f'Mean: {mean_chsh:.2f}')
    ax[1].axhline(median_chsh, color='g', linestyle='--', label=f'Median: {median_chsh:.2f}')
    ax[1].fill_between(range(len(chsh_correlations)), mean_chsh - std_chsh, mean_chsh + std_chsh, color='r', alpha=0.2, label=f'Standard Deviation: {std_chsh:.2f}')
    ax[1].set_title('CHSH Correlation')
    ax[1].set_xlabel('Sample')
    ax[1].set_ylabel('Correlation')
    ax[1].legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    """
    for i in range(500):
        save_results()
    """
    analyse_and_plot('results.txt')