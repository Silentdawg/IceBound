import pygame
from pygame.locals import *
import pickle
import sys
import buttons
from os import path

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 800
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('IceBound')

font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)


# Set up colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up font
font_time = pygame.font.Font(None, 36)

# Set up timer variables
total_minutes = 240  # Total time in minutes
current_minutes = total_minutes  # Initial time in minutes
current_seconds = total_minutes * 60  # Initial time in seconds

#define game variables
tile_size = 40
game_over = 0 
main_menu = True
score = 0
level = 1
max_level = 2
game_paused = False
menu_state = "main"

white = (255, 255, 255)
black = (0, 0, 0)


#load images
bg_img = pygame.image.load('ice.jpg')
bg2_img= pygame.image.load('bg2.png')
bg3_img= pygame.image.load('bg3.png')
restart_img = pygame.image.load('restart.png')
start_img = pygame.image.load('play.png')
exit_img = pygame.image.load('exit.png')

resume_img = pygame.image.load("button_resume.png").convert_alpha()
options_img = pygame.image.load("button_options.png").convert_alpha()
quit_img = pygame.image.load("button_quit.png").convert_alpha()
video_img = pygame.image.load('button_video.png').convert_alpha()
audio_img = pygame.image.load('button_audio.png').convert_alpha()
keys_img = pygame.image.load('button_keys.png').convert_alpha()
back_img = pygame.image.load('button_back.png').convert_alpha()




def reset_level(level):
	player.reset(100, screen_height - 130)
	blob_group.empty()
	platform_group.empty()
	#coin_group.empty()
	water_group.empty()
	exit_group.empty()

	#load in level data and create world
	if path.exists(f'level{level}_data'):
		pickle_in = open(f'level{level}_data', 'rb')
		world_data = pickle.load(pickle_in)
	world = World(world_data)

	return world

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))



class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False


		#draw button
		screen.blit(self.image, self.rect)

		return action


class Player():
	def __init__(self, x, y):
		self.reset(x, y)



	def update(self, game_over):
		dx = 0
		dy = 0
		walk_cooldown = 3
		col_thresh = 20

		if game_over == 0:
			#get keypresses
			key = pygame.key.get_pressed()
			if key[pygame.K_UP] and self.jumped == False and self.in_air == False:
				self.vel_y = -15
				self.jumped = True
			if key[pygame.K_UP] == False:
				self.jumped = False
			if key[pygame.K_LEFT]:
				dx -= 5
				self.counter += 1
				self.direction = -1
			if key[pygame.K_RIGHT]:
				dx += 5
				self.counter += 1
				self.direction = 1
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
				self.counter = 0
				self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]

			if self.counter > walk_cooldown:
				self.counter = 0	
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]

			#add gravity
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y

			#check for collision
			self.in_air = True
			for tile in world.tile_list:
				#check for collision in x direction
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#check for collision in y direction
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below the ground i.e. jumping
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					#check if above the ground i.e. falling
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False


			#check for collision with enemies
			if pygame.sprite.spritecollide(self, blob_group, False):
				game_over = -1

			#check for collision with lava
			if pygame.sprite.spritecollide(self, water_group , False):
				game_over = -1

			#check for collision with exit
			if pygame.sprite.spritecollide(self, exit_group, False):
				game_over = 1

			#check for collision with platforms
			for platform in platform_group:
				#collision in the x direction
				if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#collision in the y direction
				if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below platform
					if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
						self.vel_y = 0
						dy = platform.rect.bottom - self.rect.top
					#check if above platform
					elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
						self.rect.bottom = platform.rect.top - 1
						self.in_air = False
						dy = 0
					#move sideways with the platform
					if platform.move_x != 0:
						self.rect.x += platform.move_direction

			#update player coordinates
			self.rect.x += dx
			self.rect.y += dy

		elif game_over == -1:
			self.image = self.dead_image
			draw_text('GAME OVER!', font, black, (screen_width // 2) - 200, (screen_height // 2) -100)
			if self.rect.y > 200:
				self.rect.y -= 5

		#draw player onto screen
		screen.blit(self.image, self.rect)
		#pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

		return game_over


	def reset(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 2):
			img_right = pygame.image.load(f'penguin{num}.png')
			img_right = pygame.transform.scale(img_right, (30, 50))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.dead_image = pygame.image.load('ghost.png')
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True



class World():
	def __init__(self, data):
		self.tile_list = []

		#load images
		dirt_img = pygame.image.load('block.png')
		grass_img = pygame.image.load('iceblock.png')

		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 2:
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 3:
					blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
					blob_group.add(blob)
				if tile == 4:
					platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
					platform_group.add(platform)
				if tile == 5:
					platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
					platform_group.add(platform)
				if tile == 6:
					lava = Water(col_count * tile_size, row_count * tile_size + (tile_size // 2))
					water_group.add(lava)
				if tile == 7:
					coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					coin_group.add(coin)
				if tile == 8:
					exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
					exit_group.add(exit)
				col_count += 1
			row_count += 1

	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])
			#pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)



class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('polar.png')
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1
		self.move_counter = 0

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1

class Coin(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('fish.png')
		self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
    
class Exit(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('exit 3.png')
		self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

class Platform(pygame.sprite.Sprite):
	def __init__(self, x, y, move_x, move_y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('platform.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_counter = 0
		self.move_direction = 1
		self.move_x = move_x
		self.move_y = move_y


	def update(self):
		self.rect.x += self.move_direction * self.move_x
		self.rect.y += self.move_direction * self.move_y
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1

    
class Water(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('water.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


resume_button = buttons.Button(304, 125, resume_img, 1)
options_button = buttons.Button(297, 250, options_img, 1)
quit_button = buttons.Button(336, 375, quit_img, 1)
video_button = buttons.Button(226, 75, video_img, 1)
audio_button = buttons.Button(225, 200, audio_img, 1)
keys_button = buttons.Button(246, 325, keys_img, 1)
back_button = buttons.Button(332, 450, back_img, 1)

def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

player = Player(100, screen_height - 130)

blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

if path.exists(f'level{level}_data'):
	pickle_in = open(f'level{level}_data', 'rb')
	world_data = pickle.load(pickle_in)
world = World(world_data)


#create buttons
restart_button = Button(screen_width // 2 - 130, screen_height // 2 + 40, restart_img)
start_button = Button(screen_width // 2 - 90, screen_height // 2 -50, start_img)
exit_button = Button(screen_width // 2 - 100, screen_height // 2 +50, exit_img)


run = True
while run:
    screen.blit(bg_img, (0, 0))

    remaining_minutes = current_seconds // 60
    remaining_hours = current_seconds // 3600
    #remaining_minutes = (current_time % 3600) // 60
    #remaining_seconds = current_time % 60
    timer_text = "{:02}:{:02}".format(remaining_hours,remaining_minutes%60)
    text = font_time.render("Time: " + timer_text, True, BLACK)
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 - 320))
    screen.blit(text, text_rect)
    

    # Decrement the timer
    current_seconds -= 1
    if current_seconds < 0:
        current_seconds = 0

    # Check if the timer reaches zero or the user closes the window
    if current_seconds == 0:
        run = False
				
    if main_menu == True:
        screen.blit(bg2_img, (0, 0))
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        world.draw()

        if game_over == 0:
            blob_group.update()
            platform_group.update()
                #coin_group.draw(screen)   
                #update score
                #check if a coin has been collected
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
            draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)

        blob_group.draw(screen)
        platform_group.draw(screen)
        water_group.draw(screen)
        coin_group.draw(screen)		
        exit_group.draw(screen)                
        game_over = player.update(game_over)

                #if player has died
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                score = 0
                game_over = 0

                #if player has completed the level
        if game_over == 1:
            #reset game and go to next level
            level += 1
            if level <= max_level:
                #reset level
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text('YOU WIN!', font, black, (screen_width // 2) - 150 , (screen_height // 2) - 100)
            if restart_button.draw():
                level = 1
                #reset level
                world_data = []
                world = reset_level(level)
                score = 0
                game_over = 0

    if game_paused == True:
        screen.blit(bg3_img, (0, 0))
    #check menu state
        if menu_state == "main":
      #draw pause screen buttons
          if resume_button.draw(screen):
           game_paused = False
          if options_button.draw(screen):
           menu_state = "options"
          if quit_button.draw(screen):
           run = False
    #check if the options menu is open
        if menu_state == "options":
      #draw the different options buttons
          if video_button.draw(screen):
           print("Video Settings")
          if audio_button.draw(screen):
           print("Audio Settings")
          if keys_button.draw(screen):
           print("Change Key Bindings")
          if back_button.draw(screen):
           menu_state = "main"
		  
          
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_SPACE:
            game_paused = True
            if event.type == pygame.QUIT:
                run = False
    clock.tick(60)

    pygame.display.update()

pygame.quit()
sys.exit()