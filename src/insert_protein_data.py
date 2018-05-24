##################################################################################
##                                                                              ##
##  Module that insert the protein and peptide data from xls files              ##
##                                                                              ##
##################################################################################
import psycopg2
import sys
import os
import xlrd
import csv


try:
    conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
except:
    print("Error: It was not possible to connect to the database")
    sys.exit(1)

cur = conn.cursor()

## CSV
dirname = "../data/protein"
directory = os.fsencode(dirname)
for file in os.listdir(directory):
    filename = dirname + "/" + os.fsdecode(file)
    if not filename.endswith(".csv"): 
        continue;
    print("Processing: " + filename)

    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        
        species = str(file).split()[1][:-5]
        protein = ''
        toxclass = ''
        for row in reader:
            if row['Accession number'] != '' and row['Toxin Class'] != '':
                protein = row['Accession number']
                toxclass = row['Toxin Class']

                # New Protein 
                try:
                    cur.execute("INSERT INTO proteins(pr_acc, pr_toxclass) VALUES ('{0}', '{1}')\
                            ON CONFLICT DO NOTHING;".format(protein, toxclass))
                    cur.execute("INSERT INTO pr_sn(pr_acc, sn_sp) VALUES ('{0}', '{1}')\
                            ON CONFLICT DO NOTHING;".format(protein, species))
                except psycopg2.ProgrammingError as e:
                    print("Insert error")
                    print(e)
                    conn.rollback()
                    print("Rollback complete")

                conn.commit()

             # Add Peptide
            peptide = row['Peptides']
            try:
                cur.execute("INSERT INTO peptides(pep_seq) VALUES ('{0}')\
                        ON CONFLICT DO NOTHING;".format(peptide))
                cur.execute("INSERT INTO pep_sn(pep_seq, sn_sp) VALUES ('{0}', '{1}')\
                        ON CONFLICT DO NOTHING;".format(peptide, species))
                cur.execute("INSERT INTO pep_pr(pep_seq, pr_acc) VALUES ('{0}', '{1}') \
                        ON CONFLICT DO NOTHING;".format(peptide, protein))
            except psycopg2.ProgrammingError as e:
                print("Insert error")
                print(e)
                conn.rollback()
                print("Rollback complete")

            conn.commit()

cur.close()
conn.close()

