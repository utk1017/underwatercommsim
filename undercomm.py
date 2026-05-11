import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc

np.random.seed(42)
NUM_BITS  = 100_000          
SNR_DB    = np.arange(0, 21, 2)  
BANDWIDTH = 4_000            

print("=" * 52)
print("  Underwater Acoustic Communication Simulation")
print("=" * 52)
print(f"  Modulation  : QPSK  (2 bits / symbol)")
print(f"  Bits        : {NUM_BITS:,}")
print(f"  SNR range   : {SNR_DB[0]} – {SNR_DB[-1]} dB")
print(f"  Bandwidth   : {BANDWIDTH} Hz")
print("=" * 52)


def qpsk_modulate(bits):
   
    bits = bits[:len(bits) - len(bits) % 2]  
    pairs = bits.reshape(-1, 2)

    I =  1 - 2 * pairs[:, 0].astype(float)  
    Q =  1 - 2 * pairs[:, 1].astype(float)

    symbols = (I + 1j * Q) / np.sqrt(2)      
    return symbols

def awgn_channel(symbols, snr_db, bits_per_symbol=2):
   
    snr_linear = 10 ** (snr_db / 10)
    noise_var   = 1 / (bits_per_symbol * snr_linear)
    noise = np.sqrt(noise_var / 2) * (np.random.randn(*symbols.shape)+ 1j * np.random.randn(*symbols.shape))
    return symbols + noise


def qpsk_demodulate(received):
    
    I_bits = (np.real(received) < 0).astype(int)   
    Q_bits = (np.imag(received) < 0).astype(int)

    bits_rx = np.empty(len(received) * 2, dtype=int)
    bits_rx[0::2] = I_bits
    bits_rx[1::2] = Q_bits
    return bits_rx

def ber_theory_qpsk(snr_db):
    EbN0 = 10 ** (snr_db / 10)
    return 0.5 * erfc(np.sqrt(EbN0))


def shannon_capacity(snr_db, bandwidth):
    snr_linear = 10 ** (snr_db / 10)
    return bandwidth * np.log2(1 + snr_linear) / 1000   # kbps


ber_simulated = np.zeros(len(SNR_DB))
ber_theoretical = ber_theory_qpsk(SNR_DB)
capacity_kbps   = shannon_capacity(SNR_DB, BANDWIDTH)

print(f"\n{'SNR (dB)':>10}  {'BER (simulated)':>17}  {'BER (theory)':>14}")
print("-" * 46)

tx_bits = np.random.randint(0, 2, NUM_BITS)
tx_syms = qpsk_modulate(tx_bits)

for i, snr in enumerate(SNR_DB):
    # pass through AWGN channel
    rx_syms = awgn_channel(tx_syms, snr)

    # demodulate
    rx_bits = qpsk_demodulate(rx_syms)

    # count bit errors (compare only the bits we have symbols for)
    n = min(len(tx_bits), len(rx_bits))
    errors = np.sum(tx_bits[:n] != rx_bits[:n])
    ber_simulated[i] = errors / n

    print(f"{snr:>10.0f}  {ber_simulated[i]:>17.5f}  {ber_theoretical[i]:>14.5f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Underwater Acoustic Communication System — Simulation Results",fontsize=13, fontweight="bold", y=1.01)

ax1.semilogy(SNR_DB, ber_theoretical, "k--",  linewidth=2, label="Theoretical  $P_b = Q(\\sqrt{2E_b/N_0})$")
ax1.semilogy(SNR_DB, ber_simulated,  "b-o",  linewidth=2, markersize=7,label="Simulated (QPSK + AWGN)")
ax1.axhline(1e-3, color="green", linestyle=":", linewidth=1.4,label="Target BER = $10^{-3}$")

ax1.set_xlabel("SNR — $E_b/N_0$ (dB)", fontsize=12)
ax1.set_ylabel("Bit Error Rate (BER)", fontsize=12)
ax1.set_title("BER vs SNR\n(QPSK over AWGN channel)", fontsize=11)
ax1.set_xlim([0, 20])
ax1.set_ylim([1e-6, 1])
ax1.legend(fontsize=10)
ax1.grid(True, which="both", linestyle="--", alpha=0.6)

cross_snr = np.interp(1e-3, ber_theoretical[::-1], SNR_DB[::-1])
ax1.annotate(f"BER = $10^{{-3}}$\n@ {cross_snr:.1f} dB",
             xy=(cross_snr, 1e-3),
             xytext=(cross_snr + 2, 5e-3),
             arrowprops=dict(arrowstyle="->", color="green"),
             fontsize=9, color="green")

ax2.plot(SNR_DB, capacity_kbps, "r-s", linewidth=2, markersize=7, label=f"$C = B \\cdot \\log_2(1 + SNR)$,  B = {BANDWIDTH} Hz")
ax2.axhline(10, color="blue", linestyle=":", linewidth=1.4, label="Example system rate = 10 kbps")
ax2.fill_between(SNR_DB, capacity_kbps, alpha=0.12, color="red",  label="Achievable region")

ax2.set_xlabel("SNR — $E_b/N_0$ (dB)", fontsize=12)
ax2.set_ylabel("Capacity (kbps)", fontsize=12)
ax2.set_title("Shannon Channel Capacity vs SNR\n$C = B\\,\\log_2(1+SNR)$", fontsize=11)
ax2.set_xlim([0, 20])
ax2.legend(fontsize=10)
ax2.grid(True, linestyle="--", alpha=0.6)

plt.tight_layout()
plt.savefig("underwater_comm_results.png", dpi=150, bbox_inches="tight")
plt.show()

print("\n" + "=" * 52)
print("  SIMULATION SUMMARY")
print("=" * 52)
print(f"  Modulation      : QPSK (M=4, 2 bits/symbol)")
print(f"  Total bits      : {NUM_BITS:,}")
print(f"  Channel         : AWGN")
print(f"  Bandwidth       : {BANDWIDTH} Hz")
idx10 = np.where(SNR_DB == 10)[0][0]
print(f"  BER @ 10 dB     : {ber_simulated[idx10]:.5f} (sim) "
      f"| {ber_theoretical[idx10]:.5f} (theory)")
print(f"  Capacity @ 10dB : {capacity_kbps[idx10]:.2f} kbps")
print(f"  Plot saved      : underwater_comm_results.png")
print("=" * 52)