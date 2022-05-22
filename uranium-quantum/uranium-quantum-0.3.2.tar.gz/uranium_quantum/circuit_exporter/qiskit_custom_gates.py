import math
import numpy as np
from qiskit.quantum_info.operators import Operator
from qiskit.extensions import UnitaryGate

def gate_rotation_to_y_basis():
  return UnitaryGate(1/math.sqrt(2) * Operator([
    [1, 1],
    [1j, -1j],
    ]))

def gate_undo_rotation_to_y_basis():
  return UnitaryGate(1/math.sqrt(2) * Operator([
    [1, -1j],
    [1, 1j],
    ]))
def pauli_x_root(root, label=None):
  return UnitaryGate(np.exp(1j * np.pi/(2*root)) * Operator([
    [np.cos(np.pi/(2*root)), -1j * np.sin(np.pi/(2*root))],
    [-1j * np.sin(np.pi/(2*root)), np.cos(np.pi/(2*root))],
    ]), label=label)

def pauli_y_root(root, label=None):
  return UnitaryGate(np.exp(1j * np.pi/(2*root)) * Operator([
    [np.cos(np.pi/(2*root)), -np.sin(np.pi/(2*root))],
    [np.sin(np.pi/(2*root)), np.cos(np.pi/(2*root))],
    ]), label=label)

def pauli_z_root(root, label=None):
  return UnitaryGate(np.exp(1j * np.pi/(2*root)) * Operator([
    [1, 0],
    [0, np.exp(1j * np.pi/root)],
    ]), label=label)

def pauli_x_root_dagger(root, label=None):
  return UnitaryGate(np.exp(1j * np.pi/(2*root)) * Operator([
    [np.cos(np.pi/(2*root)), 1j * np.sin(np.pi/(2*root))],
    [1j * np.sin(np.pi/(2*root)), np.cos(np.pi/(2*root))],
    ]), label=label)

def pauli_y_root_dagger(root, label=None):
  return UnitaryGate(np.exp(1j * np.pi/(2*root)) * Operator([
    [np.cos(np.pi/(2*root)), - np.sin(np.pi/(2*root))],
    [np.sin(np.pi/(2*root)), np.cos(np.pi/(2*root))],
    ]), label=label)

def pauli_z_root_dagger(root, label=None):
  return UnitaryGate(np.exp(1j * np.pi/(2*root)) * Operator([
    [1, 0],
    [0, np.exp(-1j * np.pi/root)],
    ]), label=label)

def h(label=None):
  return UnitaryGate(1/math.sqrt(2) * Operator([
    [1, -1],
    [1, 1],
    ]), label=label)

def h_dagger(label=None):
  return UnitaryGate(1/math.sqrt(2) * Operator([
    [1, 1],
    [-1, 1],
    ]), label=label)

def hadamard_xy(label=None):
  return UnitaryGate(1/math.sqrt(2) * Operator([
    [0, 1 + 1j],
    [1 - 1j, 0],
    ]), label=label)

def hadamard_yz(label=None):
  return UnitaryGate(1/math.sqrt(2) * Operator([
    [1, -1j],
    [1j, -1],
    ]), label=label)

def c(label=None):
  return UnitaryGate(1/2 * Operator([
    [+1 - 1j, -1 - 1j],
    [+1 - 1j, +1 + 1j],
    ]), label=label)

def c_dagger(label=None):
  return UnitaryGate(1/2 * Operator([
    [+1 + 1j, +1 + 1j],
    [-1 + 1j, +1 - 1j],
    ]), label=label)

def sqrt_swap(label=None):
  return UnitaryGate(Operator([
    [1, 0, 0, 0],
    [0, (1 + 1j)/2, (1 - 1j)/2, 0],
    [0, (1 - 1j)/2, (1 + 1j)/2, 0],
    [0, 0, 0, 1],
    ]), label=label)

def sqrt_swap_dagger(label=None):
  return UnitaryGate(Operator([
    [1, 0, 0, 0],
    [0, (1 - 1j)/2, (1 + 1j)/2, 0],
    [0, (1 + 1j)/2, (1 - 1j)/2, 0],
    [0, 0, 0, 1],
    ]), label=label)

def swap_theta(theta, label=None):
  return UnitaryGate(Operator([
    [1, 0, 0, 0],
    [0, 0, np.exp(1j * theta), 0],
    [0, np.exp(1j * theta), 0, 0],
    [0, 0, 0, 1],
    ]), label=label)

def fswap(label=None):
  return UnitaryGate(Operator([
    [1, 0, 0, 0],
    [0, 0, 1, 0],
    [0, 1, 0, 0],
    [0, 0, 0, -1],
    ]), label=label)

def swap_root(root, label=None):
  return UnitaryGate(np.exp(-1j * np.pi / (4 * root)) * Operator([
    [np.exp(1j * np.pi/(2*root)), 0, 0, 0],
    [0, np.cos(np.pi/(2*root)), 1j * np.sin(np.pi/(2*root)), 0],
    [0, 1j * np.sin(np.pi/(2*root)), np.cos(np.pi/(2*root)), 0],
    [0, 0, 0, np.exp(1j * np.pi / (2 * root))],
    ]), label=label)

def swap_root_dagger(root, label=None):
  return UnitaryGate(np.exp(1j * np.pi / (4 * root)) * Operator([
    [np.exp(-1j * np.pi/(2*root)), 0, 0, 0],
    [0, np.cos(np.pi/(2*root)), -1j * np.sin(np.pi/(2*root)), 0],
    [0, -1j * np.sin(np.pi/(2*root)), np.cos(np.pi/(2*root)), 0],
    [0, 0, 0, np.exp(-1j * np.pi / (2 * root))],
    ]), label=label)

def xy(theta, label=None):
  return UnitaryGate(Operator([
    [1, 0, 0, 0],
    [0, np.cos(theta), -1j * np.sin(theta), 0],
    [0, -1j * np.sin(theta), np.cos(theta), 0],
    [0, 0, 0, 1],
    ]), label=label)

def molmer_sorensen(label=None):
  return UnitaryGate(1/math.sqrt(2) * Operator([
    [1, 0, 0, 1j],
    [0, 1, 1j, 0],
    [0, 1j, 1, 0],
    [1j, 0, 0, 1],
    ]), label=label)

def molmer_sorensen_dagger(label=None):
  return UnitaryGate(1/math.sqrt(2) * Operator([
    [1, 0, 0, -1j],
    [0, 1, -1j, 0],
    [0, -1j, 1, 0],
    [-1j, 0, 0, 1],
    ]), label=label)

def berkeley(label=None):
  return UnitaryGate(Operator([
    [np.cos(np.pi/8), 0, 0, 1j * np.sin(np.pi/8)],
    [0, np.cos(3*np.pi/8), 1j * np.sin(3*np.pi/8), 0],
    [0, 1j * np.sin(3*np.pi/8), np.cos(3*np.pi/8), 0],
    [1j * np.sin(np.pi/8), 0, 0, np.cos(np.pi/8)],
    ]), label=label)

def berkeley_dagger(label=None):
  return UnitaryGate(Operator([
    [np.cos(np.pi/8), 0, 0, -1j * np.sin(np.pi/8)],
    [0, np.cos(3*np.pi/8), -1j * np.sin(3*np.pi/8), 0],
    [0, -1j * np.sin(3*np.pi/8), np.cos(3*np.pi/8), 0],
    [-1j * np.sin(np.pi/8), 0, 0, np.cos(np.pi/8)],
    ]), label=label)

def ecp(label=None):
  c = np.cos(np.pi/8)
  s = np.sin(np.pi/8)
  return UnitaryGate(1/2 * Operator([
    [2*c, 0, 0, -1j * 2 * s],
    [0, (1 + 1j) * (c - s), (1 - 1j) * (c + s), 0],
    [0, (1 - 1j) * (c + s), (1 + 1j) * (c - s), 0],
    [-1j * 2 * s, 0, 0, 2*c],
    ]), label=label)

def ecp_dagger(label=None):
  c = np.cos(np.pi/8)
  s = np.sin(np.pi/8)
  return UnitaryGate(1/2 * Operator([
    [2*c, 0, 0, 1j * 2 * s],
    [0, (1 - 1j) * (c - s), (1 + 1j) * (c + s), 0],
    [0, (1 + 1j) * (c + s), (1 - 1j) * (c - s), 0],
    [1j * 2 * s, 0, 0, 2*c],
    ]), label=label)

def w(label=None):
  return UnitaryGate(Operator([
    [1, 0, 0, 0],
    [0, 1/math.sqrt(2), 1/math.sqrt(2), 0],
    [0, 1/math.sqrt(2), -1/math.sqrt(2), 0],
    [0, 0, 0, 1],
    ]), label=label)

def givens(theta, label=None):
  return UnitaryGate(Operator([
    [1, 0, 0, 0],
    [0, np.cos(theta), -np.sin(theta), 0],
    [0, np.sin(theta), np.cos(theta), 0],
    [0, 0, 0, 1],
    ]), label=label)

def magic(label=None):
  return UnitaryGate(1/math.sqrt(2) * Operator([
    [1, 1j, 0, 0],
    [0, 0, 1j, 1],
    [0, 0, 1j, -1],
    [1, -1j, 0, 0],
    ]), label=label)

def magic_dagger(label=None):
  return UnitaryGate(1/math.sqrt(2) * Operator([
    [1, 0, 0, 1],
    [-1j, 0, 0, 1j],
    [0, -1j, -1j, 0],
    [0, 1, -1, 0],
    ]), label=label)

def a(theta, phi, label=None):
  return UnitaryGate(Operator([
    [1, 0, 0, 0],
    [0, np.cos(theta), np.sin(theta) * np.exp(1j * phi), 0],
    [0, np.sin(theta) * np.exp(-1j * phi), -np.cos(theta), 0],
    [0, 0, 0, 1],
    ]), label=label)