# coding: utf-8


import re

# Classe permettant de stocker les données du problème
class Data():
    def __init__(self, datafileName):
        with open(datafileName, "r") as file:  #ouvre le fichier, le ferme automatiquement à la fin et gère les exceptions
            line = file.readline()  # lit la 1ère ligne
            lineTab = line.split(' ')  # sépare les éléments de la ligne dans un tableau en utilisant l'espace comme séparateur
            nb_warehouses = int(lineTab[0]) # la valeur de la 1ère case correspond au nombre d'entrepôts (attention de penser à convertir la chaîne de caractère en un entier)
            nb_customers = int(lineTab[1]) # la valeur de la 2ème case correspond au nombre de clients
            capacity = [] # création d'un tableau qui stockera les capacités des entrepôts
            opening_cost = [] # création d'un tableau qui stockera les coûts d'ouverture des entrepôts
            for i in range(nb_warehouses): # pour chaque ligne contenant les informations sur les entrepôts
                line = file.readline()  # lit la ligne suivante
                lineTab = line.split(' ')  # sépare les éléments de la ligne dans un tableau en utilisant l'espace comme séparateur
                capacity.append(int(lineTab[0]))
                opening_cost.append(float(lineTab[1]))
            demand = [] # création d'un tableau qui stockera les demandes des clients
            assignment_cost = [] # création d'un tableau qui stockera les tableaux de coûts d'affectation aux entrepôts de chaque client
            for j in range(nb_customers): # pour chaque ligne contenant les informations sur les clients
                line = file.readline()  # lit la ligne suivante
                demand.append(int(line.split(' ')[0]))
                cost =[] # création du tableau des coûts d'affectation du client aux entrepôts
                line = file.readline()  # lit la ligne suivante
                lineTab = line.split(' ')  # sépare les éléments de la ligne dans un tableau en utilisant l'espace comme séparateur
                for i in range(nb_warehouses):
                    cost.append(float(lineTab[i]))
                assignment_cost.append(cost)
        # Affichage des informations lues
        print("Nombre d'entrepôts = ", nb_warehouses)
        print("Capacité des entrepôts = ", capacity)
        print("Coût d'ouverture des entrepôts = ", opening_cost)
        print("Nombre de clients = ", nb_customers)
        print("Demande des clients = ", demand)
        #Stockage dans l'objet
        self.nb_warehouses=nb_warehouses 
        self.nb_customers=nb_customers 
        self.capacity=capacity 
        self.opening_cost=opening_cost 
        self.demand=demand 
        self.assignment_cost=assignment_cost 
            
# Import du paquet PythonMIP et de toutes ses fonctionnalités
from mip import *
import time 

def solve(data, instanceName, solutionFolder):
    # Création du modèle vide 
    model = Model(name = "CWFL", sense = mip.MINIMIZE, solver_name="CBC")

    # Création des variables z et y
    z = [model.add_var(name="z(" + str(i) + ")", var_type=BINARY) for i in range(data.nb_warehouses)]
    y = [[model.add_var(name="y(" + str(j) + "," + str(i) + ")", lb=0, ub= 1, var_type=CONTINUOUS) for i in range(data.nb_warehouses)] for j in range(data.nb_customers)]

    # Ajout de la fonction objectif au modèle
    model += (xsum(data.opening_cost[i] * z[i] for i in range(data.nb_warehouses))+xsum(data.assignment_cost[j][i]*y[j][i] for j in range(data.nb_customers) for i in range(data.nb_warehouses)) )
    
    # Ajout des contraintes au modèle
    for j in range(data.nb_customers):  
        model += (xsum([y[j][i] for i in range(data.nb_warehouses)]) == 1)  # Contraintes (2)

    for i in range(data.nb_warehouses):  
        model += (xsum([data.demand[j]*y[j][i] for j in range(data.nb_customers)]) <= data.capacity[i]*z[i])  # Contraintes (3)
    
    # Ecrire le modèle (ATTENTION ici le modèle est très grand)
    #model.write("cwfl.lp") #à décommenter si vous le souhaitez

    # Limitation du nombre de processeurs
    model.threads = 1  
    # Lancement du chronomètre
    start = time.perf_counter()
    # Résolution du modèle
    status = model.optimize(max_seconds=120)  # temps limite = 120s
    # Arrêt du chronomètre et calcul du temps de résolution
    runtime = time.perf_counter() - start
    
    print("\n----------------------------------")
    if status == OptimizationStatus.OPTIMAL:
        print("Status de la résolution: OPTIMAL")
    elif status == OptimizationStatus.FEASIBLE:
        print("Status de la résolution: TEMPS LIMITE et SOLUTION REALISABLE CALCULEE")
    elif status == OptimizationStatus.NO_SOLUTION_FOUND:
        print("Status de la résolution: TEMPS LIMITE et AUCUNE SOLUTION CALCULEE")
    elif status == OptimizationStatus.INFEASIBLE or status == OptimizationStatus.INT_INFEASIBLE:
        print("Status de la résolution: IRREALISABLE")
    elif status == OptimizationStatus.UNBOUNDED:
        print("Status de la résolution: NON BORNE")
        
    print("Temps de résolution (s) : ", runtime)    
    print("----------------------------------")

    # Si le modèle a été résolu à l'optimalité ou si une solution a été trouvée dans le temps limite accordé
    if model.num_solutions>0:
        print("Valeur de la fonction objectif de la solution calculée : ", round(model.objective_value,2))  # ne pas oublier d'arrondir si le coût doit être entier
        print("Bilan;",instanceName,";",round(runtime,3),";",status,";",round(model.objective_value,2))
        solutionfileName = solutionFolder+"/solution_"+instanceName+".txt"
        print("Nom du fichier solution : ", solutionfileName)
        with open(solutionfileName, 'w') as file:  #ouvre le fichier, le ferme automatiquement à la fin et gère les exceptions
            file.write(str(round(model.objective_value,2))) #Il faut convertir les valeurs numériques en chaîne de caractères
            file.write("\n") #Je passe à la ligne suivante
            for i in range(data.nb_warehouses):
                if (z[i].x >= 0.5):
                    file.write(str(i)) 
                    file.write("\n") #Je passe à la ligne suivante
                    for j in range(data.nb_customers):
                        if (y[j][i].x >= 1e-4):
                            file.write(str(j)+" "+str(round(y[j][i].x * 100,2)))
                            file.write("\n") #Je passe à la ligne suivante
        
    else:
        print("Bilan;",instanceName,";",round(runtime,3),";",status,";Aucune solution retournée")
    print("----------------------------------")

     
# ----------------------------------------------------------------------------
# Méthode principale
# ---------------------------------------------------------------------------- 
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Le nombre de paramètre doit être au moins égal à 1" + sys.argv[1])
        print("usage : python cwfl.py nom_fichier_data")
        sys.exit()
    datafileName = sys.argv[1]
    print("Lecture du fichier de données : ", datafileName)
    instanceName = os.path.basename(sys.argv[1]).split('.')[0]
    print("Nom de l'instance : ", instanceName)
    solutionFolder = sys.argv[2]
    print("Nom du dossier solution : ", solutionFolder)
    data = Data(datafileName)
    solve(data,instanceName,solutionFolder)
        





