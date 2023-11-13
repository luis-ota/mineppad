from ursina import *
from ursina import curve
player_foi = False


# will run when the game start
def player_():
    global player_foi, texture_list, mob_frames
    MainVariables.player = FirstPersonController(jump_height=1.269, speed=4, gravity=1)
    player_foi = True
    texture_list = {0: MainVariables.grama_txtr,
                    1: MainVariables.pedra_txtr,
                    2: MainVariables.table_txtr,
                    3: MainVariables.fornalha_txtr,
                    4: MainVariables.madeira_txtr,
                    5: MainVariables.vidro_txtr}
    mob_frames = [MainVariables.ghost_1, MainVariables.ghost_2, MainVariables.ghost_3, MainVariables.ghost_4]





class FirstPersonController(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.speed = 5
        self.origin_y = -.5
        self.camera_pivot = Entity(parent=self, y=1.8569)
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)

        camera.parent = self.camera_pivot
        camera.position = (0,0,0)
        camera.rotation = (0,0,0)
        camera.fov = 90
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)

        self.gravity = 1
        self.grounded = False
        self.jump_height = 1.5
        self.jump_duration = .5
        self.jumping = False
        self.air_time = 0


        for key, value in kwargs.items():
            setattr(self, key ,value)


    def update(self):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]

        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x= clamp(self.camera_pivot.rotation_x, -90, 90)

        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()
        origin = self.world_position + (self.up*1)
        hit_info = raycast(origin , self.direction, ignore=(self,), distance=.5, debug=False)
        if not hit_info.hit:
            self.position += self.direction * self.speed * time.dt

        if self.gravity:
            # # gravity
            ray = raycast(self.world_position+(0,2,0), self.down, ignore=(self,))
            # ray = boxcast(self.world_position+(0,2,0), self.down, ignore=(self,))

            if ray.distance <= 2.1:
                if not self.grounded:
                    self.land()
                self.grounded = True
                # make sure it's not a wall and that the point is not too far up
                if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5: # walk up slope
                    self.y = ray.world_point[1]
                return
            else:
                self.grounded = False

            # if not on ground and not on way up in jump, fall
            self.y -= min(self.air_time, ray.distance-.05) * time.dt * 100
            self.air_time += time.dt * .25 * self.gravity


    def input(self, key):
        if key == 'space':
            self.jump()


    def jump(self):
        if not self.grounded:
            return

        self.grounded = False
        self.animate_y(self.y+self.jump_height, self.jump_duration, resolution=int(1//time.dt), curve=curve.out_expo)
        invoke(self.start_fall, delay=self.jump_duration)


    def start_fall(self):
        self.y_animator.pause()
        self.jumping = False

    def land(self):
        # print('land')
        self.air_time = 0
        self.grounded = True

# get the main variables
class MainVariables:
    i = []
    limites = None
    player = Entity()
    hp = 10

    # blocks
    table_txtr = None
    grama_txtr = None
    braco_txtr = None
    terra_txtr = None
    pedra_txtr = None
    folha_txtr = None
    vidro_txtr = None
    arvore_txtr = None
    madeira_txtr = None
    fornalha_txtr = None
    block = 'carga_roubada/texturas/models/block'

    # icons 
    vidro_icon = None
    table_icon = None
    grama_icon = None
    pedra_icon = None
    madeira_icon = None
    fornalha_icon = None

    # sounds
    mob_sound = None
    mob_sound2 = None
    ghost_sound = None
    ghost_hit_sound = None

    # animals 
    porquin_txtr = None
    vaquinha_txtr = None
    vaquinha_model = 'carga_roubada/texturas/models/vaquinha_model'
    porquin_model = 'carga_roubada/texturas/models/porquin_model'

    # ghost textures
    ghost_puto = None
    ghost_0 = None
    ghost_1 = None
    ghost_2 = None
    ghost_3 = None
    ghost_4 = None


# blocks
class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture=MainVariables.grama_txtr , scale=.5, model=MainVariables.block):
        super().__init__(parent=scene,
                         position=position,
                         model=model,
                         origin_y=0.5,
                         texture=texture,
                         color=color.color(0, 0, random.uniform(0.9, 1)),
                         scale=scale
                         )

    def input(self, key):

        if self.hovered:
            if key == 'right mouse down' and len(MainVariables.i) != 0:
                position = self.position + mouse.normal
                voxel = Voxel(position=position, texture=texture_list[MainVariables.i[-1]], scale=.5,
                              model=MainVariables.block)
            if key == 'right mouse down' and len(MainVariables.i) == 0:
                print_on_screen('use scroll or arrows', scale=1, position=(-.85, -0.3102))

            if key == 'left mouse up':
                destroy(self)


# the inventory background
class Inventory(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='quad',
            scale=(.55, .1),
            origin=(-.5, .5),
            position=(-0.275, -0.35),
            texture='white_cube',
            texture_scale=(5, 1),
            color=color.black33
        )


# be able to choose items with scroll or arrows
class SetInventoryItems:
    def __init__(self):
        pass

    def run(self=None):
        class InventoryItems(Entity):
            def __init__(self, position, color=color.white, texture='white_cube'):
                super().__init__(
                    parent=camera.ui,
                    model='quad',
                    scale=(.08, .08),
                    origin=(-.5, .5),
                    position=position,
                    texture=texture,
                    texture_scale=(1, 1),
                    color=color
                )

            # the slots sizes
            slot_positions = {'slot1small': (-0.265, -0.36),  # small
                              'slot1big': (-0.27, -0.355),    # big
                              'slot2small': (-0.175, -0.36),  # small
                              'slot2big': (-0.18, -0.355),    # big
                              'slot3small': (-0.085, -0.36),  # small
                              'slot3big': (-0.09, -0.355),    # big
                              'slot4small': (0.005, -0.36),   # small
                              'slot4big': (0, -0.355),        # big
                              'slot5small': (0.095, -0.36),   # small
                              'slot5big': (0.09, -0.355),     # big
                              'slot6small': (0.185, -0.36),   # small
                              'slot6big': (0.18, -0.355)}     # big

            # to inform whether it starts forward or backward
            initwithback = 0
            initwithforward = 0
            back = False
            forward = False
            texture_index = 0

            # setting types of size
            def set_types(self, slot, name, size):
                big = (0.09, 0.09)
                small = (.08, .08)
                if size == 'small':
                    slot.scale = small
                    slot.position = self.slot_positions[name + size]  # small
                if size == 'big':
                    slot.scale = big
                    slot.position = self.slot_positions[name + size]  # big

            # edit the slot size when scroll
            def edit_slot(self, name=None, size=None):
                if name == 'slot1':
                    self.set_types(slot1, name, size)
                if name == 'slot2':
                    self.set_types(slot2, name, size)
                if name == 'slot3':
                    self.set_types(slot3, name, size)
                if name == 'slot4':
                    self.set_types(slot4, name, size)
                if name == 'slot5':
                    self.set_types(slot5, name, size)
                if name == 'slot6':
                    self.set_types(slot6, name, size)

            # defines a new color index, because when the slot reaches the last one,
            # it needs to go back to the first one, and vice versa
            def new_color_index(self):
                if self.forward:
                    if self.texture_index == 5:
                        MainVariables.i.clear()
                        self.texture_index = 0
                        self.forward = False
                        return
                    self.texture_index += 1
                    self.forward = False
                if self.back:
                    if self.texture_index == 0:
                        self.texture_index = 5
                        self.back = False
                        return
                    self.texture_index -= 1
                    self.back = False

            # here the slot is actually edited
            def change_slot(self, name, b, i):
                if self.texture_index == i:
                    self.edit_slot(name.replace(name[-1], str(int(name[-1]) - 1) if i != 0 else '6'), 'small')
                    self.edit_slot(name.replace(name[-1], str(int(name[-1]) - 1) if i != 5 else '1'), 'small')
                    self.edit_slot(name, b)
                    self.edit_slot(name.replace(name[-1], str(int(name[-1]) + 1)) if i != 0 else '2', 'small')
                    self.edit_slot(name.replace(name[-1], str(int(name[-1]) + 1)) if i != 5 else '5', 'small')
                    MainVariables.i.append(i)
                    return

            # updates the screen to see things changing in the inventory
            def change_icon(self):
                if self.initwithforward == 1 and self.initwithback == 0:
                    self.initwithforward = 1
                    self.texture_index = 0
                if self.initwithback == 1 and self.initwithforward == 0:
                    self.initwithback = 1
                    self.new_color_index()

                self.change_slot('slot1', 'big', 0)
                self.change_slot('slot2', 'big', 1)
                self.change_slot('slot3', 'big', 2)
                self.change_slot('slot4', 'big', 3)
                self.change_slot('slot5', 'big', 4)
                self.change_slot('slot6', 'big', 5)

            # idk why i did this but i don't wanna delete, so..
            def direc(self, direc):
                if direc:
                    self.forward = True
                    self.back = False
                    self.new_color_index()
                    self.change_icon()
                if not direc:
                    self.back = True
                    self.forward = False
                    self.new_color_index()
                    self.change_icon()

            # receive de scroll and arrows inputs
            def input(self, key):
                if key == 'scroll up':
                    self.initwithforward += 1
                    self.direc(True)
                if key == 'scroll down':
                    self.initwithback += 1
                    self.direc(False)
                if key == 'right arrow':
                    self.initwithforward += 1
                    self.direc(True)
                if key == 'left arrow':
                    self.initwithback += 1
                    self.direc(False)
                if key == 'x':
                    application.quit()

        # the coordinate of the slots
        slot_coordinate = {'slot1': -0.265,
                           'slot2': -0.175,
                           'slot3': -0.085,
                           'slot4': 0.005,
                           'slot5': 0.095,
                           'slot6': 0.185}

        # creating the slots
        slot1 = InventoryItems(position=(slot_coordinate["slot1"], -0.36),
                               texture=MainVariables.grama_icon)
        slot2 = InventoryItems(position=(slot_coordinate["slot2"], -0.36),
                               texture=MainVariables.pedra_icon)
        slot3 = InventoryItems(position=(slot_coordinate["slot3"], -0.36),
                               texture=MainVariables.table_icon)
        slot4 = InventoryItems(position=(slot_coordinate["slot4"], -0.36),
                               texture=MainVariables.fornalha_icon)
        slot5 = InventoryItems(position=(slot_coordinate["slot5"], -0.36),
                               texture=MainVariables.madeira_icon)
        slot6 = InventoryItems(position=(slot_coordinate["slot6"], -0.36),
                               texture=MainVariables.vidro_icon)


# generate the trees
def Tree_generate(times=None):
    def run():
        global stem
        x = random.randrange(-MainVariables.limites, MainVariables.limites)
        z = random.randrange(-MainVariables.limites, MainVariables.limites)

        for y in range(1, 3):
            stem = Voxel(position=(x, y, z), texture=MainVariables.arvore_txtr)
        x = int(stem.x - 1)
        z = int(stem.z - 1)

        def generate_leaves(z, x):
            for ze in range(z, z + 3):
                for xiz in range(x, x + 3):
                    leaf = Voxel(position=(xiz, 3, ze), texture=MainVariables.folha_txtr)
            z += 1
            x -= 1
            for ze in [z, z, z]:
                x += 1
                for xiz in [x]:
                    leaf_top = Voxel(position=(xiz, 4, ze), texture=MainVariables.folha_txtr)
            z += 3
            x -= 1
            for xiz in [x, x]:
                z -= 2
                for ze in [z]:
                    leaf_top = Voxel(position=(xiz, 4, ze), texture=MainVariables.folha_txtr)

        generate_leaves(z, x)

    done = -1
    if times > 0:
        for c in range(times):
            run()
            done += 1


# generate the mobs
def Mob_generate(type_=None, times=None, enemy=False, mob_life=6):
    def run():
        xz = []
        for vez in range(2):
            p = random.randrange(-MainVariables.limites, MainVariables.limites)
            xz.append(p)
        if not enemy:
            models = [MainVariables.vaquinha_model, MainVariables.porquin_model]
            mdl = random.choice(models)
            if mdl == MainVariables.vaquinha_model:
                txtr = MainVariables.vaquinha_txtr
            else:
                txtr = MainVariables.porquin_txtr
            mob = Mob(position=(xz[-2], .2, xz[-1]),
                      mob_life=mob_life,
                      model=mdl,
                      texture=txtr)
            mob.collider = MeshCollider(mob, mesh=mob.model, center=Vec3(0, 0, 0))
            mob.jump(h=2)
        else:
            mob = Mob(position=(xz[-2], 1, xz[-1]),
                      model=MainVariables.block,
                      enemy=True,
                      mob_life=mob_life,
                      texture=MainVariables.ghost_0)
        mob.collider = MeshCollider(mob, mesh=mob.model, center=Vec3(0, 0, 0))
        xz.clear()

    if times > 0:
        for c in range(times):
            run()


class Mob(Button):
    def __init__(self, position=(0, 0, 0), model=MainVariables.block,
                 mob_life=6, enemy=False, texture='noise'):
        super().__init__(parent=scene,
                         position=position,
                         model=model,
                         origin_y=0.5,
                         texture=texture,
                         color=color.color(0, 0, random.uniform(0.9, 1)),
                         scale=.3,
                         )

        self.kkkk = 0
        self.jumping = False
        self.direction = Vec3(0, 0, 0)
        self.paciencia = 0
        self.mob_life = mob_life
        self.enemy = enemy
        self.times_clicked = 0
        self.ja_ta = False
        self.repete = 30
        self.hitting = False
        self.grounded = True
        self.fall_speed = 0
        self.awake = False
        self.frame_anime = Sequence(Func(self.anime_txtr, frame=1),
                                    .2342069,
                                    Func(self.anime_txtr, frame=2),
                                    .2342069,
                                    Func(self.anime_txtr, frame=3),
                                    .2342069,
                                    Func(self.anime_txtr, frame=4),
                                    .2342069,
                                    Func(self.anime_txtr, frame=3),
                                    .2342069,
                                    Func(self.anime_txtr, frame=4),
                                    .2342069,
                                    Func(self.anime_txtr, frame=3),
                                    .2342069,
                                    Func(self.anime_txtr, frame=4),
                                    .2342069,
                                    Func(self.anime_txtr, frame=3),
                                    .2342069,
                                    Func(self.anime_txtr, frame=4),
                                    .2342069,
                                    Func(self.anime_txtr, frame=4),
                                    .2342069,
                                    Func(self.anime_txtr, frame=3),
                                    .2342069,
                                    Func(self.anime_txtr, frame=4),
                                    .2342069,
                                    Func(self.anime_txtr, frame=3),
                                    .2342069,
                                    Func(self.anime_txtr, frame=4),
                                    .2342069,
                                    Func(self.anime_txtr, frame=3),
                                    .2342069,
                                    Func(self.anime_txtr, frame=4),
                                    .2342069,
                                    Func(self.anime_txtr, frame=3),
                                    loop=False)

    def anime_txtr(self, frame):
        if frame == 1:
            self.texture = MainVariables.ghost_1
        elif frame == 2:
            self.texture = MainVariables.ghost_2
        elif frame == 3:
            self.texture = MainVariables.ghost_3
        elif frame == 4:
            self.texture = MainVariables.ghost_4
        elif frame=='puto':
            self.texture = MainVariables.ghost_puto

    def ReactHit(self, damage=1.0):
        if self.mob_life <= 0:
            invoke(self.anime_txtr, frame='puto')
            return

        if self.enemy:
            if self.paciencia > 2:
                invoke(self.anime_txtr, frame='puto')
                self.position -= mouse.world_normal * 55.69 * time.dt
                invoke(self.anime_txtr, frame=4, delay=1.869)
        self.grounded = False
        self.mob_life -= damage
        if self.hovered:
            invoke(self.land)
            self.paciencia += 1
            if self.mob_life >= 0:
                self.shake(magnitude=1.42069, duration=.369)

        if self.mob_life <= 0:
            self.mob_life = 100
            self.color = color.red
            self.fade_out(duration=.69)
            destroy(self, delay=.6969)
            if not self.enemy:
                Mob_generate(times=random.randint(0, 1))
                return
            if self.enemy:
                self.mob_life = 100
                Mob_generate(times=random.randint(0, 1), enemy=True)
                return
        self.times_clicked = 0

    def land(self):
        # print('land')
        self.fall_speed = 0
        self.grounded = True
        self.jumping = False

    def follow(self):
        if self.enemy:
            self.add_script(SmoothFollow(target=MainVariables.player, offset=(0, 2, 0), speed=1.420))

    def walk(self):
        if self.repete > random.uniform(50, 69):
            self.direction = Vec3(
                self.forward * (random.uniform(0, 1) - random.uniform(0, 1))
                + self.right * (random.uniform(0, 1) - random.uniform(0, 1))
            ).normalized()
            self.repete = 0
        self.look_at(self.position + self.direction)
        if not self.hitting:
            self.position += self.direction * .69420 * time.dt
    def passs(self):
        pass
    def start_fall(self):
        self.y_animator.pause()

    def jump(self, h=1.36942069):
        self.kkkk = 0
        self.jumping = True
        self.grounded = False
        self.animate_y(self.y + h, .469, resolution=int(1 // time.dt),
                       curve=curve.out_expo)
        self.position += self.direction * .969420 * time.dt
        invoke(self.start_fall, delay=.5)

    def update(self):
        self.repete += random.uniform(0.1, 0.9)

        if self.enemy:

            dist = distance(self.world_position, MainVariables.player.world_position)
            dist -= .69
            if float(dist) <= 1.6269 and self.paciencia > 2:
                MainVariables.hp -= .2
                MainVariables.player.shake() if MainVariables.hp >= 5 else self.passs()
                invoke(self.anime_txtr, frame=3)
                invoke(self.anime_txtr, frame=2, delay=.2069)
                invoke(self.anime_txtr, frame=3, delay=(.2069)*2)
                invoke(self.anime_txtr, frame=4, delay=(.2069)*3)
            if self.paciencia > 2:
                self.look_at((MainVariables.player.x, MainVariables.player.y + 1.769420, MainVariables.player.z))

        if not self.enemy:
            if self.mob_life > 0:
                if self.grounded:
                    self.walk()

        if self.enemy:
            if self.mob_life > 0:
                if 5 > self.paciencia > 2:
                    self.paciencia = 100
                    MainVariables.ghost_sound.play()
                    self.follow()
                    self.frame_anime.start()


        origin = Vec3(self.world_position)
        hit_info = raycast(origin, direction=self.direction, ignore=(self,), distance=.56942069)

        if hit_info.hit:
            self.hitting = True
            self.kkkk += 1
            if self.kkkk > 60:
                self.jump(h=2.469)
            cima_block = raycast((origin + (0, 1.42069, 0)), direction=self.direction, ignore=(self,), distance=.6)
            if not cima_block.hit:
                self.hitting = True
                if self.grounded:
                    invoke(self.jump)

        else:
            self.hitting = False

        ray = raycast(self.world_position, direction=self.down, distance=0.3, ignore=(self,))
        if ray.hit:
            self.land()
            return
        else:
            self.grounded = False

        if self.enemy is False:
            self.y -= min(self.fall_speed, ray.distance - .01725) * time.dt * 15
            self.fall_speed += time.dt * 1.469420

        if self.y < -7:
            self.ReactHit(.8)

    def input(self, key):
        if self.hovered:
            if key == 'left mouse up':
                if self.enemy is False:
                    MainVariables.mob_sound.play() if self.mob_life >= 3 else self.passs()
                    MainVariables.mob_sound2.play() if self.mob_life == 2 else MainVariables.mob_sound.play()

                elif self.paciencia > 3:
                    print(medo)
                    MainVariables.ghost_hit_sound.play()

                self.times_clicked += 1
                if self.mob_life > 0 and self.times_clicked <= 1:
                    self.ReactHit(damage=1)
                else:
                    self.times_clicked = 1


class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='/carga_roubada/texturas/models/braco',
            texture=MainVariables.braco_txtr,
            scale=0.2,
            rotation=(150, -10, 0),
            position=(0.75, -.6)
        )

    def active(self):
        # self.position = (0.65, -0.6)
        self.rotation = (150, -30.69, 0)

    def passive(self):
        # self.position = (0.75, -0.6)
        self.rotation = (150, -10, 0)

    def input(self, key):
        if key == 'right mouse down' or key == 'left mouse down':
            self.active()
            invoke(self.passive, delay=.1)


class TelaInicial(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='quad',
            scale=(1.8, 1),
            origin=(0, 0),
            position=(0, 0, 0),
            texture='white_cube',
            color=color.dark_gray
        )


medo = ''' 
                     I'M WATCHING YOU 

MMMMMMMMMMMMMNNNNmhooMMMMMMMMMMMMMMMN/-+yhysmMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNdNMNNmmddmmNMMMMMMMMM
MMMMMMMMMMmhyoooydmMMMMMMMMMMMMMMMMmmho:.```````.:odmMMMMM
MMmmMMNh/.`      ``-/ysymMMMMMMMMMMm/`             -yNMMMM
Md.yMy-               .yhMNMMMMMMMMo`               `hMMMM
MNmN/                  `/s.mNMMMMMh`                 .NMMM
MMN/                     .`dmMMMMM+       `-          sNMM
Nyh`         .:           -hmMMMMM-       `:          /NMM
shs          `.           -dmMMMMM:                   +NMM
mNd.                      .dmMMMMMo`                 `hNMM
NMMh.                     .dmMMMMMN/`               `/hNMM
MMMNh:.                  .`dmMMMMMMN+.`          `.:+omNMM
MMMhhsms/.`           `.--`mmMMMMMMMMdo:.-.`...-/shmmyhMMM
MMMohNMMNyy+/-...` `-::/hddMMMMMMMMMMMMNhhooyyhdNMNhohMMMM
MMMNysshdmNdds+o/-/+osdNMMMMMMMMMMMMMMdhmMMMMMMNdo-/mMMMMM
MMMMMMMmy/+sdNmmdddmNNmmmmMMMMMMMMMMMmddhNNMMm+.  .sMMMMMM
MMMMMMMMMN: `-yNMMMMMmhdmmMMMMMMMMMMMMMNhdms/.  `/mhMMMMMM
MMMMMMMMMN+`  `-/ymmNMMMMMMMMMMMMMMMNmdo```   `o+sMMMMMMMM
MMMMMMMMMdos-``   ``:++sddyhdhyohys/.`     ``:+Nd/NMMMMMMM
MMMMMMMMMMMMNdh/                          -y/NMMN:mMMMMMMM
MMMMMMMMMMMMMMMNyo.                     `sdm+MMMMhMMMMMMMM
MMMMMMMMMMMMMMMMMMm: `                `.::NMMhMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMy`yh---.os-+o+.+yhmNm+MMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMy-NMNMMhmMomMssMMMMMm+MMMMMMMMMMMMMMMMM

                           BOO...
'''

if __name__ == '__main__':
    from ursina.prefabs.first_person_controller import FirstPersonController
    # window.vsync = False
    app = Ursina()
    # Sky(color=color.gray)
    ground = Entity(model='plane', scale=(100,1,100), color=color.yellow.tint(-.2), texture='white_cube', texture_scale=(100,100), collider='box')
    e = Entity(model='cube', scale=(1,5,10), x=2, y=.01, rotation_y=45, collider='box', texture='white_cube')
    e.texture_scale = (e.scale_z, e.scale_y)
    e = Entity(model='cube', scale=(1,5,10), x=-2, y=.01, collider='box', texture='white_cube')
    e.texture_scale = (e.scale_z, e.scale_y)

    player = FirstPersonController(model='cube', y=1, origin_y=-.5)
    player.gun = None

    gun = Button(parent=scene, model='cube', color=color.blue, origin_y=-.5, position=(3,0,3), collider='box')
    gun.on_click = Sequence(Func(setattr, gun, 'parent', camera), Func(setattr, player, 'gun', gun))

    gun_2 = duplicate(gun, z=7, x=8)
    slope = Entity(model='cube', collider='box', position=(0,0,8), scale=6, rotation=(45,0,0), texture='brick', texture_scale=(8,8))
    slope = Entity(model='cube', collider='box', position=(5,0,10), scale=6, rotation=(80,0,0), texture='brick', texture_scale=(8,8))
    # hill = Entity(model='sphere', position=(20,-10,10), scale=(25,25,25), collider='sphere', color=color.green)
    # hill = Entity(model='sphere', position=(20,-0,10), scale=(25,25,25), collider='mesh', color=color.green)
    # from ursina.shaders import basic_lighting_shader
    # for e in scene.entities:
    #     e.shader = basic_lighting_shader

    def input(key):
        if key == 'left mouse down' and player.gun:
            gun.blink(color.orange)
            bullet = Entity(parent=gun, model='cube', scale=.1, color=color.black)
            bullet.world_parent = scene
            bullet.animate_position(bullet.position+(bullet.forward*50), curve=curve.linear, duration=1)
            destroy(bullet, delay=1)

    # player.add_script(NoclipMode())
    app.run()

