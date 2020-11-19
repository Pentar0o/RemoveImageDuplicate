#-*- coding: utf-8 -*-

import os
import glob
import sys
import time

import numpy as np
from PIL import Image
from SSIM_PIL import compare_ssim

def mse(Image1, Image2):
	err = np.sum((Image1.astype("float") - Image2.astype("float")) ** 2)
	err /= float(Image1.shape[0] * Image1.shape[1])
	
	#Plus le MSE est petit et plus les images sont similaires

	return err

def CompareImage(image1, image2, tabfile2keep, tabfile2delete):
	Image1 = Image.open(image1)
	Image2 = Image.open(image2)

	w1, h1 = Image1.size
	w2, h2 = Image2.size

	if w1>w2 :
		w = w2
		h = h2
		size = (w,h)
		Image1 = Image1.resize(size)

	else :
		w = w1
		h = h1
		size = (w,h)
		Image2 = Image2.resize(size)

	#print("Taille Image 1 : %s / %s"%(w1,h1))
	#print("Taille Image 2 : %s / %s"%(w2,h2))

	#Resize de l'image 2 à la taille de l'image 1 pour pouvoir les comparer
	size = (w,h)
	Image2 = Image2.resize(size)

	npaim1 = np.array(Image1)
	npaim2 = np.array(Image2)

	valuemse = mse(npaim1, npaim2)
	valuessim = compare_ssim(Image1, Image2)

	if (valuemse < 14000):
		#On parse pour enlever le répertoire du nom du fichier
		nomfichier1 = os.path.split(image1)
		nomfichier2 = os.path.split(image2)

		print("Comparaison des Images %s et %s" %(nomfichier1[1], nomfichier2[1]))
		print("MSE : %.2f" %valuemse)
		print("SSIM : %.2f" %valuessim)
		
		#On stock les images que l'on a traité et celles que l'on doit effacer
		if image1 not in tabfile2keep :
			if image1 not in tabfile2delete :
				tabfile2keep.append(image1)

		if image2 not in tabfile2delete :
			if image2 not in tabfile2keep :
				tabfile2delete.append(image2)


	return tabfile2keep, tabfile2delete


def main(repertoire):
	tabfile2delete = []
	tabfile2keep = []

	images_dir = os.path.join(repertoire)
	images = glob.glob(images_dir + "/*.jpg")
	
	for filename1 in images:
		for filename2 in images:
			if (filename1 != filename2):
				tabfile2keep, tabfile2delete = CompareImage(filename1, filename2, tabfile2keep, tabfile2delete)
	
	tabfile2keep.sort()
	tabfile2delete.sort()
	print("Fichier à Garder : %s" %tabfile2keep)
	print("Fichier à Delete : %s" %tabfile2delete)

	#On delete les images semblables
	for fichier in tabfile2delete:
		os.remove(fichier)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('USAGE: {} repertoire'.format(sys.argv[0]))
    else:
        t1 = time.time()
        main(sys.argv[1])
        print('Temps de Traitement : %d s'%(time.time()-t1))