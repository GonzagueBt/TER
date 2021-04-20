import xml.etree.ElementTree as ET
import numpy as np
import json

class Data():
    def __init__(self, P, num):
        root_node = ET.parse('Datas/InstanceP='+P+'/Instance'+num+'.xml').getroot()
        id_max=0
        
        #Calcul du nombre de pair, du nombre de donneur et de id_max
        for donor in root_node.findall('entry'):
            id=donor.attrib['donor_id']
            if(int(id) > int(id_max)):
                id_max=donor.attrib['donor_id']
        print('id max : ', id_max)
        print()
        #Autre méthode utilisant le fichier json (ne fonctionne pas puisque le nombre de donneur n'est pas égale à nombre 
            #de patientsx110%, comme cela devrait l'être puisque 10% de donneur altruiste)
        #with open('Datas/InstanceP='+str(50)+'/config.json') as json_data:
            #data_dict = json.load(json_data)
            #nb_paire=data_dict['patientsPerInstance']
            #nb_donor= int(nb_paire*1.12)
        
        count=0
        #initialisation tableau des couts des échanges, tableau des donneurs altruistes et des paires
        cost = np.zeros((int(id_max)+1,int(id_max)+1)) #double tableau avec le cout de chaque échange
        Index = np.zeros(int(id_max)+1) 
        altruist = [] # liste des donneurs altruistes
        pair = [] # liste des paires
        listExchange= [] # listes de tuples (les échanges entre paires et donneurs)
        listDonor=[] # liste des donneurs
        allPatient=[] #liste de listes des patients de chaque donneur
        allDonors=np.zeros((int(id_max)+1,int(int(P)*1.2)))
        allDonorsInP=np.zeros((int(id_max)+1,int(P)))
        
        #parcous du fichier html et remplissage des tableaux
        for donor in root_node.findall('entry'):
            #### Get the value from the attribute 'donor_id'###
            id = donor.attrib['donor_id']
            listDonor.append(int(id))            
            #print('id du donneur :',int(id))
            Index[int(id)]=count
            listpatients=[]
            if(donor.find('altruistic')==None):
                pair.append(int(id))
            else : 
                altruist.append(int(id))
            for exchange in donor.findall('matches/match'):
                patient=exchange.find('recipient')
                score=exchange.find('score')
                if(patient.text!=None):
                    cost[int(id)][int(patient.text)]=int(score.text)
                #print('patient : '+ patient.text +' avec un score de ' + score.text)
                arc= (int(id),int(patient.text))
                listpatients.append(int(patient.text))
                listExchange.append(arc)
                
                ind = allDonors[int(patient.text)][0]+1
                allDonors[int(patient.text)][int(ind)]=int(id)
                allDonors[int(patient.text)][0]=allDonors[int(patient.text)][0]+1
                
                if(donor.find('altruistic')==None):
                    indice = allDonorsInP[int(patient.text)][0]+1
                    allDonorsInP[int(patient.text)][int(indice)]=int(id)
                    allDonorsInP[int(patient.text)][0]=allDonorsInP[int(patient.text)][0]+1
                
            allPatient.append(listpatients)
            count=count+1
        
        self.id_max=int(id_max)
        self.cost=cost #un double tableau, le coût de l'arc u_ij se récupère en cost[i][j]
        self.N=altruist #une liste contenant tous les donneurs seuls (ensemble N)
        self.P=pair #une liste contenant toutes les paires (ensemble P)
        self.V=listDonor #une liste conetenant tous les donneurs (ensemble V)
        self.A=listExchange #une liste contenant tous les échanges (ensemble A : tous les arcs du graphe)
        self.allPatients=allPatient #une listes de liste : la liste des patients comaptible pour chaque donneur
        self.index=Index #pour un donneur i, index[i] retourne l'indice de i dans la liste allPatient : 
            # par exemple, pour le donneur id=12, la liste des patients compatible s'obtient pas allPatient[int(index[12])]
        self.allDonors=allDonors #un double tableau : pour un patient i, allDonors[i] est un tableau avec tous les donneurs
            #compatible avec 1. ATTENTION : allDonors[i][0]= le nombre de donneurs compatibles
        self.allDonorsInP=allDonorsInP # idem mais avec uniquement les donneurs en paires
        self.Instance=(P,num) #un tuple ou le premier élément contient le nombre de patient, et le 2ème le numéro de l'instance 
                                #(entre 0 et 5)