# Quick start

1. Create a virtual environment and install dependencies from `requirements.txt`.
2. Put compatible CSV sensor logs in `data/raw/io_vnbd/`.
3. Run the notebooks in order from 01 to 07.
4. The core Python modules are now functional; dataset-specific column mappings can be extended in `src/data_loader.py`.

Important: the repository is a functional research prototype. A trained model checkpoint and a production Android app are not included because they require real labelled sensor data and Android device testing.
