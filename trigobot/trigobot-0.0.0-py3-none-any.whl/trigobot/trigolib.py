from ast import Return
from types import MemberDescriptorType
from pygame import Color
from selenium import webdriver
from time import sleep, time
from pystyle import Add, Center, Anime, Colors, Colorate, Write, System
import os
import warnings
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from os import error, system, name
from time import time, strftime, gmtime, sleep
from selenium.webdriver.common.by import By
import threading, warnings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sympy import arg
import undetected_chromedriver as uc
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from colorama import Fore, Back, Style
from subprocess import Popen


driver = webdriver.Chrome(executable_path='chromedriver.exe')
driver.get('https://www.trigo-app.com/')
driver.set_window_size(2000, 2000)
driver.set_window_position(-1000000, 0)


class TrigoBot:
    def trigoLogin(Return1: Return, Return: Return):
        driver.find_element_by_xpath('/html/body/div/div/div[3]/div/header/div/div[2]/div/div/div/div[2]/div/div/div/button').click()
        sleep(3)
        driver.find_element_by_xpath('/html/body/div[1]/div/div[5]/div/div/div[2]/div/div[2]/div/div/div[2]/div/div/form/div/div/div[6]').click()
        sleep(1)
        driver.find_element_by_xpath('/html/body/div/div/div[5]/div/div/div[2]/div/div[2]/div/div/div[3]/div/div/form/div/div/div[3]/div/input').send_keys(Return)
        driver.find_element_by_xpath('/html/body/div/div/div[5]/div/div/div[2]/div/div[2]/div/div/div[3]/div/div/form/div/div/div[4]/div/input').send_keys(Return1)
        sleep(2)
        driver.find_element_by_xpath('/html/body/div[1]/div/div[5]/div/div/div[2]/div/div[2]/div/div/div[3]/div/div/form/div/div/div[7]/button').click()



class trigoCmd:

    def MakeJoinTheBot():
        link = input(Colorate.Horizontal(Colors.green_to_cyan, Center.XCenter("Mettez votre lien de groupe ->")))
        driver.get(link)
        sleep(5)
        driver.find_element_by_xpath('/html/body/div/div/div[3]/div/main/div/div/div[2]/div/div/div/div[1]/div/div/div/div/div[1]/div[3]/div/button').click()
        input(Colorate.Horizontal(Colors.red_to_yellow, Center.XCenter('Pressez "Entrée" pour continuer')))

    def post():
        os.system('cls') 
        link1 = input(Colorate.Horizontal(Colors.green_to_cyan, Center.XCenter("Mettez votre lien de groupe ->")))            #/html/body/div/div/div[3]/div/main/div/div/div[2]/div/div/div/div[1]/div/div/div/div/section/div/div/ul/li[1]/div/div/div[1]/span
        driver.get(link1)
        sleep(5)
        driver.find_element_by_xpath('/html/body/div/div/div[3]/div/main/div/div/div[2]/div/div/div/div[1]/div/div/div/div/section/div/div/ul/li[1]/div/div/div[1]/button').click()
        text = input(Colorate.Horizontal(Colors.green_to_cyan, Center.XCenter("Mettez votre texte ->")))
        sleep(4)
        driver.find_element_by_xpath('/html/body/div/div/div[3]/div/main/div/div/div[2]/div/div/div/div[1]/div/div/div/div/section/div/div/ul/li[1]/div/div[2]/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div[2]/div/div/div/div').send_keys(text)
        sleep(2)
        driver.find_element_by_xpath('/html/body/div/div/div[3]/div/main/div/div/div[2]/div/div/div/div[1]/div/div/div/div/section/div/div/ul/li[1]/div/div[2]/div/div[2]/div/div[3]/div[2]/button[2]').click()
        input(Colorate.Horizontal(Colors.red_to_yellow, Center.XCenter('Pressez "Entrée" pour continuer')))


    def if_ready():
        print(Return)

    def TrigoLocateBtn(Return: Return):
        driver.find_element_by_xpath(Return).click()

    def TrigoLocateBtn_class(Return: Return):
        driver.find_element_by_class_name(Return).click()

    def TrigoLocateBtn_id(Return: Return):
        driver.find_element_by_id(Return).click()

    def TrigoLocateBtn_tag_name(Return: Return):
        driver.find_element_by_tag_name(Return).click()

    def TrigoLocateBtn_css_selector(Return: Return):
        driver.find_element_by_css_selector(Return).click()

    def TrigoLocateBtn_link_text(Return: Return):
        driver.find_element_by_link_text(Return).click()

    def TrigoLocateTyper(Return: Return, Return1: Return):
        driver.find_element_by_xpath(Return).send_keys(Return1)

    def TrigoLocateTyper_class(Return: Return, Return1: Return):
        driver.find_element_by_class_name(Return).send_keys(Return1)

    def TrigoLocateTyper_id(Return: Return, Return1: Return):
        driver.find_element_by_id(Return).send_keys(Return1)

    def TrigoLocateTyper_tag_name(Return: Return, Return1: Return):
        driver.find_element_by_tag_name(Return).send_keys(Return1)

    def TrigoLocateTyper_css_selector(Return: Return, Return1: Return):
        driver.find_element_by_xpath(Return).send_keys(Return1)   

    def TrigoLocateTyper_link_text(Return: Return, Return1: Return):
        driver.find_element_by_xpath(Return).send_keys(Return1)     

    def TrigoWebpage(Return: Return):
        driver.get(Return)

    def TrigoRefresh():
        driver.refresh
        