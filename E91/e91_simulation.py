# %% - E91 Protocol

import random
import re
from qiskit_simulation import *

class SingletPreparationDevice:
    def __init__(self):
        pass

    def generate_bell_state_qbits(self, N):
        return [prepare_entangled_qubits(state=BellState.PHI_PLUS) for _ in range(N)]

class E91:
    def __init__(self, N=500):
        self.N = N
        
        self.abPatterns = [
            re.compile('..00$'), # search for the '..00' output (Alice obtained -1 and Bob obtained -1)
            re.compile('..01$'), # search for the '..01' output
            re.compile('..10$'), # search for the '..10' output (Alice obtained -1 and Bob obtained 1)
            re.compile('..11$')  # search for the '..11' output
        ]
        
        self.entangled_qubit_states: list[QuantumCircuit] = []

        self.alice_bases = [Basis.X, Basis.Z, Basis.W]
        self.alice_measurement_choices: list[Basis] = []
        self.alice_measurement_results: list[int] = []
        self.alice_key: list[int] = []
        
        self.bob_bases: list[Basis] = [Basis.V, Basis.Z, Basis.W]
        self.bob_measurement_choices: list[Basis] = []
        self.bob_measurement_results: list[int] = []
        self.bob_key: list[int] = []
        
        self.measurement_results: list[str] = []        
        self.common_bases_indicies: list = []

    def prepare_entangled_qubits(self):
        # Generate N pairs of maximally entangled qubits (bell states)
        # (normaly done from a singlet state preparation device)
        self.entangled_qubit_states = SingletPreparationDevice().generate_bell_state_qbits(self.N)

    def alice_generate_measurement_choices(self):
        self.alice_measurement_choices = [random.choice(self.alice_bases) for _ in range(self.N)]

    def bob_generate_measurement_choices(self):
        self.bob_measurement_choices = [random.choice(self.bob_bases) for _ in range(self.N)]

    def eve_generate_measurement_choices(self):
        self.eve_measurement_choices = [random.choice(self.bob_bases) for _ in range(self.N)]

    def apply_measures(self, eve_on_the_field=False):
        for i, bell_state in enumerate(self.entangled_qubit_states):
            apply_measurement_gate(self.alice_measurement_choices[i], 0, 0, bell_state)
            apply_measurement_gate(self.bob_measurement_choices[i], 1, 1, bell_state)
            # EVE 
            if eve_on_the_field:
                apply_measurement_gate(self.eve_measurement_choices[i], 0, 2, bell_state)
                apply_measurement_gate(self.eve_measurement_choices[i], 1, 3, bell_state)

            m, _ = execute_measurements(bell_state, shots=1, display=False)
            res = list(m.keys())[0]
            self.measurement_results.append(res)
            
            if self.abPatterns[0].search(res): # check if the key is '..00' (if the measurement results are -1,-1)
                self.alice_measurement_results.append(-1)
                self.bob_measurement_results.append(-1)
            if self.abPatterns[1].search(res):
                self.alice_measurement_results.append(1)
                self.bob_measurement_results.append(-1)
            if self.abPatterns[2].search(res): # check if the key is '..10' (if the measurement results are -1,1)
                self.alice_measurement_results.append(-1)
                self.bob_measurement_results.append(1)
            if self.abPatterns[3].search(res): 
                self.alice_measurement_results.append(1)
                self.bob_measurement_results.append(1)           
        
    def publicly_choose_common_bases(self):
        """ Return indicies of the common bases used for both alice and bob """

        self.common_bases_indicies = [i for i in range(self.N) if self.alice_measurement_choices[i] == self.bob_measurement_choices[i]]
        
    def alice_create_key(self):

        self.alice_key = [m for i,m in enumerate(self.alice_measurement_results) if i in self.common_bases_indicies]
    
    def bob_create_key(self):
        
        self.bob_key = [m for i,m in enumerate(self.bob_measurement_results) if i in self.common_bases_indicies]
        
    def check_random_bits_of_key(self, percent_to_check: float = 0.2):
        """ Check only part of the key is correct """
        abKeyMismatches = 0 # number of mismatching bits in Alice's and Bob's keys

        random_key_indicies = random.sample(range(len(self.alice_key)), int(len(self.alice_key)*percent_to_check))

        for j in random_key_indicies:
            if self.alice_key[j] != self.bob_key[j]:
                abKeyMismatches += 1
                
        return abKeyMismatches
    
    def compute_chsh_correlation(self) -> float:
        countA1B1 = [0, 0, 0, 0] # XW observable: (-1,-1)   results
        countA1B3 = [0, 0, 0, 0] # XV observable: (-1,1)    results
        countA3B1 = [0, 0, 0, 0] # ZW observable: (1,-1)    results
        countA3B3 = [0, 0, 0, 0] # ZV observable: (1,1)     results
        
        for i in range(self.N):

            alice_base: Basis
            bob_base: Basis
            count_list: list[int]

            # For all possible chosen basis couple, count how many times Alice and Bob measured the following singlets (00, 01, 10, 11)
            for alice_base, bob_base, count_list in [
                (Basis.X, Basis.W, countA1B1),
                (Basis.X, Basis.V, countA1B3),
                (Basis.Z, Basis.W, countA3B1),
                (Basis.Z, Basis.V, countA3B3)
            ]:

                if alice_base == self.alice_measurement_choices[i] and bob_base == self.bob_measurement_choices[i]:
                    b_a = self.alice_measurement_results[i]
                    b_b = self.bob_measurement_results[i]

                    if b_a == -1 and b_b == -1:
                        count_list[0] += 1

                    elif b_a == -1 and b_b == 1:
                        count_list[1] += 1
                        
                    elif b_a == 1 and b_b == -1:
                        count_list[2] += 1
                    
                    elif b_a == 1 and b_b == 1:
                        count_list[3] += 1

        # expectation values of XW, XV, ZW and ZV observables
        expect11 = (countA1B1[0] - countA1B1[1] - countA1B1[2] + countA1B1[3]) / sum(countA1B1) # -1/sqrt(2)
        expect13 = (countA1B3[0] - countA1B3[1] - countA1B3[2] + countA1B3[3]) / sum(countA1B3) # 1/sqrt(2)
        expect31 = (countA3B1[0] - countA3B1[1] - countA3B1[2] + countA3B1[3]) / sum(countA3B1) # -1/sqrt(2)
        expect33 = (countA3B3[0] - countA3B3[1] - countA3B3[2] + countA3B3[3]) / sum(countA3B3) # -1/sqrt(2) 

        # calculate the CHSC correlation value (3)
        corr = expect11 - expect13 + expect31 + expect33

        return round(abs(corr), 3)


def simulation_Alice_Bob():
    # N is the number of Qubits generated by the protocol
    p = E91(N=500)

    p.prepare_entangled_qubits()
    p.alice_generate_measurement_choices()
    p.bob_generate_measurement_choices()

    p.apply_measures()

    p.publicly_choose_common_bases()
    p.alice_create_key()
    p.bob_create_key()

    print(f"Alice Key: {''.join(['1' if b==1 else '0' for b in p.alice_key])}")
    print(f"Bob Key: {''.join(['1' if b==1 else '0' for b in p.bob_key])}")
    
    print()
    print(f"Key length: {len(p.alice_key)}")
    print(f"Mismatching bits: {p.check_random_bits_of_key(percent_to_check=1)}")
    print(f"CHSH correlation: {p.compute_chsh_correlation()}")
    print()

    print(f"First 10 basis for A. measurements:\n{[v.name for i, v in enumerate(p.alice_measurement_choices[:10])]}")
    print(f"First 10 basis for B. measurements:\n{[v.name for i, v in enumerate(p.bob_measurement_choices[:10])]}")
    print(f"First 10 basis in common indices for A. & B.: {p.common_bases_indicies[:10]}")
    print(f"N° of basis in common: {len(p.common_bases_indicies)}")


def simulation_Alice_Eve_Bob():
    # N is the number of Qubits generated by the protocol
    p = E91(N=500)

    p.prepare_entangled_qubits()
    p.alice_generate_measurement_choices()
    p.bob_generate_measurement_choices()
    p.eve_generate_measurement_choices()

    p.apply_measures(eve_on_the_field=True)

    p.publicly_choose_common_bases()
    p.alice_create_key()
    p.bob_create_key()

    print(f"Alice Key: {''.join(['1' if b==1 else '0' for b in p.alice_key])}")
    print(f"Bob Key: {''.join(['1' if b==1 else '0' for b in p.bob_key])}")
    
    print()
    print(f"Key length: {len(p.alice_key)}")
    print(f"Mismatching bits: {p.check_random_bits_of_key(percent_to_check=1)}")
    print(f"CHSH correlation: {p.compute_chsh_correlation()}")
    print()

    print(f"First 10 basis for A. measurements:\n{[v.name for i, v in enumerate(p.alice_measurement_choices[:10])]}")
    print(f"First 10 basis for B. measurements:\n{[v.name for i, v in enumerate(p.bob_measurement_choices[:10])]}")
    print(f"First 10 basis in common indices for A. & B.: {p.common_bases_indicies[:10]}")
    print(f"N° of basis in common: {len(p.common_bases_indicies)}")


if __name__ == "__main__":
    simulation_Alice_Bob()

    simulation_Alice_Eve_Bob()

# %%
# print(p.alice_measurement_results[:10])
# print(p.bob_measurement_results[:10])

# %%

# common_bases_length = len(p.common_bases_indicies)
# print((1/3)*p.N)
# print(common_bases_length)

# %%