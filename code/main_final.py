#!/usr/bin/env python
# coding: utf-8

# In[1]:


from manevra_son import run_loop, StopProcessing,StopProcessing2
from threading import Thread
from renk_son import color_start
import time

def main_function(plaka_text, park_bool, park_numarası, plaka_varlık_bool):
    try:
        run_loop(plaka_text, park_bool, park_numarası)
        print(plaka_text)
        print(park_bool)
        print(park_numarası)

    except StopProcessing2:
        plaka_varlık_bool[0] = False
        print("Py-kontrol-plaka yok")


