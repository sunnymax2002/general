module ExampleFSM(
    input logic clk,
    input logic rst_b,
    input logic X,
    output logic Y,
);

typedef enum logic [2:0] {A, B, C, D, E} State;

State currState, nextState;

// Sequential
always_ff @(posedge clk)
    if(rst_b)
        currState = nextState;
    else
        currState = A;

// Combo
always_comb
    case(currState)
        A:
            if(X)
                nextState = C;
            else
                nextState = D;
        default:
            nextState = A;
    endcase

// Output assignment
assign Y = (currState == C || currState != B);
endmodule