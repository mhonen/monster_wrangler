import pygame, random

#Initialize pygame
pygame.init()

#Set display window
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Monster Wrangler")

#Set FPS and clock
FPS = 60
clock = pygame.time.Clock()

#Define Classes
class Game():
  """A class to control game play"""
  def __init__(self, player, monster_group):
    """Initialize the game object"""
    #Set game values
    self.score = 0
    self.round_number = 0

    self.round_time = 0
    self.frame_count = 0

    self.player = player
    self.monster_group = monster_group

    #Set sounds and music
    self.next_level_sound = pygame.mixer.Sound("next_level.wav")

    #Set Font
    self.font = pygame.font.Font("Abrushow.ttf", 24)

    #Set images
    blue_image = pygame.image.load("blue_monster.png")
    green_image = pygame.image.load("green_monster.png")
    purple_image = pygame.image.load("purple_monster.png")
    yellow_image = pygame.image.load("yellow_monster.png")
    #List corresponds to the monster type (i.e. blue_image = 0)
    self.target_monster_images = [blue_image, green_image, purple_image, yellow_image]

    self.target_monster_type = random.randint(0,3)
    self.target_monster_image =self.target_monster_images[self.target_monster_type]

    self.target_monster_rect = self.target_monster_image.get_rect()
    self.target_monster_rect.centerx = WINDOW_WIDTH//2
    self.target_monster_rect.top = 30

  def update(self):
    """Update our game object"""
    self.frame_count += 1

    if self.frame_count == FPS:
      self.round_time += 1
      self.frame_count = 0

    #Check for collisions
    self.check_collision()

  def draw(self):
    """Draw the hud and other to the display"""
    #Set Colors
    WHITE = (255,255,255)
    BLUE = (20,176,235)
    GREEN = (87,201,47)
    PURPLE = (226, 73, 243)
    YELLOW = (243, 157, 20)

    #Put Monster colors into a list.  Index of color matches target_monster_images
    colors =  [BLUE, GREEN, PURPLE, YELLOW]

    #Set text
    catch_text = self.font.render("Current Catch", True, WHITE)
    catch_rect = catch_text.get_rect()
    catch_rect.centerx = WINDOW_WIDTH//2
    catch_rect.top = 5

    score_text = self.font.render("Score: " + str(self.score), True, WHITE)
    score_rect = score_text.get_rect()
    score_rect.topleft = (5,5)

    lives_text = self.font.render("Lives: " + str(self.player.lives), True, WHITE)
    lives_rect = lives_text.get_rect()
    lives_rect.topleft = (5, 35)

    round_text = self.font.render("Current Round: " + str(self.round_number), True, WHITE)
    round_rect = round_text.get_rect()
    round_rect.topleft = (5, 65)

    time_text = self.font.render("Round Time: " + str(self.round_time), True, WHITE)
    time_rect = time_text.get_rect()
    time_rect.topright = (WINDOW_WIDTH - 10, 5)

    warp_text = self.font.render("Warps: " + str(self.player.warps), True, WHITE)
    warp_rect = warp_text.get_rect()
    warp_rect.topright = (WINDOW_WIDTH - 10, 35)

    #Blit the hud
    display_surface.blit(catch_text, catch_rect)
    display_surface.blit(score_text, score_rect)
    display_surface.blit(round_text, round_rect)
    display_surface.blit(lives_text, lives_rect)
    display_surface.blit(time_text, time_rect)
    display_surface.blit(warp_text, warp_rect)
    display_surface.blit(self.target_monster_image, self.target_monster_rect)

    pygame.draw.rect(display_surface, colors[self.target_monster_type], (WINDOW_WIDTH//2 - 32, 30, 64,64), 2)
    pygame.draw.rect(display_surface, colors[self.target_monster_type], (0, 100, WINDOW_WIDTH, WINDOW_HEIGHT - 200), 4)

  def check_collision(self):
    """Check for collisions between player and monsters"""
    #Check for collision between the player and an individual monster
    #We must test the type of the monster to see if it matches the type of our target monster
    collided_monster = pygame.sprite.spritecollideany(self.player, self.monster_group)

    #We collided with a monster
    if collided_monster:
      #Caught to correct monster
      if collided_monster.type == self.target_monster_type:
        self.score += 100 * self.round_number
        #Remove caught monster
        collided_monster.remove(self.monster_group)
        if(self.monster_group):
          #There are more monsters to catch
          self.player.catch_sound.play()
          self.choose_new_target()
        else:
          #The round is complete
          self.player.reset()
          self.start_new_round()
      #Caught the wrong monster
      else:
        self.player.die_sound.play()
        self.player.lives -= 1
        #Check for Game Over
        if self.player.lives <= 0:
          self.pause_game("Final Score: " + str(self.score), "Press Enter to play again.")
          self.reset_game()
        self.player.reset()


  def start_new_round(self):
    """Populate board with new monsters"""
    #Provide a scroe bonus based on round time
    self.score += int(10000*self.round_number/(1 + self.round_time))

    #Reset round values
    self.round_time = 0
    self.frame_count = 0
    self.round_number += 1
    self.player.warps += 1

    #remove any remaining monsters from reset
    for monster in self.monster_group:
      self.monster_group.remove(monster)

    #Put new into the monster group
    for i in range(self.round_number):
      self.monster_group.add(Monster(random.randint(0, WINDOW_WIDTH -64), random.randint(100, WINDOW_HEIGHT-164), self.target_monster_images[0], 0))
      self.monster_group.add(Monster(random.randint(0, WINDOW_WIDTH -64), random.randint(100, WINDOW_HEIGHT-164), self.target_monster_images[1], 1))
      self.monster_group.add(Monster(random.randint(0, WINDOW_WIDTH -64), random.randint(100, WINDOW_HEIGHT-164), self.target_monster_images[2], 2))
      self.monster_group.add(Monster(random.randint(0, WINDOW_WIDTH -64), random.randint(100, WINDOW_HEIGHT-164), self.target_monster_images[3], 3))

    #Choose a new target monster
    self.choose_new_target()

    #Play next level sound
    self.next_level_sound.play()

  def choose_new_target(self):
    """Choose a new target monster for the player"""
    #Chooses correct remaining monsters that are not NULL
    target_monster = random.choice(self.monster_group.sprites())
    self.target_monster_type = target_monster.type
    self.target_monster_image = target_monster.image

  def pause_game(self, main_text, sub_text):
    """Pause the game"""

    global running
    
    #Set Color
    WHITE = (255,255,255)
    BLACK = (0,0,0)

    #Create the main pause text
    main_text = self.font.render(main_text, True, WHITE)
    main_rect = main_text.get_rect()
    main_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)

    #Create the sub pause text
    sub_text = self.font.render(sub_text, True, WHITE)
    sub_rect = sub_text.get_rect()
    sub_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 64)

    #Display the pause text
    display_surface.fill(BLACK)
    display_surface.blit(main_text, main_rect)
    display_surface.blit(sub_text, sub_rect)
    pygame.display.update()

    #Pause the game
    is_paused = True
    while is_paused:
      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_RETURN:
            is_paused = False
        if event.type == pygame.QUIT:
          is_paused = False
          running = False

  def reset_game(self):
    """Reset the game"""
    self.score = 0
    self.round_number = 0

    self.player.lives = 5
    self.player.warps = 2
    self.player.reset()

    self.start_new_round()

class Player(pygame.sprite.Sprite):
  """A player class that the use can control"""
  def __init__(self):
    """Initialize player"""
    super().__init__()
    self.image = pygame.image.load("knight.png")
    self.rect = self.image.get_rect()
    self.rect.centerx = WINDOW_WIDTH//2
    self.rect.bottom = WINDOW_HEIGHT

    self.lives = 5
    self.warps = 2
    self.velocity = 8

    self.catch_sound = pygame.mixer.Sound("catch.wav")
    self.die_sound = pygame.mixer.Sound("die.wav")
    self.warp_sound = pygame.mixer.Sound("warp.wav")

  def update(self):
    """Update the player"""
    keys = pygame.key.get_pressed()

    #Move the player
    if keys[pygame.K_LEFT] and self.rect.left > 0:
      self.rect.x -= self.velocity
    if keys[pygame.K_RIGHT] and self.rect.right < WINDOW_WIDTH:
      self.rect.x += self.velocity
    if keys[pygame.K_UP] and self.rect.top > 100:
      self.rect.y -= self.velocity
    if keys[pygame.K_DOWN] and self.rect.bottom < WINDOW_HEIGHT - 100:
      self.rect.y += self.velocity

  def warp(self):
    """Warps player to the bottom safe zone"""
    if self.warps > 0:
      self.warps -= 1
      self.warp_sound.play()
      self.rect.bottom = WINDOW_HEIGHT

  def reset(self):
    """Resets the players position"""
    self.rect.centerx = WINDOW_WIDTH//2
    self.rect.bottom = WINDOW_HEIGHT

class Monster(pygame.sprite.Sprite):
  """A class to create enemy monster objects"""
  def __init__(self, x, y, image, monster_type):
    """Initialize the monster"""
    super().__init__()
    self.image = image
    self.rect = self.image.get_rect()
    self.rect.topleft = (x, y)

    #Monster type is an int 0-> blue, 1-> green, 2-> purple, 3-> yellow
    self.type = monster_type

    #Set random motion
    self.dx = random.choice([-1, 1])
    self.dy = random.choice([-1, 1])
    self.velocity = random.randint(1, 5)

  def update(self):
    """Update the monster"""
    self.rect.x += self.dx*self.velocity
    self.rect.y += self.dy*self.velocity

    #Bounce the monster off the edge of the display
    if self.rect.left <= 0 or self.rect.right >= WINDOW_WIDTH:
      self.dx = -1 * self.dx
    if self.rect.top <= 100 or self.rect.bottom >= WINDOW_HEIGHT - 100:
      self.dy = -1 * self.dy

#Create a player group and player object
my_player_group = pygame.sprite.Group()
my_player = Player()
my_player_group.add(my_player)

#Create monster group..Will add additonal code later after Monster class is completed
my_monster_group = pygame.sprite.Group()

#Create a game object
my_game = Game(my_player, my_monster_group)
my_game.pause_game("Monster Wrangler", "Press 'Enter' to begin")
my_game.start_new_round()

#The main game loop
running = True
while running:
  #See if player is trying to quit
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    #Player warps to safety when pressingthe space key
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_SPACE:
          my_player.warp()

  #Fill the display
  display_surface.fill((0,0,0))

  #update a draw sprite groups
  my_player_group.update()
  my_player_group.draw(display_surface)

  my_monster_group.update()
  my_monster_group.draw(display_surface)

  #Update and draw the Game
  my_game.update()
  my_game.draw()

  #update display
  pygame.display.update()
  clock.tick(FPS)

#End the game
pygame.quit()
