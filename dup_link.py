#!/usr/bin/python3
import os,hashlib,stat,argparse,time
from tqdm import tqdm
#BASE= os.environ['HOME'] +'/dev'
# We work in the current directory
BASE=os.getcwd()
# Intialize some dictionnaries. Variables name are in french for the moment
taille={}
footprint={}
# Do not deal with files smaller then MinSize
MinSize=8192
compteur=0
MaxChaineLength=0
TailleTotale=0
# Global behavior. Can be changed on CLI
DryRun=False
LinkType='Hard'
ReportHL=False

parser = argparse.ArgumentParser(description='Find duplicated files, and replace those with links')
parser.add_argument("--dryrun", action='store_true', help="If set, do not modify anything")
parser.add_argument("--soft", action='store_true', help="If set, Creates Soft links instead of Hard links")
parser.add_argument("--reporthl", action='store_true', help="If set, reports hard links for the same file")

args = parser.parse_args()
if args.dryrun:
    print("Dry Run")
    DryRun=True

if args.soft:
        print("Soft Links")
        LinkType='Soft'

if args.reporthl:
        print("Report Hard Links")
        ReportHL=True

def DeleteFile(filename):
        ## If file exists, delete it ##
        try:
                os.remove(filename)
                return True
        except:    ## Show an error ##
                return False

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

# Return a list of keys having value ValueToFind
def getKeysByValue(dictOfElements, valueToFind):
        # We initialize the list of keys
        listOfKeys = list()
        # Make a list of all the dictionnary values
        listOfItems = dictOfElements.items()
        # For each item, check if it is equal to the value to find.
        # If so, append it to the list of keys to returne
        for item  in listOfItems:
                if item[1] == valueToFind:
                        listOfKeys.append(item[0])
        return listOfKeys

# Lets walk through the subdirectories, and inventory all files
for root, repertoires, fichiers in tqdm(os.walk(BASE)):
        # We do not want hidden files and directories
        fichiers = [f for f in fichiers if not f[0] == '.']
        repertoires[:] = [d for d in repertoires if not d[0] == '.']
        for fichier in fichiers:
                chaine=root+'/'+fichier
                if os.path.isfile(chaine):
                        tailleFichier=os.path.getsize(chaine)
                        TailleTotale+=tailleFichier
                        # We do not care of small files, and symoblic links
                        if not os.path.islink(chaine) and tailleFichier > MinSize:
                                # Number of file to consider
                                compteur+=1
                                taille[chaine]=tailleFichier
                                        
print("\nLet's compute files'hashes")
for x in tqdm(sorted(set(taille.values()))):
        SameSize=list()
        SameSize=getKeysByValue(taille,x)
        if len(SameSize) >1:
                for fichier in SameSize:
                        footprint[fichier]=str(md5sum(fichier))

SavedBytes=0
RemovedFileCount=0
HashesCount=len(set(footprint.values()))
print(str(HashesCount) + ' hashes ' + str(compteur) + ' to analyze',end='\n')
for x in set(footprint.values()):
        SameFootPrint=()
        SameFootPrint=getKeysByValue(footprint,x)
        if len(SameFootPrint) >1:
                premier=SameFootPrint[0]
                print('\nFiles identical to the file '+premier,end='\n')
                for y in range(1,len(SameFootPrint)):
                        if not is_hard_link(premier,SameFootPrint[y]):
                                SavedBytes+=taille[premier]
                                RemovedFileCount+=1
                                if not DryRun:
                                        print("Remove and link "+SameFootPrint[y]+" to "+premier)
                                        if DeleteFile(SameFootPrint[y]):
                                                if LinkType=='Soft':
                                                        os.symlink(premier,SameFootPrint[y])
                                                else:
                                                        try:
                                                                os.link(premier,SameFootPrint[y])
                                                        except:
                                                                print("Create symlink instead of hard link")
                                                                os.symlink(premier,SameFootPrint[y])
                                        else:
                                                print("!!! Error. File "+SameFootPrint[y]+" could not be removed !",end='\n')
                                else:
                                        print("\tDry Run. No File Removed. Duplicated File :"+SameFootPrint[y],end='\n')
                        elif ReportHL:
                                print("\tHard link to the same file "+SameFootPrint[y])

print("Removed Files Count: "+str(RemovedFileCount),end='\n')
print("SavedBytes: "+str(format(SavedBytes/1024/1024,'.2f'))+" Mo",end='\n')
print("\tAll files size: "+str(format(TailleTotale/1024/1024,'.2f'))+ " Mo",end='\n')