import numpy as np
import re
import random 
import math

class Obj():
	def __init__(self,number):
		self.__x = 0
		self.__y = 0
		self.__z = 0
		self.__radius = 0
		self.distance = np.zeros(number)

class Disper_Generator(Obj):
	"""docstring for Disper_Generator"""
	def __init__(self):
		self.__number = 0
		Obj.__init__(self,self.__number)

 
	def sphere(self,radius):
		self.__radius = radius
		return self.__radius


	def set_operation(self,type_):
		self.__type_ = type_
		return self.__type_

	def set_mesh(self,name):
		self.__name_mesh = name
		return self.__name_mesh

	def number_object(self,number):
		self.__number = number
		return self.__number

	def k_move(self,k_move):
		self.__k_move = k_move
		return self.__k_move


	def __read_box_point(self):
		with open(self.__name_mesh,'r') as f:
			self.list_file = f.readlines()
			for i in self.list_file:
				mark = (i.strip().split(';'))
				if mark[-1] == '//disp_generator':
					self.pos_object = int((mark[0][re.search(r'\(',mark[0]).span()[0]+1:re.search(r'\)',mark[0]).span()[0]]))
					coord = (mark[0][re.search(r'\{',mark[0]).span()[0]+1:re.search(r'\}',mark[0]).span()[0]]).split(',')
					self.node = [float(i) for i in coord]
					self.node[3] += self.node[0]
					self.node[4] += self.node[1]
					self.node[5] += self.node[2]
					break

	def __generate_random_position(self):
		self.object_ = [Obj(self.__number) for i in range(self.__number)]
		for i in range(self.__number):
			self.object_[i].__x = random.uniform(self.node[0]+self.__radius,self.node[3]-self.__radius)
			self.object_[i].__y = random.uniform(self.node[1]+self.__radius,self.node[4]-self.__radius)
			self.object_[i].__z = random.uniform(self.node[2]+self.__radius,self.node[5]-self.__radius)
			self.object_[i].__radius = self.__radius
		return

	def __moving(self):

		def reflection_move_boundary(obj_node,bl,br,radius):
			if obj_node < bl:
				obj_node = bl+radius*0.1

			if obj_node > br:
				obj_node = br-radius*0.1
			return obj_node		
					
		def move_point(d,step,delta,object_i,object_j):
			return delta*(object_i-object_j)/d*step

		blx = self.node[0]+self.__radius
		brx = self.node[3]-self.__radius
		bly = self.node[1]+self.__radius 
		bry = self.node[4]-self.__radius
		blz = self.node[2]+self.__radius 
		brz = self.node[5]-self.__radius

		number_contact = []
		while (True):
			k = 0
			for i in range(self.__number):
				flag = 0
				for j in range(i+1,self.__number):
					x_2 = (self.object_[i].__x-self.object_[j].__x)*(self.object_[i].__x-self.object_[j].__x)
					y_2 = (self.object_[i].__y-self.object_[j].__y)*(self.object_[i].__y-self.object_[j].__y)
					z_2 = (self.object_[i].__z-self.object_[j].__z)*(self.object_[i].__z-self.object_[j].__z)
					

					d = max(math.sqrt(x_2+y_2+z_2),self.object_[i].__radius*1e-3)
					self.object_[i].distance[j] = d
					self.object_[j].distance[i] = d

					if (d < self.object_[i].__radius+self.object_[j].__radius): 
						flag = 1

						delta = 1.0/(self.object_[i].__radius*self.object_[i].__radius+self.object_[j].__radius*self.object_[j].__radius)
						step = self.__k_move*(self.object_[i].__radius+self.object_[i].__radius)*(self.object_[i].__radius+self.object_[i].__radius) 

						DX = move_point(d,step,delta,self.object_[i].__x,self.object_[j].__x)
						DY = move_point(d,step,delta,self.object_[i].__y,self.object_[j].__y)
						DZ = move_point(d,step,delta,self.object_[i].__z,self.object_[j].__z)
						
						self.object_[i].__x += DX
						self.object_[i].__y += DY
						self.object_[i].__z += DZ

						self.object_[j].__x -= DX
						self.object_[j].__y -= DY
						self.object_[j].__z -= DZ

						self.object_[i].__x = reflection_move_boundary(self.object_[i].__x,blx,brx,self.__radius)
						self.object_[i].__y = reflection_move_boundary(self.object_[i].__y,bly,bry,self.__radius)
						self.object_[i].__z = reflection_move_boundary(self.object_[i].__z,blz,brz,self.__radius)
						
						self.object_[j].__x = reflection_move_boundary(self.object_[j].__x,blx,brx,self.__radius)
						self.object_[j].__y = reflection_move_boundary(self.object_[j].__y,bly,bry,self.__radius)
						self.object_[j].__z = reflection_move_boundary(self.object_[j].__z,blz,brz,self.__radius)

				if flag == 1:
					if k > 0: k-=1
				else:
					k+=1
			number_contact.append(k)
			print('iteration =', len(number_contact),'Progress =',int(number_contact[-1]/self.__number*100),'%')
			if number_contact[-1] == self.__number:
				print('End iteration on', k)
				break
		return

	def __generate_result_file(self):
		Volume = ''
		for i in range(self.__number):
			self.list_file.append(f"Sphere({self.pos_object+i+1}) = {{{self.object_[i].__x},{self.object_[i].__y},{self.object_[i].__z}, {self.object_[i].__radius}, -Pi/2, Pi/2, 2*Pi}};") # 
			Volume += 'Volume{'+str(self.pos_object+i+1)+'};'
		self.list_file.append(f"Boolean{self.__type_}{{Volume{{{str(self.pos_object)}}}; Delete;}} {{{Volume} Delete;}}") 
		with open('reuslt.geo','w') as f:
			for i in self.list_file:
				print(i.strip(),file=f)					
		return

	def run(self):

		print("Read input GMSH file")
		self.__read_box_point()
		print("Generate particles position")
		self.__generate_random_position()
		print("Moving particles")
		self.__moving()
		print("Save results file: reuslt.geo")
		self.__generate_result_file()
		print("End work")
		return

