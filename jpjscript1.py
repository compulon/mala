from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
import time
import json
from selenium.webdriver.support.ui import Select
from PIL import Image, ImageEnhance, ImageFilter
import matplotlib.pylab as plt
import cv2
import numpy as np
import urllib
import os
import tensorflow as tf
import logging
import pytesseract
import solve_captchas_with_model as SolveCaptcha
from imutils import paths
import imutils


class ClassScript1():
	def __init__(self):

		# PATH binary driver chrome 
		self.CHROMEDRIVER_PATH = '/usr/bin/chromedriver'
		
		# PATH binary driver chromium 
		self.CHROMIUMDRIVER_PATH = '/usr/bin/chromium-browser'
		#self.PATH = "/home/compulon/Desarrollos/Freelance/Proyectos/Webscrapping Python RD/download/"

		os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
		tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

		self.i = 8
		#pytesseract.pytesseract.tesseract_cmd = 'home/compulon/Desarrollos/Freelance'
		
	# Initialize driver driver browser without head.	
	def start_driver(self):
		options = Options()
		#options.binary_location = self.CHROMIUMDRIVER_PATH
		options.add_argument('--headless')
		options.add_argument("--window-size=1200x800")
		#options.add_argument("--start-maximized")
		options.add_argument('--no-sandbox')
		options.add_argument('--disable-dev-shm-usage')
		options.add_argument("--disable-extensions")
		options.add_argument('--ignore-certificate-errors')
		options.add_argument("--test-type")
		#self.driverBrowser = webdriver.Chrome(executable_path = self.CHROMEDRIVER_PATH, chrome_options = options)
		self.driverBrowser = webdriver.Firefox(options=options, executable_path='/home/compulon/Desarrollos/Freelance/Proyectos/Bot para rellenar formularios automáticamente/geckodriver-v0.25.0-linux64/geckodriver')


	# Closure for resource optimization
	def close_driver(self):
		self.driverBrowser.close()
		self.driverBrowser.quit()

	# Validate the status of the page
	def status_page(self, xpath_element_located, url):
		self.driverBrowser.get(url)
		# Wait explicitly
		try:
			wait = WebDriverWait(self.driverBrowser,60)
			element = wait.until(EC.presence_of_element_located((By.XPATH, xpath_element_located)))
		except TimeoutException:
			return False
		else:
			return True

	
	def extract_single_letters_from_captchas(self):
		img = Image.open("image_captcha1.png")
		width, height = img.size
		right = int (width/6)
		size_separator = 24
		for i in range(4):						
			left =  right
			top = 1
			right = int(width/6) + size_separator
			bottom = height
			size_separator = size_separator + 18
			print(left, top, bottom, right)			
			img2 = img.crop((left, top, right, bottom))
			img2.save("letter_image_captcha"+str(i)+".png")

	def download_image_captcha(self, i):		
		
		imgcaptcha = self.driverBrowser.find_element_by_xpath('//img[@class="captcha"]')
		#print(imgcaptcha.get_attribute('src'))
		location = imgcaptcha.location    
		size = imgcaptcha.size   
		#print(len(size),"***",location)
		self.driverBrowser.save_screenshot('screenshot.png')
		img = Image.open('screenshot.png') # uses PIL library to open image in memory
		#img.save('screenshot.png')
		left = location['x']
		top = location['y']
		right = location['x'] + size['width']
		bottom = location['y'] + size['height']
		img = img.crop((left+15, top+10, right-15, bottom)) # defines crop points
		img.save('image_captcha'+ str(i) +'.png')

	def resolvecaptcha(self):		
		imgcaptcha = self.driverBrowser.find_element_by_css_selector('img.captcha')
		location = imgcaptcha.location    
		size = imgcaptcha.size   
		self.driverBrowser.save_screenshot('screenshot.png')
		img = Image.open('screenshot.png') # uses PIL library to open image in memory
		img.save('screenshot.png')
		left = location['x']
		top = location['y']
		right = location['x'] + size['width']
		bottom = location['y'] + size['height']
		img = img.crop((left+15, top+10, right-15, bottom)) # defines crop points
		img.save('image_captcha.png')
		result_captcha = SolveCaptcha.solve_captchas_with_model()		
		return result_captcha
	
	def parse(self, find_by, element_located):
		try:
			wait = WebDriverWait(self.driverBrowser,3)
			if(find_by == "xpath"):
				element = wait.until(EC.presence_of_element_located((By.XPATH, element_located)))
			elif(find_by == "id"):
				element = wait.until(EC.presence_of_element_located((By.ID, element_located)))
			elif(find_by == "css"):
				element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, element_located)))
		except TimeoutException:
			return False
		else:
			return element

	def consult_jpj(self, identification_number):
		dict_result = {}
		url = "https://www.jpj.gov.my/en/web/main-site/semakan-tarikh-luput-lesen-memandu"
		status = self.status_page('//*[@id="wrapper"]', url)
		if (status):
			select_organism = Select(self.driverBrowser.find_element_by_id('_drivinglicense_WAR_JPJDXPPluginportlet_catid'))
			select_organism.select_by_visible_text("MALAYSIAN PUBLIC (MYKAD)")
			textidnumber = self.driverBrowser.find_element_by_id('_drivinglicense_WAR_JPJDXPPluginportlet_idNumber')
			textidnumber.send_keys(identification_number)
			repeat = True
			while repeat: 			
				captcha_text = self.resolvecaptcha()
				print(captcha_text)
				txtcaptcha = self.driverBrowser.find_element_by_id('_drivinglicense_WAR_JPJDXPPluginportlet_captchaText')
				txtcaptcha.send_keys(captcha_text)
				self.driverBrowser.find_element_by_css_selector('button#submitAjax').click()
				
				
					#self.driverBrowser.execute_script("document.getElementById('submitAjax').click();")
					#time.sleep(5)

					#error_captcha = self.driverBrowser.find_elements_by_css_selector('div.lfr-alert-container')				

					#print(len(error_captcha))
					#if len(error_captcha) > 0:
						#time.sleep(3)
						#error_captcha[0].
						#self.parse("id", 'yui_patched_v3_18_1_1_1572971993630_300').click()#f
				button_close = self.driverBrowser.find_elements_by_css_selector('button.close')
				print(len(button_close))
				if len(button_close) > 0: 
					try:
						button_close[0].click()
					except ElementNotInteractableException:
						pass
				else:
					#result = #self.parse('css','span#resultAjax div.box div.output-error')#
					result = self.driverBrowser.find_elements_by_xpath('//span[@id="resultAjax"]/div[@class="box"]/div[@class="output-error"]')
					print(len(result))
					if len(result) > 0: #result != False:
						print("No data...")
						repeat = False
					else:
						element = self.parse('css','span#resultAjax div.box table#t1 tbody tr td table')
						print(element)
						repeat = (element == False)
						if element != False:
							print(element.text)
					#button_close = WebDriverWait(self.driverBrowser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.close')))
						#button_close.click()
						
						#self.driverBrowser.find_element_by_id("reloadcaptcha").click()
					#else:
						#self.parse("css","button.close").click()#self.driverBrowser.find_element_by_css_selector('button.close').click()
						#self.driverBrowser.execute_script("document.getElementByClassName('close').click();")

						#time.sleep(3)
					
					#self.driverBrowser.find_elements_by_css_selector('span#resultAjax div.box table#t1 tbody tr td table')				
					#result = element[0].find_elements_by_css_selector("table#t1")
					#print(len(element))
					#time.sleep(3)
				
					
				 #(len(element) < 1)
				#name = element[0].find_element_by_css_selector('p span:nth-child(1)').text
				#print(name)
			
			###return json.dumps(dict_result, ensure_ascii = False, indent = 4)
			
		else:
			return False
	
	# Eject script
	def run(self, identification_number):
		#self.extract_single_letters_from_captchas()
		self.start_driver()
		
		result = self.consult_jpj(identification_number)
		#print(result)
		self.close_driver()		

# Example

Script1 = ClassScript1()
#Script1.run("890312145805")
#Script1.run("800822075155")
Script1.run("860413335475")
#Script1.run("731129055280")
#Script1.run("951101146863")