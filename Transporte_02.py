
# Importar librerías
from ortools.linear_solver import pywraplp
import pandas as pd

# Conjuntos
plantas = ['P1', 'P2', 'P3', 'PF']
clientes = ['C1', 'C2', 'C3']

num_plantas = len(plantas)
num_clientes = len(clientes)

# Parámetros
costo = {
    ('P1', 'C1'): 150,
    ('P1', 'C2'): 200,
    ('P1', 'C3'): 350,
    ('P2', 'C1'): 560,
    ('P2', 'C2'): 1200,
    ('P2', 'C3'): 85,
    ('P3', 'C1'): 690,
    ('P3', 'C2'): 300,
    ('P3', 'C3'): 178,
    ('PF', 'C1'): 0,
    ('PF', 'C2'): 0,
    ('PF', 'C3'): 0
    }

capacidad = {
    'P1': 1000,
    'P2': 1000,
    'P3': 1000,
    'PF': 200
    }

demanda = {
    'C1': 1000,
    'C2': 1000,
    'C3': 1200
    }

# Instanciar el modelo
solver = pywraplp.Solver('Transporte2', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

# Instanciar el infinito
inf = solver.infinity()

# Variables de decisión
X = {}  #Diccionario vacío

for planta in plantas:
    for cliente in clientes:
        X[planta,cliente] = solver.NumVar(0.0, inf, 'X[%s,%s]' % (planta, cliente))


# Función objetivo
solver.Minimize(solver.Sum([X[planta,cliente]*costo[(planta,cliente)] for planta in plantas for cliente in clientes]))

# Restricciones
# Capacidad de las plantas
rest_cap = [] #Lista con los nombres de las restricciones
for planta in plantas:
    solver.Add(solver.Sum([X[planta,cliente] for cliente in clientes]) <= capacidad[planta], name = 'capacidad_%s' % planta)
    rest_cap.append('capacidad_%s' % planta)

# Demanda de los clientes
rest_dem = [] #Lista con los nombres de las restricciones
for cliente in clientes:
    solver.Add(solver.Sum([X[planta,cliente] for planta in plantas]) >= demanda[cliente], name = 'demanda_%s' % cliente)
    rest_dem.append('demanda_%s' % cliente)


# Resolver el modelo
sol = solver.Solve()

# Imprimir resultados
print('Número de variables =', solver.NumVariables())
print('Número de restricciones =', solver.NumConstraints())
print('Costo = ', solver.Objective().Value())
print('Tiempo = ', solver.WallTime(), 'milisegundos')
    

#Mostrar resultados

# Variables de decisión
cols1 = ['Variable', 'Valor', 'Status', 'Costo_Reducido']
data1 = []
for planta in plantas:
    for cliente in clientes:
        data1.append([X[planta,cliente].name(), X[planta,cliente].solution_value(),
                      X[planta,cliente].basis_status(), X[planta,cliente].reduced_cost(),
                      ])

# Convertir en dataframe de pandas
sal1 = pd.DataFrame(data1, columns = cols1)


# Restricciones
cols2 = ['Restricción','Status','Valor_Dual']
restricciones = rest_cap + rest_dem
data2 = []
for restriccion in restricciones:
    data2.append([solver.Constraint(restriccion).name(),
                  solver.Constraint(restriccion).basis_status(),
                  solver.Constraint(restriccion).dual_value()])

# Convertir en dataframe de pandas
sal2 = pd.DataFrame(data2, columns = cols2)


#Exportar a Excel
writer = pd.ExcelWriter('Resultados.xlsx')
sal1.to_excel(writer, sheet_name="Variables")
sal2.to_excel(writer, sheet_name="Restricciones")
writer.save()


