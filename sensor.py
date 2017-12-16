import random
import math
class Sensor:
	def __init__(self,num,high,middle,low):
		self.num = num
		self.illuminance = 300
		self.tmp_illuminance = 0
		self.next_illuminance = 0
		self.influence = []
		self.target_illuminance = 0
		self.HIGH_THRESHOLD = high
		self.MIDDLE_THRESHOLD = middle
		self.LOW_THRESHOLD = low
		self.rank = []
		with open('influence.csv') as f:
			for line in f:
				index = 0
				item = line.split('\t')
				for i in item:
					if(index == self.num):
						self.influence.append(float(i))
					index += 1

	def calc_now_illuminance(self,light_num,cd):
		self.tmp_illuminance += self.influence[light_num] * cd

	def update_illuminance(self,snum):
		self.illuminance = int(self.tmp_illuminance)

# KC111で実験する場合はコメント外す
#		with open("./illuminance.txt","r") as f:
#			for line in f:
#				item = line.split(",")
#				print(self.num)
#				self.illuminance = int(item[snum])
		self.tmp_illuminance = 0

	def set_now_illuminance(self,lum):
		self.illuminance = int(lum)

	def get_now_illuminance(self):
		return self.illuminance

	def get_num(self):
		return self.num

	def get_influence(self, light_num):
		return self.influence[light_num]

	def set_target_illuminance(self, lum):
		self.target_illuminance = int(lum)

	def get_target_illuminance(self):
		return self.target_illuminance

	def update_related_light(self,light,LIGHT_NUM):
		self.rank = []
		for i in range(0,LIGHT_NUM):
			if(light[i].get_regression(self.num) > self.HIGH_THRESHOLD):
				self.rank.append(1)
			elif(light[i].get_regression(self.num) > self.MIDDLE_THRESHOLD):
				self.rank.append(2)
			elif(light[i].get_regression(self.num) > self.LOW_THRESHOLD):
				self.rank.append(3)
			else:
				self.rank.append(0)

	def get_related_rank(self,light_num):
		return self.rank[light_num]

	def calc_next_illuminance(self,light_num,cd):
		self.tmp_illuminance += self.influence[light_num] * cd

	def update_next_illuminance(self):
		self.next_illuminance = int(self.tmp_illuminance)# + random.normalvariate(0,math.sqrt(5)))
		self.tmp_illuminance = 0

	def set_next_illuminance(self,lum):
		self.next_illuminance = int(lum)

	def get_next_illuminance(self):
		return self.next_illuminance
