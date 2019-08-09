#!/usr/bin/python3
import os,hashlib,stat,argparse
#BASE= os.environ['HOME'] +'/dev'
# We work in the current directory
BASE=os.getcwd()
# Intialize some dictionnaries. Variables name are in french for the moment
taille={}
empreinte={}
# Do not deal with files smaller then MinSize
MinSize=8192
compteur=0
MaxChaineLength=0
TailleTotale=0
# Global behavior. Can be changed on CLI
DryRun=False
LinkType='Soft'

parser = argparse.ArgumentParser(description='Find duplicated files, and replace those with links')
parser.add_argument("--dryrun", action='store_true', help="If set, do not modify anything")
parser.add_argument("--hard", action='store_true', help="If set, Creates Hard links instead of soft links")

args = parser.parse_args()
if args.dryrun:
    print("Dry Run")
    DryRun=True

if args.hard:
        print("Hard Links")
        LinkType=True

def DeleteFile(filename):
        ## If file exists, delete it ##
        if os.path.isfile(filename):
                os.remove(filename)
                if os.path.isfile(filename):
                        return False
                else:
                        return True
        else:    ## Show an error ##
                print("Error: %s file not found" % filename)

def is_hard_link(filename, other):
        s1 = os.stat(filename)
        s2 = os.stat(other)
        return (s1[stat.ST_INO], s1[stat.ST_DEV]) == (s2[stat.ST_INO], s2[stat.ST_DEV])

def sha256sum(filename):
        h  = hashlib.sha256()
        b  = bytearray(128*1024)
        mv = memoryview(b)
        with open(filename, 'rb', buffering=0) as f:
                for n in iter(lambda : f.readinto(mv), 0):
                        h.update(mv[:n])
                return h.hexdigest()

def md5sum(filename):
        with open(filename, mode='rb') as f:
                d = hashlib.md5()
                while True:
                        buf = f.read(4096) # 128 is smaller than the typical filesystem block
                        if not buf:
                                break
                        d.update(buf)
                return d.hexdigest()

def getKeysByValue(dictOfElements, valueToFind):
        listOfKeys = list()
        listOfItems = dictOfElements.items()
        for item  in listOfItems:
                if item[1] == valueToFind:
                        listOfKeys.append(item[0])
        return  listOfKeys

for root, repertoires, fichiers in os.walk(BASE):
        fichiers = [f for f in fichiers if not f[0] == '.']
        repertoires[:] = [d for d in repertoires if not d[0] == '.']
        for fichier in fichiers:
                chaine=root+'/'+fichier
                if os.path.isfile(chaine):
                        tailleFichier=os.path.getsize(chaine)
                        TailleTotale+=tailleFichier
                        if not os.path.islink(chaine) and tailleFichier > MinSize:
                                compteur+=1
                                Affichage=str(compteur)+" "+chaine
                                if len(Affichage)>MaxChaineLength:
                                        MaxChaineLength=len(Affichage)
                                print(" "*MaxChaineLength,end='')
                                print("\b"*MaxChaineLength,end='',flush=True)
                                print(Affichage,end='',flush=True)
                                print("\b"*len(Affichage),end='',flush=True)
                                taille[chaine]=tailleFichier
                                
                        # elif os.path.islink(root+'/'+fichier):
                        #         print(root+'/'+fichier+' is a link')
                        # else:
                        #         print(root+'/'+fichier+' has a size of 0')

print(" "*MaxChaineLength,end='')
print("\b"*MaxChaineLength,end='',flush=True)
print("Number of files to compare :"+str(compteur),end='\n')

SameSizeCount=len(set(taille.values()))
print(str(compteur-SameSizeCount) + ' files out of ' + str(compteur) + ' have the same size',end='\n')
for x in sorted(set(taille.values())):
        MemeTaille=list()
        MemeTaille=getKeysByValue(taille,x)
        if len(MemeTaille) >1:
                for fichier in MemeTaille:
                        #empreinte[fichier]=str(sha256sum(fichier))+'.'+str(MemeTaille)
                        #Lempreinte=str(md5sum(fichier))+'finmd5'+str(x)
                        Lempreinte=str(md5sum(fichier))
                        empreinte[fichier]=Lempreinte
                        #print(fichier+': '+Lempreinte,end='\n')

SavedBytes=0
RemovedFileCount=0
HashesCount=len(set(empreinte.values()))
print(str(HashesCount) + ' hashes ' + str(compteur) + ' to analyze',end='\n')
for x in set(empreinte.values()):
        MemeEmpreinte=list()
        MemeEmpreinte=getKeysByValue(empreinte,x)
        if len(MemeEmpreinte) >1:
                premier=MemeEmpreinte[0]
                print('\nFichiers identiques au fichier '+premier,end='\n')
                for y in range(1,len(MemeEmpreinte)):
                        if not is_hard_link(premier,MemeEmpreinte[y]):
                                #print('\t'+MemeEmpreinte[y],end='\n')
                                SavedBytes+=taille[premier]
                                RemovedFileCount+=1
                                if not DryRun:
                                        print("Remove and link "+MemeEmpreinte[y]+" to "+premier)
                                        if DeleteFile(MemeEmpreinte[y]):
                                                if LinkType=='Soft':
                                                        os.symlink(premier,MemeEmpreinte[y])
                                                else:
                                                        os.link(premier,MemeEmpreinte[y])
                                        else:
                                                print("!!! Error. File "+MemeEmpreinte[y]+" could not be removed !",end='\n')
                                else:
                                        print("Dry Run. Duplicated File :"+MemeEmpreinte[y]+" not removed",end='\n')
                        else:
                                print("\tLien vers le même fichier"+MemeEmpreinte[y])

print("Removed Files Count: "+str(RemovedFileCount),end='\n')
print("SavedBytes: "+str(SavedBytes/1024/1024)+" Mo",end='\n')
print("\tAll files size: "+str(TailleTotale/1024/1024)+ " Mo",end='\n')