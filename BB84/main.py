import numpy as np
import random
from enum import Enum


class PolarizedFilter(Enum):
    RECTANGULAR = 1
    DIAGONAL = 2
    

class PolarizationAngle(Enum):
    VERTICAL = 0
    HORIZONTAL = 1
    BL_TR = 3 #bottom-left - top-right
    TL_BR = 4 #top-left - bottom-right


class Photon:
    def __init__(self, polarization_angle: PolarizationAngle):
        self.polarization_angle = polarization_angle

    
    def measure(self, pflt: PolarizedFilter):
        # 1.1
        # a) collapse the photon into one of the states of the base
        # b) return the measured value
        #     if Rectangular: vertical=0, horizontal=1
        #     if Diagonal: BL_TR = 0, TL_BR=1
        
        if pflt == PolarizedFilter.RECTANGULAR:
            if self.polarization_angle in [PolarizationAngle.BL_TR, PolarizationAngle.TL_BR]: # The data is lost
                return 0
            
            elif self.polarization_angle == PolarizationAngle.VERTICAL: # The mesurement is correct and the data is 0
                return 0
            
            elif self.polarization_angle == PolarizationAngle.HORIZONTAL: # The mesurement is correct and the data is 1
                return 1
            
        elif pflt == PolarizedFilter.DIAGONAL:
            if self.polarization_angle in [PolarizationAngle.VERTICAL, PolarizationAngle.HORIZONTAL]: # The data is lost
                return 0
            
            elif self.polarization_angle == PolarizationAngle.BL_TR: # The mesurement is correct and the data is 0
                return 0
            
            elif self.polarization_angle == PolarizationAngle.TL_BR: # The mesurement is correct and the data is 1
                return 1
            
        return None


class BB84:
    def __init__(self):
        bit_count = 0
        
        alice_bits_a = []
        alice_bits_b = []
        alice_photons = []
        
        bob_photons = []
        bob_bits_b = []
        bob_bits_a = []
        
        key_alice = []
        key_bob = []
        
        eve_photons = []
        eve_bits_b = []
        eve_bits_a = []
        key_eve = []
        

    def alice_generate_bits(self, n):
        # 1.2
        # generate 2 random arrays A and B of n bits
        self.alice_bits_a = [random.randint(0, 1) for _ in range(n)]
        
        self.alice_bits_b = [random.randint(0, 1) for _ in range(n)]

        
    def alice_encode_photons(self):
        # 1.3
        # encode the photons using the correct polarization
        self.alice_photons = []
        
        for bit_a, bit_b in zip(self.alice_bits_a, self.alice_bits_b):
            if bit_a == 0 and bit_b == 0:  # Base: Vertical and Rectangular
                self.alice_photons.append(Photon(PolarizationAngle.VERTICAL))
            elif bit_a == 0 and bit_b == 1:  # Base: Horizontal and Rectangular
                self.alice_photons.append(Photon(PolarizationAngle.HORIZONTAL))
            elif bit_a == 1 and bit_b == 0:  # Base: BL_TR and Diagonal
                self.alice_photons.append(Photon(PolarizationAngle.BL_TR))
            elif bit_a == 1 and bit_b == 1:  # Base: TL_BR and Diagonal
                self.alice_photons.append(Photon(PolarizationAngle.TL_BR))

    
    def alice_send_to_bob(self):
        # 1.4
        # move the photons from alice's array to bob's array
        self.bob_photons = self.alice_photons
        self.alice_photons = []

    
    def bob_generate_random_base(self):
        # 1.6
        # generate random base bits B for Bob
        self.bob_bits_b = [random.randint(0, 1) for _ in range(len(self.alice_photons))]


    def eve_generate_random_base(self, p_eve):

        self.eve_bits_b = [random.randint(0, 1) if random.uniform(0, 1) <= p_eve else None for k in range(len(self.alice_photons))] # Random bases


    def bob_measure_photons(self):
        # 1.6
        # measure bob's photons and construct A array of bob
        self.bob_bits_a = []

        for i, photon in enumerate(self.bob_photons):

            if self.bob_bits_b[i] == 0:
                self.bob_bits_a.append(photon.measure(PolarizedFilter.RECTANGULAR))
                
            else:
                self.bob_bits_a.append(photon.measure(PolarizedFilter.DIAGONAL))
    

    def eve_measure_photons(self):
        self.eve_bits_a = []

        for i, photon in enumerate(self.eve_photons):

            if self.eve_bits_b[i] == 0:
                self.eve_bits_a.append(photon.measure(PolarizedFilter.RECTANGULAR))
                
            elif self.eve_bits_b[i] == 1:
                self.eve_bits_a.append(photon.measure(PolarizedFilter.DIAGONAL))

            else:
                self.eve_bits_a.append(None)    
    

    def base_disclosure(self):
        # 1.7
        # alice and bob now can publicly disclose the bases
        # task: check alice's base bits B against bob's base bits B 
        # keep only the bits A where the base bits match
        # fill in key_alice with alice's bits A and key_bob with bob's bits B
        
        n = len(self.alice_bits_a)

        self.key_alice = []
        self.key_bob = []
        self.key_eve = []
        
        for i in range(n):
            if self.alice_bits_b[i] == self.bob_bits_b[i]:

                self.key_alice.append(self.alice_bits_a[i])

                self.key_bob.append(self.bob_bits_a[i])

                if self.alice_bits_b[i] == self.eve_bits_b[i] and self.eve_bits_a[i] is not None:
                    self.key_eve.append(self.eve_bits_a[i])
                else:
                    self.key_eve.append(None)
            else:
                pass

    # ----------------
    
    def alice_send_to_bob_with_information_loss(self, p_loss):
        # 1.9
        # same as alice_send_to_bob, but now each photon has a probability p_loss
        # to arrive to bob with flipped polarization

        self.bob_photons = []

        for photon in self.alice_photons:
            if random.random() < p_loss:
                # Flip the polarization
                if photon.polarization_angle == PolarizationAngle.VERTICAL:
                    flipped_polarization = PolarizationAngle.HORIZONTAL

                elif photon.polarization_angle == PolarizationAngle.HORIZONTAL:
                    flipped_polarization = PolarizationAngle.VERTICAL

                elif photon.polarization_angle == PolarizationAngle.BL_TR:
                    flipped_polarization = PolarizationAngle.TL_BR

                elif photon.polarization_angle == PolarizationAngle.TL_BR:
                    flipped_polarization = PolarizationAngle.BL_TR

                else:
                    flipped_polarization = photon.polarization_angle

                flipped_photon = Photon(flipped_polarization)
                self.bob_photons.append(flipped_photon)
            else:
                # No flip, send the original photon
                self.bob_photons.append(photon)

        self.alice_photons = []
    
    # ----------------
    
    def alice_send_to_bob_with_eve(self):
        # 1.11
        # same as alice_send_to_bob, but now Eve tries to intercept the photons
        # a) first move the photons from alice's array to bob's array
        # b) for each photon, eve decides to measure it with probability p_eve
        #     the photons that eve decides not to measure will be unaffected
        # c) Eve generates random bases (use None for the ones she does not measure)
        # d) Eve measures the photons that she decided to measure and obtains bits A
        # e) the final photons are then sent to Bob as usual
        # f) edit the base_disclosure() function so Eve also gets her key bits
        #    for the photons that she measured, in the correct positions
        self.eve_photons = []
        self.bob_photons = []
        
        n = len(self.alice_photons)

        for i, photon in enumerate(self.alice_photons):
            
            # Sending from Alice to Eve
            if self.eve_bits_b[i] == 0: # Rectangular filter
                if photon.polarization_angle in [PolarizationAngle.VERTICAL, PolarizationAngle.HORIZONTAL]: # She receives the photon
                    new_photon = photon
                
                else: # Diagonal filter 
                    new_photon = random.choice([Photon(PolarizationAngle.BL_TR), Photon(PolarizationAngle.TL_BR)]) # 50% chance of being reflected

                self.eve_photons.append(new_photon)

            elif self.eve_bits_b[i] == 1: # Rectangular filter
                if photon.polarization_angle in [PolarizationAngle.BL_TR, PolarizationAngle.TL_BR]: # She receives the photon
                    new_photon = photon
                
                else: 
                    new_photon = random.choice([Photon(PolarizationAngle.VERTICAL), Photon(PolarizationAngle.HORIZONTAL)]) # 50% chance of being reflected

                self.eve_photons.append(new_photon)

            else: # She does not measure it (None)
                new_photon = photon

                self.eve_photons.append(None)
            

            # Sending from Eve to Bob
            self.bob_photons.append(new_photon)



def test_BB84():
    # 1.8 - test BB84
    # generate 256 photons from alice to bob and obtain the final key
    # a) how many bits does the key have?
    # b) how many key bits are correct? (i.e. do they match between key_alice and key_bob)

    bb84 = BB84()

    bb84.alice_generate_bits(n=256)
    bb84.alice_encode_photons()
    
    print([photon.polarization_angle.name for photon in bb84.alice_photons])

    bb84.alice_send_to_bob_with_information_loss(p_loss=0.05)
    #bb84.alice_send_to_bob()

    bb84.bob_generate_random_base()
    bb84.bob_measure_photons()

    bb84.base_disclosure()

    print(bb84.key_alice)
    print(bb84.key_bob)

    n = len(bb84.key_bob)

    correct_bits = sum([1 if bb84.key_alice[i] == bb84.key_bob[i] else 0 for i in range(n)])

    print(f"key_bits: {n}, correct_bits: {correct_bits}, percentage: {round(correct_bits/n, 2)}")


def test_BB84_w_eve():
    # 1.12 - test BB84 with Eve with a p=0.05
    # a) how many bits does the key have?
    # b) how many key bits are correct? (i.e. do they match between key_alice and key_bob)
    # c) how many bits did Eve get without being detected?
    bb84 = BB84()

    bb84.alice_generate_bits(n=256)
    bb84.alice_encode_photons()

    print(f"alice_photons: {[photon.polarization_angle.name for photon in bb84.alice_photons]}")

    bb84.eve_generate_random_base(p_eve=0.05)
    bb84.bob_generate_random_base()

    bb84.alice_send_to_bob_with_eve()

    bb84.eve_measure_photons()
    bb84.bob_measure_photons()
    print(f"eve_photons: {[photon.polarization_angle.name if photon is not None else None for photon in bb84.eve_photons]}")
    print(f"bob_photons: {[photon.polarization_angle.name for photon in bb84.bob_photons]}")
    print("\n")

    print(f"eve_bits_a: {bb84.eve_bits_a}")
    print(f"bob_bits_a: {bb84.bob_bits_a}")
    print("\n")

    print(f"alice_bits_b: {bb84.alice_bits_b}")
    print(f"bob_bits_b: {bb84.bob_bits_b}")
    print(f"eve_bits_b: {bb84.eve_bits_b}")
    print("\n")
    
    bb84.base_disclosure()

    print(f"bb84.key_alice: {bb84.key_alice}")
    print(f"bb84.key_eve: {bb84.key_eve}")
    print(f"bb84.key_bob: {bb84.key_bob}")
    print("\n")

    eve_correct_bits = sum([1 if bb84.key_alice[i] != None and bb84.key_alice[i] == bb84.key_eve[i] else 0 for i in range(len(bb84.key_alice))])
    bob_correct_bits = sum([1 if bb84.key_alice[i] != None and bb84.key_alice[i] == bb84.key_bob[i] else 0 for i in range(len(bb84.key_alice))])

    print(f"eve_key_bits: {len(bb84.key_eve)}, eve_correct_bits: {eve_correct_bits}, percentage: {round(eve_correct_bits/len(bb84.key_eve), 10)}")
    print(f"bob_key_bits: {len(bb84.key_bob)}, bob_correct_bits: {bob_correct_bits}, percentage: {round(bob_correct_bits/len(bb84.key_bob), 10)}")

test_BB84_w_eve()