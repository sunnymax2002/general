# SymPy for symbolic operations
from sympy import *

# For plotting
import matplotlib.pyplot as plt

# Numpy for efficient matrices
import numpy as np

# Enable pretty LATEX printing to show equations
init_printing(use_unicode=True)

# Create symbols and expressions
x, y, z = symbols('x y z')
expr = 2*x + y

# Pretty print, instead of normal print
pprint(expr)

# Differentiate an expression
d = diff(sin(x)*exp(x), x)
pprint(d)

# Integrate
q = integrate(d*cos(x), x)

pprint(q)

# Transfer function using control
print("Transfer Functions using control library")
import control

# System parameters
K = 3   # Gain
T = 4   # Time constant

num = np.array([K])
den = np.array([T, 1])

H = control.tf(num, den)
print('H(s) = ', H)

# Bode plot using control system lib
control.bode(H, dB=True)
plt.show()
exit()

t, y = control.step_response(H)

# Plot the step response
plt.plot(t, y)
plt.title("Step Response")
plt.grid()
plt.show()

# Transfer function using scipy.signal
print("Transfer Functions using scipy.signal library")
import scipy.signal as signal

# Frequencies of interest
w_start = 0.01
w_end = 10
w_step = 0.01
w = np.linspace(w_start, w_end, 1 + int( (w_end - w_start) / w_step))

G = signal.TransferFunction(num, den)
print('G(s) = ', G)

# Bode Plot
w, mag, phase = signal.bode(G, w)

plt.figure()
plt.subplot(2, 1, 1)
plt.semilogx(w, mag)
plt.title("Bode Plot")
plt.grid(b=None, which='major', axis='both')
plt.grid(b=None, which='minor', axis='both')
plt.ylabel("Magnitude (dB)")

plt.subplot(2, 1, 2)
plt.semilogx(w, phase)
plt.grid(b=None, which='major', axis='both')
plt.grid(b=None, which='minor', axis='both')
plt.ylabel("Phase (degree)")
plt.xlabel("Frequency (rad/sec)")

plt.show()

# TODO: State Space modelling: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.StateSpace.html


