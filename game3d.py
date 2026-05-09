from ursina import *
import random
import sys
import os
import atexit
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from supervivencia import Player as LogicPlayer
except ImportError:
    print("Error: No se encuentra supervivencia.py")
    sys.exit(1)

# --- CLASES DE ENTIDADES ---

class Oso(Entity):
    def __init__(self, **kwargs):
        super().__init__(model='cube', color=color.brown, scale=(1.5, 1.2, 2.5), collider='box', **kwargs)
        self.head = Entity(parent=self, model='cube', color=color.brown, scale=(0.6, 0.6, 0.4), y=0.5, z=0.6)
        self.ear_l = Entity(parent=self.head, model='cube', color=color.brown, scale=(0.2, 0.2, 0.1), x=-0.3, y=0.3)
        self.ear_r = Entity(parent=self.head, model='cube', color=color.brown, scale=(0.2, 0.2, 0.1), x=0.3, y=0.3)
        
        # Patas
        self.legs = []
        for x_pos in [-0.4, 0.4]:
            for z_pos in [-0.8, 0.8]:
                leg = Entity(parent=self, model='cube', color=color.brown, scale=(0.3, 0.6, 0.3), x=x_pos, y=-0.8, z=z_pos)
                self.legs.append(leg)
        
        self.health = 20 # Vida reducida a 20 como pediste
        self.health_label = Text(parent=self, text="20/20", y=2, billboard=True, scale=5, color=color.red)
        self.attack_cooldown = 0
        self.walk_timer = 0

    def update(self):
        self.health_label.text = f"{int(self.health)}/20"
        # Mirar al jugador si está cerca
        dist = distance(self, player)
        if dist < 20:
            self.look_at(player)
            self.rotation_x = 0 # No rotar hacia arriba/abajo
            
            if dist > 3:
                # Caminar hacia el jugador
                self.position += self.forward * time.dt * 3
                # Animación de patas
                self.walk_timer += time.dt * 10
                for i, leg in enumerate(self.legs):
                    leg.rotation_x = math.sin(self.walk_timer + (i % 2) * math.pi) * 30
            else:
                # Atacar
                self.attack_cooldown -= time.dt
                if self.attack_cooldown <= 0:
                    logic_player.health -= 5
                    logic_player.clamp_stats()
                    show_pickup("¡EL OSO TE MORDIÓ! -5 HP")
                    self.attack_cooldown = 2.0 # Atacar cada 2 segundos
                    
def show_damage(pos, val):
    t = Text(text=f"-{val}", position=pos + Vec3(0,2,0), origin=(0,0), color=color.red, scale=3, billboard=True)
    t.animate_y(t.y + 1, duration=1)
    t.animate_color(color.clear, duration=1)
    destroy(t, delay=1)

def create_water():
    e = Entity()
    Entity(parent=e, model='cube', color=color.blue, scale=0.5, y=0.25)
    return e

def create_food():
    e = Entity()
    Entity(parent=e, model='sphere', color=color.red, scale=0.5, y=0.25)
    Entity(parent=e, model='cube', color=color.green, scale=(0.05, 0.3, 0.05), y=0.55, rotation_z=30)
    return e

def create_medkit():
    e = Entity()
    Entity(parent=e, model='cube', color=color.white, scale=(0.6, 0.4, 0.3), y=0.2)
    Entity(parent=e, model='cube', color=color.red, scale=(0.15, 0.3, 0.31), y=0.2)
    Entity(parent=e, model='cube', color=color.red, scale=(0.3, 0.15, 0.31), y=0.2)
    Entity(parent=e, model='cube', color=color.gray, scale=(0.2, 0.1, 0.05), y=0.45)
    return e

def create_carne_cruda():
    e = Entity()
    Entity(parent=e, model='cube', color=color.red, scale=(0.4, 0.2, 0.4), y=0.1)
    return e

def create_carne_asada():
    e = Entity()
    Entity(parent=e, model='cube', color=color.rgb(100, 50, 0), scale=(0.4, 0.2, 0.4), y=0.1)
    return e

def spawn_resource():
    r_type = random.choice(["agua", "comida", "botiquin"])
    creators = {"agua": create_water, "comida": create_food, "botiquin": create_medkit}
    x = random.choice([random.uniform(-40, -5), random.uniform(5, 40)])
    z = random.choice([random.uniform(-40, -5), random.uniform(5, 40)])
    ent = creators[r_type]()
    ent.position = (x, 0, z)
    ent.r_type = r_type
    return ent

def spawn_oso():
    if len(osos) < 4:
        ox = random.uniform(-40, 40)
        oz = random.uniform(-40, 40)
        # Solo spawnear lejos del jugador
        if distance((ox, 1, oz), player.position) > 15:
            oso = Oso(position=(ox, 1, oz))
            osos.append(oso)

def show_pickup(text_str):
    t = Text(text=text_str, origin=(0,0), y=0, color=color.yellow, scale=2, z=-5)
    t.animate('y', 0.2, duration=1.5)
    t.animate('color', color.clear, duration=1.5)
    destroy(t, delay=1.5)

def toggle_inventory():
    inventory_panel.enabled = not inventory_panel.enabled
    mouse.locked = not inventory_panel.enabled
    mouse.visible = inventory_panel.enabled
    if inventory_panel.enabled:
        update_inventory_ui()

def input(key):
    global game_time
    if key == 'i' or key == 'escape':
        toggle_inventory()
        
    if key == 'c' and distance(player, fogata) < 5:
        tiene_carne_cruda = "carne_cruda" in logic_player.inventory.resources and logic_player.inventory.resources["carne_cruda"].quantity > 0
        if tiene_carne_cruda:
            logic_player.inventory.consume_resource("carne_cruda", 1.0)
            logic_player.inventory.add_resource("carne_asada", 1.0, "raciones", "vital", quiet=True)
            show_pickup("+ 1 CARNE ASADA")
            update_inventory_ui()
            
    if key == 'left mouse button' or key == 'e':
        # Ataque
        for o in osos[:]:
            if distance(player, o) < 6:
                o.health -= 3
                show_damage(o.position, 3)
                if o.health <= 0:
                    carne = create_carne_cruda()
                    carne.position = (o.x, 0.2, o.z)
                    carne.r_type = "carne_cruda"
                    items.append(carne)
                    osos.remove(o)
                    destroy(o)
                    show_pickup("¡OSO ELIMINADO!")
                break
            
    if key == 'z' and distance(player, fogata) < 5 and (game_time > 0.6 or game_time < 0.2):
        if not logic_player.is_dead:
            night_overlay.animate_color(color.black, duration=1)
            def wake_up():
                global game_time
                logic_player.sleep()
                game_time = 0.0
                night_overlay.animate_color(color.rgba(0.02, 0.02, 0.06, 0.0), duration=1)
            invoke(wake_up, delay=1.2)

def update():
    global tick_counter, game_time
    is_moving = False # Inicializar para evitar errores con el inventario
    
    if logic_player.is_dead:
        death_text.enabled = True
        mouse.locked = False
        mouse.visible = True
        if held_keys['r']:
            logic_player.reset()
            player.position = (0, 1.5, 0)
            death_text.enabled = False
            mouse.locked = True
            for item in items: destroy(item)
            items.clear()
            for _ in range(15): items.append(spawn_resource())
            for z in enemigos: destroy(z)
            enemigos.clear()
            for o in osos: destroy(o)
            osos.clear()
            game_time = 0.0
        return

    # Movimiento 3D
    base_speed = 10 * time.dt
    current_speed = base_speed * (1.8 if held_keys['shift'] else 1.0)
    
    if not inventory_panel.enabled:
        if held_keys['w']: player.position += player.forward * current_speed
        if held_keys['s']: player.position -= player.forward * current_speed
        if held_keys['a']: player.position -= player.right * current_speed
        if held_keys['d']: player.position += player.right * current_speed
        
        if not player.grounded:
            player.vy -= 40 * time.dt
            player.y += player.vy * time.dt
            if player.y <= 1.5:
                player.y = 1.5
                player.vy = 0
                player.grounded = True
        
        if held_keys['space'] and player.grounded:
            player.vy = 15
            player.grounded = False
            
        player.rotation_y += mouse.velocity[0] * 100
        camera.rotation_x -= mouse.velocity[1] * 100
        camera.rotation_x = clamp(camera.rotation_x, -30, 45)
            
        # Animación Caminar
        is_moving = held_keys['w'] or held_keys['s'] or held_keys['a'] or held_keys['d']
        if is_moving and player.grounded:
            anim_speed = 25 if held_keys['shift'] else 15
            player.brazo_izq.rotation_x = math.sin(time.time() * anim_speed) * 45
            player.brazo_der.rotation_x = math.sin(time.time() * anim_speed + math.pi) * 45
            player.pierna_izq.rotation_x = math.sin(time.time() * anim_speed + math.pi) * 45
            player.pierna_der.rotation_x = math.sin(time.time() * anim_speed) * 45
        else:
            player.brazo_izq.rotation_x = lerp(player.brazo_izq.rotation_x, 0, time.dt * 10)
            player.brazo_der.rotation_x = lerp(player.brazo_der.rotation_x, 0, time.dt * 10)
            player.pierna_izq.rotation_x = lerp(player.pierna_izq.rotation_x, 0, time.dt * 10)
            player.pierna_der.rotation_x = lerp(player.pierna_der.rotation_x, 0, time.dt * 10)
            
        player.x = clamp(player.x, -45, 45)
        player.z = clamp(player.z, -45, 45)
            
        # Items
        for item in items[:]:
            if distance(player, item) < 3.5:
                qty = random.randint(1, 3) if item.r_type in ["agua", "comida"] else 1
                unit = "litros" if item.r_type == "agua" else "raciones"
                cat = "vital" if item.r_type in ["agua", "comida", "carne_cruda", "carne_asada"] else "medicina"
                
                logic_player.inventory.add_resource(item.r_type, float(qty), unit, cat, quiet=True)
                show_pickup(f"+ {qty} {item.r_type.upper()}")
                items.remove(item)
                destroy(item)

    # Vitales
    tick_counter += 1
    if tick_counter >= 120:
        logic_player.hunger -= 1
        logic_player.thirst -= 1.5
        logic_player.clamp_stats()
        tick_counter = 0
        
    # Variables de estado de tiempo
    es_noche = game_time > 0.6 or game_time < 0.2
    es_noche_enemigos = game_time > 0.55 and game_time < 0.95
    
    # CICLO TIEMPO (Día lento, Noche normal)
    if not es_noche:
        game_time += time.dt / 180.0 # El día dura 3 veces más (3 min reales)
    else:
        game_time += time.dt / 60.0  # La noche dura 1 min real
        
    if game_time >= 1.0:
        game_time = 0.0
        logic_player.day += 1
        
    total_hours = game_time * 24 + 6
    if total_hours >= 24: total_hours -= 24
    clock_text.text = f"DIA: {logic_player.day}\nHORA: {int(total_hours):02d}:{int((total_hours%1)*60):02d}"
    stats_text.text = f"HP: {int(logic_player.health)}\nHUNGER: {int(logic_player.hunger)}\nTHIRST: {int(logic_player.thirst)}"

    pivot_cielo.rotation_z = -(game_time * 360) + 90
    
    night_overlay.color = color.rgba(0.02, 0.02, 0.06, 0.8 if es_noche else 0)
        
    # Enemigos Nocturnos
    if es_noche_enemigos:
        if len(enemigos) < 6:
            ex, ez = player.x + random.uniform(-20, 20), player.z + random.uniform(-20, 20)
            if distance((ex, 0, ez), fogata.position) > 12:
                zombie = Entity(model='cube', color=color.black, scale=(0.8, 1.8, 0.8), position=(ex, 0.9, ez), collider='box')
                enemigos.append(zombie)
        for z in enemigos[:]:
            if distance(z, fogata) > 10:
                z.look_at(player)
                z.position += z.forward * time.dt * 4
            if distance(z, player) < 1.5:
                logic_player.health -= 15 * time.dt
                logic_player.clamp_stats()
    else:
        for z in enemigos: destroy(z)
        enemigos.clear()

    # Spawning
    if not es_noche_enemigos and random.random() < 0.002: spawn_oso()
        
    # Fogata
    cerca = distance(player, fogata) < 5
    tiene_carne = "carne_cruda" in logic_player.inventory.resources and logic_player.inventory.resources["carne_cruda"].quantity > 0
    texto = ""
    if es_noche:
        if cerca: texto += "Presiona [Z] para Dormir\n"; night_warning.enabled = False
        else: night_warning.enabled = True; night_warning.text = "¡Noche Peligrosa! Busca fuego"
    else:
        night_warning.enabled = False
        if cerca: texto += "Día tranquilo...\n"
    if cerca and tiene_carne: texto += "Presiona [C] para Cocinar\n"
    fogata_text.text = texto
    fogata_text.color = color.yellow if cerca else color.clear

    for item in items: item.rotation_y += 50 * time.dt
        
    # SONIDOS ELIMINADOS PARA EVITAR ERRORES DE ARCHIVO FALTANTE

def update_inventory_ui():
    for child in inventory_panel.children[:]:
        if child.name != 'bg': 
            destroy(child)
    Text(text="INVENTARIO", parent=inventory_panel, y=0.35, origin=(0,0), scale=2, color=color.orange)
    y = 0.2
    for name, res in logic_player.inventory.resources.items():
        if res.quantity <= 0: continue
        creators = {"agua": create_water, "comida": create_food, "botiquin": create_medkit, "carne_cruda": create_carne_cruda, "carne_asada": create_carne_asada}
        if name in creators:
            icon = creators[name]()
            icon.parent = inventory_panel
            icon.scale = 0.08
            icon.position = (-0.3, y, -1)
        Text(text=f"{name.upper()}: {int(res.quantity)}", parent=inventory_panel, y=y, x=-0.1)
        btn = Button(text="Usar", parent=inventory_panel, y=y, x=0.3, scale=(0.12, 0.04), color=color.azure)
        btn.on_click = lambda n=name: [logic_player.consume_item(n), update_inventory_ui()]
        y -= 0.08
    Button(text="Cerrar", parent=inventory_panel, y=-0.4, scale=(0.2, 0.05), color=color.red, on_click=toggle_inventory)

if __name__ == "__main__":
    app = Ursina(title="Supervivencia 3D", borderless=False)
    logic_player = LogicPlayer("Sobreviviente_3D")
    atexit.register(logic_player.save_game)
    
    ground = Entity(model='plane', scale=(100, 1, 100), color=color.lime, texture='white_cube', texture_scale=(50, 50), collider='box')
    for _ in range(100):
        Entity(model='cube', color=color.green, scale=(0.1, random.uniform(0.2, 1), 0.1), position=(random.uniform(-45, 45), 0, random.uniform(-45, 45)))
    
    player = Entity(position=(0, 1.5, 0))
    player.vy = 0
    player.grounded = True
    torso = Entity(parent=player, model='cube', color=color.blue, scale=(0.8, 1.2, 0.4))
    cabeza = Entity(parent=player, model='cube', color=color.peach, scale=(0.6, 0.6, 0.6), y=0.9)
    pelo = Entity(parent=cabeza, model='cube', color=color.brown, scale=(1.05, 0.2, 1.05), y=0.4)
    player.brazo_izq = Entity(parent=player, model='cube', color=color.peach, scale=(0.3, 1.2, 0.3), x=-0.55, y=0.6, origin_y=0.5)
    player.brazo_der = Entity(parent=player, model='cube', color=color.peach, scale=(0.3, 1.2, 0.3), x=0.55, y=0.6, origin_y=0.5)
    player.pierna_izq = Entity(parent=player, model='cube', color=color.dark_gray, scale=(0.35, 1.2, 0.35), x=-0.2, y=-0.6, origin_y=0.5)
    player.pierna_der = Entity(parent=player, model='cube', color=color.dark_gray, scale=(0.35, 1.2, 0.35), x=0.2, y=-0.6, origin_y=0.5)
    
    fogata = Entity(position=(5, 0, 5))
    Entity(parent=fogata, model='cube', color=color.orange, scale=(0.4, 0.6, 0.4), y=0.3)
    fogata_text = Text(parent=fogata, text="", y=2.5, billboard=True, scale=5, color=color.yellow)
    
    camera.parent = player
    camera.position = (0, 2.5, -8)
    camera.look_at(cabeza)
    camera.fov = 90
    mouse.locked = True

    pivot_cielo = Entity()
    sol = Entity(parent=pivot_cielo, model='sphere', color=color.yellow, scale=10, x=80, unlit=True)
    luna = Entity(parent=pivot_cielo, model='sphere', color=color.light_gray, scale=8, x=-80, unlit=True)

    tick_counter, game_time = 0, 0.0
    items, enemigos, osos = [], [], []
    for _ in range(15): items.append(spawn_resource())
    
    night_overlay = Entity(parent=camera.ui, model='quad', scale=2, color=color.rgba(0,0,0,0), z=5)
    stats_text = Text(text="", position=window.top_left + Vec2(0.02, -0.02), scale=1.5, background=True)
    clock_text = Text(text="", position=window.top_right + Vec2(-0.3, -0.02), scale=1.5, background=True)
    night_warning = Text(text="", y=0.3, scale=2, color=color.red, enabled=False, background=True)
    death_text = Text(text="HAS MUERTO\n'R' REINICIAR", scale=3, color=color.red, enabled=False, background=True)
    
    inventory_panel = Entity(parent=camera.ui, enabled=False)
    bg = Entity(parent=inventory_panel, model='quad', scale=(0.8, 0.9), color=color.black90, z=1, name='bg')
    
    Entity(parent=camera.ui, model='quad', scale=0.01, color=color.white) # Mira

    app.run()
