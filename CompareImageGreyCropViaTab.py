#-*- coding: utf-8 -*-

import os
import glob
import sys
import time

import numpy as np
from PIL import Image, ImageOps
from SSIM_PIL import compare_ssim

from progress.bar import Bar

def mse(Image1, Image2):
	err = np.sum((Image1.astype("float") - Image2.astype("float")) ** 2)
	err /= float(Image1.shape[0] * Image1.shape[1])
	
	#Plus le MSE est petit et plus les images sont similaires

	return err

def CompareImage(image1, image2, tabfile2keep, tabfile2delete):
    Image1 = Image.open(image1)
    Image2 = Image.open(image2)
    
    #On passe les images en gris pour voir si on compare mieux
    Image1 = ImageOps.grayscale(Image1)
    Image2 = ImageOps.grayscale(Image2)

    #### Voir le gain de temps en passant en gris une fois le resize ####

    w1, h1 = Image1.size
    w2, h2 = Image2.size

    if w1>w2 :
        w = w2
        #On calcul le ratio de l'image pour ne pas la déformer lors du resize
        ratio = w1/h1
        delta = round((w1/ratio) - h2)
        haut = round(delta/2)
        bas = haut + h2

        size = (w2,round(w2/ratio))
        Image1 = Image1.resize(size)


        (left, upper, right, lower) = (0, haut , w, bas)
        Image1 = Image1.crop((left, upper, right, lower))

    else :
        w = w1
        #On calcul le ratio de l'image pour ne pas la déformer lors du resize
        ratio = w2/h2
        delta = round((w2/ratio)-h1)
        haut = round(delta/2)
        bas = haut + h1 

        size = (w1,round(w1/ratio))
        Image2 = Image2.resize(size)

        (left, upper, right, lower) = (0, haut , w, bas)

        Image2 = Image2.crop((left, upper, right, lower))

    npaim1 = np.array(Image1)
    npaim2 = np.array(Image2)

    valuemse = mse(npaim1, npaim2)
    valuessim = compare_ssim(Image1, Image2)

    #On parse pour enlever le répertoire du nom du fichier
    # nomfichier1 = os.path.split(image1)
    # nomfichier2 = os.path.split(image2)	
    # print("Comparaison des Images %s et %s" %(nomfichier1[1], nomfichier2[1]))
    # print("Taille Image 1 : %s / %s"%(w1,h1))
    # print("Taille Image 2 : %s / %s"%(w2,h2))
    # print("MSE : %.2f" %valuemse)
    # print("SSIM : %.2f" %valuessim)


    if (valuemse < 2500 and valuessim > 0.25):

        if image2 not in tabfile2delete :
            if image2 not in tabfile2keep :
                tabfile2delete.append(image2)

	#On stock les images que l'on a traité et celles que l'on doit effacer
    if image1 not in tabfile2keep :
        if image1 not in tabfile2delete :
	        tabfile2keep.append(image1)
	
	


    return tabfile2keep, tabfile2delete


def main(repertoire):
    tabfile2delete = []
    tabfile2keep = []
    tabfile = []

    images_dir = os.path.join(repertoire)
    images = glob.glob(images_dir + "/*.jpg")

    #On load les noms des images dans un tableau
    for fichier in images:
        tabfile.append(fichier)
    tabfile.sort()

    bar = Bar('Traitement', max=(images.__len__()))
    
    for _ in range (images.__len__()) :
        filename1 = tabfile.pop()
        for filename2 in tabfile:
            tabfile2keep, tabfile2delete = CompareImage(filename1, filename2, tabfile2keep, tabfile2delete)
        bar.next()

    bar.finish()

    tabfile2keep.sort()
    tabfile2delete.sort()
    print("Fichier à Garder : %s" %len(tabfile2keep))
    print("Fichier à Delete : %s" %len(tabfile2delete))

	#On delete les images semblables
	#for fichier in tabfile2delete:
	#	os.remove(fichier)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('USAGE: {} repertoire'.format(sys.argv[0]))
    else:
        t1 = time.time()
        main(sys.argv[1])
        print('Temps de Traitement : %d s'%(time.time()-t1))