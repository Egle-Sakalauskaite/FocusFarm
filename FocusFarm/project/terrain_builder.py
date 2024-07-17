import noise
from PIL import Image
import math

import random


char_orientations_dict = {'NE': (0,-1), 'SE': (1,0), 'SW': (0,1), 'NW': (-1,0)}

class Tile:
	def __init__(self, x_pos: int, y_pos: int, z_pos: int, texture_id=0, terrain_height='low'):
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.z_pos = z_pos
		self.texture_id = texture_id
		self.terrain_height = terrain_height


class Character:
	# x_pos and y_pos are map coordinates (tile row and column)
	def __init__(self, x_pos: int, y_pos: int, char_name: str, state: str, orientation: str, animation_num: str, char_id):
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.char_name = char_name
		self.state = state
		self.animation_num = animation_num
		self.orientation = orientation
		self._pos_changed = True
		self.id = char_id

		# the time between each move in frames 
		self.move_time = 8

		# the number of frames since the last move
		self.frames_since_moved = 0

		# target tiles both tuples (column, row)
		self.next_tile = None
		self.target_tile = None

	# returns map column, row, z_pos
	# caching of the position because looping over all tiles is time intensive
	def get_full_pos(self, map_tiles) -> tuple[int,int,int]:
		if self._pos_changed:
			underlying_tile = None
			for i in range(len(map_tiles)):
				if map_tiles[i].x_pos == self.x_pos and map_tiles[i].y_pos == self.y_pos:
					underlying_tile = map_tiles[i]
					break
			
			if underlying_tile is None:
				print(f"underlying_tile for character position ({self.x_pos}, {self.y_pos}) not found")
				return 0, 0, 0

			self._z_pos = underlying_tile.z_pos + 1
			self._pos_changed = False
			
		return self.x_pos, self.y_pos, self._z_pos

	# move to a new tile position
	def move_to_next(self):
		if self.next_tile is not None:
			self.x_pos = self.next_tile[0]
			self.y_pos = self.next_tile[1]

			self.frames_since_moved = 0
			self._pos_changed = True
			self.next_tile = None
		else:
			print(f"no next tile set; could not move")

	# move in incremental steps towards the next tile
	def move_increment(self):

		def euclidean_dist(x_pos, y_pos, target_x, target_y):
			return math.sqrt((target_x - x_pos) ** 2 + (target_y - y_pos) ** 2)

		steps_left = self.move_time - self.frames_since_moved
		# ensures that the new z_pos gets calculated once the char is on the target square
		if steps_left <= 1:
			self.move_to_next()
		else:
			# distance_to_next = euclidean_dist(self.x_pos, self.y_pos, *self.next_tile)
			# the total distance to the next tile is always 1 (only 4 move directions)
			global char_orientations_dict
			direction = char_orientations_dict[self.orientation]

			self.x_pos += direction[0] * (1 / self.move_time)
			self.y_pos += direction[1] * (1 / self.move_time)

class Node:
	def __init__(self, column, row):
		self.column = column
		self.row = row


class TerrainBuilder:

	def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
		self.SCREEN_WIDTH = SCREEN_WIDTH
		self.SCREEN_HEIGHT = SCREEN_HEIGHT

		# terrain generation constants and data
		self.high_terrain_tile_ids = range(0,16)
		self.high_terrain_tile_dec_ids = range(49,56)
		self.high_terrain_tile_dec_prob = 5 # percent

		self.mid_terrain_tile_ids = range(21,37)
		self.mid_terrain_tile_dec_ids = range(48,58)
		self.low_terrain_tile_ids = range(94,97)
		self.low_terrain_tile_dec_ids = range(74,79)

		self.high_terrain_min = 0.57
		self.mid_terrain_min = 0.40
		self.low_terrain_dec_min = 0.39


	# generates a 2d perlin noise map
	# which is later used to procedurally generate the terrain
	# the width and height are the number of tile rows/columns
	def generate_noise_map(self, seed, width=20, height=20):
		# noise params
		scale = 0.1
		octaves = 6
		persistence = 0.1
		lacunarity = 2.0

		noise_map = [[0.0] * width for _ in range(height)]

		# generate noise for each pixel in the noise map
		# values are in range [-1,1]
		for x in range(width):
			for y in range(height):
				value = noise.pnoise2(
								x * scale, 
								y * scale,
								octaves=octaves,
								persistence=persistence,
								lacunarity=lacunarity,
								repeatx=1024,
								repeaty=1024,
								base=seed
								)

				# normalize
				normalized_value = (value + 1) / 2.0

				noise_map[y][x] = normalized_value

		return noise_map

	def generate_binary_noise_map(self, seed: int, width: int, height: int, num_tiles_map: int) -> list[list[int]]:
		# threshold value is the percentage of filled tiles to empty tiles
		threshold = num_tiles_map / (width * height)

		# noise params
		scale = 0.1
		octaves = 6
		persistence = 0.1
		lacunarity = 2.0

		noise_map = [[0] * width for _ in range(height)]

		# generate noise for each pixel in the noise map
		# values are in range [-1,1]
		for x in range(width):
			for y in range(height):
				value = noise.pnoise2(
								x * scale, 
								y * scale,
								octaves=octaves,
								persistence=persistence,
								lacunarity=lacunarity,
								repeatx=1024,
								repeaty=1024,
								base=seed
								)

				# normalize
				normalized_value = (value + 1) / 2.0

				bin_val = 0
				if normalized_value > threshold:
					bin_val = 1

				noise_map[y][x] = bin_val

		self.boundary_node_map = noise_map
		return noise_map


	def flood_fill(self, node, node_counter, max_nodes, start_node):
		# if node not within bounds
		try:
			# if outside bounds
			if self.boundary_node_map[node.row][node.column] == 0:
				return node_counter  
			# if already visited
			if self.final_shape_node_map[node.row][node.column] == 1:
				return node_counter

		except IndexError:
			return node_counter  # Return node_counter without incrementing

		# or if max number of nodes is reached
		if node_counter >= max_nodes:
			return node_counter

		self.final_shape_node_map[node.row][node.column] = 1
		node_counter += 1

		# Recursively fill in neighboring nodes, prioritizing those closer to the start node
		neighbors = [
			# south
			(Node(row=node.row+1, column=node.column), math.sqrt((node.row+1 - start_node.row)**2 + (node.column - start_node.column)**2)),
			# north
			(Node(row=node.row-1, column=node.column), math.sqrt((node.row-1 - start_node.row)**2 + (node.column - start_node.column)**2)),
			# west
			(Node(row=node.row, column=node.column-1), math.sqrt((node.row - start_node.row)**2 + (node.column-1 - start_node.column)**2)),
			# east
			(Node(row=node.row, column=node.column+1), math.sqrt((node.row - start_node.row)**2 + (node.column+1 - start_node.column)**2))
		]

		# Sort the neighbors by their distance to the start node
		neighbors.sort(key=lambda x: x[1])

		# Recursively fill in the closest neighboring nodes
		for neighbor, _ in neighbors:
			node_counter = self.flood_fill(neighbor, node_counter, max_nodes, start_node)

		return node_counter  
	

	# method performs a circular flood fill from the center
	# radius determined by given total number of tiles
	# returns a pixelmap with given width, height
	# in which values 1 represent land
	def create_island_pixelmap(self, num_tiles_island, noise_map_width, noise_map_height):
		island_radius = int(math.sqrt(num_tiles_island / math.pi)) + 1
		island_pixel_map = [[0]*noise_map_width for _ in range(noise_map_height)]
		island_tiles_counter = 0

		center_x = noise_map_width // 2
		center_y = noise_map_height // 2
		stack = [(center_x, center_y)]

		while stack:
			x, y = stack.pop()

			# check if within bounds and not already visited
			if (
				0 <= x < noise_map_width
				and 0 <= y < noise_map_height
				and island_pixel_map[x][y] != 1
				and (x - center_x) ** 2 + (y - center_y) ** 2 <= island_radius ** 2
				and island_tiles_counter < num_tiles_island
			):
				island_pixel_map[x][y] = 1
				island_tiles_counter += 1

				# Add neighboring pixels to the stack
				stack.append((x + 1, y))
				stack.append((x - 1, y))
				stack.append((x, y + 1))
				stack.append((x, y - 1))

		print(f"placed {island_tiles_counter} tiles")
		return island_pixel_map


	def find_first_node(self, noise_map_width, noise_map_height):
		x,y = noise_map_width//2, noise_map_height//2
		while self.boundary_node_map[y][x] == 0 and y > 0:
			y -= 1

		return Node(row=y, column=x)

	# generates the island terrain
	# returns a list of Tile objects 
	def generate_terrain(self, seed=None, num_tiles_map=400, shape='square'):
		# pick tile id at random
		# still gives deterministic results
		# because the number generator is initialized with a set seed
		def pick_tile_id(main_noise_val: float) -> tuple[int,str]:
			terrain_type_identifier = ''
			# high terrain (dirt)
			if main_noise_val > self.high_terrain_min:
				texture_id = random.choice(self.high_terrain_tile_ids)
				terrain_type_identifier = 'high'
			# medium terrain (grass)
			elif main_noise_val > self.mid_terrain_min:
				texture_id = random.choice(self.mid_terrain_tile_ids)
				terrain_type_identifier = 'mid'
			# low terrain (water)
			else:
				terrain_type_identifier = 'low'
				if main_noise_val > self.low_terrain_dec_min:
					texture_id = random.choice(self.low_terrain_tile_dec_ids)
				else:
					texture_id = random.choice(self.low_terrain_tile_ids)

			return texture_id, terrain_type_identifier

		# get the z position of the tile based on the main noisemap value
		# water tiles are always on z=0
		def get_tile_height(noise_val: float) -> int:
			if noise_val > self.mid_terrain_min:
				return int((noise_val - 0.5) * 10)
			else:
				return 0

		def noise_shape_island(noise_map_width, noise_map_height, num_tiles_map):
			self.boundary_node_map = self.generate_binary_noise_map(seed=seed+2, width=noise_map_width, height=noise_map_height, num_tiles_map=num_tiles_map)
			self.final_shape_node_map = [[0] * noise_map_width for _ in range(noise_map_height)]
			start_node = self.find_first_node(noise_map_width, noise_map_height)
			self.flood_fill(start_node, 0, num_tiles_map, start_node)
			return self.final_shape_node_map

		def square_shape_island(noise_map_width, noise_map_height, num_tiles_map):
			exact_w_h = int(math.sqrt(num_tiles_map))
			border_w = (noise_map_width - exact_w_h) // 2
			border_h = (noise_map_height - exact_w_h) // 2
			pixel_map = [[0]*noise_map_width for _ in range(noise_map_height)]
			tiles_counter = 0

			for y in range(border_h, noise_map_height - border_h):
				for x in range(border_w, noise_map_width - border_w):
					pixel_map[y][x] = 1
					tiles_counter += 1

			print(f"tiles placed: {tiles_counter}")
			return pixel_map



		if seed is None:
			seed = random.randint(1,1000)
		print(f"the seed used was: {seed}")

		noise_map_width = int(math.sqrt(num_tiles_map * 2))
		noise_map_height = int(math.sqrt(num_tiles_map * 2))

		self.noise_map_width = noise_map_width
		self.noise_map_height = noise_map_height

		# generate perlin noise map for terrain 
		main_noise_map = self.generate_noise_map(seed, width=noise_map_width, height=noise_map_height)

		# noise shaped island
		if shape == 'noise':
			island_node_map = noise_shape_island(noise_map_width, noise_map_height, num_tiles_map)
		# circular island
		elif shape == 'circle':
			island_node_map = self.create_island_pixelmap(num_tiles_map, noise_map_width, noise_map_height)
		# square island
		elif shape == 'square':
			island_node_map = square_shape_island(noise_map_width, noise_map_height, num_tiles_map)
		elif shape == 'fill':
			island_node_map = [[1]*noise_map_width for _ in range(noise_map_height)]

		map_tiles = []

		# create a 2d list that keeps track of walkable tiles (for characters)
		# binary values, 1 for walkable
		walkable_tiles_map = [[0]*noise_map_width for _ in range(noise_map_height)]

		# set the seed for the random number generator
		random.seed(seed)

		for row_num in range(noise_map_width):
			for column_num in range(noise_map_height):
				main_noise_val = main_noise_map[row_num][column_num]
				island_noise_val = island_node_map[row_num][column_num]
				if island_noise_val == 1:
					# t = Tile((row_num - noise_map_height / 2), (column_num - noise_map_width / 2), get_tile_height(main_noise_val))
					t = Tile(row_num, column_num, get_tile_height(main_noise_val))
					t.texture_id, t.terrain_height = pick_tile_id(main_noise_val)
					map_tiles.append(t)

					# if terrain in high or mid then it is walkable
					if t.terrain_height == 'mid' or t.terrain_height == 'high':
						walkable_tiles_map[row_num][column_num] = 1

		# self.place_terrain_decorations(map_tiles)

		return map_tiles

	def sort_map_tiles(self, map_tiles):
		mid_x = self.noise_map_width // 2
		mid_y = self.noise_map_height // 2

		return sorted(map_tiles, key=lambda tile: (tile.x_pos**2 + tile.y_pos**2))



	# places decorations (stones, tree trunks) on suitable tiles (high or mid terrain)
	# when a decoration is placed, the tile becomes unwalkable
	def place_terrain_decorations(self, map_tiles):
		for tile in map_tiles:
			# high terrain decorations:
			if tile.terrain_height == 'high':
				# if some probability
				if random.randint(1,100) <= self.high_terrain_tile_dec_prob:
					# place a random decoration on tile
					dec_id = random.choice(self.high_terrain_tile_dec_ids)
					dec_tile = Tile(tile.x_pos, tile.y_pos, tile.z_pos+1, dec_id, 'decoration')
					map_tiles.append(dec_tile)




def count_zeros_2d(my_list):
    count = 0
    for row in my_list:
        for element in row:
            if element == 0:
                count += 1
    return count




