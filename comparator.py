import main

VERSION = 0.1

with open(f"results/results_v{VERSION}.txt", "w") as o_f:
    o_f.write(f"Version: {VERSION}\n")
    o_f.write(f"Ejemplos calibrado:\n")
    with open("calidad_minima_ejemplares_calibrado.txt", "r") as i_f:
        for index_ in range(1, 101):
            teacher_value = float(i_f.readline().strip().split(" ")[-1])
            my_value = main.main(f"Ejemplares_calibrado/ejemplar_calibrado_{index_}.txt",
                                 f"Ejemplares_calibrado/solution_ejemplar_calibrado_{index_}.txt",
                                 debug=False,
                                 force=True)
            result = f" {index_}- \tT.V.: {'%.1f'%teacher_value}  \t{'<=' if teacher_value < my_value else '>'}\t" \
                     f"M.V.: {'%.1f'%my_value}   \t|\t%: {'%.1f'%(100 * (my_value - teacher_value) / teacher_value)}" \
                     f"{'   LOST!' * (teacher_value <= my_value)}"
            print(result)
            o_f.write(f"{result}\n")
    o_f.write(f"Ejemplos prueba:\n")
    with open("calidad_minima_ejemplares_prueba.txt", "r") as i_f:
        for index_ in range(1, 101):
            teacher_value = float(i_f.readline().strip().split(" ")[-1])
            my_value = main.main(f"Ejemplares_prueba/ejemplar_prueba_{index_}.txt",
                                 f"Ejemplares_prueba/solution_ejemplar_prueba_{index_}.txt",
                                 debug=False,
                                 force=True)
            result = f" {index_}- \tT.V.: {'%.1f'%teacher_value}  \t{'<=' if teacher_value < my_value else '>'}\t" \
                     f"M.V.: {'%.1f'%my_value}   \t|\t%: {'%.1f'%(100 * (my_value - teacher_value) / teacher_value)}" \
                     f"{'   LOST!' * (teacher_value <= my_value)}"
            print(result)
            o_f.write(f"{result}\n")

