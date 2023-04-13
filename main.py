from gmsh_disperse_generator import*

Dis = Disper_Generator()

Dis.set_mesh('examples/micro.geo') #initial gmsh-file
Dis.sphere(0.1) #step move particle
Dis.k_move(0.001) #step move particle
Dis.number_object(800) #number particle
Dis.set_operation('Fragments') #Type boolean operation:  Difference or Fragments
Dis.run() #run script


