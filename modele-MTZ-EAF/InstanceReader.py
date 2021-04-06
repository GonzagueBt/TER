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
        #Autre méthode utilisant le fichier json (ne fonctionne puisque le nombre de donneurn'est pas égale à nombre de patients x 
            # x110%)
        #with open('Datas/InstanceP='+str(50)+'/config.json') as json_data:
            #data_dict = json.load(json_data)
            #nb_paire=data_dict['patientsPerInstance']
            #nb_donor= int(nb_paire*1.12)
        
        #initialisation tableau des couts des échanges, tableau des donneurs altruistes et des paires
        cost = np.zeros((int(id_max)+1,int(id_max)+1))
        altruist = []
        pair = []
        listExchange= []
        listDonor=[]
        
        #parcous du fichier html et remplissage des tableaux
        for donor in root_node.findall('entry'):
            #### Get the value from the attribute 'donor_id'###
            id = donor.attrib['donor_id']
            listDonor.append(id)
            print('id du donneur :',int(id))
            for exchange in donor.findall('matches/match'):
                patient=exchange.find('recipient')
                score=exchange.find('score')
                if(patient.text!=None):
                    cost[int(id)][int(patient.text)]=int(score.text)
                #print('patient : '+ patient.text +' avec un score de ' + score.text)
                arc= (int(id),int(patient.text))
                listExchange.append(arc)
                if(donor.find('altruistic')!=None):
                    pair.append(int(id))
                else : 
                    altruist.append(int(id))
                #print('le donneur est altruiste : ', altruist)
        #print("liste des échanges : ",listExchange)
        self.nb_pair=len(pair)
        self.nb_donor=len(listDonor)
        self.cost=cost #un double tableau, le coût de l'arc u_ij se récupère en cost[i][j]
        self.N=altruist #une liste contenant tous les donneurs seuls (ensemble N)
        self.P=pair #une liste contenant toutes les paires (ensemble P)
        self.V=listDonor #une liste conetenant tous les donneurs (ensemble V)
        self.A=listExchange #une liste contenant tous les échanges (ensemble a : tous les arcs du graphe)
        self.Instance=(P,num) #un tuple ou le premier élément contient le nombre de patient, et le 2ème le numéro de l'instance 
                                #(entre 0 et 5)