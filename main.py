# ===================================
# Author: Luís Otávio
# GitHub: https://github.com/luis-ss/mineppad
# Youtube Video:
# Date created: 22/02/2021
# ==================================
#
# Welcome to...
#
#                                   -=- MINEPPAD -=-
#  ___________________________________________________________________________________
# |                                                                                   |
# |                  ...                   /+o++++/:                                  |
# |           .-://++++++/:`          `.:++ooo++o+++o++/-`                            |
# |         -//:/++++++++///      `.-/++++++oo+++o++++o+++/:.                         |
# |         /+.`.+++++++////. ```:+o+++++o++++++oo++++++oo+o+/:` :y+s++o-/:.-``` `    |
# |         -+////:::++/////:`yhyo/o+++++o+oo++oo++++o+oo++//::./yysossssyyyysyy/::-  |
# |       ``.----::://///////`ydy+/+++/++ooooo++++++oo+++//:-:::oy+////////+yyyo:+y+  |
# |    .:///++++++++/////////`+dy+/+++://+o++o++++++//:::/::::/:oyysssooo+oyys/-shy:  |
# |   :++++++++++++////////:-.ydy+/+///::/oo++/++//::-----::::::oyyyyyyyyyyyo::yhds.  |
# |  `++++++++++///::::::::/ohddy//+o+///:://////:/:::-:::/:::::oyyyyyyyyys/:oyhdh+   |
# |  .++++++++/--/osyyhhhdddddddy++/o////+///////::::::::::://:-/osssyyyyo:/syhdmy:   |
# |   /+++++++`/hdddddddddddddddy///++////+o+//+/:://::::/::://`-///////::oyyhmmds`   |
# |   .++++++/ yddddddddddddddhyo+//++o++++/++/+/::/:::::::::/:`oyyyyssssyyyhmmmh+    |
# |    -/+++//.+dddddddh++++//++ `./+++++/++/+++::-:///::/::-.`.syyyyyyyyhhmmmmdy:    |
# |     `-::::..ddddddddhhhhssdd.   `.-//o+///+/::::::/:/-.`   .ymmmmmdddmdddddds`    |
# |             sdddddddddds``sd/       `-/+/+oo/::/:-.`         -::/+osyhhddmdy+     |
# |               .+syhhyyso/-`             .:///::.                      ``.---`     |
# |___________________________________________________________________________________|

from modulos.classes import *
from ursina.prefabs.health_bar import HealthBar

app = Ursina()

# setting menu

tela_inicial = TelaInicial()
window.title = 'Mineppad'
start_button = Button(
    scale=(.3, .1),
    position=(0, 0, 0),
    color=color.lime.tint(-.25),
    text='Start', )
text = Text(text='MINEPPAD', wordwrap=10, origin=(-.5, .5), position=(-.195, .2, 0), background=True, scale=(3, 3))

player = Entity()


# play button do this
def play():
    inventory.visible = True
    SetInventoryItems.run()
    health_bar.visible = True
    destroy(start_button)
    tela_inicial.visible = False
    text.visible = False
    window.exit_button.visible = False
    player_()
    hand = Hand()
    # creating the ground
    MainVariables.limites //= 2
    MainVariables.limites += 1

    for y in range(0, -3, -1):
        for z in range(-MainVariables.limites, MainVariables.limites):
            for x in range(-MainVariables.limites, MainVariables.limites):
                voxel = Voxel(position=(x, y, z))
    # setting the mobs and trees
    Tree_generate(times=10)
    Mob_generate(mob_life=8, times=random.randint(2,3), enemy=True)
    Mob_generate(mob_life=4, times=random.randint(1,5))


# setting the map limits in m²
MainVariables.limites = 25

# setting the inventory
inventory = Inventory()
health_bar = HealthBar(bar_color=color.lime.tint(-.25), roundness=.5, max_value=10, position=(-0.25, -0.3102))
inventory.visible = False
health_bar.visible = False

# decreases the player's HP if he falls
mundo_y = -5
vidas = 5
count=0
if health_bar.value > 0:
    def aumenta_vida():
        if MainVariables.hp<10:
            MainVariables.hp+=1
        if MainVariables.hp>10:
            MainVariables.hp = 10
    def update():
        global mundo_y, vidas, count
        count+=.69
        if MainVariables.hp<10 and count>69:
            invoke(aumenta_vida, delay=6.69)
            count=0
        MainVariables.hp = round(MainVariables.hp, 1)
        if MainVariables.hp // 1 == MainVariables.hp:
            MainVariables.hp = int(MainVariables.hp)

        if not health_bar.value == MainVariables.hp:
            health_bar.value = MainVariables.hp

        if MainVariables.player.y < mundo_y:
            mundo_y -= 15
            MainVariables.hp -= 1

        if health_bar.value <= 0:
            print('aaa')
            vidas -= 1
            mundo_y = 0
            MainVariables.player.position = (random.randint(-MainVariables.limites, MainVariables.limites),
                                             6.9,
                                             random.randint(-MainVariables.limites, MainVariables.limites))
            MainVariables.hp = 11

        if vidas == 0:
            pass
start_once = Sequence(Func(play), loop=False)


# just will start once
def seq():
    start_once.start()


carga_roubada = {
    'porquin_txtr': load_texture('carga_roubada/texturas/mobs/porquin_txtr.png'),
    'vaquinha_txtr': load_texture('carga_roubada/texturas/mobs/vaquinha_txtr.png'),
    'braco_txtr': load_texture('carga_roubada/texturas/blocos/braco_txtr.png'),
    'table_txtr': load_texture('carga_roubada/texturas/blocos/table_txtr.png'),
    'ghost_puto': load_texture('carga_roubada/texturas/mobs/ghost_txtr/ghost_putasso.png'),
    'mob_sound': Audio('mob_sound', loop=False, autoplay=False, volume=.05),
    'mob_sound2': Audio('mob_sound2', loop=False, autoplay=False, volume=.5),
    'ghost_sound': Audio('ghost_risada_cabulosa', loop=False, autoplay=False, volume=.2),
    'ghost_hit_sound': Audio('ai_ui_do_ghost', loop=False, autoplay=False, volume=.2)
}
updict = {}
for frame in ['0', '1', '2', '3', '4']:
    filename = 'ghost_frame' + frame + '.png'
    updict[f'ghost_{frame}'] = load_texture(f'carga_roubada/texturas/mobs/ghost_txtr/{filename}')
carga_roubada.update(updict)
# send to modulos

MainVariables.porquin_txtr = carga_roubada['porquin_txtr']
MainVariables.vaquinha_txtr = carga_roubada['vaquinha_txtr']
MainVariables.braco_txtr = carga_roubada['braco_txtr']
MainVariables.table_txtr = carga_roubada['table_txtr']
MainVariables.ghost_0 = carga_roubada['ghost_0']
MainVariables.ghost_1 = carga_roubada['ghost_1']
MainVariables.ghost_2 = carga_roubada['ghost_2']
MainVariables.ghost_3 = carga_roubada['ghost_3']
MainVariables.ghost_4 = carga_roubada['ghost_4']
MainVariables.ghost_puto = carga_roubada['ghost_puto']
MainVariables.mob_sound = carga_roubada['mob_sound']
MainVariables.mob_sound2 = carga_roubada['mob_sound2']
MainVariables.ghost_sound = carga_roubada['ghost_sound']
MainVariables.ghost_hit_sound = carga_roubada['ghost_hit_sound']


if __name__ == '__main__':
    start_button.on_click = seq
    app.run()
