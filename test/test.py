# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_counter_increments(dut):
    dut._log.info("Start counter test")

    # Start clock: 10 us period
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initialize inputs
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    # Assert reset (active low) for a few cycles
    dut._log.info("Asserting reset")
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)

    # Release reset
    dut._log.info("Releasing reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    # After reset, counter should start at 0
    dut._log.info("Checking initial counter value")
    assert int(dut.uo_out.value) == 0, f"Expected 0 after reset, got {int(dut.uo_out.value)}"

    # Check that the counter increments every clock cycle
    cycles_to_check = 8
    for i in range(1, cycles_to_check + 1):
        await ClockCycles(dut.clk, 1)
        observed = int(dut.uo_out.value)
        expected = i & 0xFF
        assert observed == expected, f"At cycle {i}: expected {expected}, got {observed}"

    # Verify unused outputs are zero as implemented
    dut._log.info("Checking unused IOs are zero")
    assert int(dut.uio_out.value) == 0
    assert int(dut.uio_oe.value) == 0

    dut._log.info("Counter test passed")
