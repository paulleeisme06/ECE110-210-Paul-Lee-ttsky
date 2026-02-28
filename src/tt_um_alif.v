/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_alif (
    input  wire [7:0] ui_in,    // Input Current (I)
    output wire [7:0] uo_out,   // [7:1] V_mem, [0] Spike
    input  wire [7:0] uio_in,   // [7:4] Adapt Leak, [3:0] Vm Leak
    output wire [7:0] uio_out,  // Monitoring Adaptation State
    output wire [7:0] uio_oe,   // IO Enable
    input  wire       ena,      
    input  wire       clk,      
    input  wire       rst_n     
);

    // --- Internal State Registers ---
    reg [7:0] v_mem;        
    reg [7:0] adaptation;   
    reg spike;

    // --- Parameters ---
    localparam [7:0] THRESHOLD  = 8'd200;
    localparam [7:0] ADAPT_STEP = 8'd40; 

    // --- ALIF Logic (Combined for simplicity) ---
    always @(posedge clk) begin
        if (!rst_n) begin
            v_mem <= 0;
            adaptation <= 0;
            spike <= 0;
        end else begin
            if (v_mem >= THRESHOLD) begin
                // FIRE
                spike <= 1'b1;
                v_mem <= 8'h00; // Reset
                // Increase adaptation (with overflow protection)
                adaptation <= (adaptation < (8'hFF - ADAPT_STEP)) ? adaptation + ADAPT_STEP : 8'hFF;
            end else begin
                spike <= 1'b0;
                
                // 1. Integration & Vm Leak
                // Current Vm = Vm + Input - (Constant Leak + Adaptation Fatigue)
                if (v_mem + ui_in > ({4'b0, uio_in[3:0]} + (adaptation >> 2)))
                    v_mem <= v_mem + ui_in - ({4'b0, uio_in[3:0]} + (adaptation >> 2));
                else
                    v_mem <= 0;

                // 2. Adaptation Decay (Gradually recover from fatigue)
                if (adaptation > {4'b0, uio_in[7:4]})
                    adaptation <= adaptation - {4'b0, uio_in[7:4]};
                else
                    adaptation <= 0;
            end
        end
    end

    // --- Pin Assignments ---
    assign uo_out  = {v_mem[7:1], spike}; 
    assign uio_out = adaptation;          
    assign uio_oe  = 8'hFF;               // Enable all outputs for monitoring

    // Cleanup
    wire _unused = &{ena, 1'b0};

endmodule