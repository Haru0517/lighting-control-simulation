from light import *
from sensor import *
import pygame
from pygame.locals import *
import sys
import os
import math
import random
import time
import copy

argv = sys.argv
argc = len(argv)



def main(mode,USE_SENSOR,system_message,message_count,pattern_num):
	LIGHT_NUM = 15				#照明台数
	SENSOR_MAX_NUM = 99
	SENSOR_NUM = len(USE_SENSOR)
	STEP_LIMIT = 100000000
	LOOP_LIMIT = 100000000
	WEIGHT = 8
	HIGH_THRESHOLD = 0.2
	MIDDLE_THRESHOLD = 0.1
	LOW_THRESHOLD = 0.05
	TOLERANCE = 20
	MAX_LUMINANCE = 1300			#最大点灯光度
	MIN_LUMINANCE = MAX_LUMINANCE*0.3	#最小点灯光度
	INITIAL_CD = MIN_LUMINANCE
	STEP_TIME = 0.05			#1ステップのスリープ秒数
	FUNC_THRESHOLD = HIGH_THRESHOLD
	SHC_STEP = 50
	THRESHOLD = 0.01
	CHANGE_TARGET_STEP = 10000000
	MAX_DATA_NUM = 500
	DB_CHANGE_RATE = 0.1
	WRITE_TOLERANCE = TOLERANCE * SENSOR_NUM
	database = []
	db_flg = False
	simulation_flg = False
	light = []				#照明の配列
	sensor = []				#センサの配列
	loop_count = 0
	OFFSET_X = 0
	OFFSET_Y = 0
	DISTANCE = 0
	LIGHT_POS = []
	SENSOR_POS = []
	check_flg = [True,False,False]

	conver_count = 0
	convergence_flg = False
	convergence_flg_t = False

	pressed_sensor = -1
	mouse_pressed = False

	pause_flg = False

	ill_pattern = [[300,500,400],[400,750,600],[300,500,700],[600,450,750],[700,400,700,400]]

	if mode == '1':
		OFFSET_X = 214
		OFFSET_Y = 156
		DISTANCE = 167
		for i in range(LIGHT_NUM*2):
			LIGHT_POS.append( (OFFSET_X+(i//5)*DISTANCE,OFFSET_Y+(i%5)*DISTANCE) )

		DISPLAY_WIDTH = 1280
		DISPLAY_HEIGHT = 960
		SCR_RECT = Rect(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT)
		pygame.init()
		myfont = pygame.font.SysFont('Arial', 35)
		screen = pygame.display.set_mode(SCR_RECT.size)
		pygame.display.set_caption('知的照明システム 光度収束シミュレータ')
		roomImg = pygame.image.load("./img/1280x960/room1280x960.png").convert()  #部屋画像
		sensorImg = pygame.image.load("./img/1280x960/sensor.png").convert() #
		lum20Img = pygame.image.load("./img/1280x960/luminance_20_4000.gif").convert_alpha()  #20%画像
		lum40Img = pygame.image.load("./img/1280x960/luminance_40_4000.gif").convert_alpha()  #40%画像
		lum60Img = pygame.image.load("./img/1280x960/luminance_60_4000.gif").convert_alpha()  #60%画像
		lum80Img = pygame.image.load("./img/1280x960/luminance_80_4000.gif").convert_alpha()  #80%画像
		lum100Img = pygame.image.load("./img/1280x960/luminance_100_4000.gif").convert_alpha()  #100%画像
	else:
		OFFSET_X = 107
		OFFSET_Y = 78
		DISTANCE = 83.5
		for i in range(LIGHT_NUM*2):
			LIGHT_POS.append( (OFFSET_X+(i//5)*DISTANCE,OFFSET_Y+(i%5)*DISTANCE) )
		SENSOR_OFFSET_X = 75
		SENSOR_OFFSET_Y = 376
		SENSOR_DISTANCE_X = 42
		SENSOR_DISTANCE_Y = 41
		for i in range(SENSOR_MAX_NUM):
			SENSOR_POS.append( [SENSOR_OFFSET_X+SENSOR_DISTANCE_X*(i//9),SENSOR_OFFSET_Y-SENSOR_DISTANCE_Y*(i%9)] )
		DISPLAY_WIDTH = 640
		DISPLAY_HEIGHT = 510
		SCR_RECT = Rect(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT)
		pygame.init()
		myfont = pygame.font.SysFont('Arial', 18)
		screen = pygame.display.set_mode(SCR_RECT.size)
		pygame.display.set_caption('知的照明システム収束シミュレータ')
		roomImg = pygame.image.load("./img/640x480/room640x480.png").convert()  #部屋画像
		sensorImg = pygame.image.load("./img/640x480/sensor.png").convert()
		upImg = pygame.image.load("./img/640x480/arrow_up.png").convert()
		downImg = pygame.image.load("./img/640x480/arrow_down.png").convert()
		lum20Img = pygame.image.load("./img/640x480/luminance_20_4000.gif").convert_alpha()  #20%画像
		lum40Img = pygame.image.load("./img/640x480/luminance_40_4000.gif").convert_alpha()  #40%画像
		lum60Img = pygame.image.load("./img/640x480/luminance_60_4000.gif").convert_alpha()  #60%画像
		lum80Img = pygame.image.load("./img/640x480/luminance_80_4000.gif").convert_alpha()  #80%画像
		lum100Img = pygame.image.load("./img/640x480/luminance_80_4000.gif").convert_alpha()  #100%画像
		empty_box = pygame.image.load("./img/640x480/shikaku.png").convert()
		check_box = pygame.image.load("./img/640x480/check.png").convert()

	for i in range(LIGHT_NUM):
		light.append(Light(i,INITIAL_CD,INITIAL_CD,WEIGHT,MAX_LUMINANCE,MIN_LUMINANCE,SENSOR_NUM,SENSOR_MAX_NUM))
		light[i].initialize_regression(SENSOR_MAX_NUM)

	for i in range(SENSOR_MAX_NUM):
		sensor.append(Sensor(i,HIGH_THRESHOLD,MIDDLE_THRESHOLD,LOW_THRESHOLD))

	#ステップ数初期化
	step = 0

	#目標照度を設定
#	for i in range(SENSOR_NUM):
#		sensor[i].set_target_illuminance(random.randint(MIN_ILLUMINANCE,MAX_ILLUMINANCE))
	for i in range(SENSOR_NUM):
		sensor[USE_SENSOR[i]].set_target_illuminance(ill_pattern[pattern_num-1][i])

	# sensor[USE_SENSOR[0]].set_target_illuminance(400)
	# sensor[USE_SENSOR[1]].set_target_illuminance(500)
	# sensor[USE_SENSOR[2]].set_target_illuminance(650)
	#初期光度で点灯
	for i in range(LIGHT_NUM):
		light[i].set_now_cd(INITIAL_CD)
	for i in range(LIGHT_NUM):
		#各センサの照度値を算出
		for j in range(SENSOR_NUM):
			sensor[USE_SENSOR[j]].calc_now_illuminance(i,light[i].get_now_cd())
	#各センサの照度値確定
	for i in range(SENSOR_NUM):
		sensor[USE_SENSOR[i]].update_illuminance(i)


##############################################################################
##------------------------------------------------------------

	#################################################
	## 全ての照明の各センサに対する影響度を調べる
	#################################################

	sensorEffects =  [[[0,0] for i in range(LIGHT_NUM)] for j in range(SENSOR_NUM)]

	#それぞれの照明を1個ずつ最大照度にする
	for i in range(LIGHT_NUM):
		light[i].set_now_cd(MAX_LUMINANCE)

		#3つのセンサへの影響度を保存する
		for j in range(SENSOR_NUM):
			for k in range(LIGHT_NUM):
				#各センサの照度値を算出
				sensor[USE_SENSOR[j]].calc_now_illuminance(k,light[k].get_now_cd())
			#各センサの照度値確定
			sensor[USE_SENSOR[j]].update_illuminance(j)
			sensorEffects[j][i] = [i, sensor[USE_SENSOR[j]].get_now_illuminance()]
			#print("照明{0} センサ{1} : {2}".format(i, j, sensorEffects[j][i]))

		#光度を元に戻す
		light[i].set_now_cd(MIN_LUMINANCE)


	#####################################################
	##各センサに対する照明ごとの順位（有効さ）を調べる
	#####################################################

	#有効順に並び替える
	for j in range(SENSOR_NUM):
		sensorEffects[j].sort(key=lambda x:x[1])
		sensorEffects[j].reverse()

	#配列の3番目の要素に順位を追加
	for j in range(SENSOR_NUM):
		for i in range(LIGHT_NUM):
			sensorEffects[j][i].append(i)

	#照明番号順に戻す
	for j in range(SENSOR_NUM):
		sensorEffects[j].sort(key=lambda x:x[0])

	#表示
	for j in range(SENSOR_NUM):
		print("センサ{0}".format(j))
		for i in range(LIGHT_NUM):
			print(sensorEffects[j][i])


	#現在光度
	currentCd = [INITIAL_CD for i in range(LIGHT_NUM)]

	file= open("result2.csv","w")#書き込みモードでオープン
	for i in range(LIGHT_NUM):
		file.write("照明{0},".format(i))
	for j in range(SENSOR_NUM):
		file.write("センサ{0},".format(j))
	file.write("\n")

	while(True):



#################################################
#						#
#	照明制御アルゴリズムを書くここから	#
#						#
#################################################
		#全てのセンサの目標との差を調べる
		diffLx = [0 for j in range(SENSOR_NUM)]			#目標との差[lx]
		currentLx = [0 for j in range(SENSOR_NUM)]	#現在の照度
		for j in range(SENSOR_NUM):
			currentLx[j] = sensor[USE_SENSOR[j]].get_now_illuminance()
			goalLx = ill_pattern[pattern_num-1][j]
			diffLx[j] = goalLx - currentLx[j]


		#最も絶対値の大きいdiffLxを調べる
		maxDiff = 0
		for j in range(SENSOR_NUM):
			if abs(diffLx[j]) > abs(maxDiff):
				maxDiff = diffLx[j]


		#最も遠いセンサとの比を計算する（比でやるべきかは分からん）
		diffLxRatio = [diffLx[j]/maxDiff for j in range(SENSOR_NUM)]
		#print(diffLxRatio)


		#各センサにおいて理想の順位となる照明を判断する（この計算式がベストかは分からん）
		idealOrder = [0 for j in range(SENSOR_NUM)]
		for j in range(SENSOR_NUM):
			#(0から14位までに入るようにclampする)
			idealOrder[j] = clamp(int(LIGHT_NUM*(1-diffLxRatio[j])), 0, LIGHT_NUM)
		#print(idealOrder)


		#idealOrderに基づいて，どの照明を変更するのが効果的か判断する
		bestLight = -1
		bestLightValue = 100		#とりあえず大きい数字入れとく
		for i in range(LIGHT_NUM):
			tmpValue = 0
			for j in range(SENSOR_NUM):
				tmpValue += abs(sensorEffects[j][i][2]-idealOrder[j])
			if tmpValue < bestLightValue:
				if (maxDiff > 0 and currentCd[i] < MAX_LUMINANCE) \
					or (maxDiff < 0 and MIN_LUMINANCE < currentCd[i]):
					bestLight = i
					bestLightValue = tmpValue


		#選択した照明の光度を変更する（この変更量が最適かは分からん）
		if(bestLight >= 0):
			nextCd = clamp(currentCd[bestLight]+maxDiff*0.5, MIN_LUMINANCE, MAX_LUMINANCE)
			light[bestLight].set_now_cd(nextCd)
			currentCd[bestLight] = nextCd


		#ファイルに照明番号の光度の変化を出力する
		for i in range(LIGHT_NUM):
			file.write("{0},".format(currentCd[i]))
		for j in range(SENSOR_NUM):
			file.write("{0},".format(currentLx[j]))
		file.write("\n")


		#デバッグ表示
		print("照明番号:{0}".format(bestLight), end="")
		print("　順位：", end="")
		for j in range(SENSOR_NUM):
			print(sensorEffects[j][bestLight][2],"", end="")
		print("　理想順位：", end="")
		for j in range(SENSOR_NUM):
			print(idealOrder[j],"", end="")
		print()



## ill_pattern[1][1] →　パターン1のセンサ１の目標照度

		##########################################################
		## 例							##
		## 照明0の光度を1000に設定する				##
		## light[0]からlight[14]まで15個の照明が存在する	##
		## 光度の上限は	MAX_LUMINANCE = 1300			##
		## 光度の下限は	MIN_LUMINANCE = MAX_LUMINANCE*0.3	##
		##########################################################


		#light[7].set_now_cd(1000)

		##########################################################
		## 例							##
		## 照明0から14まで光度1000を設定する			##
		## 光度の上限は	MAX_LUMINANCE = 1300			##
		## 光度の下限は	MIN_LUMINANCE = MAX_LUMINANCE*0.3	##
		##########################################################

		#for i in range(LIGHT_NUM):
		#	light[i].set_now_cd(1000)

		##########################################################
		## 例							##
		## 照度センサ0番の値を取得する				##
		##########################################################

		#ill = sensor[USE_SENSOR[0]].get_now_illuminance()
		#print(ill)


		##########################################################
		## 例							##
		## 照度センサ0から3番の値を取得する			##
		## 実機の場合はsensor.pyを編集する			##
		##########################################################

		#for i in range(SENSOR_NUM):
		#	print(sensor[USE_SENSOR[i]].get_now_illuminance())

		##########################################################
		## 例							##
		## 照度センサ0から3番の値を取得する別の書き方		##
		## 実機の場合はsensor.pyを編集する			##
		##########################################################

		#for i in USE_SENSOR:
		#	print(sensor[i].get_now_illuminance())



		##########################################################
		## 例							##
		## 実際の照明に現在光度を反映する			##
		## シミュレーションのときはコメントアウト		##
		##########################################################

		#update_cd(light,LIGHT_NUM)


#################################################
#						#
#	照明制御アルゴリズムを書くここまで	#
#						#
#################################################

		for i in range(LIGHT_NUM):
			#各センサの照度値を算出
			for j in range(SENSOR_NUM):
				sensor[USE_SENSOR[j]].calc_now_illuminance(i,light[i].get_now_cd())
		#各センサの照度値確定
		for i in range(SENSOR_NUM):
			sensor[USE_SENSOR[i]].update_illuminance(i)

		step += 1
		time.sleep(STEP_TIME)
		pause_count = 0
		while True:
			step,initflg,mouse_pressed,pressed_sensor,mouse_x,mouse_y,USE_SENSOR,SENSOR_NUM,pause_flg,STEP_TIME,system_message,message_count = chkKeyEvent(step,sensor,CHANGE_TARGET_STEP,SENSOR_MAX_NUM,sensorImg,USE_SENSOR,SENSOR_NUM,SENSOR_POS,STEP_TIME,mouse_pressed,pressed_sensor,pause_flg,system_message,message_count,LIGHT_NUM,light,LIGHT_POS,lum20Img,upImg,downImg,MIN_LUMINANCE,MAX_LUMINANCE,check_flg,empty_box,screen)
			# if pause_count == 0:
			display_update(screen,light,LIGHT_NUM,sensor,SENSOR_NUM,SENSOR_MAX_NUM,SENSOR_POS,USE_SENSOR,LIGHT_POS,myfont,roomImg,sensorImg,lum20Img,lum40Img,lum60Img,lum80Img,lum100Img,mode,mouse_pressed,pressed_sensor,mouse_x,mouse_y,system_message,upImg,downImg,pause_flg,empty_box,check_box,check_flg)
				# pause_count = 1
			if pause_flg == False:
				break

		if message_count > 0:
			message_count -= 1
		else:
			system_message = ''

		if initflg == True:
			break

	return step,USE_SENSOR,system_message,message_count

def clamp(value, _min, _max):
	return max(_min, min(value, _max))

def update_cd(light,LIGHT_NUM):
	cd_str = ""
	for i in range(LIGHT_NUM):
		cd_str += repr(light[i].get_now_cd()) + ',0,0,0,'

	with open("cd_info.txt","w") as f:
		f.write(cd_str)


def chkKeyEvent(step,sensor,CHANGE_TARGET_STEP,SENSOR_MAX_NUM,sensorImg,USE_SENSOR,SENSOR_NUM,SENSOR_POS,STEP_TIME,mouse_pressed,pressed_sensor,pause_flg,system_message,message_count,LIGHT_NUM,light,LIGHT_POS,lum20Img,upImg,downImg,MIN_LUMINANCE,MAX_LUMINANCE,check_flg,empty_box,screen):
	init_flg = False
	mouse_x = 0
	mouse_y = 0
	for event in pygame.event.get():
		if event.type == QUIT: sys.exit()
		if event.type == KEYDOWN:  # キーを押したとき
			# ESCキーならスクリプトを終了
			if event.key == K_ESCAPE:
				sys.exit()
			if event.key == K_SPACE:
				step = CHANGE_TARGET_STEP
				system_message = '目標照度変更'
				message_count = 23
			if event.key == K_BACKSPACE:
				init_flg = True
				system_message = '全点灯：収束開始'
				message_count = 20
			if event.key == K_DELETE:
				init_flg = True
				USE_SENSOR = [16,60,73]
				system_message = '初期状態'
				message_count = 10
			if event.key == K_p:
				if pause_flg == True:
					pause_flg = False
					system_message = ''
				else:
					pause_flg = True
					system_message = 'pause'
#			if event.key == K_1 and event.key == K_UP:
#				ill = sensor[USE_SENSOR[0]].set_target_illuminance+50
#				if ill > MAX_ILLUMINANCE:
#					ill = MAX_ILLUMINANCE
#				sensor[USE_SENSOR[0]].set_target_illuminance(ill)


			if event.key == K_UP:
				STEP_TIME -= 0.01
				if STEP_TIME < 0:
					STEP_TIME = 0
				system_message = '実行速度UP'
				message_count = 10
			if event.key == K_DOWN:
				STEP_TIME += 0.01
				system_message = '実行速度DOWN'
				message_count = 10

		if event.type == MOUSEBUTTONDOWN and event.button == 1:
			x, y = event.pos
			for i in range(LIGHT_NUM*2):
				if i % 2 == 0:
					if LIGHT_POS[i][0]+lum20Img.get_width()/2-20 < x and x < LIGHT_POS[i][0]+lum20Img.get_width()/2-20+upImg.get_width():
						if LIGHT_POS[i][1]-20 < y and y < LIGHT_POS[i][1]-20+upImg.get_height():
							if light[i//2].get_now_cd() + (math.factorial(check_flg.index(True)) + check_flg.index(True)*4) * 13 > MAX_LUMINANCE:
								light[i//2].set_now_cd(MAX_LUMINANCE)
							else:
								light[i//2].set_now_cd(light[i//2].get_now_cd() + (math.factorial(check_flg.index(True)) + check_flg.index(True)*4) * 13 )

					if LIGHT_POS[i][0]+lum20Img.get_width()/2-20 < x and x < LIGHT_POS[i][0]+lum20Img.get_width()/2-20+downImg.get_width():
						if LIGHT_POS[i][1] < y and y < LIGHT_POS[i][1]+downImg.get_height():
							if light[i//2].get_now_cd() - (math.factorial(check_flg.index(True)) + check_flg.index(True)*4) * 13 < MIN_LUMINANCE:
								light[i//2].set_now_cd(MIN_LUMINANCE)
							else:
								light[i//2].set_now_cd(light[i//2].get_now_cd() - (math.factorial(check_flg.index(True)) + check_flg.index(True)*4) * 13)
				#各センサの照度値を算出
				for j in range(SENSOR_NUM):
					if i % 2 == 0:
						sensor[USE_SENSOR[j]].calc_now_illuminance(i//2,light[i//2].get_now_cd())
			#各センサの照度値確定
			for i in range(SENSOR_NUM):
				sensor[USE_SENSOR[i]].update_illuminance(i)


			for i in USE_SENSOR:
				if SENSOR_POS[i][0] < x and x < SENSOR_POS[i][0]+sensorImg.get_width():
					if SENSOR_POS[i][1] < y and y < SENSOR_POS[i][1]+sensorImg.get_height():
						mouse_pressed = True
						pressed_sensor = i
						mouse_x = x
						mouse_y = y
			chk_flg_index = -1
			for i in range(3):
				if x > screen.get_width()-120+50*i and x < screen.get_width()-120+50*i+empty_box.get_width() and y > screen.get_height()-70 and y > screen.get_height()-70+empty_box.get_height():
					chk_flg_index = i

			if chk_flg_index != -1:
				for i in range(3):
					if i == chk_flg_index:
						check_flg[i] = True
					else:
						check_flg[i] = False


		if event.type == MOUSEBUTTONUP and event.button == 1:
			x, y = event.pos
			if mouse_pressed == True:
				mouse_pressed == False
				for i in range(SENSOR_MAX_NUM):
					if SENSOR_POS[i][0] < x and x < SENSOR_POS[i][0]+sensorImg.get_width():
						if SENSOR_POS[i][1] < y and y < SENSOR_POS[i][1]+sensorImg.get_height():
							if USE_SENSOR.count(i) != 0:
								mouse_pressed = True
								break
							try:
								USE_SENSOR[USE_SENSOR.index(pressed_sensor)] = i
							except ValueError:
								mouse_pressed = True
								break
							system_message = 'センサが移動されました'
							message_count = 10
							sensor[i].set_target_illuminance(sensor[pressed_sensor].get_target_illuminance())
							sensor[pressed_sensor].set_target_illuminance(0)
							mouse_x = x
							mouse_y = y
							step = 0
		if event.type == MOUSEBUTTONDOWN and event.button == 3:
			x, y = event.pos
			for i in range(SENSOR_MAX_NUM):
				if SENSOR_POS[i][0] < x and x < SENSOR_POS[i][0]+sensorImg.get_width():
					if SENSOR_POS[i][1] < y and y < SENSOR_POS[i][1]+sensorImg.get_height():
						if (i in USE_SENSOR) == False:
							USE_SENSOR.append(i)
							sensor[i].set_target_illuminance(300)
							SENSOR_NUM = len(USE_SENSOR)
							step = 0
						else:
							USE_SENSOR.remove(i)
							sensor[i].set_target_illuminance(0)
							SENSOR_NUM = len(USE_SENSOR)

	if mouse_pressed:
		mouse_x,mouse_y = pygame.mouse.get_pos()

	return step,init_flg,mouse_pressed,pressed_sensor,mouse_x,mouse_y,USE_SENSOR,SENSOR_NUM,pause_flg,STEP_TIME,system_message,message_count


def display_update(screen,light,LIGHT_NUM,sensor,SENSOR_NUM,SENSOR_MAX_NUM,SENSOR_POS,USE_SENSOR,LIGHT_POS,myfont,roomImg,sensorImg,lum20Img,lum40Img,lum60Img,lum80Img,lum100Img,mode,mouse_pressed,pressed_sensor,mouse_x,mouse_y,system_message,upImg,downImg,pause_flg,empty_box,check_box,check_flg):
	screen.fill((0,0,0))
	screen.blit(roomImg, (0,0))

	for i in range(LIGHT_NUM*2):
		if i % 2 == 0:
			if light[i//2].get_now_cd() == 0:
				continue
			elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() < 0.4:
				screen.blit(lum20Img,(LIGHT_POS[i][0]-lum20Img.get_width()/2,LIGHT_POS[i][1]-lum20Img.get_height()/2))
			elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() < 0.6:
				screen.blit(lum40Img,(LIGHT_POS[i][0]-lum40Img.get_width()/2,LIGHT_POS[i][1]-lum40Img.get_height()/2))
			elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() < 0.8:
				screen.blit(lum60Img,(LIGHT_POS[i][0]-lum60Img.get_width()/2,LIGHT_POS[i][1]-lum60Img.get_height()/2))
			elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() < 1:
				screen.blit(lum80Img,(LIGHT_POS[i][0]-lum80Img.get_width()/2,LIGHT_POS[i][1]-lum80Img.get_height()/2))
			elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() == 1:
				screen.blit(lum100Img,(LIGHT_POS[i][0]-lum100Img.get_width()/2,LIGHT_POS[i][1]-lum100Img.get_height()/2))


	if mode == '1':
		for i in range(LIGHT_NUM*2):
			if i % 2 == 0:
				text = myfont.render(repr(light[i//2].get_now_cd()*100//light[i//2].get_max_luminance())+'%', True, (0,0,0))
				if light[i//2].get_now_cd() == 0:
					screen.blit(text,(LIGHT_POS[i][0]-20,LIGHT_POS[i][1]-90))
					continue
				elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() < 0.4:
					screen.blit(text,(LIGHT_POS[i][0]-20,LIGHT_POS[i][1]-90))
				elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() < 0.55:
					screen.blit(text,(LIGHT_POS[i][0]-20,LIGHT_POS[i][1]-90))
				elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() < 0.7:
					screen.blit(text,(LIGHT_POS[i][0]-20,LIGHT_POS[i][1]-90))
				elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() < 0.85:
					screen.blit(text,(LIGHT_POS[i][0]-20,LIGHT_POS[i][1]-90))
				elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() < 1:
					screen.blit(text,(LIGHT_POS[i][0]-20,LIGHT_POS[i][1]-90))
				elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() == 1:
					screen.blit(text,(LIGHT_POS[i][0]-20,LIGHT_POS[i][1]-90))

		#sensor0
		screen.blit(sensorImg,(120*2,90*2))
		#current
		text = myfont.render(repr(sensor[USE_SENSOR[0]].get_now_illuminance()) + ' Lx', True, (0,0,0))
		screen.blit(text,(115*2,113*2))
		#mokuhyou
		text = myfont.render(repr(sensor[USE_SENSOR[0]].get_target_illuminance()) + ' Lx', True, (255,0,0))
		screen.blit(text,(115*2,130*2))

		#sensor1
		screen.blit(sensorImg,(328*2,132*2))
		#current
		text = myfont.render(repr(sensor[USE_SENSOR[1]].get_now_illuminance()) + ' Lx', True, (0,0,0))
		screen.blit(text,(322*2,157*2))
		#mokuhyou
		text = myfont.render(repr(sensor[USE_SENSOR[1]].get_target_illuminance()) + ' Lx', True, (255,0,0))
		screen.blit(text,(322*2,172*2))

		#sensor2
		screen.blit(sensorImg,(410*2,340*2))
		#current
		text = myfont.render(repr(sensor[USE_SENSOR[2]].get_now_illuminance()) + ' Lx', True, (0,0,0))
		screen.blit(text,(400*2,305*2))
		#mokuhyou
		text = myfont.render(repr(sensor[USE_SENSOR[2]].get_target_illuminance()) + ' Lx', True, (255,0,0))
		screen.blit(text,(400*2,320*2))

		#text = myfont.render('Intelligent Lighting System', True, (0,0,0))
		#screen.blit(text,(screen.get_width()-400,screen.get_height()-70))

		power = 0
		for i in range(LIGHT_NUM):
			power += light[i].get_now_cd()
		text = myfont.render('power ' + repr(power), True, (0,0,0))
		screen.blit(text,(10*2,screen.get_height()-70))

	else:
		for i in range(LIGHT_NUM*2):
			if i % 2 == 0:
				text = myfont.render(repr(light[i//2].get_now_cd()*100//light[i//2].get_max_luminance())+'%', True, (0,0,0))
				if light[i//2].get_now_cd() == 0:
					screen.blit(text,(LIGHT_POS[i][0]-10,LIGHT_POS[i][1]-45))
					continue
				elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() < 0.4:
					screen.blit(text,(LIGHT_POS[i][0]-10,LIGHT_POS[i][1]-45))
				elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() < 0.55:
					screen.blit(text,(LIGHT_POS[i][0]-10,LIGHT_POS[i][1]-45))
				elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() < 0.7:
					screen.blit(text,(LIGHT_POS[i][0]-10,LIGHT_POS[i][1]-45))
				elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() < 0.85:
					screen.blit(text,(LIGHT_POS[i][0]-10,LIGHT_POS[i][1]-45))
				elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() < 1:
					screen.blit(text,(LIGHT_POS[i][0]-10,LIGHT_POS[i][1]-45))
				elif light[i//2].get_now_cd()/light[i//2].get_max_luminance() == 1:
					screen.blit(text,(LIGHT_POS[i][0]-15,LIGHT_POS[i][1]-45))



	for i in range(LIGHT_NUM*2):
		if pause_flg == True:
			if i % 2 == 0:
				screen.blit(upImg,(LIGHT_POS[i][0]+lum20Img.get_width()/2-20,LIGHT_POS[i][1]-20))
				screen.blit(downImg,(LIGHT_POS[i][0]+lum20Img.get_width()/2-20,LIGHT_POS[i][1]))


#		print(USE_SENSOR)
		for i in USE_SENSOR:
			if mouse_pressed == True and i == pressed_sensor:
				screen.blit(sensorImg,(mouse_x-sensorImg.get_width()/2,mouse_y-sensorImg.get_height()/2))

			screen.blit(sensorImg,(SENSOR_POS[i][0],SENSOR_POS[i][1]))
			text = myfont.render(repr(sensor[i].get_target_illuminance()), True, (255,0,0))
			screen.blit(text,(SENSOR_POS[i][0]-30,SENSOR_POS[i][1]))
			text = myfont.render(repr(sensor[i].get_now_illuminance()), True, (0,0,0))
			screen.blit(text,(SENSOR_POS[i][0]-30,SENSOR_POS[i][1]+17))


		#text = myfont.render('Intelligent Lighting System', True, (0,0,0))
		#screen.blit(text,(screen.get_width()-240,screen.get_height()-50))

#		pygame.draw.circle(screen,(255,0,0),(320,240),15)

		power = 0
		for i in range(LIGHT_NUM):
			power += light[i].get_now_cd()
		text = myfont.render('power ' + repr(power//(13*15)) + ' %', True, (0,0,0))
		screen.blit(text,(10,screen.get_height()-50))

		pygame.draw.rect(screen,(255,255,255),Rect(0, screen.get_height()-30, screen.get_width(), 30))
		pygame.draw.line(screen,(0,0,0),(0,screen.get_height()-30),(screen.get_width(),screen.get_height()-30))


		#system message
		text = myfont.render(system_message, True, (127,0,0))
		screen.blit(text,(10,screen.get_height()-20))

	for box_num in range(3):
		if box_num == 0:
			text = myfont.render("1%", True, (127,0,0))
		else:
			text = myfont.render(repr(box_num*5) + "%", True, (127,0,0))

		screen.blit(text,(screen.get_width()-147+50*box_num,screen.get_height()-50))
		if check_flg[box_num] == True:
			screen.blit(check_box,(screen.get_width()-120+50*box_num,screen.get_height()-50))
		else:
			screen.blit(empty_box,(screen.get_width()-120+50*box_num,screen.get_height()-50))


	pygame.display.flip()


def calcDatabase(light,LIGHT_NUM,sensor,SENSOR_NUM,database):
	value = 10000
	ret = ''
	for data in database:
		tmp = calcIlluminanceDiff(sensor,SENSOR_NUM,data[1])
		if tmp < value:
			value = tmp
			ret = data[0].split(' ')
	if len(ret) == 0:
		return

	for i in range(LIGHT_NUM):
		light[i].set_target_cd(ret[i])

def calcIlluminanceDiff(sensor,SENSOR_NUM,item):
	value = item.split(' ')
	ret = 0
	for i in range(SENSOR_NUM):
		ret += math.fabs( sensor[USE_SENSOR[i]].get_now_illuminance() - int(value[i]) )

	return ret

def writeDatabase(light,LIGHT_NUM,sensor,SENSOR_NUM,USE_SENSOR,database,TOLERANCE,MAX_DATA_NUM,WRITE_TOLERANCE):
	key = ''
	item = ''
	ret = ''
	sum = 0
	value = 10000
	write_flg = False
	for data in database:
		ret = data[1].split(' ')
		tmp = 0
		for i in range(SENSOR_NUM):
			tmp += math.fabs( sensor[USE_SENSOR[i]].get_now_illuminance() - int(ret[USE_SENSOR[i]]) )
		if tmp < value:
			value = tmp

	if value > WRITE_TOLERANCE:
		write_flg = True

	if write_flg == False:
		return

	for l in light:
		if l.get_num() != LIGHT_NUM-1:
			key += repr(l.get_now_cd()) + ' '
		else:
			key += repr(l.get_now_cd())

	for s in sensor:
		if s.get_num() != SENSOR_NUM-1:
			item += repr(s.get_now_illuminance()) + ' '
		else:
			item += repr(s.get_now_illuminance())

	if (key in database) == False and chkConvergence(sensor,SENSOR_NUM,USE_SENSOR) == False:
		if len(database) == MAX_DATA_NUM:
			database.pop(0)
		database.append( (key,item) )
		with open('database.txt','a') as f:
			f.write(key + ',' + item + '\n')


def chkConvergence(sensor, SENSOR_NUM,USE_SENSOR):
	for i in range(SENSOR_NUM):
		if math.fabs( sensor[USE_SENSOR[i]].get_now_illuminance() - sensor[USE_SENSOR[i]].get_target_illuminance() ) >= 50:
			return False
	return True

def chkTrueConvergence(sensor,SENSOR_NUM,USE_SENSOR,TOLERANCE):
	for i in range(SENSOR_NUM):
		if math.fabs( sensor[USE_SENSOR[i]].get_now_illuminance() - sensor[USE_SENSOR[i]].get_target_illuminance() ) >= TOLERANCE:
			return False
	return True

#回帰係数の計算
def cal_regression(Light,sensor,SENSOR_NUM,SENSOR_MAX_NUM,USE_SENSOR,THRESHOLD):
	x = 2*[0.0]
	y = SENSOR_MAX_NUM*[0.0]
	y_ = SENSOR_MAX_NUM*[0.0]
	e = SENSOR_MAX_NUM*[0.0]
	s = SENSOR_MAX_NUM*[0.0]
	w = [[0.0 for j in range(2)]for i in range(SENSOR_MAX_NUM)]
	p = Light.p
	b = Light.b
	R = 0.1
	x[0]= 1.0
	x[1]= Light.get_next_cd() - Light.get_now_cd()
	for i in USE_SENSOR:
		y[i] = sensor[i].get_next_illuminance() - sensor[i].get_now_illuminance()
		if  math.fabs(y[i]) > 50 :
			return 0

		#観測予測誤差共分散
		s[i]=( x[0]*p[i][0][0] + x[1]*p[i][1][0] )*x[0] + ( x[0]*p[i][0][1] + x[1]*p[i][1][1] )*x[1] +R

		#フィルタゲイン
		w[i][0]=(p[i][0][0]*x[0]+p[i][0][1]*x[1])/s[i]
		w[i][1]=(p[i][1][0]*x[0]+p[i][1][1]*x[1])/s[i]

		#推定誤差共分散
		p[i][0][0]=p[i][0][0]-w[i][0]*s[i]*w[i][0]
		p[i][0][1]=p[i][0][1]-w[i][0]*s[i]*w[i][1]
		p[i][1][0]=p[i][1][0]-w[i][1]*s[i]*w[i][0]
		p[i][1][1]=p[i][1][1]-w[i][1]*s[i]*w[i][1]

		#観測予測値
		y_[i]=x[0]*b[i][0]+x[1]*b[i][1]

		#観測予測誤差
		e[i]=y[i]-y_[i]

		#推定値
		b[i][0]=b[i][0]+w[i][0]*e[i]
		b[i][1]=b[i][1]+w[i][1]*e[i]
		if b[i][1] < THRESHOLD :
			b[i][1] = 0
		#if b[i][1] > 10 : b[i][1] = 10
	#回帰係数の更新
	Light.update_regression(p,b,USE_SENSOR)


#次光度決定関数
def nextGenerator(light, rank, neighbor_num):
	RAPID_INCREASE = [0.01,0.12]#G
	INCREASE = [-0.02,0.07]#F
	SLOW_INCREASE = [-0.03,0.05]#E
	ADJUSTMENT = [-0.02,0.02]#D
	SLOW_DECREASE = [-0.05,0.03]#C
	DECREASE = [-0.07,0.03]#B
	RAPID_DECREASE = [-0.10,-0.01]#A
	lum = 0
	OFF_DO_FLG = False
	#近傍選択(rank,neighbor_num)
	case = {(1,2):'C',(1,3):'D',(1,4):'E',(1,5):'F',(1,6):'G',
			(2,2):'B',(2,3):'C',(2,4):'D',(2,5):'E',(2,6):'F',
			(3,2):'A',(3,3):'B',(3,4):'C',(3,5):'D',(3,6):'E',
			(-1,1):'Z'}

	while True:

		if case[(rank,neighbor_num)] == 'Z':
			light.set_neighbor('Z')
			lum = int(light.get_now_cd() + light.get_now_cd() * random.uniform(RAPID_DECREASE[0],RAPID_DECREASE[1]))
		elif case[(rank,neighbor_num)] == 'A':
			light.set_neighbor('A_RAPID_DECREASE')
			lum = int(light.get_now_cd() + light.get_now_cd() * random.uniform(RAPID_DECREASE[0],RAPID_DECREASE[1]))
		elif case[(rank,neighbor_num)] == 'B':
			light.set_neighbor('B_DECREASE')
			lum = int(light.get_now_cd() + light.get_now_cd() * random.uniform(DECREASE[0],DECREASE[1]))
		elif case[(rank,neighbor_num)] == 'C':
			light.set_neighbor('C_SLOW_DECREASE')
			lum = int(light.get_now_cd() + light.get_now_cd() * random.uniform(SLOW_DECREASE[0],SLOW_DECREASE[1]))
		elif case[(rank,neighbor_num)] == 'D':
			light.set_neighbor('D_ADJUSTMENT')
			lum = int(light.get_now_cd() + light.get_now_cd() * random.uniform(ADJUSTMENT[0],ADJUSTMENT[1]))
		elif case[(rank,neighbor_num)] == 'E':
			light.set_neighbor('E_SLOW_INCREASE')
			if light.get_on_count() < 10 and light.get_now_cd() == 0:
				light.add_on_count()
			elif light.get_now_cd() == 0:
				lum = light.get_min_luminance()
				light.set_on_flg(True)
				light.init_min_count()
				light.init_on_count()
			else:
				lum = int(light.get_now_cd() + light.get_now_cd() * random.uniform(SLOW_INCREASE[0],SLOW_INCREASE[1]))
		elif case[(rank,neighbor_num)] == 'F':
			light.set_neighbor('F_INCREASE')
			if light.get_on_count() < 10 and light.get_now_cd() == 0:
				light.add_on_count()
			elif light.get_now_cd() == 0:
				lum = light.get_min_luminance()
				light.set_on_flg(True)
				light.init_min_count()
				light.init_on_count()
			else:
				lum = int(light.get_now_cd() + light.get_now_cd() * random.uniform(INCREASE[0],INCREASE[1]))
		elif case[(rank,neighbor_num)] == 'G':
			light.set_neighbor('G_RAPID_INCREASE')
			if light.get_on_count() < 10 and light.get_now_cd() == 0:
				light.add_on_count()
			elif light.get_now_cd() == 0:
				lum = light.get_min_luminance()
				light.set_on_flg(True)
				light.init_min_count()
				light.init_on_count()
			else:
				lum = int(light.get_now_cd() + light.get_now_cd() * random.uniform(RAPID_INCREASE[0],RAPID_INCREASE[1]))

		if lum > light.get_max_luminance():
			lum = light.get_max_luminance()
			break
		elif lum <= light.get_min_luminance()+6:
			lum = light.get_min_luminance()
			if light.get_min_count() > 10 and OFF_DO_FLG == True:
				lum = 0
				light.set_off_flg(True)
			light.add_min_count()
			break
		elif lum != light.get_now_cd():
			light.init_min_count()
			break

	light.set_next_cd(lum)


#表示
def printInfo(light, LIGHT_NUM, sensor, SENSOR_NUM,USE_SENSOR,power,step,SHC_STEP,db_flg):

	info = '---------------------------\n'
	if db_flg == True:
		info += 'algorithm : DB Estimate\n'
	elif step < SHC_STEP:
		info += 'algorithm : SHC\n'
	else:
		info += 'algorithm : ANA/RC\n'

	info += repr(step-SHC_STEP) + 'step (' + repr(step) + 'step)\n\n'

	info += '照明\n'
	for i in range(LIGHT_NUM):
		if step > SHC_STEP:
			light_info = repr(i+1) + ' lum ' + repr(light[i].get_now_cd()) + ' value ' + repr(int(light[i].get_objective_func_value())) + ' neighbor ' + repr(light[i].get_neighbor() ) + ' accept ' + repr(light[i].get_change_count()/step)  + '\n'
		else :
			light_info = repr(i+1) + ' lum ' + repr(light[i].get_now_cd()) + ' value ' + repr(int(light[i].get_objective_func_value())) + ' accept ' + repr( light[i].get_change_count()/step ) + '\n'
		for j in range(SENSOR_NUM):
			light_info += '[' + repr(USE_SENSOR[j]) + '] = ' + repr(int(light[i].get_regression(USE_SENSOR[j]) * 1000) / 1000.0) + ' '
		info += light_info + '\n'
	info += '\n'

	if chkConvergence(sensor,SENSOR_NUM,USE_SENSOR):
		info += '照度センサ (収束完了)\n'
	else :
		info += '照度センサ\n'
	for i in range(SENSOR_NUM):
		info += repr(sensor[USE_SENSOR[i]].get_num()) + ' current ' + repr(sensor[USE_SENSOR[i]].get_now_illuminance()) + '  target ' + repr(sensor[USE_SENSOR[i]].get_target_illuminance()) + '\n'
	info += '\n'

	info += '電力 ' + repr(power)
	print(info)


#重複のないmin以上，max未満の整数がcnt個格納されたリストを返す
def make_randint_list(min, max, cnt):
	list = []
	i = 0
	while cnt != i:
		r = random.randint(min, max-1)
		try:
			list.index(r)   # 既にリストに存在するか
		except ValueError as e:
			list.append(r)  # 無い場合はリストに格納
			i += 1
	return list


def load_image(filename, colorkey=None):
	filename = os.path.join("data", filename)
	try:
		image = pygame.image.load(filename)
	except pygame.error:
		print ('Cannot load image:' + filename)
		raise SystemExit
	image = image.convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	return image





if __name__ == '__main__':
	USE_SENSOR = [16,46,97] # pattern 1,2
#	USE_SENSOR = [16,60,73] # pattern 3
#	USE_SENSOR = [46,49,73] # pattern 4
#	USE_SENSOR = [46,49,73,76] # pattern 5
	pattern_num = 1

	system_message = ''
	message_count = 0
	while True:
		if argc == 2:
			step,USE_SENSOR,system_message,message_count = main(argv[1],USE_SENSOR,system_message,message_count,pattern_num)
		else:
			step,USE_SENSOR,system_message,message_count = main('0',USE_SENSOR,system_message,message_count,pattern_num)
