from .BoolODE import main

def run_boolODE(
    bool_path, ics_path, save_path, 
    max_time=20, timesteps=100, num_cells=100):
    main([
        "--path", bool_path, 
        "--ics", ics_path, 
        "--max-time", str(max_time), 
        "--num-cells", str(num_cells), 
        "--timesteps", str(timesteps),
        "--outPrefix", save_path, 
        "--do-parallel"
    ])