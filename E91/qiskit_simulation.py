# %% - Qiskit imports
from numpy import pi
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit.quantum_info import Statevector
from qiskit.visualization import array_to_latex, plot_distribution
from IPython.display import display
from qiskit_aer import AerSimulator
from enum import Enum

class Basis(Enum):
    X = 1
    W = 2
    Z = 3
    V = 4
    # X, Z, W - Alice
    # V, Z, W - Bob
    
class BellState(Enum):
    PHI_PLUS = 0
    PHI_MINUS = 1
    PSI_PLUS = 3
    PSI_MINUS = 4

# %% - Define Encoding circuit

def prepare_entangled_qubits(state: BellState) -> QuantumCircuit:
    qreg_q = QuantumRegister(2, 'q')
    creg_c = ClassicalRegister(4, 'c')
    circuit = QuantumCircuit(qreg_q, creg_c)

    if state == BellState.PHI_PLUS:
        pass
    elif state == BellState.PHI_MINUS:
        circuit.x(qreg_q[0])
    elif state == BellState.PSI_PLUS:
        circuit.x(qreg_q[1])
    elif state == BellState.PSI_MINUS:
        circuit.x(qreg_q[0])
        circuit.x(qreg_q[1])
    
    circuit.barrier(qreg_q)
    circuit.h(qreg_q[0])
    circuit.cx(qreg_q[0], qreg_q[1])
    
    return circuit
    # print_statevector(circuit)
    
def apply_measurement_gate(operator: Basis, qreg_bit_no: int, creg_bit_no: int, circuit: QuantumCircuit):
    qreg_q = circuit.qregs[0]
    creg_c = circuit.cregs[0]
    circuit.barrier(qreg_q, label=operator.name)

    if operator == Basis.X: 
        # X basis
        circuit.h(qreg_q[qreg_bit_no])

    elif operator == Basis.W: 
        # W basis
        circuit.s(qreg_q[qreg_bit_no])
        circuit.h(qreg_q[qreg_bit_no])
        circuit.t(qreg_q[qreg_bit_no])
        circuit.h(qreg_q[qreg_bit_no])
        
    elif operator == Basis.Z:
        # Z basis
        pass
    elif operator == Basis.V:
        # V basis
        circuit.s(qreg_q[qreg_bit_no])
        circuit.h(qreg_q[qreg_bit_no])
        circuit.tdg(qreg_q[qreg_bit_no])
        circuit.h(qreg_q[qreg_bit_no])

    circuit.measure(qreg_q[qreg_bit_no], creg_c[creg_bit_no])
    circuit.barrier(qreg_q, label=operator.name)

def execute_measurements(circuit: QuantumCircuit, shots: int = 1000, display = True) -> tuple[dict, dict]:
    simulator = AerSimulator()
    circ = transpile(circuit, simulator)

    result = simulator.run(circ, shots=shots).result()
    counts: dict[str, int] = result.get_counts(circ)
    
    probabilities = {}
    for k, v in counts.items():
        probabilities[k] = round(v*100 / shots, 1)
    
    if display:
        print(probabilities)
    
    return counts, probabilities

# %% - Test circuits

# qreg_q = QuantumRegister(2, 'q')
# creg_c = ClassicalRegister(2, 'c')
# circuit = QuantumCircuit(qreg_q, creg_c)

# circuit = prepare_entangled_qubits(BellState.PHI_PLUS)
# psi = Statevector(circuit)

# apply_measurement_gate(Basis.Z, 0, circuit)
# apply_measurement_gate(Basis.Z, 1, circuit)
# execute_measurements(circuit, shots=100, display=True)

# circuit.draw('mpl')