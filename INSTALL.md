# Installation Guide

## Quick Start

### For both projects:
```bash
pip install -r requirements.txt
```

### For individual projects:

#### Surface Codes (surface_codes.py):
```bash
pip install -r requirements_surface_codes.txt
```

#### Spin Squeezing (squeeze.py):
```bash
pip install -r requirements_squeeze.txt
```

## GPU Acceleration (Optional)

For GPU acceleration in `squeeze.py`, install CuPy based on your CUDA version:

### CUDA 12.x:
```bash
pip install cupy-cuda12x
```

### CUDA 11.x:
```bash
pip install cupy-cuda11x
```

### Check CUDA version:
```bash
nvidia-smi
# or
nvcc --version
```

## Troubleshooting

### If you encounter issues with QuTip:
```bash
# Try installing with conda instead
conda install -c conda-forge qutip
```

### If matplotlib doesn't display plots:
```bash
# For headless systems, install a backend
pip install matplotlib[gui]
```

### For Apple Silicon Macs:
CuPy is not available for macOS. The code will automatically fall back to CPU mode.

## Running the Code

### Surface Codes:
```bash
python surface_codes.py
```

### Spin Squeezing:
```bash
python squeeze.py
```

Or use the shell script:
```bash
bash run_squeeze.sh
```