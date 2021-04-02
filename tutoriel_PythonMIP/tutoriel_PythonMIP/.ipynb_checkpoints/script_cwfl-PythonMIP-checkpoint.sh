# usage : ./experimentationCWFL.sh repertoire_ou_sont_les_instances repertoire_ou_on_veut_stocker_les_resultats

echo Campagne experimentale CWFL
echo Repertoire de donnees $1
echo Repertoire de sortie $2

mkdir -p $2
echo `date` > $2/date.txt

for instance in `ls $1` ; do  # pour chaque instance dans le repertoire $1
    echo Résolution de l\'instance $instance
    python3 cwfl-PythonMIP.py $1/$instance $2 >> $2/log_${instance}.txt   # écriture de la sortie console dans un fichier log
done
grep Bilan $2/log* >> $2/bilan.csv  # les lignes contenant le mot "Bilan" seront concaténées dans le fichier bilan.csv