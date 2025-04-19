#!/bin/bash

INPUT_FILE="latency_pavlik.txt"
DATA_FILE="latency_sparse.dat"
PLOT_SCRIPT="latency_plot.plt"
OUTPUT_PNG="latency_chart.png"

# Step 1: AWK that works with mawk
awk '
BEGIN {
    for (i = 0; i <= 30; i++) {
        tid[i] = 0;  # cumulative iteration
    }
    # print header
    printf "Iteration";
    for (i = 0; i <= 30; i++) {
        printf "\tT%d", i;
    }
    print "";
}
/^T:/ {
    # extract T
    t_raw = $0;
    sub(/^.*T:[ \t]*/, "", t_raw);
    split(t_raw, t_arr, /[ \t]+/);
    t = t_arr[1] + 0;

    # extract C
    c_raw = $0;
    sub(/^.*C:[ \t]*/, "", c_raw);
    split(c_raw, c_arr, /[ \t]+/);
    c = c_arr[1] + 0;

    # extract Avg
    a_raw = $0;
    sub(/^.*Avg:[ \t]*/, "", a_raw);
    split(a_raw, a_arr, /[ \t]+/);
    avg = a_arr[1] + 0;

    # update cumulative iteration
    tid[t] += c;

    # print row with NaN except current thread
    printf "%d", tid[t];
    for (i = 0; i <= 30; i++) {
        if (i == t) {
            printf "\t%d", avg;
        } else {
            printf "\tNaN";
        }
    }
    print "";
}
' "$INPUT_FILE" > "$DATA_FILE"


