import pygame
import random
import abc
import os

RIGHT = "right"
LEFT = "left"

pygame.init()
pygame.mixer.init()
FPS = 60

WIDTH, HEIGHT = screensize = (1600, 700)
screen = pygame.display.set_mode(screensize)

scene = pygame.image.load("textures/static/background.png")
(SCENE_W, SCENE_H), (SCENE_X, SCENE_Y) = scene.get_size(), (0, 0)

pygame.display.set_caption("БУМЕР WEST")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()


class Object(pygame.sprite.Sprite):

    objects = []

    def __init__(self, image: pygame.image, hp: int, x: int, y: int):
        pygame.sprite.Sprite.__init__(self)
        self.hp = hp
        self.image = image
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        Object.objects.append(self)


class Actor(Object):

    def __init__(self, right_slice, left_slice, speed, folder, **kwargs):
        super().__init__(**kwargs)
        self.folder = folder
        self.actor_slice = right_slice
        self.right_slice, self.left_slice = right_slice, left_slice
        self.speed = self.start_speed = speed
        self.move_pos = list(range(1, len(os.listdir(os.path.join(self.folder, "right-move")))+1))
        self.change_side_count = len(os.listdir(os.path.join(self.folder, "change-side")))-1
        self.side_pos = [self.change_side_count, RIGHT]
        self.side_textures = [f"{self.folder}/change-side/{i}.png" for i in range(1, self.change_side_count+2)]
        self.direction = RIGHT

    def change_side(self):
        if self.side_pos[0] not in [0, self.change_side_count] or self.side_pos[1] != self.direction:
            if self.direction == RIGHT:
                self.side_pos[0] += 1
                if self.side_pos[0] == self.change_side_count:
                    self.side_pos[1] = RIGHT
            elif self.direction == LEFT:
                self.side_pos[0] -= 1
                if self.side_pos[0] == 0:
                    self.side_pos[1] = LEFT
            self.image = pygame.image.load(self.side_textures[self.side_pos[0]])

    def change_move(self):
        if self.direction == self.side_pos[1]:
            self.image = pygame.image.load(f"{self.folder}/{self.direction}-move/{self.move_pos[0]}.png")
            self.move_pos.insert(0, self.move_pos[-1])
            self.move_pos.pop(-1)

    def move_right(self):
        self.actor_slice = self.right_slice
        self.direction = RIGHT
        if self.rect.x < WIDTH-self.width:
            self.rect.x += self.start_speed
        self.change_move()

    def move_left(self):
        self.actor_slice = self.left_slice
        self.direction = LEFT
        if self.rect.x > 0:
            self.rect.x -= self.start_speed
        self.change_move()


class Cloud(Object):

    cloud_creation_time = 100

    def __init__(self, speed, **kwargs):
        if Cloud.cloud_creation_time == 100:
            path = "textures/objects/clouds"
            image = pygame.image.load(os.path.join(path, random.choice(os.listdir(path))))
            width, height = image.get_size()
            kwargs["image"], kwargs["x"], kwargs["y"] = image, -width, random.randint(-height//2, 200)
            super().__init__(**kwargs)
            self.speed = speed
            all_sprites.add(self)
            Cloud.cloud_creation_time = 0
        else:
            Cloud.cloud_creation_time += 1

    def update(self):
        if self.rect.x < WIDTH:
            self.rect.x += self.speed
        else:
            all_sprites.remove(self)


class Platform(Object):

    items = []

    def __init__(self, area_slice, **kwargs):
        super().__init__(**kwargs)
        all_sprites.add(self)
        self.area_slice = area_slice
        Platform.items.append(self)

    def interact_with_plat(self, player):
        return True


class MainPlatform(Platform):

    def __init__(self, area_slice, **kwargs):
        super().__init__(area_slice, **kwargs)

    def interact_with_plat(self, player):
        if player.jump and not player.fixated:
            if player.rect.y + (player.speed-1)**2 + player.height >= self.rect.y:
                player.rect.y = self.rect.y-player.height
                player.jump = False
                player.speed = player.start_speed
                return False


class Bullet(Object):

    def __init__(self, speed, direction, **kwargs):
        super().__init__(**kwargs)
        self.speed = speed
        self.direction = direction
        self.push()

    def push(self):
        if 0 < self.rect.x < WIDTH:
            self.rect.x += self.speed**2*self.direction
            self.speed += 1
        else:
            all_sprites.remove(self)

    def update(self):
        self.push()


class move_scene(abc.ABC):

    @classmethod
    def move_all_right(cls, obj, x_coord):
        global SCENE_X
        if SCENE_X > WIDTH - SCENE_W:
            if x_coord >= WIDTH*0.65:
                for i_object in Object.objects:
                    if i_object != obj:
                        i_object.rect.x -= obj.start_speed
                SCENE_X -= obj.start_speed
                obj.change_move()
                return True

    @classmethod
    def move_all_left(cls, obj, x_coord):
        global SCENE_X
        if SCENE_X < 0:
            if x_coord <= WIDTH*0.35:
                for i_object in Object.objects:
                    if i_object != obj:
                        i_object.rect.x += obj.start_speed
                SCENE_X += obj.start_speed
                obj.change_move()
                return True


class Player(Actor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anger, self.jump, self.fixated, self.in_car, self.interact_with_plat = (False for _ in range(5))
        self.attack_count = 1
        self.total_attack = len(os.listdir(f"{self.folder}/{self.direction}-attack/"))
        self.bullet_timeout = 0
        self.reloading = random.randint(3, 5)*FPS
        all_sprites.add(self)

    def move_up(self):
        if self.jump:
            if self.speed >= 0:
                self.rect.y -= self.speed**2
            else:
                self.rect.y += self.speed**2
            self.speed -= 1

    def find_platform(self):
        for plat in Platform.items:
            if plat.interact_with_plat(self):
                sprite_y = self.rect.y+self.height
                plat_y = plat.rect.y
                if 0 <= abs(sprite_y-plat_y) <= 5:
                    sprite_coords = [sprite_x for sprite_x in range(int(self.rect.x),
                                     int(self.rect.x+self.width))]
                    area = [plat_x for plat_x in range(int(plat.rect.x),
                            int(plat.rect.x+plat.width))]
                    area = set(area[plat.area_slice])
                    sprite_coords = set(sprite_coords[self.actor_slice])
                    set_of_coords = sprite_coords.copy()
                    set_of_coords.update(area)
                    if len(sprite_coords)+len(area) != len(set_of_coords) and self.jump and not self.fixated:
                        self.rect.y = plat_y-self.height
                        self.speed = self.start_speed
                        self.fixated = True
                        self.jump = False
                        break
                    else:
                        if len(sprite_coords)+len(area) == len(set_of_coords):
                            if self.fixated:
                                self.fixated = False
                                if not self.jump:
                                    self.jump = True
                                    self.speed = -self.start_speed

    def interact_with_car(self, car):
        if isinstance(car, Car):
            if not self.in_car:
                sprite_coords = [sprite_x for sprite_x in range(int(self.rect.x),
                                 int(self.rect.x + self.width))]
                car_coords = [car_x for car_x in range(int(car.rect.x),
                              int(car.rect.x + car.width))]
                car_coords = set(car_coords[car.actor_slice])
                sprite_coords = set(sprite_coords[self.actor_slice])
                set_of_coords = sprite_coords.copy()
                set_of_coords.update(car_coords)
                if len(sprite_coords) + len(car_coords) != len(set_of_coords):
                    self.in_car = True
                    car.actor = self
                    car.move = True
            else:
                self.jump = True
                self.speed = 3
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
                self.in_car = False
                car.actor = None
                car.move = False

    def push_bullet(self):
        if self.bullet_timeout == self.reloading and self.attack_count == self.total_attack:
            bullet_direction = -1 if self.direction == LEFT else 1
            bullet_1x, bullet_1y = self.rect.x+(self.width+self.width*bullet_direction)/2, self.rect.y+self.height/2
            bullet_2x, bullet_2y = bullet_1x-20, bullet_1y-20
            bullet_1 = Bullet(speed=5, direction=bullet_direction,
                              image=pygame.image.load("textures/objects/bullet.png"), hp=10, x=bullet_1x, y=bullet_1y)
            bullet_2 = Bullet(speed=5, direction=bullet_direction,
                              image=pygame.image.load("textures/objects/bullet.png"), hp=10, x=bullet_2x, y=bullet_2y)
            for bullet in [bullet_1, bullet_2]:
                all_sprites.add(bullet)
            self.bullet_timeout = 0
            self.reloading = random.randint(3, 5) * FPS/3

    def attack(self):
        if self.anger or self.attack_count != 1:
            self.image = pygame.image.load(f"{self.folder}/{self.direction}-attack/{self.attack_count}.png")
            if self.anger:
                if self.attack_count < self.total_attack:
                    self.attack_count += 1
            else:
                self.attack_count -= 1

    def update(self):
        if self.bullet_timeout < self.reloading:
            self.bullet_timeout += 1
        self.change_side()
        self.move_up()
        self.find_platform()
        self.attack()


class Car(Actor, Platform):

    def __init__(self, area_slice, right_slice, left_slice, speed, folder, **kwargs):
        super().__init__(area_slice=area_slice, right_slice=right_slice, left_slice=left_slice,
                         speed=speed, folder=folder, **kwargs)
        self.move = False
        self.actor = None
        all_sprites.add(self)

    def fixate_actor(self):
        if self.actor:
            self.actor.image = pygame.transform.scale(self.actor.image, (self.actor.width-5, self.actor.height-10))
            self.actor.rect.y = self.rect.y+self.height-self.actor.height - 15
            if self.direction == RIGHT:
                self.actor.rect.x = self.rect.x+150
            else:
                self.actor.rect.x = self.rect.x+200

    def update(self):
        self.change_side()
        self.fixate_actor()


class Button(pygame.sprite.Sprite):

    def __init__(self, x, y, function):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("textures/static/menu_button.png")
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.function = function
        all_sprites.add(self)

    def update(self):
        all_sprites.remove(self)
        all_sprites.add(self)
        if pygame.mouse.get_pressed()[0]:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.function()


class Label(Object):

    def __init__(self, car, **kwargs):
        kwargs["x"], kwargs["y"] = car.obj.x, car.obj.y
        super().__init__(**kwargs)
        self.obj = car

    def update(self):
        self.rect.x, self.rect.y = self.obj.rect.x, self.obj.rect.y


def add_player():
    player_image = pygame.image.load("textures/actors/Leha/player-right.png")
    player_width, player_height = player_image.get_size()
    player_x, player_y = (WIDTH-player_width)/2, HEIGHT-player_height
    actor = Player(right_slice=slice(29, 92), left_slice=slice(17, 80), speed=5, folder="textures/actors/Leha",
                    image=player_image, hp=100, x=player_x, y=player_y)
    return actor


def create_menu_button():
    pygame.mixer.music.load("music/western.mp3")
    # pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.2)

    def button_logic():
        if pygame.mixer.music.get_pos() > 0:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.play()
    button = Button(WIDTH-100, 50,
                    function=button_logic)
    return button


def create_clouds():
    amount_of_clouds = random.randint(1, 3)
    [Cloud(speed=random.randint(1, 3), hp=1) for _ in range(amount_of_clouds)]


def create_platform():
    main_platform_image = pygame.image.load("textures/static/platform.png")
    MainPlatform(slice(0, 1600), image=main_platform_image, hp=1000,
                 x=0, y=HEIGHT)
    stone_images = [pygame.image.load(f"textures/objects/stones/_000{i}_stone.png") for i in range(1, 5)]
    stone_slices = [(32, 69), (29, 95), (13, 42), (16, 45)]
    count = random.randint(150, 200)
    for s_slice, image in zip(stone_slices, stone_images):
        s_width, s_height = image.get_size()
        s_slice = slice(*s_slice)
        Platform(s_slice, image=image, hp=200,
                 x=count, y=HEIGHT-s_height)
        count += random.randint(200, 350)


def create_car():
    car_image = pygame.image.load("textures/actors/BMW/player-right.png")
    width, height = car_image.get_size()
    auto = Car(area_slice=slice(0, 813), right_slice=slice(0, 813), left_slice=slice(0, 813), speed=10,
               folder="textures/actors/BMW", image=car_image, hp=400, x=WIDTH//2, y=HEIGHT-height)
    return auto


def player_logic(player: Player, car: Car):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player.jump = True
    if not keys[pygame.K_RETURN]:
        if keys[pygame.K_RIGHT]:
            x = player.rect.x+player.width / 1.5
            if move_scene.move_all_right(player, x) is None and not player.in_car:
                player.move_right()
            else:
                player.direction = RIGHT
        elif keys[pygame.K_LEFT]:
            x = player.rect.x + player.width / 2
            if move_scene.move_all_left(player, x) is None and not player.in_car:
                player.move_left()
            else:
                player.direction = LEFT
        elif [keys[ord(value)] for value in ["E", "e", "У", "у"]].count(True) > 0:
            player.interact_with_car(car)
        elif not (keys[pygame.K_RIGHT] and keys[pygame.K_LEFT]):
            player.image = pygame.image.load(f"{player.folder}/player-{player.direction}.png")
        player.anger = False
    else:
        if not player.in_car:
            player.anger = True
            if keys[pygame.K_LSHIFT]:
                player.push_bullet()


def car_logic(car: Car):
    keys = pygame.key.get_pressed()
    if car.move:
        if keys[pygame.K_RIGHT]:
            x = car.rect.x + car.width / 2
            if move_scene.move_all_right(car, x) is None:
                car.move_right()
            else:
                car.direction = RIGHT
        elif keys[pygame.K_LEFT]:
            x = car.rect.x + car.width / 4
            if move_scene.move_all_left(car, x) is None:
                car.move_left()
            else:
                car.direction = LEFT
        elif not (keys[pygame.K_RIGHT] and keys[pygame.K_LEFT]):
            car.image = pygame.image.load(f"{car.folder}/player-{car.direction}.png")


if __name__ == '__main__':
    menu_button = create_menu_button()
    create_platform()
    Leha = add_player()
    BMW = create_car()
    run = True
    while run:
        clock.tick(FPS)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False
        player_logic(Leha, BMW)
        car_logic(BMW)
        create_clouds()
        all_sprites.update()
        screen.blit(scene, (SCENE_X, 0))
        all_sprites.draw(screen)
        pygame.display.flip()
    pygame.quit()
