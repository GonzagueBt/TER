# Import du paquet PythonMIP et de toutes ses fonctionnalités
from mip import *
# Import du paquet time pour calculer le temps de résolution
import time 
import InstanceReader

def solve(data, L, K):
    print("Instance P"+data.Instance[0]+"-"+data.Instance[1]+ " with " + "L=" +str(L)+ " and K=" + str(K)+ " in progress...")
    # Création du modèle vide 
    model = Model(name = "MTZ-EAF", sense = mip.MAXIMIZE, solver_name="GUROBI")
    
    #### Création des variables y, u et t ####
    y=[]
    u=[]
    for i in range(data.id_max+1):
        y.append([])
        for j in range(data.id_max+1):
            y[i].append(model.add_var(name="y(" + str(i) + "," + str(j) + ")", var_type=BINARY))

    for k in range(data.id_max+1):
        u.append([])
        for i in range(data.id_max+1):
            u[k].append([])
            for j in range(data.id_max+1):
                u[k][i].append(model.add_var(name="u("+str(k) + "," + str(i) + "," + str(j)+ ")", var_type=BINARY))
    
    t = [model.add_var(name="t(" + str(i)  + ")", lb=0, ub=(L-1) , var_type=INTEGER) for i in range(data.id_max+1)]
    #On a fait la contrainte 21 : ti <= L-1 pour tout i de V    
    
    
    #### fonction objectif ####
    model += (xsum(data.cost[data.A[i][0]][data.A[i][1]] * y[data.A[i][0]][data.A[i][1]]  for i in range(len(data.A)))
             + xsum(data.cost[data.A[i][0]][data.A[i][1]] * u[k][data.A[i][0]][data.A[i][1]] for k in (data.P) for i in range(len(data.A)) ))
    
    
    #### Les contraintes ####
    
    # Contrainte 17
    for i in (data.P):
        for k in (data.P):
            model += (xsum(u[k][i][j] for j in data.allPatients[int(data.index[int(i)])])
                      - xsum(u[k][int(data.allDonorsInP[i][j])][i] for j in range(1,int(data.allDonorsInP[i][0])+1)) == 0 ) 
    
    #Contrainte 18
    for i in (data.P):
        model += (xsum(y[i][j] for j in data.allPatients[int(data.index[int(i)])])
                      <= xsum(y[int(data.allDonors[i][j])][i] for j in range(1,int(data.allDonors[i][0])+1))  ) 
        
    for i in (data.P):
        model += (xsum(u[k][i][j]  for k in (data.P) for j in data.allPatients[int(data.index[int(i)])])
                      + xsum(y[int(data.allDonors[i][j])][i] for j in range(1,int(data.allDonorsInP[i][0])+1)) <=1  )  
    
    #Contrainte 19
    for i in (data.P):
        model += (xsum(y[i][j] for j in data.allPatients[int(data.index[int(i)])])
                  + xsum(u[k][i][j]  for k in (data.P) for j in data.allPatients[int(data.index[int(i)])]) <= 1)
    
    #Contrainte 20
    for i in (data.N):
        model += (xsum(y[i][j] for j in data.allPatients[int(data.index[int(i)])]) <= 1 )
        
    #Contrainte 21
    for k in (data.P):
        model += (xsum(u[k][data.A[i][0]][data.A[i][1]] for i in range(len(data.A))) <= K)
        
    
    #Contrainte 23
    for i in (data.P):
        for k in (data.P):
            if(k>=i):
                break
            model += (xsum(u[k][i][j] for j in (data.allPatients[int(data.index[int(i)])]))
                      - xsum(u[k][k][j] for j in (data.allPatients[int(data.index[int(k)])])) <= 0)
            
    #Contrainte 24
    for i in (data.P):
        for k in (data.P):
            if(k<=i):
                continue
            model += (xsum(u[k][i][j] for j in (data.allPatients[int(data.index[int(i)])])) == 0)
        
    
    #CONTRAINTE NON EXISTENTE DANS LE MODELE mais semble nécessaire
    for i in (data.N):
        for k in (data.P): 
            model += (xsum(u[k][i][j] for j in (data.allPatients[int(data.index[int(i)])])) == 0)
            
            
    #Contrainte 25
    # !!! ne fonctionne pas  !!!
    for i in range(len(data.A)):
        model += (t[data.A[i][0]] - t[data.A[i][1]] #+ len(data.P) * y[data.A[i][1]][data.A[i][0]] 
                  + (len(data.P)+2) * y[data.A[i][0]][data.A[i][1]] <= len(data.P)+1)
            
    #Contrainte 26:
    for i in (data.N):
        model += (t[i]==0)
        
                  
    # Limitation du nombre de processeurs
    model.threads = 1  
    # Lancement du chronomètre
    start = time.perf_counter()
    # Résolution du modèle
    status = model.optimize(max_seconds=300)  # temps limite = 5min
    # Arrêt du chronomètre et calcul du temps de résolution
    runtime = time.perf_counter() - start
    
    solutionfileName = 'Solutions/P'+data.Instance[0]+'bis/L='+str(L)+'&K='+str(K)+'.txt'
    with open(solutionfileName, 'a') as file:  #ouvre le fichier, le ferme automatiquement à la fin et gère les exceptions  
        file.write("P"+data.Instance[0]+"-"+data.Instance[1]+"\n")
        file.write("----------------------------------\n")
        if status == OptimizationStatus.OPTIMAL:
            file.write("Status de la resolution: OPTIMAL")
        elif status == OptimizationStatus.FEASIBLE:
            file.write("Status de la resolution: TEMPS LIMITE et SOLUTION REALISABLE CALCULEE")
        elif status == OptimizationStatus.NO_SOLUTION_FOUND:
            file.write("Status de la resolution: TEMPS LIMITE et AUCUNE SOLUTION CALCULEE")
        elif status == OptimizationStatus.INFEASIBLE or status == OptimizationStatus.INT_INFEASIBLE:
            file.write("Status de la resolution: IRREALISABLE")
        elif status == OptimizationStatus.UNBOUNDED:
            file.write("Status de la resolution: NON BORNE")
        file.write("\n")
        file.write("Temps de resolution (s) : "+ str(runtime)+ "\n")    
        file.write("----------------------------------\n")

        # Si le modèle a été résolu à l'optimalité ou si une solution a été trouvée dans le temps limite accordé
        if model.num_solutions>0:
            file.write("Solution calculee \n")
            file.write("-> Valeur de la fonction objectif de la solution calculee : " + str(model.objective_value) + "\n")  # ne pas oublier d'arrondir si le coût doit être entier
            file.write("-> Meilleure borne superieure sur la valeur de la fonction objectif = "+ str(model.objective_bound)+ "\n")
            file.write("-> Distance : " + str(round(model.gap*100,2)) + "%\n")
            file.write("----------------------------------\n")
            for i in range(data.id_max+1):
                for j in range(data.id_max+1):
                    if(y[i][j].x>0.5):
                        file.write("(chemin) le donneur " + str(i) + " donne son rein au patient " + str(j) + " en position " + str(round(t[i].x)) +"\n")
            for k in range(data.id_max+1):
                for i in range(data.id_max+1):
                    for j in range(data.id_max+1):
                        if(u[k][i][j].x>0.5):
                            file.write("(cycle) le donneur " + str(i) + " donne son rein au patient " + str(j) + " dans le cycle " + str(k) +"\n")
            donneur=0
            for i in (data.V):
                test=0 
                for j in (data.allPatients[int(data.index[int(i)])]):
                    if(y[i][j].x>0.5):
                        test=1
                for k in range (data.id_max+1):       
                    for j in (data.allPatients[int(data.index[int(i)])]):
                        if(u[k][i][j].x>0.5):
                            test=1
                if(test==0):
                    donneur=donneur+1
            file.write(str(donneur)+" donneurs ne donnent pas leur rein\n")
            patient=0
            for i in (data.P):
                test=0 
                for j in range(1,int(data.allDonorsInP[i][0])+1):
                    if(y[int(data.allDonorsInP[i][j])][i].x>0.5):
                        test=1
                for k in range (data.id_max+1):       
                    for j in range(1,int(data.allDonorsInP[i][0])+1):
                        if(u[k][int(data.allDonorsInP[i][j])][i].x>0.5):
                            test=1
                if(test==0):
                    patient=patient+1
            file.write(str(patient) + " patients n'ont pas de donneur\n")
            file.write("--------------------------------------------------------------------\n")
            file.write("\n")
            
    solutionfileName = 'Solutions/P'+data.Instance[0]+'bis/Bilan-N'+data.Instance[1]+'.txt'
    with open(solutionfileName, 'a') as file:  #ouvre le fichier, le ferme automatiquement à la fin et gère les exceptions
        file.write("L="+str(L)+" et K="+str(K)+"\n")
        file.write("----------------------------------\n")
        if status == OptimizationStatus.OPTIMAL:
            file.write("Status de la resolution: OPTIMAL")
        elif status == OptimizationStatus.FEASIBLE:
            file.write("Status de la resolution: TEMPS LIMITE et SOLUTION REALISABLE CALCULEE")
        elif status == OptimizationStatus.NO_SOLUTION_FOUND:
            file.write("Status de la resolution: TEMPS LIMITE et AUCUNE SOLUTION CALCULEE")
        elif status == OptimizationStatus.INFEASIBLE or status == OptimizationStatus.INT_INFEASIBLE:
            file.write("Status de la resolution: IRREALISABLE")
        elif status == OptimizationStatus.UNBOUNDED:
            file.write("Status de la resolution: NON BORNE")
        file.write("\n")
        file.write("Temps de resolution (s) : "+ str(runtime)+"\n")    
        file.write("----------------------------------\n")

        # Si le modèle a été résolu à l'optimalité ou si une solution a été trouvée dans le temps limite accordé
        if model.num_solutions>0:
            file.write("Solution calculee \n")
            file.write("-> Valeur de la fonction objectif de la solution calculee : " + str(model.objective_value) + "\n")  # ne pas oublier d'arrondir si le coût doit être entier
            file.write("-> Meilleure borne superieure sur la valeur de la fonction objectif = "+ str(model.objective_bound)+ "\n")
            file.write("-> Distance : " + str(round(model.gap*100,2)) + "%\n")
            file.write("--------------------------------------------------------------------\n")
            file.write("\n")