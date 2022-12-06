# How to download
First of all you need to clone this repository using the command:
```bash
git clone <LINK_TO_REPOSITORY>
```
`<LINK_TO_REPOSITORY>` can be either:
- HTTPS: "https://github.com/SeverinoDaDalt/mo_d_organitzacio_industrial_2022-23.git"
- SSH: "git@github.com:SeverinoDaDalt/mo_d_organitzacio_industrial_2022-23.git"

For CLI users run this instead:
```bash
gh repo clone SeverinoDaDalt/mo_d_organitzacio_industrial_2022-23
```

# Requirements

Python 3 is the only requirement for running the code.

# How to run

In order to run this code go to the main folder of this project.

There, run the following line of code:
```bash
python main.py -i <INPUT_FILE_NAME> -o <OUTPUT_FILE_NAME>
```

- `<INPUT_FILE_NAME>` is the name of the input file (for example: "ejemplar_prueba_1.txt"). This file needs to be 
previously placed in the folder named "my_inputs/". If the file is anywhere else, the code will fail.
- `<OUTPUT_FILE_NAME>` is the name of the output_file (for example: "solucion_prueba_1.txt"). This is the where the
code will write the output. It can be found in "my_ouputs/" folder, or in the "debug_outputs" if the debug mode was 
activated.

Other parameters:
- `-f` or `--force`: add this at the end of your code (`python main.py -i ejemplar_prueba_1.txt -o 
solucion_prueba_1.txt -f`) if you want to override the previous output file with the same name 
(In the previous example, if "solucion_prueba_1.txt" already existed, the `-f` parameter would have overwritten the 
previous version with the new one).
- `-d` or `--debug`: DEBUG MODE. Not recommended. Just for debugging. If this is set output will be written in the
"debug_outputs/" folder.