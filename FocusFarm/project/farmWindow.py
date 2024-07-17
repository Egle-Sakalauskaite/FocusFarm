import pygame
import os

import math
import random


from terrain_builder import TerrainBuilder, Character, count_zeros_2d
from Timer_class import Timer


class FarmWindow:
    # takes number of user's nature points and the points trend (if losing points or gaining)
    def __init__(self, database, task=None):
        # clock to control fps
        self.clock = pygame.time.Clock()
        self.target_fps = 4

        # change this variable to toggle if the timer is shown
        self.SHOW_TIMER = True
        self.SHOW_TASK_NAME = True
        self.task_name = ''

        # enable debugging aids
        self.DEBUGGING = False

        # create instance of timer class
        # set timer time based on task duration
        self.timer = Timer()

        if task is not None:
            duration = task.est_duration - task.progress
            self.task_name = task.title
            self.task = task
        # if no task passed do not display the time
        else:
            self.SHOW_TIMER = False
            self.SHOW_TASK_NAME = False
        
        self.timer.set_max_duration(duration)

        # used for zooming in/out
        self.scaling_factor = 1.0

        # set database
        self.db = database

        self.db.create_table_characters()

        if self.DEBUGGING:
            self.debugging_startup()

        pygame.init()
        self.screen_width = 1000
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Farm Window")

        # Set the working directory to the script's directory
        script_directory = os.path.dirname(os.path.realpath(__file__))
        os.chdir(script_directory)

        # Use os.path.join to create file paths
        assets_dir = os.path.join("assets", "stag_icon.png")
        pygame_icon = pygame.image.load(assets_dir)
        pygame.display.set_icon(pygame_icon)

        pygame_icon = pygame.image.load(r'assets/stag_icon.png')
        pygame.display.set_icon(pygame_icon)
            

        # Create a hidden buffer for drawing the surface elements
        self.static_island_buffer = pygame.Surface((self.screen_width, self.screen_height))
        self.dynamic_buffer = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

        self.set_tileset_spritesheet(r"assets/spritesheet.png")
        self.set_character_spritesheet()
        self.set_font_spritesheet('assets/alphabet.png')

        map_seed, self.initial_nature_points, user_points_trend = self.db.get_user_data()

        self.generate_game()

    # some command line setup steps for debugging
    def debugging_startup(self):
        map_seed, nature_points, user_points_trend = self.db.get_user_data()

        print("------ FOCUSFARM -------\n\tDebugger\n")
        print("Current user stats:\n\
                (N) nature points: {nature_points}\n\
                (T) points trend: {user_points_trend}\n\
                (S) map seed: {map_seed}\n")
        change = input("do you want to change any of these (N/T/S), else type n")
        while change != 'n':
            if change == 'N':
                nature_points = int(input("desired number of nature points:\t"))
            elif change == 'T':
                points_trend = int(input("desired points trend:\t"))
            elif change == 'S':
                map_seed = int(input("desired map seed:\t"))
            change = input("do you want to change any of these (N/T/S), else type n")

        self.db.set_user_data(nature_points, user_points_trend, map_seed)
        print("succesfully saved data")
        

    # takes user's nature points (earned through finishing tasks)
    # converts to the island parameters:
    # num_tiles_island and num_animals
    # for now: every point gives one tile and every 50 points gives an animal
    def nature_points_to_island_params(self, nature_points):
        POINTS_PER_ANIMAL = 50
        POINTS_PER_TILE = 1

        num_animals = math.floor(nature_points / POINTS_PER_ANIMAL)
        num_tiles = math.floor(nature_points / POINTS_PER_TILE)

        return num_tiles, num_animals

    # determines the number of points from studying a given amount of time
    # for now: every 120 seconds gives one point
    def timer_to_nature_points(self, elapsed_time_s):
        if self.DEBUGGING:
            time_per_point_s = 5
        else:
            time_per_point_s = 300
        return self.initial_nature_points + math.floor(elapsed_time_s / time_per_point_s)


    def set_tileset_spritesheet(self, filename, tile_w=32, tile_h=32, num_tile_columns=11, num_tiles_total=121):
        self.tileset = pygame.image.load(filename)
        self._tile_w = tile_w
        self._tile_h = tile_h
        self._num_tile_columns = num_tile_columns
        self._num_tiles_total = num_tiles_total

    def set_character_spritesheet(self):
        # set the dict of the different characters which has a value of a dict
        # of the different states (as key) and their animation length (as value)
        self.character_states_anim = {
                                'stag': {
                                            'idle': 24,
                                            'walk': 11
                                    },
                                'boar': {
                                            'idle': 7,
                                            'walk': 4
                                    },
                                # 'wolf': {
                                #             'idle': 4
                                #     }
            }
        self.characters = []

        # constant character variables
        self.char_orientations_list = ['NE', 'SE', 'SW', 'NW']
        self.char_move_directions = [(0,-1), (1,0), (0,1), (-1,0)]
        self.char_states_list = ['idle', 'walk']

        self.character_spritesheets = dict()

        for animal, states in self.character_states_anim.items():
            for state, value in states.items():
                for orient in self.char_orientations_list:
                    file_path = f"assets/characters/{animal}_{orient}_{state}.png"
                    spritesheet_name = f"{animal}_{orient}_{state}"
                    image = pygame.image.load(file_path)
                    self.character_spritesheets[spritesheet_name] = image

    # when adding a new font, it is expected that this spritesheet first contains the alphabet (capitals)
    # then the numbers and finally the characters ($, :, ?, !). 
    # if not the case, change accordingly in get_letter_pos() method
    def set_font_spritesheet(self, filename, letter_w=160, letter_h=160, num_font_columns=8, num_font_rows=5):
        self._font_letter_w = letter_w
        self._font_letter_h = letter_h

        self._num_font_columns = num_font_columns
        self._num_font_rows = num_font_rows

        self.font_sheet = pygame.image.load(filename)

    # generate the island based on database user data and characters
    # retrieves these parameters and then calls the generate_island method
    # call every time a change is made to the database, so that the view updates
    def generate_game(self):

        # get game data from database
        map_seed, nature_points, user_points_trend = self.db.get_user_data()

		# make nature points an attribute
		# used in caching value for timer update method
        self.nature_points = nature_points

        self.num_tiles_island, self.num_animals = self.nature_points_to_island_params(nature_points)
        self.island_radius = int(math.sqrt(self.num_tiles_island / math.pi))

        self.generate_island(seed=map_seed)

    # generates the island by initializing the TerrainBuilder class
    # also blits the tile textures on the static island buffer surface
    def generate_island(self, seed):
        tb = TerrainBuilder(self.screen_width, self.screen_height)
        # num_tiles_map = int(math.pi * (self.island_radius**2))

        max_num_tiles = 500

        tiles_map_unsorted = tb.generate_terrain(seed=seed, num_tiles_map=max_num_tiles, shape='fill')
        self.tiles_map = tb.sort_map_tiles(tiles_map_unsorted)
        map_max_w_h = int(2 * math.sqrt(max_num_tiles))

        self.walkable_tiles_map = [[0]*map_max_w_h for _ in range (map_max_w_h)]
        self.blit_static_surface()

        # add animals to the island
        animals_to_add = self.num_animals - len(self.characters)
        for i in range(animals_to_add):
            self.add_random_character()

    def blit_static_surface(self):
        self.static_island_buffer.fill((255,255,255))

        self.num_tiles_island, self.num_animals = self.nature_points_to_island_params(self.nature_points)
        self.island_radius = int(math.sqrt(self.num_tiles_island / math.pi))

        for tile_index in range(self.num_tiles_island):
            tile = self.tiles_map[tile_index]
            tile_map_source_square = (*self.get_tile_texture(tile.texture_id), self._tile_w, self._tile_h)
            scaled_source_square = pygame.transform.scale(self.tileset.subsurface(tile_map_source_square), (self._tile_w * self.scaling_factor, self._tile_h * self.scaling_factor))
            screen_x, screen_y = self.tile_coords_to_screen_coords(tile.x_pos, tile.y_pos, tile.z_pos)
            self.static_island_buffer.blit(
                                            scaled_source_square,  
                                            (screen_x, screen_y),
                                            )

            # update walkable tiles map
            if tile.terrain_height == 'high' or tile.terrain_height == 'mid':
                self.walkable_tiles_map[tile.y_pos][tile.x_pos] = 1

            # add visual aids for debugging purposes
            if self.DEBUGGING:
                if self.walkable_tiles_map[tile.y_pos][tile.x_pos] == 1:
                    color = (0,255,0)
                else:
                    color = (255,0,0)
                line_start_coords = (screen_x + self._tile_w / 4, screen_y + self._tile_h // 2)
                line_end_coords = (screen_x + (3 * self._tile_w) / 4, screen_y + self._tile_h // 2)
                pygame.draw.line(self.static_island_buffer, color, line_start_coords, line_end_coords)


    # isometric coords to screen coordinates
    def tile_coords_to_screen_coords(self, tile_column, tile_row, tile_z):
        # the y position of the tile has to be adjusted to make tiles appear on the same level
        # this adjustment is done based on distance to the origin
        # Adjust the vertical position by a fraction of the tile height 
        # also take into account the z position of the tile
        vertical_adjustment = (self._tile_h / 4) * (tile_column + tile_row) + (self._tile_h / 4) * tile_z

        x = (self.screen_width / (2 * self.scaling_factor)) + (tile_column - tile_row) * (self._tile_w / 2)
        y = (0.5 - (1/40) * self.island_radius) * self.screen_height * (2 - self.scaling_factor) + (tile_column + tile_row) * (self._tile_h / 2) - vertical_adjustment

        return x * self.scaling_factor, y * self.scaling_factor

    # isometric coords to screen coordinates
    # adjusted for the tile width and height
    def tile_coords_to_screen_coords_tile_size_adjusted(self, tile_column, tile_row, tile_z, tile_w, tile_h):
        x_un, y_un = self.tile_coords_to_screen_coords(tile_column, tile_row, tile_z)

        width_adj = (tile_w - self._tile_w) // 2
        height_adj = (tile_h - self._tile_h) // 2

        x = x_un - width_adj * self.scaling_factor
        y = y_un - height_adj * self.scaling_factor
        
        return x, y

    # return the x,y pos of the texture on the spritemap by id
    def get_tile_texture(self, texture_id: int) -> tuple[int, int]:
        if not isinstance(texture_id, int):
            raise ValueError('texture id should be an int')
        texture_id = texture_id % self._num_tiles_total
        # Create a subsurface for the tile
        tile_x = (texture_id % self._num_tile_columns) * self._tile_w
        tile_y = math.floor(texture_id / self._num_tile_columns) * (self._tile_h)
        return tile_x, tile_y

    # place tile on the screen
    # this will blit to the dynamic surface
    # for static tiles use the generate_island method
    def place_tile(self, tile):
        tile_map_source_square = (*self.get_tile_texture(tile.texture_id), self._tile_w, self._tile_h)
        scaled_source_square = pygame.transform.scale(self.tileset.subsurface(tile_map_source_square), (self._tile_w * self.scaling_factor, self._tile_h * self.scaling_factor))
        self.dynamic_buffer.blit(
                                        scaled_source_square,  
                                        self.tile_coords_to_screen_coords(tile.x_pos, tile.y_pos, tile.z_pos),
                                        )

    # get a random terrain tile position that exists and is mid or high (not water)
    # get random column, row from the walkable_tiles_map
    # this map is also updated according to other animal's positions
    def get_random_walkable_tile_pos(self) -> tuple[int,int]:

        for i in range(len(self.walkable_tiles_map)**2):
            random_row = random.randint(0, len(self.walkable_tiles_map) - 1)
            random_column = random.randint(0, len(self.walkable_tiles_map[0]) - 1)

            if self.walkable_tiles_map[random_row][random_column] == 1:
                return random_column, random_row

        print("No walkable tile found")
        return None, None
       

    # add a new character. Creates a new instance of the Character class
    # random animal in random non-water position which does not already contain an animal
    def add_random_character(self):
        # create all random character attributes
        random_animal = random.choice(list(self.character_states_anim.keys()))
        random_tile_col, random_tile_row = self.get_random_walkable_tile_pos()
        start_state = 'idle'
        random_orientation = random.choice(self.char_orientations_list)
        animation_len = self.character_states_anim[random_animal][start_state]
        random_anim_num = random.randint(0, animation_len - 1)


        # if a walkable tile was found
        if random_tile_col is not None  and random_tile_row is not None:
            # create instance of the character class
            new_char = Character(random_tile_col, random_tile_row, random_animal, start_state, random_orientation, random_anim_num)

            self.characters.append(new_char)

            # update the walkable tiles map (tile with animal on it is not walkable)
            self.walkable_tiles_map[random_tile_row][random_tile_col] == 0

            # add the character to the database
            self.db.add_character(new_char)

    # add a list of characters (retrieved from database)
    def add_characters(self):
        chars = self.db.retrieve_characters()
        self.characters.extend(chars)

        # update walkable tiles map for all characters
        for char in self.characters:
            self.walkable_tiles_map[char.y_pos][char.x_pos] == 0


    def move_character(self, char):
        def find_next_tile(char):
            # find next tile
            # loop over all directions and calculate their distances
            move_directions_with_distances = []
            for direction in self.char_move_directions:
                next_tile = (char.x_pos + direction[0], char.y_pos + direction[1])
                distance = abs(next_tile[0] - char.target_tile[0]) + abs(next_tile[1] - char.target_tile[1])
                move_directions_with_distances.append((direction, distance))

            # Sort the list based on distances
            sorted_move_directions = sorted(move_directions_with_distances, key=lambda x: x[1])

            char.next_tile = None

            # loop over first 3 sorted move directions to find the best tile that is walkable
            # first 3 because otherwise moving backwards
            for move in sorted_move_directions[:3]:
                move_dir = move[0]
                next_tile_x, next_tile_y = char.x_pos + move_dir[0], char.y_pos + move_dir[1]
                # if the tile is indeed walkable
                if self.walkable_tiles_map[next_tile_y][next_tile_x] == 1:
                    # and if the next tile is not the last tile (ijsberen)
                    if next_tile_x != char.last_tile[0] or next_tile_y != char.last_tile[1]:
                        char.next_tile = (next_tile_x, next_tile_y)
                        char.orientation = self.char_orientations_list[self.char_move_directions.index(move_dir)]
                        break
                    else:
                        print("ijsbeer")
            
        if char.target_tile is None:
            # pick new random target tile
            char.target_tile = self.get_random_walkable_tile_pos()

        # if next tile has not been calculated yet
        if char.next_tile is None:
            find_next_tile(char)

        discrete_movement = False

        # if target reached, or if no next tile found
        # go back to idle state
        if char.next_tile == char.target_tile or char.next_tile == None:
            char.state = 'idle'
        elif discrete_movement:
            # if not reached and move time over, move the character
            char.frames_since_moved += 1
            if char.frames_since_moved >= char.move_time:
                # remove current square from walkable tiles
                self.walkable_tiles_map[char.y_pos][char.x_pos] == 1
                # move character to next tile
                char.move_to_next()
                # add current square to walkable tiles
                self.walkable_tiles_map[char.y_pos][char.x_pos] == 0
        else:
            char.move_increment()
            char.frames_since_moved += 1
            # if has just moved
            # if char.frames_since_moved == 0:
            #     self.walkable_tiles_map[char.y_pos][char.x_pos] == 0




    # updates the animations of the dynamic elements
    def update_dynamic_elements(self):
        for char in self.characters:
            if char.state == 'walk':
                self.move_character(char)

            animation_len = self.character_states_anim[char.char_name][char.state]
            new_anim_num = (char.animation_num + 1) % animation_len

            if char.state == 'idle':
                # if the animation cycle was completed there is a chance that the state/orientation
                # of the animal changes. This chance depends on the fps. 
                state_duration_sec = 5
                state_duration_frames = 1 + (state_duration_sec * self.target_fps) // animation_len

                if new_anim_num == 0:
                    chance = random.randint(1, state_duration_frames * 2)
                    if chance == 1:
                        # change orientation
                        char.orientation = random.choice(self.char_orientations_list)
                    elif chance == state_duration_frames:
                        # change state
                        char.state = random.choice(list(self.character_states_anim[char.char_name].keys()))
                        print(f"chose new state for {char.char_name}: {char.state}")

            char.animation_num = new_anim_num

    # renders the characters on the dynamic buffer
    # N.B. the clock will also be rendered on this surface
    def render_dynamic_buffer(self):
        for char in self.characters:
            spritesheet_name = f"{char.char_name}_{char.orientation}_{char.state}"
            spritesheet_image = self.character_spritesheets[spritesheet_name]
            img_w, tile_h = spritesheet_image.get_size()
            tile_w = img_w / self.character_states_anim[char.char_name][char.state]

            tile_map_source_square = (char.animation_num * tile_w, 0, tile_w, tile_h)
            scaled_source_square = pygame.transform.scale(spritesheet_image.subsurface(tile_map_source_square), (tile_w * self.scaling_factor, tile_h * self.scaling_factor))

            screen_x, screen_y = self.tile_coords_to_screen_coords_tile_size_adjusted(*char.get_full_pos(self.tiles_map), tile_w * self.scaling_factor, tile_h * self.scaling_factor)

            # if debugging, draw box around the character
            if self.DEBUGGING:
                # box color based on character state
                color = (255,0,0)
                if char.state == 'walk':
                    color = (0,0,255)
                pygame.draw.rect(self.dynamic_buffer, color, pygame.Rect(screen_x, screen_y, tile_w, tile_h), 2)

            self.dynamic_buffer.blit(
                                    scaled_source_square,
                                    (screen_x, screen_y)
                                    )

    # takes a string of length 1 and returns the letter pos on the font spritesheet
    def get_letter_pos(self, letter: str):
        if len(letter) != 1:
            print(f"single letter expected")
            return 0,0
        if letter.isalpha():
            letter_unicode = ord(letter.upper())
            letter_num = letter_unicode - ord('A')
        elif letter.isnumeric():
            letter_unicode = ord(letter)
            letter_num = letter_unicode - ord('0') + 26
        elif letter == ':':
            letter_num = 37
        elif letter == '?':
            letter_num = 38
        elif letter == '!':
            letter_num = 39
        elif letter == ' ':
            return None
        else:
            # if letter not found print question mark
            letter_num = 38

        x_pos = (letter_num % self._num_font_columns) * self._font_letter_w
        y_pos = math.floor(letter_num / self._num_font_columns) * self._font_letter_h

        return x_pos, y_pos


    def draw_text_buffer(self, text, letter_scale, x_pos, y_pos):
        # draw letters on dynamic buffer
        lsf = letter_scale

        for i, letter in enumerate(text):
            letter_sheet_pos = self.get_letter_pos(letter)
            # if it is not a space
            if letter_sheet_pos is not None:
                tile_map_source_square = (*letter_sheet_pos, self._font_letter_w, self._font_letter_h)
                scaled_source_square = pygame.transform.scale(self.font_sheet.subsurface(tile_map_source_square), (self._font_letter_w * lsf, self._font_letter_h * lsf))
                self.dynamic_buffer.blit(
                                                scaled_source_square,  
                                                (x_pos + (self._font_letter_w / 2) * i * lsf, y_pos),
                                                )

    # clock numbers are rendered on the dynamic buffer surface
    def render_clock(self, time_str):
        # letter scaling factor
        lsf = 1.0

        clock_x = (self.screen_width - len(time_str) * (self._font_letter_w / 2) * lsf) // 2
        clock_y = self.screen_height / 16

        self.draw_text_buffer(time_str, lsf, clock_x, clock_y)
    
    # update everything concerned with the timer
    # also the nature points and island params depend on the timer
    # update accordingly
    def update_timer(self):
        # update the timer render
        time_str = self.timer.get_timer_value()
        self.render_clock(time_str)

        # update the game based on elapsed time
        # the island grows with time
        elapsed_time_s = int(self.timer.elapsed_time())
        new_nature_points = self.timer_to_nature_points(elapsed_time_s)

        # if more nature points than before
        if new_nature_points > self.nature_points:
            # update the user database
            self.db.set_user_data(user_nature_points=new_nature_points)
            self.nature_points = new_nature_points
            self.blit_static_surface()
            
            # add animals to the island
            animals_to_add = self.num_animals - len(self.characters)
            for i in range(animals_to_add):
                self.add_random_character()


    def render_task_name(self):
        # get task name
        # TODO: get task name from Task object
        letter_scale = 0.3
        text_x = (self.screen_width - len(self.task_name) * (self._font_letter_w / 2) * letter_scale) // 2
        text_y = self.screen_height * (14/16)

        self.draw_text_buffer(self.task_name, letter_scale, text_x, text_y)

    def update_farm(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.static_island_buffer, (0, 0))
        transparent_color = (255, 255, 255, 0)
        self.dynamic_buffer.fill(transparent_color)
        self.update_dynamic_elements()
        self.render_dynamic_buffer()

    def update(self):
        self.update_farm()
        if self.SHOW_TIMER:
            self.update_timer()
        if self.SHOW_TASK_NAME:
            self.render_task_name()

        self.screen.blit(self.dynamic_buffer, (0, 0))

        pygame.display.flip()

    # before the program is quit some last changes are made to the database
    def beforeQuit(self):
        # update the progress attribute of the task object in the database
        # progress is the amount of minutes elapsed
        elapsed_time_s = self.timer.elapsed_time()
        self.task.progress = int(elapsed_time_s / 60)
        self.db.edit_task(self.task)

        # loop over all the characters and save their current state
        for char in self.characters:
            pass

    def loop(self):
        running = True
        while running:
            # handle all the key events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.beforeQuit()
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Scroll up (zoom in)
                        self.scaling_factor += 0.1
                        self.blit_static_surface()
                    elif event.button == 5:  # Scroll down (zoom out)
                        self.scaling_factor -= 0.1
                        self.blit_static_surface()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.timer.toggle_running()

            # the methods to execute each loop
            self.update()

            self.clock.tick(self.target_fps)


        pygame.quit()
