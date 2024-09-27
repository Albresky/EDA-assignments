# 1. project name
open_project prj -reset

# 2. set top name
set_top matmult
# 3. add files
add_files matmult.c
add_files -tb tb_matmult.c

# 4. solution name
open_solution "solution1" -reset

# 5. device name
set_part virtex7

# 6. clock setting
create_clock -period 13 -name default
config_export -version 2.0.1;

set CSIM 1
set CSYNTH 1
set COSIM 1


if {$CSIM == 1} {
  puts "Starting Csim..."
  csim_design
}

if {$CSYNTH == 1} {
  puts "Starting Csynth..."
  csynth_design
}

if {$COSIM == 1} {
  puts "Starting Cosim..."
  cosim_design
}

exit
