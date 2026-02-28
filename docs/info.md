<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.
I thi
You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

The design implements an Adaptive Leaky Integrate-and-Fire (ALIF) neuron, a biomimetic digital circuit optimized for the TinyTapeout 1x1 tile. Unlike a standard LIF neuron, this architecture incorporates an internal feedback mechanism to simulate Spike-Frequency Adaptation (SFA). This is a critical feature in biological neural processing that allows neurons to reduce their firing rate in response to a constant stimulus, preventing energetic saturation and enabling temporal coding.

### Architecture and Signal Integration
The system is built around a dual-register state machine consisting of an 8-bit Membrane Potential (V_mem) register and an 8-bit Adaptation (A) register. As illustrated in Figure 1, the neuron operates by integrating the input current (I_in), received via the ui_in pins, while simultaneously subtracting two "leak" components: a constant membrane leak (L_v) and a dynamic adaptation current (A). By using dedicated 8-bit registers for these states, the design ensures that temporal information is preserved across clock cycles, allowing for complex firing behaviors.

#### Figure 1: ALIF Functional Architecture

![Figure 1: ALIF Functional Architecture](block_diagram.png)

This diagram illustrates the hardware implementation of the ALIF neuron. The design processes input current (I_in) modulated by a constant membrane leak (L_v) and a dynamic adaptation signal (A) to produce the membrane potential (V_mem).

### Temporal Dynamics and Firing Logic
The membrane potential (V_mem) accumulates value until it reaches a hard-coded threshold of 200. Referring to the feedback loop shown in Figure 1, every time a spike is generated on uo_out[0], the Adaptation register (A) increments. This value is then fed back into the primary summation node to be subtracted from the next integration cycle. This specific design choice—using subtractive feedback—is what allows the neuron to exhibit "fatigue." Even with a constant input current, the increasing adaptation level slows the rate of integration, effectively lengthening the time required to reach the next threshold crossing.

### Configuration and Design Optimization
To maintain high hardware efficiency within a single TinyTapeout tile, the design utilizes fixed-point arithmetic instead of area-intensive floating-point units. The neuron's behavior is fully configurable through the uio_in pins, where the lower four bits control the membrane leak rate (L_v) and the upper four bits control the adaptation decay rate (L_a). This optimization allows the user to tune the neuron's sensitivity and recovery speed, providing a flexible platform for neuromorphic experiments while maintaining a low gate count.

## How to test

The ALIF neuron is verified using a Cocotb-based Python testbench that performs a full temporal characterization of the spike-frequency adaptation (SFA) and recovery dynamics.

### Functional Verification and Waveform Analysis
To verify the adaptation mechanism, a constant high-input current (I_in = 80) is applied. As demonstrated in the timing diagram (Figure 2), we can observe the precise sub-threshold dynamics of the 8-bit membrane potential (V_mem) and the resulting spike pulses on uo_out[0].

#### Figure 2: Waveform/Timing Diagram

![Figure 2: Waveform/Timing Diagram](timing_diagram.png)

This waveform shows the Vmem register and the spike output. The markers demonstrate the transition from high-frequency firing to a slower, adapted state.

### Characterization of Spike-Frequency Adaptation
By analyzing the waveform at the steady-state window, we can pinpoint the exact cycles where the negative feedback loop takes effect:
 - Initial Burst Phase: Immediately following the reset (at 0ps), the neuron fires rapidly with an Inter-Spike Interval (ISI) of only 4 clock cycles (40,000ps), as the adaptation register is still near zero.
 - Observation Window (9,600,000ps ~ 10,400,000ps): As seen in Figure 2, after the adaptation state has had time to accumulate, the "staircase" penalty is at its peak. By this timestamp, the integration slope of V_mem has become significantly shallower.

### Recovery and State Decay
The testbench further validates the "leaky" nature of the adaptation register by setting the input current to zero after the primary firing window. As verified in the simulation logs, the adaptation state (A) successfully decays back toward zero. This confirms that the neuron recovers its baseline sensitivity, ensuring the hardware is ready for subsequent stimuli without permanent "fatigue" saturation.

### Reproducing Results
 - To run the simulation and verify the metrics, execute the following commands in a Linux or Docker environment:
```bash
cd test
make
```
 - This will compile the Verilog and run the Cocotb testbench.
 - Check Terminal Output: The testbench will print the detected ISIs directly to the console. As shown in Figure 3, you should see the ISI values incrementing from 4 toward 33.

#### Figure 3: Example of Testbench Results

![Figure 3: Testbench Results](testbench_results.png)

This console log captures the real-time calculation of Inter-Spike Intervals, confirming the transition from a 4-cycle burst to a 33-cycle adapted state.

## External hardware

This project is a self-contained digital macro designed for the TinyTapeout 1x1 tile. While no physical external components are required for simulation, the design is engineered to interface with standard CMOS-level digital systems.

### Intended Interface
In a physical deployment, the chip would be integrated as follows:
 - Digital Controller: A microcontroller or FPGA would drive the ui_in (Stimulus) and uio_in (Parameter) pins to modulate the neuron's behavior dynamically.
 - Monitoring: The uo_out pins provide a real-time digital monitor. For biological-time visualization, the 7-bit $V_{mem}$ output can be passed through an external R-2R ladder DAC to observe the sawtooth membrane dynamics on an oscilloscope.
 - Event-Based Systems: The uo_out[0] spike signal is compatible with standard Address Event Representation (AER) protocols used in larger neuromorphic arrays.
