"""Se charge de la gestion des opérations sur les mangas"""
import os, pathlib, zipfile, mangaManagement.variables as variables
from fpdf import FPDF
from PIL import Image

"""Returns the list of manga to convert and additional data"""
def getMangaUnconvertedList(scanPathList, imagesExtension):
    mangaList = []
    print(getHeader("Liste(s) de(s) manga(s):\n"))
    for scanPath in scanPathList:
        for name in os.listdir(scanPath):
            if os.path.exists(scanPath + name + "/" + imagesExtension): #if the images folder exist
                if (len(os.listdir(scanPath + name + "/" + imagesExtension)) != 0):  # Si le manga contient des images à convertir
                    mangaList.append(
                        [
                            name,   #The manga name
                            "{0}{1}/".format(scanPath, name),   #The manga chapters directory path
                        ]
                    )
                    print(getBold(str(len(mangaList)) + "-" + mangaList[-1][0]))
    return mangaList

"""Renvoie la liste récursive des chemins de tout les fichiers d'un dossier en fonction ou non d'une extension"""
def getPathTreeList(filesPathList, extensionList=["*"]):
    filesList = []
    for filesPath in filesPathList:
        for extension in extensionList:
            for fileName in sorted(os.listdir(filesPath)):
                if(os.path.isfile(filesPath + fileName)):   #Si on a un fichier on ajoute dans la liste
                    if(extension == "*"):
                        filesList.append(filesPath + fileName)
                    elif(strEndBy(fileName, extension)):
                        filesList.append(filesPath + fileName)
                elif(os.path.isdir(filesPath + fileName)):  #Si on a un dossier on le parcours pour ajouter ses fichiers
                    for temp in getPathTreeList([filesPath + fileName + "/"], extension):
                        filesList.append(temp)
    return filesList

def convertToCbz(picturesPath, toCovertedFilePath):
    zipFile = zipfile.ZipFile(toCovertedFilePath, mode='w')
    try:
        for image in getPathTreeList([picturesPath]):
            imageCbzPath = (picturesPath.split("/")[-2]) + "/" + (image.split(picturesPath))[1]
            zipFile.write(image, arcname=(imageCbzPath))
            print(getOkGreen(imageCbzPath+" Cbz=> "+toCovertedFilePath))
    finally:
        zipFile.close()

def decompressCbz(convertedFilePath, mangaChapsPath, mangaName):
    with zipfile.ZipFile(convertedFilePath, "r") as zipeFile:
        print(getOkGreen(convertedFilePath+ " dCbz => " +mangaChapsPath))
        zipeFile.extractall(mangaChapsPath)

def convertToCbr(picturesPath, toCovertedFilePath):
    zipFile = zipfile.ZipFile(toCovertedFilePath, mode='w')
    try:
        for image in getPathTreeList([picturesPath]):
            imageCbzPath = (picturesPath.split("/")[-2]) + "/" + (image.split(picturesPath))[1]
            zipFile.write(image, arcname=(imageCbzPath))
            print(getOkGreen(imageCbzPath+" Cbr=> "+toCovertedFilePath))
    finally:
        zipFile.close()

def decompressCbr(convertedFilePath, mangaChapsPath, mangaName):
    with zipfile.ZipFile(convertedFilePath, "r") as zipeFile:
        print(getOkGreen(convertedFilePath+ " dCbr => " +mangaChapsPath))
        zipeFile.extractall(mangaChapsPath)

def convertToPdf(picturesPath, toCovertedFilePath):
    imagePathList, convertedImageObjectList = getPathTreeList([picturesPath]), []
    
    convertedPrec = picturesPath.split("/")[-2] + "/"

    cover = (eval("Image.open(r'"+imagePathList[0]+"')")).convert('RGB')    #on converti la première page
    print(getOkGreen(( convertedPrec + (imagePathList[0]).split("/")[-1] )+" Pdf=> "+toCovertedFilePath))

    for count in range(1, len(imagePathList)):
        convertedImageObjectList.append((eval("Image.open(r'"+imagePathList[count]+"')")).convert('RGB'))   #convesion des page en pdf
        print(getOkGreen( convertedPrec + ((imagePathList[count]).split("/"))[-1] +" Pdf=> "+toCovertedFilePath))

    eval("cover.save(r'"+ toCovertedFilePath +"', save_all=True, append_images=convertedImageObjectList)")  #on crée le pdf

def decompressPdf(convertedFilePath, mangaChapsPath, mangaName):
    with open(convertedFilePath, "rb") as file:
        pdf = file.read()

    mangaChapName = strWithoutChain((((convertedFilePath.split("/"))[-1]).split(".pdf"))[0], mangaName+"_")
    mangaChapName = strWithoutChain((((convertedFilePath.split("/"))[-1]).split(".pdf"))[0], mangaName+"_")
    creatDir(mangaChapsPath+mangaChapName)

    startmark = b"\xff\xd8"
    startfix = 0
    endmark = b"\xff\xd9"
    endfix = 2
    i = 0

    njpg = 0
    print(getOkGreen(convertedFilePath+" dPdf=> "+mangaChapsPath))
    while True:
        istream = pdf.find(b"stream", i)
        if istream < 0:
            break
        istart = pdf.find(startmark, istream, istream + 20)
        if istart < 0:
            i = istream + 20
            continue
        iend = pdf.find(b"endstream", istart)
        if iend < 0:
            raise Exception("Didn't find end of stream!")
        iend = pdf.find(endmark, iend - 20)
        if iend < 0:
            raise Exception("Didn't find end of JPG!")

        istart += startfix
        iend += endfix
        jpg = pdf[istart:iend]
        goodNjpg = getNamePatternOrder(str(njpg)+".jpg", variables.nomberNomber)
        with open(mangaChapsPath+mangaChapName+"/Chap"+mangaChapName+"_"+goodNjpg, "wb") as jpgfile:
            jpgfile.write(jpg)

        njpg += 1
        i = iend

# def convertToPdf2(picturesPath, toCovertedFilePath):
#     imagePathList = getPathTreeList([picturesPath])
#     cover = Image.open(imagePathList[0])
    
#     pdf = FPDF(unit = "pt", format = cover.size)
#     for page in imagePathList:
#         pdf.add_page()
#         pdf.image(page, 0, 0)
#     pdf.output(toCovertedFilePath, "F")


"""Retourne le format de conversion choisi par l'utilisateur"""
def inputConvertTypeList(mangaFormats=["Cbz"], message="Quel sont les formats de conversion?(séparé par un espace):"):
    print(getHeader("Liste des choix:"))
    while(True):
        status, formatList = True, []
        for comp in range(0, len(mangaFormats)):
            print(str(comp+1)+"-"+mangaFormats[comp].capitalize())

        allRep = input(getOkBlue(message))
        
        for rep in allRep.split(" "):
            rep = int(rep)
            if(rep < 1 or rep > len(mangaFormats)):
                status = False
            else:
                formatList.append(mangaFormats[rep-1].capitalize())
        if(status):
            break
        else:
            formatList = []
    return formatList

"""Renvoie intéligement la liste des manga à traiter"""
def inputMangaNumList(mangaList):
    while True:  # Boucle de vérification des données entrantes
        mangaNumList, errors = (
            input(
                getOkBlue(
                    "\nEntrez le(s) numéro(s) de manga(s) à convertir (séparé par des espaces), ou * pour tout:"
                )
            ).split(" "),
            [],
        )

        if (
            len(mangaNumList) == 1 and mangaNumList[0] == "*"
        ):  # Pour compiler tous les dossiers
            mangaNumList = []
            for i in range(0, len(mangaList)):
                mangaNumList.append(i + 1)

        for manga_num in mangaNumList:  # Gestion des erreurs
            try:
                manga_num = int(manga_num) - 1
                if manga_num < 0 or manga_num > len(mangaList) - 1:
                    errors.append(manga_num)
                    print(
                        getFail(
                            "Veuillez entrer des nombres compris entre 1 et "
                            + str(len(mangaList))
                            + "\n"
                        )
                    )
            except TypeError:
                errors.append(manga_num)
                print(
                    getFail(
                        "Veuillez entrer des entiers compris entre 1 et "
                        + str(len(mangaList))
                        + "\n"
                    )
                )
            except ValueError:
                errors.append(manga_num)
                print(
                    getFail(
                        "Veuillez entrer des entiers compris entre 1 et "
                        + str(len(mangaList))
                        + "\n"
                    )
                )
        if len(errors) == 0:
            break
    return mangaNumList

"""Suprimme intéligement et en fonction de la réponse de l'utilisateur, les images d'un dossier de manga"""
def rmMangasImages(mangaList, mangaNumList, imagesExtension="Jpg"):
    if len(mangaNumList) > 1:
        rep = input(getWarning("Voulez vous supprimer des images?(o/n):"))
    else:
        rep = "o"
    if rep == "o":
        for mangaNum in mangaNumList:  # Boucle de gestion des images après compression
            mangaNum = int(mangaNum) - 1
            name, MangaPath,= mangaList[mangaNum]  # Definition des variables après lecture des informations
            imagePath = MangaPath+imagesExtension+"/"
            
            # Gestion des images après convertion #BYMawena
            rep = input(getWarning("Suprimer les images de {0} ?(o/n):".format(mangaList[mangaNum][0])))
            if rep == "o":
                os.system("rm -r '{0}'*".format(imagePath))
                print(getWarning("Images de {0} suprimées".format(mangaList[mangaNum][0])))

"""Demande l'autorisation de suprimer des fichiers avec une certaine extension d'un dossier en fonction de la réponse de l'utilisateur"""
def rmItems(Path, extention):
    rep = input(
        getWarning(
            'Suprimer les fichiers de {0} ayant l\'extention "{1}"?(o/n)'.format(
                Path, extention
            )
        )
    )
    if rep == "o":
        os.system("rm -r {0}*.pdf".format(Path, extention))
        print(
            getWarning(
                "Les fichiers {1} du dossier {0} ont été suprimées".format(
                    Path, extention
                )
            )
        )

"""Créée un dossier si besoin en le spécifiant à l'utilisateur"""
def creatDir(dirPath):
    if os.path.exists(dirPath) == False:
        print(getWarning("Creation du dossier: [" + dirPath + "]"))
        os.makedirs(dirPath)

"""vérifie si un des mots d'un liste est présent dans un mot principale"""
def containsListWords(principal, wordList):
    principal = principal.upper()
    for word in wordList:
        if principal.__contains__(word.upper()):
            return True
    return False

"""Renvoie un dictionnaire en fonction d'un fichier"""
def readByLineList(directoryListFilePathList):
    fileText = ""
    for directoryListFilePath in directoryListFilePathList:
        with open(directoryListFilePath, "r") as file:
            fileText = fileText + file.read()
    return fileText.split("\n")

"""Renvoie le dossier contenant l'executable"""
def getExeDirectoryPath():
    return str(pathlib.Path(__file__).parent) + "/"

"""Renvoie le nom du fichier modifier en fonction d'une taille de nom prédéfini"""
def getNamePatternOrder(fileName, nomberNomber):
    fileName, extension = (fileName.split("."))
    for temp in range(0, nomberNomber - (len(fileName))):
        fileName = "0" + fileName
    return fileName + "." + extension  #On crée le chemin de sauvegarde de l'image

"""Renome les fichiers d'un dossier en fonction d'une taille de nom prédéfini'"""
def renameByOrderPatternOne(directoryPath, nomberNomber, extension="*"):
    for fileName in os.listdir(directoryPath):
        if(os.path.isfile(directoryPath+fileName) and (strEndBy(fileName, extension) or extension == "*")):
            newFileName = getNamePatternOrder(fileName, nomberNomber)
            if(fileName != newFileName):    #Si le fichier n'était pas conformément nommé
                os.rename(directoryPath+fileName, directoryPath+newFileName)
                print(getWarning("[" + directoryPath+fileName + "] => [" + directoryPath+newFileName + "]"))

"""Vérifie si une chaîne de caractère se termine par une autre sous-chaîne"""
def strEndBy(chain, endChain):
    return ((chain[-1 * len(endChain):-1]+chain[-1]) == endChain)

def strStartByChain(chain, startChain):
    return (chain[0:len(startChain)] == startChain)

def strWithoutChain(chain, toDeleteChain):
    return chain.replace(toDeleteChain, "")

def getHeader(temp):
    return "\033[95m" + temp + "\033[0m"

def getOkBlue(temp):
    return "\033[94m" + temp + "\033[0m"

def getOkGreen(temp):
    return "\033[92m" + temp + "\033[0m"

def getWarning(temp):
    return "\033[93m" + temp + "\033[0m"

def getFail(temp):
    return "\033[91m" + temp + "\033[0m"

def getBold(temp):
    return "\033[1m" + temp + "\033[0m"

def getUnderline(temp):
    return "\033[4m" + temp + "\033[0m"