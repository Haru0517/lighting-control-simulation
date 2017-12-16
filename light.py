class Light:
	def __init__(self,num,cd,next_cd,weight,max,min,SENSOR_NUM,SENSOR_MAX_NUM,):
		self.num = num
		self.cd = cd
		self.next_cd = next_cd
		self.weight = weight
		self.max_luminance = max
		self.min_luminance = min
		self.regression = []
		self.p =[[[ 0.0 for l in range(2)] for k in range(2)] for i in range(SENSOR_MAX_NUM)]
		self.b =[[0.0 for k in range(2)] for i in range(SENSOR_MAX_NUM)]
		self.change_count = 0
		for i in range(SENSOR_MAX_NUM):
			self.regression.append(10)
		self.on_flg = False
		self.off_flg = False
		self.on_count = 0

	def set_next_cd(self,lum):
		self.next_cd = int(lum)

	def set_now_cd(self,lum):
		self.cd = int(lum)

	def get_now_cd(self):
		return self.cd

	def get_next_cd(self):
		return self.next_cd

	def get_num(self):
		return self.num

	def set_objective_func_value(self,value):
		self.func_value = value

	def get_objective_func_value(self):
		return self.func_value

	def set_next_objective_func_value(self,value):
		self.next_func_value = value

	def get_next_objective_func_value(self):
		return self.next_func_value

	def get_weight(self):
		return self.weight

	def set_neighbor(self,neighbor):
		self.neighbor = neighbor

	def get_max_luminance(self):
		return self.max_luminance

	def get_min_luminance(self):
		return self.min_luminance

	def update_to_next(self):
		self.cd = self.next_cd

	def set_regression(self, r, sensor_num):
		self.regression[sensor_num] = r

	def get_regression(self,sensor_num):
		return self.regression[sensor_num]

	def initialize_regression(self,SENSOR_MAX_NUM):
		for i in range(SENSOR_MAX_NUM):
			self.p[i][0][0]=100000.0
			self.p[i][0][1]=0.0
			self.p[i][1][0]=0.0
			self.p[i][1][1]=100000.0
			self.b[i][0]=1.0
			self.b[i][1]=10.0
			self.regression[i] = 10.0

	def update_regression(self,p,b,USE_SENSOR):
		self.p = p
		self.b = b
		for i in range(len(USE_SENSOR)):
			self.regression[USE_SENSOR[i]] = b[USE_SENSOR[i]][1]

	def add_change_count(self):
		self.change_count += 1

	def get_change_count(self):
		return self.change_count

	def set_change_count(self,count):
		self.change_count = count

	def init_change_count(self):
		self.change_count = 0

	def set_change_var(self,var):
		self.change_var = var

	def get_change_var(self):
		return self.change_var

	def set_neighbor(self,neighbor):
		self.neighbor = neighbor

	def get_neighbor(self):
		return self.neighbor

	def add_min_count(self):
		self.min_count += 1

	def get_min_count(self):
		return self.min_count

	def init_min_count(self):
		self.min_count = 0

	def set_on_flg(self,flg):
		self.on_flg = flg

	def get_on_flg(self):
		return self.on_flg

	def set_off_flg(self,flg):
		self.off_flg = flg

	def get_off_flg(self):
		return self.off_flg

	def set_target_cd(self,cd):
		self.target_cd = int(cd)

	def get_target_cd(self):
		return self.target_cd

	def get_on_count(self):
		return self.on_count

	def add_on_count(self):
		self.on_count += 1

	def init_on_count(self):
		self.on_count = 0
