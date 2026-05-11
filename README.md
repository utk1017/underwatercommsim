#  Underwater Acoustic Communication System

> A Python simulation of a digital underwater communication system implementing QPSK modulation over an AWGN channel.


---

## Overview

Underwater communication is fundamentally different from terrestrial wireless communication. Radio waves attenuate extremely rapidly in seawater due to its high electrical conductivity, making RF-based systems impractical beyond a few centimetres. **Acoustic waves** are therefore the primary medium for underwater data transmission ,used in ocean monitoring, submarine navigation, autonomous underwater vehicles (AUVs), and offshore infrastructure.

This project simulates a simplified underwater acoustic communication link using core digital communications principles:

- **QPSK modulation** for efficient 2 bits/symbol transmission
- **AWGN channel model** as a first-order approximation of underwater noise
- **BER vs SNR analysis** validated against the theoretical Q-function bound
- **Shannon capacity** to establish the information-theoretic upper limit

The simulation is written entirely in Python using NumPy, Matplotlib, and SciPy.

---

## Background


| Property | Radio (RF) | Acoustic |
|---|---|---|
| Attenuation in water | Extremely high (~170 dB/km at 1 MHz) | Low (0.1–10 dB/km) |
| Usable range | A few centimetres | Up to tens of kilometres |
| Bandwidth available | Very limited | 1 Hz – ~100 kHz |
| Speed of propagation | 3×10⁸ m/s | ~1500 m/s |

Acoustic communication is the only practical long-range solution underwater, which is why this project focuses on the acoustic channel.

### Key challenges of the underwater acoustic channel

- **Limited bandwidth** : typically only a few kHz usable
- **High ambient noise** : from shipping, marine life, wind-driven surface waves
- **Multipath propagation** : reflections from the surface and seabed cause ISI
- **Doppler spreading** : caused by transmitter/receiver motion and water currents

This simulation models the channel as AWGN , the standard first-order approximation used to establish baseline performance before adding multipath and fading effects.

---

## System Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Random    │     │     QPSK     │     │     AWGN     │
│  Bit Source │────▶│  Modulator   │────▶│   Channel    │
│  (100,000)  │     │ 2 bits/sym   │     │  +Gaussian   │
└─────────────┘     └──────────────┘     │    noise     │
                                         └──────┬───────┘
                                                │
                    ┌──────────────┐     ┌──────▼───────┐
                    │     BER      │     │     QPSK     │
                    │  Calculator  │◀────│  Demodulator │
                    │ Tx vs Rx bits│     │  Coherent    │
                    └──────┬───────┘     └──────────────┘
                           │
                    ┌──────▼───────┐
                    │   Plots:     │
                    │ BER vs SNR   │
                    │ + Shannon C  │
                    └──────────────┘
```

### Block descriptions

**QPSK Modulator**  
Takes pairs of input bits and maps them to one of four complex constellation points using Gray coding. Gray coding ensures adjacent symbols differ by only one bit, minimising the BER at moderate-to-high SNR. Each symbol carries 2 bits and has unit average power.

```
Bit pair → Phase
  00     →  +45°   (+1+j) / √2
  01     → +135°   (-1+j) / √2
  11     → +225°   (-1-j) / √2
  10     → +315°   (+1-j) / √2
```

**AWGN Channel**  
Models the underwater ambient noise as complex additive Gaussian noise. For each SNR point, the noise variance is set as:

```
σ² = 1 / (bits_per_symbol × 10^(SNR_dB / 10))
```

Both in-phase (I) and quadrature (Q) noise components are generated independently from N(0, σ²/2).

**QPSK Demodulator (Coherent Detection)**  
Performs minimum Euclidean distance detection. Since QPSK points are separated by the I and Q axes, coherent detection reduces to two independent binary decisions — the sign of the received I component and the sign of the received Q component.

**BER Calculator**  
Compares the transmitted bit stream against the received bit stream and computes the fraction of incorrectly decoded bits.

---

## Theory

### QPSK BER over AWGN

The theoretical bit error rate for QPSK with coherent detection over an AWGN channel is:

```
Pb = Q( √(2·Eb/N0) ) = (1/2) · erfc( √(Eb/N0) )
```

where:
- `Eb` = energy per bit
- `N0` = one-sided noise power spectral density
- `Q(·)` = Gaussian Q-function
- `erfc(·)` = complementary error function

This serves as the theoretical lower bound that the simulation is validated against.

### Shannon–Hartley Channel Capacity

The maximum error-free data rate achievable over a bandlimited AWGN channel is:

```
C = B · log₂(1 + SNR)   [bits/s]
```

where:
- `C` = channel capacity in bits per second
- `B` = signal bandwidth in Hz
- `SNR` = signal-to-noise ratio (linear scale)

For this simulation, `B = 4000 Hz` (a typical usable underwater acoustic band). At `SNR = 10 dB`, this gives `C ≈ 13.84 kbps` — the theoretical ceiling no system can exceed at that SNR.

### Noise Model

The complex baseband noise added at each SNR point follows:

```
n = nI + j·nQ,    nI, nQ ~ N(0, σ²/2)

where σ² = N0/2 = 1 / (2 × bits_per_symbol × 10^(SNR/10))
```

---

## Results

![BER vs SNR and Shannon Capacity](results/ber_plot.png)

### BER vs SNR

| SNR (dB) | BER Simulated | BER Theoretical |
|:---:|:---:|:---:|
| 0 | ~0.0797 | 0.0787 |
| 2 | ~0.0378 | 0.0375 |
| 4 | ~0.0129 | 0.0125 |
| 6 | ~0.0022 | 0.0024 |
| 8 | ~0.0002 | 0.0002 |
| 10 | ~0.00001 | ~0.000004 |

Key observations:
- Simulated BER matches the theoretical curve closely across all SNR values
- BER drops below `10⁻³` at approximately **8–9 dB SNR**
- At 10 dB and above, the channel is essentially error-free for QPSK

### Shannon Capacity

| SNR (dB) | Capacity (kbps) |
|:---:|:---:|
| 0 | 4.00 |
| 5 | 8.00 |
| 10 | 13.84 |
| 15 | 20.00 |
| 20 | 26.58 |

The system operates comfortably below the Shannon limit, confirming that reliable communication at the chosen operating point is theoretically achievable.

---

## Project Structure

```
underwater-comm-simulation/
│
├── simulation.py          # main simulation — run this
├── requirements.txt       # pip dependencies (3 packages)
├── README.md              # this file
│
└── results/
    └── ber_plot.png       # output plot (auto-saved on run)
```

---

## How to Run

### Prerequisites

- Python 3.7 or above
- pip

### Installation

```bash
# 1. clone the repository
git clone https://github.com/your-username/underwater-comm-simulation.git
cd underwater-comm-simulation

# 2. install dependencies
pip install -r requirements.txt
```

### Run

```bash
python simulation.py
```

The script will:
1. Print a BER comparison table to the terminal
2. Display two plots (BER vs SNR and Shannon Capacity vs SNR)
3. Save the plot automatically to `results/ber_plot.png`

---

## Sample Output

```
====================================================
  Underwater Acoustic Communication Simulation
====================================================
  Modulation  : QPSK  (2 bits / symbol)
  Bits        : 100,000
  SNR range   : 0 – 20 dB
  Bandwidth   : 4000 Hz
====================================================

  SNR (dB)    BER (simulated)    BER (theory)
----------------------------------------------
         0            0.07969         0.07865
         2            0.03778         0.03751
         4            0.01287         0.01250
         6            0.00219         0.00239
         8            0.00019         0.00019
        10            0.00001         0.00000
        12            0.00000         0.00000

====================================================
  SIMULATION SUMMARY
====================================================
  Modulation      : QPSK (M=4, 2 bits/symbol)
  Total bits      : 100,000
  Channel         : AWGN
  Bandwidth       : 4000 Hz
  BER @ 10 dB     : 0.00001 (sim) | 0.00000 (theory)
  Capacity @ 10dB : 13.84 kbps
  Plot saved      : results/ber_plot.png
====================================================
```

---

## Concepts Covered

This project directly applies the following digital communications topics:

| Topic | Where applied |
|---|---|
| Gaussian noise and AWGN channel model | Channel simulation block |
| Nyquist sampling theorem and PCM | Signal representation |
| QPSK modulation and signal-space representation | Modulator block |
| Gray coding | Bit-to-symbol mapping |
| Coherent detection and minimum distance decision | Demodulator block |
| BER analysis and Q-function | Performance evaluation |
| Shannon–Hartley channel capacity theorem | Capacity plot |

---

## References

1. J. G. Proakis and M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill, 2008.
2. S. Haykin, *Communication Systems*, 4th ed., Wiley, 2001.
3. C. E. Shannon, "A Mathematical Theory of Communication," *Bell System Technical Journal*, vol. 27, 1948.
4. M. Stojanovic, "On the relationship between capacity and distance in an underwater acoustic communication channel," *ACM SIGMOBILE*, vol. 11, 2007.

---

## Author

**[Your Name]**  
B.Tech Electronics & Communication Engineering  
[Institution Name] — [Year]  
[LinkedIn](https://linkedin.com/in/your-profile) · [GitHub](https://github.com/your-username)
