# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, ClockCycles

@cocotb.test()
async def test_alif_adaptation(dut):
    # 1. Setup: 100MHz clock (standard for TinyTapeout simulations)
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # 2. Reset Sequence
    dut._log.info("Resetting ALIF Neuron...")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # 3. Stimulus Configuration
    # ui_in = 80 (High input current to drive frequent firing)
    # uio_in = 0x24: 
    #   Lower nibble (0x4) = Vm Leak (subtracted every cycle)
    #   Upper nibble (0x2) = Adaptation Decay (how fast the "fatigue" recovers)
    dut.ui_in.value = 80
    dut.uio_in.value = 0x24 
    
    spike_times = []
    dut._log.info("Simulation started: Monitoring Inter-Spike Intervals (ISI)")

    # 4. Observation Loop
    # We run for 3000 cycles to ensure the adaptation state has time to saturate
    for i in range(3000):
        await RisingEdge(dut.clk)
        # Check if bit 0 of uo_out (spike bit) is high
        if int(dut.uo_out.value) & 0x01:
            spike_times.append(i)
            # Log the adaptation state (uio_out) at the moment of spiking
            adapt_val = int(dut.uio_out.value)
            dut._log.info(f"Spike at cycle {i} | Adaptation Level: {adapt_val}")

    # 5. Metric Analysis (The "A" grade section)
    if len(spike_times) >= 3:
        isi = [spike_times[j] - spike_times[j-1] for j in range(1, len(spike_times))]
        dut._log.info(f"Calculated ISIs: {isi}")
        
        # Verify adaptation: The time between spikes should get longer
        # as the adaptation state builds up.
        first_isi = isi[0]
        last_isi = isi[-1]
        
        dut._log.info(f"First ISI: {first_isi} cycles, Last ISI: {last_isi} cycles")
        
        assert last_isi > first_isi, f"Adaptation failed: ISI did not increase ({first_isi} to {last_isi})"
        dut._log.info("SUCCESS: Neuron exhibited spike-frequency adaptation.")
    else:
        # If the neuron doesn't fire enough, you might need to increase ui_in or lower the threshold
        assert False, f"Insufficient spikes ({len(spike_times)}) to verify adaptation. Try increasing ui_in."

    dut._log.info("ALIF Verification Completed.")