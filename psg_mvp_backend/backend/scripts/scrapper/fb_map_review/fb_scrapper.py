"""
Selenium Facebook scrapper to scrape the review session.
Auth is not handled.

TODO: this is a script badly written by a freelancer

To run:
    1. change CHROME_DRIVER_PATH
    2. >> python run_all <path to your url input file>


"""
# -*- coding: utf-8 -*-
import time
import pandas as pd
from os import path
import os
from pathlib import Path
import json

from seleniumwire import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import traceback
import typer
import aiohttp, aiofiles, asyncio

# import grequests
import shutil # to save it locally

CHROME_DRIVER_PATH = "./chromedriver"
fb_page = "https://www.facebook.com/caixinbeauty/reviews/?ref=page_internal"

def testAsync():
    urls = ['https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/104053461_279931313415794_6315182741251005890_n.jpg?_nc_cat=108&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=iWV89kJUC9IAX9lTSns&_nc_ht=scontent-sjc3-1.xx&oh=00d0f5b09c51993148c601dc97a3b32a&oe=60F142DC', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/82000284_3257717590909545_6173756703335514112_n.jpg?_nc_cat=110&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=J4xA0GI9yDsAX8MqJdm&_nc_ht=scontent-sjc3-1.xx&oh=dd167b30da8201404e33f8313e3e7bb7&oe=60F12477', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/11219696_981906078548982_8537452104827127954_n.jpg?_nc_cat=110&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=yrmPMeeuaEwAX_BhkOA&_nc_ht=scontent-sjc3-1.xx&oh=c86d496908ca2794462251d2f2b54d68&oe=60F02CD3', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/194298870_6441398542544308_7688443416175900601_n.jpg?_nc_cat=106&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=1tL97AvM2tsAX9tuCHP&_nc_ht=scontent-sjc3-1.xx&oh=8288bc695b4b1352b60d2e9a92d3180e&oe=60EFFD39', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/48368400_2184297334935475_2625833560417763328_n.jpg?_nc_cat=100&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=rOY5MInKSVMAX9hWeoC&_nc_ht=scontent-sjc3-1.xx&oh=3e26608865bfcec06742c1747f8e3bbf&oe=60EFCFF0', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/176151019_4466549963358377_5919040944142775423_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=xrFvipgzj4QAX_-JCEo&_nc_ht=scontent-sjc3-1.xx&oh=e32a221cbba2a69d6a2dbbb1b67e30c7&oe=60F0DCE0', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/17155457_1433744556699280_2204289610230142261_n.jpg?_nc_cat=105&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=3ly_gf7d5ogAX89ElRr&_nc_oc=AQn4tq54Lv9t5u7uFQTHvauMKPYvL9bnXeanXZTW6T-xz1xj7pORezBxVztvJjbvkKc&_nc_ht=scontent-sjc3-1.xx&oh=6c98fb57429d3d66010bafbd3b222d06&oe=60EFB01B', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/52358921_551820212006156_8792800259760717824_n.jpg?_nc_cat=102&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=JjcLtomWdWcAX8dkY-Q&_nc_ht=scontent-sjc3-1.xx&oh=3671fa3b49472d93cc59f207fcbd7f72&oe=60F1556C', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/79681571_185338819307407_8004347128681857024_n.jpg?_nc_cat=105&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=GTSKvDvLxGEAX_MGa-6&_nc_ht=scontent-sjc3-1.xx&oh=36c2c3953ab6ebcddeda31200dd0a754&oe=60F150AA', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/10402771_234231500109307_272150264313100853_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=-vYbGRYAE1UAX8_ybwp&_nc_ht=scontent-sjc3-1.xx&oh=3cd858d12da9f328fab5a1826a3baba0&oe=60EFC044', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/15726797_1524130294269332_4927380412133653848_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=3rdB3WgBjwoAX_VkcCs&_nc_ht=scontent-sjc3-1.xx&oh=9e65abe39c6b49ded2f1138d39b0dc8e&oe=60F05BB2', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t31.18172-1/cp0/p50x50/15138465_1453956394633438_3083969429266449631_o.jpg?_nc_cat=103&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=DEdpJM4ZHsEAX-lRR24&_nc_ht=scontent-sjc3-1.xx&oh=f6c98ced543bdce52fbc32bc02bc9038&oe=60F1A0F8', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/1457671_10201839924217380_353032506_n.jpg?_nc_cat=111&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=B9hYApGMd4gAX-Lc5f9&_nc_ht=scontent-sjc3-1.xx&oh=791b606513661684e1abe17f0ea7fce7&oe=60F18D72', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/18057906_790360557789567_4245398828458650219_n.jpg?_nc_cat=110&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=gLERimJ08msAX9mzz-I&_nc_ht=scontent-sjc3-1.xx&oh=5bf928d0faec615d339408a78441b4cd&oe=60EFF0CD', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/83866448_2731329943629082_1895760171741741056_n.jpg?_nc_cat=100&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=ULZpNfdNfwQAX_rWUKn&_nc_ht=scontent-sjc3-1.xx&oh=e0624972c67063e6fb8d12839ae1160b&oe=60F07E42', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/30124358_1611628378907011_6165407209308364888_n.jpg?_nc_cat=106&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=QjyZdOBDnfUAX915XAy&_nc_ht=scontent-sjc3-1.xx&oh=64aece427d90908b0966fce44e465068&oe=60F19F8B', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/132702909_3717389791617528_3530042208303707266_n.jpg?_nc_cat=110&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=oxSgd2EkSSgAX83gKQ6&_nc_ht=scontent-sjc3-1.xx&oh=172f93dc40fd40d1a2a82d12211fe40c&oe=60F14FD2', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/52602827_2083170241758792_7712413498583547904_n.jpg?_nc_cat=107&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=nK8fziu5RM4AX-PkihI&_nc_ht=scontent-sjc3-1.xx&oh=1e4e66a5415e55dd54e94a288f54ca01&oe=60F08710', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/112915247_10213549395168811_412365431893954119_n.jpg?_nc_cat=105&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=7eBHO7yGPSYAX8alDYB&_nc_ht=scontent-sjc3-1.xx&oh=134077100248f0135ec1e2433df0913a&oe=60F10A10', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/69696220_107542037291329_578647569261920256_n.jpg?_nc_cat=108&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=375i7TFL5HUAX8iFUxW&_nc_ht=scontent-sjc3-1.xx&oh=a136154e7802427cc477d28df08a7aed&oe=60F156C2', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/91908175_2396516043942690_8637006759254294528_n.jpg?_nc_cat=106&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=2zQNXxdvjQ0AX-fYXVz&_nc_ht=scontent-sjc3-1.xx&oh=83a2d3f3213e71b1deb58affb4789f5e&oe=60F06667', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/83438760_2962184317137428_2475293152806699008_n.jpg?_nc_cat=107&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=NtGePvysl24AX_7mnir&_nc_oc=AQnjJZleSbq2fiLsTTEOklEELeVNQfveIGq9_dKMrSeYXbwZLz77w8sy9NLORzMmJeI&_nc_ht=scontent-sjc3-1.xx&oh=67fb847cda1ce97c137603b132c92878&oe=60F04A34', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/17862721_641289802748629_2316083382083026993_n.jpg?_nc_cat=108&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=H01rZRnCVbcAX-RaNIB&_nc_ht=scontent-sjc3-1.xx&oh=2657e85d4bf2092436e736d28a690702&oe=60F1A1BB', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/187967887_4250847174967722_2921636628442179622_n.jpg?_nc_cat=102&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=rWjCqidQ_i4AX8gn0jH&_nc_ht=scontent-sjc3-1.xx&oh=625ab52829c76ba0e12e213a91c93786&oe=60EFCC67', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/40108930_110641159886665_2421363322940030976_n.jpg?_nc_cat=106&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=4U_v5xpmj_YAX-lFakB&_nc_ht=scontent-sjc3-1.xx&oh=a3afed33d129fee206ab443600a1ce53&oe=60F06F60', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.30497-1/cp0/c15.0.50.50a/p50x50/84688533_170842440872810_7559275468982059008_n.jpg?_nc_cat=1&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=OHqm9hP0kPcAX-acd8o&_nc_ht=scontent-sjc3-1.xx&oh=9686eefcb4c1dc92f2e4b220ed371ff0&oe=60F19F1F', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/145898905_2778276949104936_7182179906992033904_n.jpg?_nc_cat=102&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=H7FGL58XOx8AX8SW_Dl&_nc_ht=scontent-sjc3-1.xx&oh=14adaf307eb9dfa69865426da0049174&oe=60F0FFEA', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/12418108_1121037291254982_4954090341054197411_n.jpg?_nc_cat=103&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=d6nybqaugK4AX8WfMou&_nc_ht=scontent-sjc3-1.xx&oh=21928efeb5d9c5a3aa95f77539b8cc7e&oe=60F0773A', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/162072326_4408499852499984_644024558873627543_n.jpg?_nc_cat=102&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=6TLL_6VcQXkAX_YKLqt&_nc_ht=scontent-sjc3-1.xx&oh=99755cef7b1dffd88580971fde74e4b1&oe=60F02CD6', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/133805029_3938215386198353_2167976130120804389_n.jpg?_nc_cat=107&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=GTzPQ3jX9g8AX9YVbOh&_nc_ht=scontent-sjc3-1.xx&oh=ed1bc7aa648bc8793f95c452a16b8f4c&oe=60F1960C', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/103052815_1620796044753326_2982227124253148166_n.jpg?_nc_cat=107&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=jJu19X-nmd0AX9IbnLN&_nc_ht=scontent-sjc3-1.xx&oh=96e3e96d421102a012f845872d33cbf8&oe=60F0125A', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t31.18172-1/cp0/p50x50/23593384_107657056678572_8474607271216228714_o.jpg?_nc_cat=109&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=R8xYLqmT_wkAX886hMi&_nc_ht=scontent-sjc3-1.xx&oh=9fd69ade6ec11f16f39feb05acf1f742&oe=60F0D8B4', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/28871803_1702193999831951_6591978546783059968_n.jpg?_nc_cat=103&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=EoG7-O8v2QUAX8tiorh&_nc_ht=scontent-sjc3-1.xx&oh=5a3547022909e4a8e77aca916fcc7ebc&oe=60F0FE02', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/31285955_1936772799668915_8481146527840993280_n.jpg?_nc_cat=105&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=bKwGclH4wo8AX-liat7&_nc_ht=scontent-sjc3-1.xx&oh=250579a86a07b5b504b38d301cf24121&oe=60EFF85E', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/91869952_2915676081805003_7609816350608850944_n.jpg?_nc_cat=103&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=OMfLBG7szhkAX86LAu5&_nc_ht=scontent-sjc3-1.xx&oh=6460aaac5ed1e2130b897039fd3132ad&oe=60F066EC', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/12651096_938181576219715_1258836313201426245_n.jpg?_nc_cat=109&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=YnTjY6WO_QgAX_l7p5w&_nc_ht=scontent-sjc3-1.xx&oh=9d0d31daa3c219a12fcbbc5ebcd6445f&oe=60F00C7B', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/93118294_3477090758973544_1676311437682671616_n.jpg?_nc_cat=110&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=RP6QgLRhJE4AX9MCdQJ&_nc_ht=scontent-sjc3-1.xx&oh=76275f84155d3e9c87cd65b289fb1c9d&oe=60F13FCF', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/70866408_1463557710466245_5381149870729986048_n.jpg?_nc_cat=111&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=J1tPK0rW734AX_715hI&_nc_ht=scontent-sjc3-1.xx&oh=15b6cff526192299a698fecdf330aca5&oe=60F17503', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/52661093_10156217689137333_583499692600459264_n.jpg?_nc_cat=108&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=TcQFsnpjttMAX8oPsib&_nc_ht=scontent-sjc3-1.xx&oh=d0450100c7a8913734e673c0470c0e09&oe=60F07096', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/132151530_2812173479039640_5870812483061705095_n.jpg?_nc_cat=109&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=v3lj840NU1kAX_njjgJ&_nc_ht=scontent-sjc3-1.xx&oh=529d70b87ad5ca90d9d13dcdefe3d093&oe=60EFF454', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/170729752_4320274641324046_6602483880704611329_n.jpg?_nc_cat=104&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=nKCyad0qVdIAX9JYxx9&_nc_ht=scontent-sjc3-1.xx&oh=5d113667ef01e5358a844728192a5925&oe=60EFEBB1', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/49395805_989140667946895_200564677686591488_n.jpg?_nc_cat=103&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=h1WTs7KUyusAX-B7zgB&_nc_ht=scontent-sjc3-1.xx&oh=fb475b80760151ec2809f173c2013074&oe=60F0E4A5', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/30124032_115721719279781_5662657089760133120_n.jpg?_nc_cat=105&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=U5JJdfwY284AX_NUM3S&_nc_ht=scontent-sjc3-1.xx&oh=c5ef445a8ce84b6d20ff285aaff8b86d&oe=60F0A403', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/181857834_4134295019986088_8145733902418460946_n.jpg?_nc_cat=108&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=p6mniPmEGQoAX9oOUzI&_nc_ht=scontent-sjc3-1.xx&oh=e59123bb5283073d1a3ac198e832f388&oe=60F05197', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/24177040_10209167893028821_4131157042532589119_n.jpg?_nc_cat=111&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=TPF01oVoJnEAX-ba26U&_nc_ht=scontent-sjc3-1.xx&oh=c9ec027ba373835149b5ef49eda1ef30&oe=60F17231', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/186036023_10215508791472628_2963303884786600941_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=B8vRS9kwxbMAX_dTCBR&_nc_ht=scontent-sjc3-1.xx&oh=f78659b740b7c5b313e2f8ee118b5dfb&oe=60F07603', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/195459001_4078195295597617_1568913564482240016_n.jpg?_nc_cat=102&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=NOQN1868_90AX9SghCE&_nc_ht=scontent-sjc3-1.xx&oh=899d98a0eff1f22e5c412d2604b58505&oe=60F19FEC', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/168267045_3000542266832427_2887511535437351746_n.jpg?_nc_cat=104&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=37-1BsB2aUgAX97vthG&_nc_ht=scontent-sjc3-1.xx&oh=254621df13057468d66e02b79c35565b&oe=60F1402C', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/205786583_10159370629014280_50294126767570085_n.jpg?_nc_cat=108&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=w7zXCHBzE3QAX95NcuT&_nc_ht=scontent-sjc3-1.xx&oh=5d2332036515177cfcad3e8d7963f9a4&oe=60EFFAF4', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/10570362_1093418920671940_6658545819989387222_n.jpg?_nc_cat=104&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=iR_AJEtIOFoAX_QnYbd&_nc_ht=scontent-sjc3-1.xx&oh=46c0123337d3a5b3c002e3776a350d2a&oe=60F085D6', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/28055819_2021945794490248_4800428049913691778_n.jpg?_nc_cat=108&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=-H-VfUmCOxgAX_5CTNw&_nc_ht=scontent-sjc3-1.xx&oh=0a05d443e5310c94b580703b7afc459a&oe=60F05A13', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/69542638_3000798866613345_532518984847720448_n.jpg?_nc_cat=100&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=jVA4sv02HqkAX-LNwKi&_nc_ht=scontent-sjc3-1.xx&oh=c8f515abc3d57a2d12022886bb0cbae9&oe=60F0B50D', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t31.18172-1/cp0/p50x50/13002443_1336889566326423_3071126566481640240_o.jpg?_nc_cat=102&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=q5j68HoYQroAX956NbF&_nc_ht=scontent-sjc3-1.xx&oh=155be816c8850c81b4ff6902d72395fe&oe=60EFDA7B', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/31958164_1919287091424435_7932616007992999936_n.jpg?_nc_cat=105&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=SrRasklDDpMAX_fnBtd&_nc_ht=scontent-sjc3-1.xx&oh=00b6e4b1a2450081d0950d95aa841978&oe=60F01388', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/33030774_1909828682390119_6143674988617531392_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=TkhcUYZ_xsEAX-uUUXd&_nc_ht=scontent-sjc3-1.xx&oh=bd0d817b68c58719d040d0d28d10a7d1&oe=60F11320', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/27654481_1721679257853305_6316925231247037522_n.jpg?_nc_cat=111&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=CjGQjL5WJjgAX9qL4ok&_nc_ht=scontent-sjc3-1.xx&oh=bbd22314263e2e10545c0dcbafb1c0bd&oe=60EFC042', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/136431493_3788650591155209_6128776794943588028_n.jpg?_nc_cat=107&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=ZF97ZF8zehsAX-6EFk3&_nc_ht=scontent-sjc3-1.xx&oh=95a8f7827dd9b058bb5f575107ac5406&oe=60F0EBA4', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t31.18172-1/cp0/p50x50/14138701_1062505173864016_8491155648084822126_o.jpg?_nc_cat=100&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=E9-JA6bJx_sAX-NH7WK&_nc_oc=AQk1zz5jf25R-wcUhKwi7-H4vgpOKEMne3Fb3EK3l75aQ4WGFr_QQQR8RSbPcQaUT_g&_nc_ht=scontent-sjc3-1.xx&oh=93aec8d9c9c9a7a2eeeaee5bb2def958&oe=60F115C1', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/183592365_3943175589051994_2088467820194833604_n.jpg?_nc_cat=103&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=FxF_PG8GfwcAX8z7VlZ&_nc_ht=scontent-sjc3-1.xx&oh=d921adac2d3eece0ca8a4098b76ffa88&oe=60F08EB6', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/c8.0.50.50a/p50x50/69880685_111455970233596_2904360617605332992_n.jpg?_nc_cat=110&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=w4M7G5FXqrMAX_t3o3U&_nc_ht=scontent-sjc3-1.xx&oh=34c96e48240f3b8b723838f0c13ac7f6&oe=60EFDC5E', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/208603567_10227575569843024_338060363350717368_n.jpg?_nc_cat=110&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=BOHVaZOqhssAX_c8uh2&_nc_ht=scontent-sjc3-1.xx&oh=d1828611a2a7ab7e035518c2f17152e8&oe=60F00C43', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/17309360_10208395331982712_2474073980863060322_n.jpg?_nc_cat=107&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=fXalVczCdpIAX9-VrFD&_nc_ht=scontent-sjc3-1.xx&oh=52545f9cc0a3d35ee4c93a16523f3185&oe=60F0FF52', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/61941822_3038279159522367_6628451348931149824_n.jpg?_nc_cat=111&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=_5jmDQtyWeEAX_FrlQy&_nc_ht=scontent-sjc3-1.xx&oh=f16984f01ee5e593bd25b7d366c5de4d&oe=60F1661E', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/93054141_3250514071634616_391213341038608384_n.jpg?_nc_cat=105&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=KtMPzgvQP80AX_dzr1l&_nc_ht=scontent-sjc3-1.xx&oh=9201a3ce85d80cefb4fa83f3a233a4a4&oe=60F0E748', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t31.18172-1/cp0/p50x50/14067856_1232089256813755_2103296462362113307_o.jpg?_nc_cat=104&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=wMNhuxHMoCUAX_NYKQ6&_nc_ht=scontent-sjc3-1.xx&oh=5520602f3f09f358ec21a98c55b62a1d&oe=60EFC68B', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/69829383_111097973603022_2712545728898531328_n.jpg?_nc_cat=105&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=HaX6qlVrzGsAX9rOMLe&_nc_ht=scontent-sjc3-1.xx&oh=b35a483fd0b1f67a20391532ed1b9b95&oe=60F12254', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/158717276_10159756608950809_351991827489149762_n.jpg?_nc_cat=104&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=9Qe8sUASPXoAX9QUilW&_nc_ht=scontent-sjc3-1.xx&oh=b108a384292f3f3589a809eddf06d46c&oe=60F04841', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/c87.234.612.612a/s50x50/187182492_4187188147994774_6344515139394828502_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=hEVlSwM-8ZMAX9yec71&_nc_ht=scontent-sjc3-1.xx&oh=6d91a8ce9ef9a634431001c1e7522d86&oe=60EFEE99', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/136673912_6074224862617784_1029534011683194367_n.jpg?_nc_cat=100&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=nV_0iZQrwUQAX_EAbfT&_nc_ht=scontent-sjc3-1.xx&oh=f0693e82a14fd07c6364caed01ffdb1c&oe=60F12C72', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/135781670_500685974246456_6259547409375333044_n.jpg?_nc_cat=103&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=vdofFEZZS3kAX9B3NKt&_nc_oc=AQndf4KUH2IIdzTmkLiNquZ2-OYhRwD1EqT8vXmkW-OD7NZiI9LtoEonN1fdwtM2bRs&_nc_ht=scontent-sjc3-1.xx&oh=ec00fcc8413d1cda2ce26398603ebd63&oe=60F0D06B', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.30497-1/cp0/c15.0.50.50a/p50x50/84688533_170842440872810_7559275468982059008_n.jpg?_nc_cat=1&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=OHqm9hP0kPcAX-acd8o&_nc_ht=scontent-sjc3-1.xx&oh=9686eefcb4c1dc92f2e4b220ed371ff0&oe=60F19F1F', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/170043669_1782769845229131_7855968095286868293_n.jpg?_nc_cat=106&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=6JcwhrCjDIcAX-M46IC&_nc_ht=scontent-sjc3-1.xx&oh=9cb8b3a4f90556ef70903a1fb0a164ee&oe=60F0846E', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/54800081_2264173570500604_76243885776437248_n.jpg?_nc_cat=109&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=Ed7I01Anv7oAX-yFkT8&_nc_ht=scontent-sjc3-1.xx&oh=9148ce0d6a20f12cefd12c1050d82aad&oe=60F081DB', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/119643759_2231964733614147_6386485779651037654_n.jpg?_nc_cat=108&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=g4pqnvhPG7sAX81g7JO&_nc_ht=scontent-sjc3-1.xx&oh=d44f38efa29067cad1a5d205e1ec1164&oe=60F00260', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t31.18172-1/cp0/c0.0.50.50a/p50x50/27982947_549615978744549_1045559608813376509_o.jpg?_nc_cat=100&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=qD_SSacFf18AX_zWnk9&_nc_ht=scontent-sjc3-1.xx&oh=1c2a19bb5bdd1c52ee336fae23e4fd40&oe=60EFE23E', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/131675410_4019837728035566_6789993687494270775_n.jpg?_nc_cat=106&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=Zl5P8gZ3U_EAX-YEAam&_nc_ht=scontent-sjc3-1.xx&oh=40cc8ddc93c197fe0b4d022ffce3815e&oe=60EFB6E8', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/120328473_10223913505255534_7052587646191638419_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=gIqpm09eQn8AX_eEgVC&_nc_ht=scontent-sjc3-1.xx&oh=6c275664b02307489d36f84bbaca6e86&oe=60F14616', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/11667362_10206900755828155_5026913002661239033_n.jpg?_nc_cat=100&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=oDyQ-LFOV3MAX-K0g5A&_nc_ht=scontent-sjc3-1.xx&oh=ec71f389868d61d6b83573bed13c6f6e&oe=60F0AAA2', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/108222640_10221871142595277_5978091830459214434_n.jpg?_nc_cat=110&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=RH30DP9xwwIAX8eElrZ&_nc_ht=scontent-sjc3-1.xx&oh=841edf5f905680b88e9bad9cb1763617&oe=60F10287', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/108222640_10221871142595277_5978091830459214434_n.jpg?_nc_cat=110&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=RH30DP9xwwIAX8eElrZ&_nc_ht=scontent-sjc3-1.xx&oh=841edf5f905680b88e9bad9cb1763617&oe=60F10287', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/12644867_10205743418325712_1722418737294607389_n.jpg?_nc_cat=109&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=ePbma-1nFMoAX_mN-tO&_nc_ht=scontent-sjc3-1.xx&oh=e05fed6d3655b776262f84dc285e6610&oe=60F0C914', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/69762049_10214519115478409_6611475701147107328_n.jpg?_nc_cat=105&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=QdTtPtI5roUAX__h-dD&_nc_ht=scontent-sjc3-1.xx&oh=af2a4c52c1b6f00b4ef6846d2018c79e&oe=60EFEC77', 'https://static.xx.fbcdn.net/rsrc.php/v3/y4/r/-PAXP-deijE.gif', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/179473247_10215999229892526_3692202751515028820_n.jpg?_nc_cat=111&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=s1Xi9l-80mgAX-PA-Mh&_nc_ht=scontent-sjc3-1.xx&oh=3f108c41ea7a502b625d1628f7d3b6ce&oe=60F09E05', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/60440351_10206307935053506_4865699287780032512_n.jpg?_nc_cat=105&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=sQveW1r3_lwAX-Hh0P-&_nc_ht=scontent-sjc3-1.xx&oh=ff23a04dda1bd551f5b7591bb7031ed0&oe=60F15C60', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/93561798_10207429747699229_8957155133326622720_n.jpg?_nc_cat=102&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=zpRhqYkiMWAAX8L1fvs&_nc_ht=scontent-sjc3-1.xx&oh=5445aea35214103689afee286a2f0705&oe=60F162A8', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/190610417_10159748623817755_4716167069407275989_n.jpg?_nc_cat=107&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=dAyXN9W3a3IAX9PqPZ8&_nc_ht=scontent-sjc3-1.xx&oh=cfa50761ee940936b4e93501b7890f63&oe=60F0572F', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/32222462_10156435743984433_3794522675947241472_n.jpg?_nc_cat=102&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=nYcNoLDHzREAX8PMVeQ&_nc_ht=scontent-sjc3-1.xx&oh=52c7a1cdf68af671556ce8cd700ff59f&oe=60F03585', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/c0.2.50.50a/p50x50/95630565_10157677576747961_6938103840839303168_n.jpg?_nc_cat=102&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=C6NRnkcxaqgAX-849QB&_nc_ht=scontent-sjc3-1.xx&oh=73206611b32480694dd95b785f02e126&oe=60F0D67B', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/1898061_10151933477987113_699341844_n.jpg?_nc_cat=105&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=mdt_bP6Ec8wAX9OXj48&_nc_ht=scontent-sjc3-1.xx&oh=cbff503593e4af25113d5548e2122c5a&oe=60EFF107', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/93964423_3966273330064538_635764926287183872_n.jpg?_nc_cat=104&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=0t35NhFemSYAX_ZpVoJ&_nc_ht=scontent-sjc3-1.xx&oh=4136cf19bd29b74e78d788df9260e8b4&oe=60EFBA18', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/208135933_5995284360489241_2427209697820992203_n.jpg?_nc_cat=100&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=x_y9k2DIeLkAX8T6vHt&_nc_ht=scontent-sjc3-1.xx&oh=0afa6417b934fe57814759c48bbd2b4e&oe=60F01A75', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/119812210_4738580506166911_1232833850805658402_n.jpg?_nc_cat=104&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=NKGZqXQBCPIAX-4C2p2&_nc_ht=scontent-sjc3-1.xx&oh=eac5da7a2e12f81c831bab1f6f76cdca&oe=60F0C699', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/190205938_5539204969482825_4284973421939246140_n.jpg?_nc_cat=108&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=rC116hoM-68AX9Pc7np&_nc_ht=scontent-sjc3-1.xx&oh=d4f3907f3cdf430c5df6b1e159c9a354&oe=60EFD17A', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/54435701_2596726120369313_8750911628406423552_n.jpg?_nc_cat=106&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=oyvSyDw15QEAX-affVh&_nc_ht=scontent-sjc3-1.xx&oh=8b3993371dc4772f25b69315c6fc34c9&oe=60F14E8B', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/81347755_3149578321723676_8962259560223997952_n.jpg?_nc_cat=100&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=G1sZUjZ8zS8AX8vtTbj&_nc_ht=scontent-sjc3-1.xx&oh=5bdaf5fdf381e3f93c18ed490f44730f&oe=60F01812', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/70878206_2822896984391332_7144901980656238592_n.jpg?_nc_cat=106&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=W2cCma2gHd8AX-Y_PQZ&_nc_ht=scontent-sjc3-1.xx&oh=333a86463bc19716c0f2f87a8b62c882&oe=60F18FEB', 'https://www.facebook.com/rsrc.php/v3/y4/r/-PAXP-deijE.gif', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/86757083_3138390589513381_7580339968581566464_n.jpg?_nc_cat=107&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=hXMuIfaKeboAX93PggP&_nc_ht=scontent-sjc3-1.xx&oh=f141789f1744ebe7d73a7ff2884f5ba5&oe=60EFDF94', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/12347656_1061730243858430_5333106340401181308_n.jpg?_nc_cat=100&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=aWhfLdPBVQoAX-U6Stj&_nc_ht=scontent-sjc3-1.xx&oh=3d4aff7031c6eb9490c094a4dc870e04&oe=60EFFB70', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t31.18172-1/cp0/p50x50/10900044_926156567397227_3855162840370973455_o.jpg?_nc_cat=105&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=DhcXyEyDo1EAX-HIgDi&_nc_ht=scontent-sjc3-1.xx&oh=d03fac460c3aaed02beed74e75932ddf&oe=60F0B118', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/19510583_1635379066497052_2951370976427318278_n.jpg?_nc_cat=103&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=6zg5hvr_ebsAX9HlP86&_nc_ht=scontent-sjc3-1.xx&oh=5a093104cbb3bdc924fcf14c0ee13c6c&oe=60F09C63', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/127057680_3845987002087141_5663348313218072487_n.jpg?_nc_cat=110&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=YypRZd6NFWsAX9aRvDJ&_nc_ht=scontent-sjc3-1.xx&oh=282278b683d5a50419166318d6b51be0&oe=60F0A5A6', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/145708086_3986968817989011_4450669507259647513_n.jpg?_nc_cat=108&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=x4J5WMvfXjAAX80cu3V&_nc_ht=scontent-sjc3-1.xx&oh=3a624bae8b9d23c26136bbfc966be0df&oe=60F17B0F', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/189418884_4346702018674315_7295615835392679904_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=KZ-oCT45qFcAX8zjlUV&_nc_ht=scontent-sjc3-1.xx&oh=e9c582c49831da92fb36f4e3fbd903b3&oe=60F0D6FE', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/11745805_1011316798892685_7171589632582927399_n.jpg?_nc_cat=102&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=gu84hKvGJGEAX9Xl5L6&_nc_ht=scontent-sjc3-1.xx&oh=88f7b803b4e4cb8533e3df3704c6d05f&oe=60F12A54', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/120539733_3642110349172659_2136811769562527943_n.jpg?_nc_cat=109&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=hvLZcH2XXZMAX-az9eb&_nc_ht=scontent-sjc3-1.xx&oh=b19852f708f3b02839e5449ca986afe5&oe=60F0AB4B', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/127278871_3745601555460819_7350485593166217776_n.jpg?_nc_cat=106&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=fZiGHboVq8IAX8fLqoi&_nc_ht=scontent-sjc3-1.xx&oh=679df9d404f748968629ab8f4a6ad8cf&oe=60F0F930', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/549172_509546285762446_760625847_n.jpg?_nc_cat=100&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=nG3FMKbZiBAAX9kKi2b&_nc_ht=scontent-sjc3-1.xx&oh=c752b25083b739a2ba26eba26af40d00&oe=60F1217B', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/161786247_3984094828279693_1379543127860746012_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=rU33cRzshB8AX-Awyze&_nc_ht=scontent-sjc3-1.xx&oh=570bd8c3accfb20399aea0b6e5b29522&oe=60F19618', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/46359874_2227907043967773_7743445491995639808_n.jpg?_nc_cat=102&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=q4_6_6sGs4EAX9cVVL6&_nc_ht=scontent-sjc3-1.xx&oh=e733753ef4852d8c654845f1b5583024&oe=60F133DE', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/30712582_1835379059847822_5950323910476374245_n.jpg?_nc_cat=100&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=IAbcoE8_d3YAX9PaDA3&_nc_ht=scontent-sjc3-1.xx&oh=1c4c40838a3cd7587a268a64a8608834&oe=60F0D541', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/69651100_2576857522374781_7124936726396534784_n.jpg?_nc_cat=106&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=OCOurNX5gmoAX_eLCAG&_nc_ht=scontent-sjc3-1.xx&oh=e34978a9492e76157a651617efa80e9e&oe=60EFC5FE', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/139886133_3793175050705107_4115592646104360270_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=ljB1tTvtWe0AX90wqp6&_nc_ht=scontent-sjc3-1.xx&oh=27e6510704fb5e6788a4e1227ce6dba9&oe=60F12F71', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/150913453_3867839063271950_6556697882692055298_n.jpg?_nc_cat=107&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=Th8ICKf_WMkAX--ANfM&_nc_ht=scontent-sjc3-1.xx&oh=6422dd9282ec02017fc43dbe6168b5ae&oe=60F08D3F', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/135757021_3710338279012497_5378776232634337709_n.jpg?_nc_cat=108&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=cJHl5QyvjrEAX_kXFpC&_nc_ht=scontent-sjc3-1.xx&oh=33fe8ed0f7a1b8341e141a71d99f05a2&oe=60EFBAA1', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/200744396_4228661323859758_1118157723444294421_n.jpg?_nc_cat=103&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=k9P5IKFDsWIAX9r50Br&_nc_ht=scontent-sjc3-1.xx&oh=9a93a86b32e64cf8cc1e2f63cc8dcb03&oe=60F02DD3', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/25550256_1601516243220634_2190866732721241113_n.jpg?_nc_cat=103&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=30FYPKp_Ss8AX9yjY9I&_nc_ht=scontent-sjc3-1.xx&oh=7563c26ad36ed2e8c35539d464d686b2&oe=60F10B9F', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/29792174_1682863058470635_7103994096902193507_n.jpg?_nc_cat=104&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=kNkB9zV16w8AX8efsDc&_nc_ht=scontent-sjc3-1.xx&oh=defa5849b97e9931c658618aaa4d51a7&oe=60F0D9CC', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/53036207_2104592659627866_9069597828107468800_n.jpg?_nc_cat=100&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=y4Ynbt21cosAX9uP1eI&_nc_ht=scontent-sjc3-1.xx&oh=3c46187228fd4c3aa871682741ab6c3d&oe=60F18EB3', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/70505775_2440556789368746_5644197011084279808_n.jpg?_nc_cat=109&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=okvAbb5vyvMAX9ePpeM&_nc_ht=scontent-sjc3-1.xx&oh=f02ca9ab752a644d6803bdac42cbd753&oe=60F0131A', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/178653067_3985064134904294_9149507343856526199_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=45LZp4HbFNMAX-KXyFD&_nc_ht=scontent-sjc3-1.xx&oh=3809111e813db63b44893769f7c1f28a&oe=60F0518B', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/c0.10.50.50a/p50x50/269517_113345928758317_8235087_n.jpg?_nc_cat=104&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=ydxD9pwtmmQAX-ZSM8O&_nc_ht=scontent-sjc3-1.xx&oh=b7152b2361e8de26f077a5b1576af730&oe=60F11EA3', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/180077964_3928690560557025_248516132861264456_n.jpg?_nc_cat=109&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=Pwbtb3Ay1aUAX_VGjbN&_nc_ht=scontent-sjc3-1.xx&oh=77534daa233a8093cdbe88a8b32bb888&oe=60F12182', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/91428237_2844917485600455_3396257934911471616_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=dZjl_ZSZeZsAX8xWHri&_nc_ht=scontent-sjc3-1.xx&oh=24941964c348fddb63a5a04d1020110a&oe=60F0F738', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/125246825_3461250050577575_1295817673218200021_n.jpg?_nc_cat=100&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=8h89Z9fuw0oAX_3DwVh&_nc_ht=scontent-sjc3-1.xx&oh=2483b83f2a07815fb909d812c86416aa&oe=60F19A88', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/c0.8.50.50a/p50x50/12241758_899494630142535_4704191219499452984_n.jpg?_nc_cat=106&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=jCv84woMqV8AX__JMgO&_nc_ht=scontent-sjc3-1.xx&oh=4ad1221b9248c631442a78e5100cd269&oe=60F0033A', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/84591990_2685487024903667_3791903514695827456_n.jpg?_nc_cat=102&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=Yb3fX5DbrSwAX_x1D6X&_nc_ht=scontent-sjc3-1.xx&oh=12c7aed720ddb695eb89d537dd3dd5e8&oe=60EFD56E', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/132430781_3532552903480771_5629207286777840440_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=hObjUuK9EOAAX-rV7Az&_nc_ht=scontent-sjc3-1.xx&oh=384302f5c884959e7ef7db567bd691fa&oe=60F08F47', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/1451557_413299258799694_1969439570_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=wn7XCkM6ulIAX9l0YTz&_nc_ht=scontent-sjc3-1.xx&oh=25e73c17dada1e364303dd1786eb7011&oe=60F08146', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/c0.0.50.50a/p50x50/72550668_2257154071078032_8817181238616915968_n.jpg?_nc_cat=111&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=qVdndEjjcnoAX_US4Xb&_nc_ht=scontent-sjc3-1.xx&oh=f88aac1c0185a70ce101d05a178d2c6d&oe=60F0F685', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t31.18172-1/cp0/c66.66.819.819a/s50x50/857774_336272333143519_257834309_o.jpg?_nc_cat=105&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=pYSqd5dBs-kAX9Y9qTJ&_nc_ht=scontent-sjc3-1.xx&oh=e46fa73224261b415675458e6aa3f6d6&oe=60F0CC05', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/10464034_604547802981052_1311217030135721184_n.jpg?_nc_cat=108&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=9WZWDcIYa98AX-Rsdpd&_nc_ht=scontent-sjc3-1.xx&oh=5a89c61204511dd32b5f8e6e72f30f58&oe=60F01E6E', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/36410360_1338992736204408_9089068512588070912_n.jpg?_nc_cat=103&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=Lrvh7IkgtJoAX-lAw_y&_nc_oc=AQkdbAao7p7MnFGDc_4h5scAYAwChuMp79D2vFov3U0Z4d14bmi3ZARSOSJbzptAoGg&_nc_ht=scontent-sjc3-1.xx&oh=bdc19a6ed140f8afd29ade27f38c732c&oe=60F185D0', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/27867436_2281457682080963_121522209005854917_n.jpg?_nc_cat=111&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=6paPJ7hPoiYAX_ARTOq&_nc_oc=AQm6Ng9CL9QagYm7gkzRq9PK-feSwfzP0TOKG_a_U_nKa74IN3BBBOVb5wJoqEprK1s&_nc_ht=scontent-sjc3-1.xx&oh=e880d219818d6f23e3155f2133023ad8&oe=60F0E909', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/10635915_1603704506512707_8784159246017229453_n.jpg?_nc_cat=107&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=90YRpXYTEg4AX8DrPZJ&_nc_ht=scontent-sjc3-1.xx&oh=26e3153afa3a20aa176448337c045c3c&oe=60F03515', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/10635915_1603704506512707_8784159246017229453_n.jpg?_nc_cat=107&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=90YRpXYTEg4AX8DrPZJ&_nc_ht=scontent-sjc3-1.xx&oh=26e3153afa3a20aa176448337c045c3c&oe=60F03515', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/179147690_2975665289334422_1807636716262930637_n.jpg?_nc_cat=110&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=nA8fSxPnHV8AX8IiPR4&_nc_ht=scontent-sjc3-1.xx&oh=f057c3c0cb1bfb68db707ebfc832e0d5&oe=60F0F9F7', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t31.18172-1/cp0/p50x50/18671489_1921755788099558_4569499377307200849_o.jpg?_nc_cat=109&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=9IC-Ss7sYn8AX_vOGsu&_nc_ht=scontent-sjc3-1.xx&oh=fd99b8aa3471d962e29603b233ea9411&oe=60F0AE9B', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/67766971_2371689069786794_8203210642836946944_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=vNi5ni0c_FgAX-2JYcu&_nc_ht=scontent-sjc3-1.xx&oh=e4f3afd36e6af85a480f74d88993d5e4&oe=60F049D5', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/143426252_2896138177289509_6213706002679198438_n.jpg?_nc_cat=111&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=rsLj1ZzA4MMAX_-JXKm&_nc_ht=scontent-sjc3-1.xx&oh=8846f991438f0c0afe359ad40a984d8a&oe=60F1990F', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/40049136_2181627435455296_2892610252803407872_n.jpg?_nc_cat=102&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=QxvUlbpPiAYAX_kXhUJ&_nc_ht=scontent-sjc3-1.xx&oh=71682c5929d9aa9fca249c40d042cc2d&oe=60F1104A', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/12074885_1634174853501189_1657602666556398997_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=OGHbybLC9XwAX9Ir9jS&_nc_ht=scontent-sjc3-1.xx&oh=42f60f15a0e7075bf7eddc66caa62312&oe=60F07121', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/1503882_1381916258765570_7235729472747459739_n.jpg?_nc_cat=105&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=OYW1X2W7aGcAX80mbo0&_nc_ht=scontent-sjc3-1.xx&oh=270bff5ddcfc6f78ed9f8a19372f354f&oe=60F040FF', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/209537920_2273137739483543_900534124990083323_n.jpg?_nc_cat=109&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=T0iT3UdMoRsAX--7I80&_nc_ht=scontent-sjc3-1.xx&oh=b9231d3a370f693865dd7ee0e38cc57a&oe=60F007A9', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/174800332_2193336170797174_3523150329754552329_n.jpg?_nc_cat=100&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=k7SXA0TIIU8AX-nJ0SP&_nc_ht=scontent-sjc3-1.xx&oh=c65e37911ffea50e8da4227c21adb248&oe=60F1A168', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/146581973_3711297508988611_4858154213101005744_n.jpg?_nc_cat=104&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=jalaqx9THoQAX__b_On&_nc_ht=scontent-sjc3-1.xx&oh=da50889e8e5c0246c536dd2b1ec3f401&oe=60F058A2', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/188985318_2074055509425109_8912874700875748516_n.jpg?_nc_cat=102&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=SD7weHnC0_wAX85yS7E&_nc_ht=scontent-sjc3-1.xx&oh=08f13b5be869c4d58f2230f203f04366&oe=60F1A150', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/10481190_323149791175177_7067783793289332486_n.jpg?_nc_cat=111&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=euWmrgP9BwIAX8jxlFE&_nc_ht=scontent-sjc3-1.xx&oh=5ae1eacae0fcd9950c9592b25b003607&oe=60EFAC4A', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/126990692_1722992207860649_7321505670255071099_n.jpg?_nc_cat=104&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=P7aBWxGMtv0AX_9UwBb&_nc_oc=AQlNWst-TlhWCXZxMT5Q2pvzYSHA8cDF1FAMpe-7fVhzQXQmYI2BqolIpPxJcgwAa3E&_nc_ht=scontent-sjc3-1.xx&oh=9cb1d98bfad6b3bcebe32e79ba94fafe&oe=60F0D326', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t39.30808-1/cp0/p50x50/207264872_2335133709953639_2678361713951333726_n.jpg?_nc_cat=100&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=8XyvEhLkVpYAX_-pFcK&_nc_ht=scontent-sjc3-1.xx&oh=444d1f24f0fc978bf24758e070e7c5ac&oe=60F0D106', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/190153202_1886178461535349_5981513766743888636_n.jpg?_nc_cat=109&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=kChqOq5NbkoAX_2ZhML&_nc_ht=scontent-sjc3-1.xx&oh=1cd4baa41087a22fedd6b3ec6e0aab36&oe=60F0A587', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t31.18172-1/cp0/c65.65.819.819a/s50x50/860150_133508460151853_1657392630_o.jpg?_nc_cat=105&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=5Qo4VhsgxQEAX_dsXbd&_nc_ht=scontent-sjc3-1.xx&oh=f1d7d992750fa9e33406fecae5508a61&oe=60F0E1B1', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/p50x50/10441236_334203040083123_456082507587334991_n.jpg?_nc_cat=102&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=NF7Utzph5wEAX_kw8Ol&_nc_ht=scontent-sjc3-1.xx&oh=fd5778ab964a35debcb6eabd44675e64&oe=60F117C3', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/35798471_889975854536045_4962234841035702272_n.jpg?_nc_cat=108&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=i8ic4RsYOykAX-Iln_Y&_nc_ht=scontent-sjc3-1.xx&oh=62d21cd8d9fc64123668743df8d3d44a&oe=60F0BE8C', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/186453550_1812260735615171_533242315906623878_n.jpg?_nc_cat=111&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=6DqxHMmmSagAX-2ljYL&_nc_oc=AQko0enQAY9PRZNd1JYP7LtIQmPKsvZPO6aZB4_AV__R69NFZFBodKiwPLkWUO9OZ-k&_nc_ht=scontent-sjc3-1.xx&oh=98345f2368fc174e77018717608bbaf7&oe=60F014E2', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-1/cp0/c0.0.50.50a/p50x50/1236625_176289159229557_874450482_n.jpg?_nc_cat=102&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=D3Fi4GI9NMkAX_tGMiZ&_nc_ht=scontent-sjc3-1.xx&oh=032579276591f79308dfdadfd42a025f&oe=60F098DD', 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/70120401_1158877950966458_213629001833381888_n.jpg?_nc_cat=111&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=nYFU8cifSM0AX-kSl_B&_nc_ht=scontent-sjc3-1.xx&oh=ae53cc69f1ea05f86a6623fe45941d5f&oe=60F095FF']
    #
    # for idx, url in enumerate(urls):
    #     if idx > 0:
    #         break
    #     print("%s : %s" % (idx, url))
    #     _ensure_image_(url)

    #url = 'https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-1/cp0/p50x50/104053461_279931313415794_6315182741251005890_n.jpg?_nc_cat=108&ccb=1-3&_nc_sid=dbb9e7&_nc_ohc=iWV89kJUC9IAX9lTSns&_nc_ht=scontent-sjc3-1.xx&oh=00d0f5b09c51993148c601dc97a3b32a&oe=60F142DC'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_ensure_image_(urls))

    #print("after loop")


def convert_month(month):
    months_english = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
                      'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11',
                      'December': '12'}

    months_french = {'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04', 'mai': '05', 'juin': '06',
                     'juillet': '07', 'août': '08', 'septembre': '09', 'octobre': '10', 'novembre': '11',
                     'décembre': '12'}

    if month in months_french:
        return months_french[month]
    if month in months_english:
        return months_english[month]


class Articless:
    def __init__(self):
        self.articles_list = []
        self.recommend_elements = []


    def append_articles(self, article_element):
        self.articles_list.append(article_element)


    def append_recommend_container_elements(self, element):
        self.recommend_elements.append(element)


class Users:
    def __init__(self):
        self.users_list = []
        self.recommend_status = []
        self.user_comment = []
        self.post_date = []
        self.user_profile_review = []
        self.page_url = []

    def append_user(self, user, counter):
        self.users_list.append(user)


    def append_recommend(self, recommend):
        self.recommend_status.append(recommend)


    def append_commentary(self, comment):
        self.user_comment.append(comment)


    def append_date(self, date):
        self.post_date.append(date)


    def append_user_profile(self, user_href):
        self.user_profile_review.append(user_href)


    def append_page_url(self, url):
        self.page_url.append(url)



def defining_driver():
    """
    Please change the webdriver path to your corresponding one

    :return:
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--start-maximized')
    options.add_argument('window-size=1536x824')
    wire_options = {
        'connection_timeout': 1000
    }
    driver = webdriver.Chrome("./chromedriver", seleniumwire_options=wire_options, options=options)
    return driver


def get_all_articles_main_container_in_current_page(driver):
    global UserClass
    global Articles
    global counter_skip

    try:
        WebDriverWait(driver, 50).until(EC.invisibility_of_element_located((By.XPATH, '//span[@class="uiMorePagerLoader pam uiBoxWhite noborder"]')))
        time.sleep(3)
        articles = WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.XPATH, '//div[@role="article"]')))
        #print("articles:", articles)
        for article in articles:
            try:
                user = article.find_element_by_xpath('.//a[@aria-hidden="true"]')
                assert user.get_attribute('data-ft') is not None
            except:
                try:
                    user = article.find_element_by_xpath('.//span[@aria-hidden="true"]')
                    assert user.get_attribute('data-ft') is not None
                except:
                    continue

            user_name = user.get_attribute('title')
            UserClass.append_user(user_name, counter_skip)
            nex_div_img = user.find_element_by_xpath('.//div[@class="_38vo"]').find_element_by_tag_name('div').find_element_by_tag_name('img')
            UserClass.append_user_profile(nex_div_img.get_attribute('src'))
            element = user.find_element_by_xpath("./following-sibling::div")
            Articles.append_recommend_container_elements(element)

            parent_one = user.find_element_by_xpath("..")
            parent_two = parent_one.find_element_by_xpath("..")
            goal = parent_two.find_element_by_xpath("..")
            Articles.append_articles(goal)

        #GET RECOM STATUS
        for ele in Articles.recommend_elements:
            status_container_h5 = ele.find_element_by_tag_name('h5')
            status = status_container_h5.find_element_by_tag_name('i')
            if status.get_attribute('className') == '_51mq img sp_OkVielxDWJh sx_9bfe1b':
                UserClass.append_recommend(recommend='Does not recommend')
            elif status.get_attribute('className') == '_51mq img sp_OkVielxDWJh sx_844e6e':
                UserClass.append_recommend(recommend='Recommends')
            #GET DATE
            date = ele.find_element_by_xpath('.//div[@data-testid="story-subtitle"]').find_element_by_tag_name('abbr').get_attribute('innerText')
            UserClass.append_date(date)


        #GET COMMENT
        for ele in Articles.articles_list:
            final_parag = ''
            try:
                comment_element = ele.find_element_by_xpath('.//div[@data-testid="post_message"]')
                try:
                    see_more = comment_element.find_element_by_xpath('.//a[@class="see_more_link"]')
                    see_more.click()
                except:
                    pass
                paragraphes_element = comment_element.find_elements_by_tag_name('p')
                for parag in paragraphes_element:
                    final_parag += parag.get_attribute('innerText') + "\n"
                UserClass.append_commentary(final_parag)
            except:
                ll = traceback.format_exc()
                UserClass.append_commentary("No commentary found")
    except Exception as e:
        ll = traceback.format_exc()
        print(type(ll))
        #print(e)
        #print(ll)
        #raise Exception("Please Send This message to your freelancer as screenshot %s" % str(e))
        raise ValueError(ll)

UserClass = Users()
Articles = Articless()
counter_skip = 0

# def run_all(input_file):
#     failed_cnt = 0
#     with open(input_file, 'r') as f:
#         lines = f.readlines()
#         for line in lines:
#             tokens = line.split()
#             print(tokens)
#
#             try:
#                 output_name = './scrap_results/%s_%s.csv' % (tokens[0], tokens[1])
#                 if path.exists(output_name) or tokens[1] in skips :
#                     print("%s is done, skipped" % tokens[1])
#                     continue
#
#                 fb_scapper(tokens[0], tokens[1], tokens[2])
#             except Exception as e:
#                 failed_cnt += 1
#                 print("Failed on url %s" % tokens[2])
#
#     print("failed_cnt: ", failed_cnt)


def fb_scapper(clinic_uuid, fb_page):
    print("part 0")
    global UserClass
    UserClass = Users()
    global Articles
    Articles = Articless()
    global counter_skip
    counter_skip = 0

    driver = defining_driver()
    driver.get(fb_page)
    clicked=False

    print("part 1")
    while True:
        try:
            to_scroll_into_view = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="clearfix uiMorePager stat_elem _4288 _52jv"]')))
            actions = ActionChains(driver)
            actions.move_to_element(to_scroll_into_view).perform()
            if clicked is False:
                try:
                    time.sleep(2)
                    container_close = driver.find_element_by_xpath('//div[@class="_62up"]')
                    a = container_close.find_element_by_tag_name('a')
                    a.click()
                    time.sleep(1)
                    clicked = True
                except:
                    pass
            time.sleep(2)
        except Exception as e:
            break

    print("part 2")
    time.sleep(10)
    get_all_articles_main_container_in_current_page(driver=driver)
    # print(UserClass.users_list)
    # print(len(UserClass.users_list))
    # print("\n")
    # print(UserClass.recommend_status)
    # print(len(UserClass.recommend_status))
    # print("\n")
    # print(UserClass.user_comment)
    # print(len(UserClass.user_comment))
    # print("\n")
    # print(UserClass.post_date)
    # print(len(UserClass.post_date))
    # print("\n")
    # print(UserClass.user_profile_review)
    # print(len(UserClass.user_profile_review))

    for item in range(len(UserClass.users_list)):
        UserClass.append_page_url(fb_page)

    df = pd.DataFrame({"User_Name":UserClass.users_list,
                       "Recommendation_Status":UserClass.recommend_status,
                       "User_Comment":UserClass.user_comment,
                       "User_Interaction_Date":UserClass.post_date,
                       "User_Profile":UserClass.user_profile_review,
                       "Page_Source":UserClass.page_url
                       })
    if False:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_ensure_image_(UserClass.user_profile_review, clinic_uuid))

    df["clinic_uuid"] = clinic_uuid
    df.to_csv('./output/%s.csv' % (clinic_uuid), encoding='utf-8')

def run_one(clinic_uuid, url):
    try:
        output_name = './output/%s.csv' % (clinic_uuid)
        if path.exists(output_name):
            #print("%s is done, skipped" % clinic_uuid)
            pass
        else:
            fb_scapper(clinic_uuid, url)
    except Exception as e:
        print("Failed on %s with url %s" % (clinic_uuid, url))
        print(e)
        error = {
            "clinic_uuid": clinic_uuid,
            "error":str(e),
            "url":url
        }
        with open('./output/error_%s.json' % (clinic_uuid), 'w', encoding='utf-8') as f:
            json.dump(error, f, ensure_ascii=False, indent=4)

async def fetch(session, url, full_path):
    async with session.get(url) as response:
        if response.status == 200:
            f = await aiofiles.open(full_path, mode='wb')
            await f.write(await response.read())
            await f.close()

async def _ensure_image_(urls,clinic_uuid):
    root_images = './user_images_fb'

    async with aiohttp.ClientSession() as session:
        for idx, url in enumerate(urls):
            # if idx > 5:
            #     break

            tmp = url.split(".jpg")[0]
            filename = clinic_uuid + "__" + tmp.split("/")[-1] + ".jpg"
            full_path = os.path.join(root_images, filename)

            if Path(full_path).is_file():
                #print('file exists')
                continue

            #print("would query image_url %s and download at %s" % (url, full_path))

            await fetch(session, url, full_path)

if __name__ == "__main__":
    #typer.run(fb_scapper)
    #typer.run(run_all)
    #typer.run(tmp)
    typer.run(run_one)
