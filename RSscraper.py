# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 12:48:48 2021

@author: Jan Odenthal, University of Heidelberg
"""

from pyppeteer import launch
import asyncio
import nest_asyncio
import regex as re
import urllib.request
import os
nest_asyncio.apply()

url = "https://www.realself.com/photos/surgical/rhinoplasty#page=%s&tags=8085-9952&location=2022"
output_folder = "C:/Users/jano1/Desktop/Neuer Ordner/Rhinoplastic_man_side"
async def main():
    global browser
    cc = 1626
    browser = await launch(headless=False, executablePath = "C:/Program Files/Google/Chrome/Application/chrome.exe", ignoreDefaultArgs = ["--enable-automation"])
    for integer in range (70, 1000):  
        page = await browser.newPage()
        string = str(integer)
        this_url = url % string
        print(this_url)
        await page.goto(this_url, waitUntil = ["networkidle0"])
        cont = await page.content()
        match_strings = re.findall("data-src=\"//fi.realself.com/.*(?:jpg|png)", cont)
        for match_string in match_strings:
            file = 'https://' + match_string[12::]
            if "before" in file:
                cc = cc+1
                image_folder = output_folder + "/" + str(cc)
            if not os.path.exists(image_folder):
                os.mkdir(image_folder)
            new_page = await browser.newPage()
            await new_page.goto(file)
            name = os.path.basename(file)
            if "before" in file or "after" in file:
                urllib.request.urlretrieve(file, image_folder + "/" + name)
            await new_page.close()
        await page.close()
    await browser.close()
        
asyncio.run(main())