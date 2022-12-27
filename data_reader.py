import re


def read(file_name):
    """
    Reads data from file.
    INPUT: file_name [string]
    OUTPUT: the following values as integers or nested lists of integers:
    - F: numero de lineas de fabricación
    - TP: numero de tipos de producto
    - N: numero de obras
    - H: periodos de tiempo maximo
    - D[j][p]: unidades de producto 'p' que se requieren en la obra 'j'
    - PL[j][p]: periodo limite en el que debe salir de fabrica la demanda de producto 'p' para la obra 'j'
    - Cap[i][p]: unidades de producto 'p' que puede generar la linea 'i' por unidad de tiempo. Si Cap[i][p] = 0, no se
      puede producir este producto en esta linea
    - CostF[i][p]: coste de fabricacion de una unidad de producto 'p' en la linea 'i'. Si Cap[i][p] = 0, entonces
      Cost[i][p] = 0
    - CostT[j]: coste, por viaje, de transporte de productos a la obra 'j' 
    - alpha: factor de penalización impuesto por la empresa (>= 1)
    - CR[j][p]: coste de compra (fabricacion y transporte) del una unidad de producto 'p' para la obra 'j' 
    """

    with open(file_name, "r") as i_file:
        # F
        F = int(i_file.readline())
        
        # TP
        TP = int(i_file.readline())
        
        # N
        N = int(i_file.readline())
        
        # H
        H = int(i_file.readline())

        # D
        D = []
        for j in range(N):
            nueva_linea = i_file.readline()
            unidades_obra_j_por_producto = re.split("\*", nueva_linea)
            unidades_obra_j_por_producto = [int(elem) for elem in unidades_obra_j_por_producto]
            D.append(unidades_obra_j_por_producto)

        # PL
        PL = []
        for j in range(N):
            nueva_linea = i_file.readline()
            periodo_limite_obra_j_por_producto = re.split("\*", nueva_linea)
            periodo_limite_obra_j_por_producto = [int(elem) for elem in periodo_limite_obra_j_por_producto]
            PL.append(periodo_limite_obra_j_por_producto)

        # Cap
        Cap = []
        for i in range(F):
            nueva_linea = i_file.readline()
            unidades_linea_i_por_producto = re.split("\*", nueva_linea)
            unidades_linea_i_por_producto = [int(elem) for elem in unidades_linea_i_por_producto]
            Cap.append(unidades_linea_i_por_producto)

        # CostF
        CostF = []
        for i in range(F):
            nueva_linea = i_file.readline()
            coste_produccion_linea_i_por_producto = re.split("\*", nueva_linea)
            coste_produccion_linea_i_por_producto = [float(elem) for elem in coste_produccion_linea_i_por_producto]
            CostF.append(coste_produccion_linea_i_por_producto)
            
        # CostT
        nueva_linea = i_file.readline()
        CostT = re.split("\*", nueva_linea)
        CostT = [float(elem) for elem in CostT]
        
        # alpha
        alpha = float(i_file.readline())

        # CR
        CR = []
        for j in range(N):
            nueva_linea = i_file.readline()
            coste_obra_j_por_producto = re.split("\*", nueva_linea)
            coste_obra_j_por_producto = [float(elem) for elem in coste_obra_j_por_producto]
            CR.append(coste_obra_j_por_producto)
            
    return F, TP, N, H, D, PL, Cap, CostF, CostT, alpha, CR




