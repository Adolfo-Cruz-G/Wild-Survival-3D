import json
import os
import random
import time
from datetime import datetime
from typing import List, Dict

class Resource:
    def __init__(self, name: str, quantity: float, unit: str, category: str):
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.category = category

    def to_dict(self):
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "category": self.category
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["quantity"], data["unit"], data["category"])

class History:
    def __init__(self):
        self.logs = []

    def add_log(self, action: str, resource_name: str, amount: float, current_total: float):
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "resource": resource_name,
            "amount": amount,
            "total_after": current_total
        }
        self.logs.append(log_entry)

    def to_dict(self):
        return self.logs

    @classmethod
    def from_dict(cls, data):
        history = cls()
        history.logs = data
        return history

class Inventory:
    def __init__(self):
        self.resources: Dict[str, Resource] = {}
        self.history = History()

    def add_resource(self, name: str, quantity: float, unit: str, category: str, quiet: bool = False):
        name = name.lower()
        if name in self.resources:
            self.resources[name].quantity += quantity
        else:
            self.resources[name] = Resource(name, quantity, unit, category)
        self.history.add_log("ADD", name, quantity, self.resources[name].quantity)
        if not quiet:
            print(f"Agregado {quantity} {unit} de {name}. Total: {self.resources[name].quantity} {unit}.")

    def consume_resource(self, name: str, quantity: float) -> bool:
        name = name.lower()
        if name in self.resources:
            if self.resources[name].quantity >= quantity:
                self.resources[name].quantity -= quantity
                self.history.add_log("CONSUME", name, quantity, self.resources[name].quantity)
                print(f"Consumido {quantity} de {name}. Restante: {self.resources[name].quantity} {self.resources[name].unit}.")
                if self.resources[name].quantity == 0:
                    print(f"¡Atención! Te has quedado sin {name}.")
                return True
            else:
                print(f"No hay suficiente cantidad de {name}. Tienes {self.resources[name].quantity} {self.resources[name].unit}.")
                return False
        else:
            print(f"El recurso '{name}' no existe en el inventario.")
            return False

    def display_inventory(self):
        print("\n--- INVENTARIO ---")
        if not self.resources:
            print("El inventario está vacío.")
        else:
            for name, res in self.resources.items():
                print(f"- {res.name.capitalize()}: {res.quantity} {res.unit} (Categoría: {res.category})")
        print("------------------\n")

    def show_history(self):
        print("\n--- HISTORIAL DE ACCIONES ---")
        if not self.history.logs:
            print("No hay acciones registradas.")
        else:
            for log in self.history.logs[-10:]: # Show last 10 logs
                print(f"[{log['timestamp']}] {log['action']} | {log['amount']} {log['resource']} -> Total restante: {log['total_after']}")
        print("-----------------------------\n")

    def to_dict(self):
        return {
            "resources": {k: v.to_dict() for k, v in self.resources.items()},
            "history": self.history.to_dict()
        }

    @classmethod
    def from_dict(cls, data):
        inv = cls()
        if "resources" in data:
            inv.resources = {k: Resource.from_dict(v) for k, v in data["resources"].items()}
        if "history" in data:
            inv.history = History.from_dict(data["history"])
        return inv

class Player:
    def __init__(self, name: str):
        self.name = name
        self.inventory = Inventory()
        
        # Estadísticas Vitales
        self.health = 100
        self.hunger = 100
        self.thirst = 100
        self.day = 1
        
        self.is_dead = False
        
        self.save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
        self.save_file = os.path.join(self.save_dir, f"save_{self.name.lower().replace(' ', '_')}.json")
        self.load_game()

    def _setup_initial_resources(self):
        self.inventory.add_resource("agua", 10.0, "litros", "vital", quiet=True)
        self.inventory.add_resource("comida", 10.0, "raciones", "vital", quiet=True)
        self.inventory.add_resource("botiquin", 2.0, "unidades", "medicina", quiet=True)

    def reset(self):
        self.inventory = Inventory()
        self.health = 100
        self.hunger = 100
        self.thirst = 100
        self.day = 1
        self.is_dead = False
        self._setup_initial_resources()
        self.save_game()

    def print_hud(self):
        print(f"\n=======================================================")
        print(f" 🌞 DÍA {self.day} | 👤 JUGADOR: {self.name.upper()}")
        print(f" ♥ Salud: {self.health}/100 | 🍗 Hambre: {self.hunger}/100 | 💧 Sed: {self.thirst}/100")
        print(f"=======================================================")

    def clamp_stats(self):
        self.health = max(0, min(100, self.health))
        self.hunger = max(0, min(100, self.hunger))
        self.thirst = max(0, min(100, self.thirst))

        if self.health == 0:
            self.is_dead = True

    def consume(self):
        print("\n¿Qué quieres consumir?")
        print("1. Agua (+30 Sed)")
        print("2. Comida (+30 Hambre)")
        print("3. Botiquín (+40 Salud)")
        print("4. Cancelar")
        opc = input("Elige una opción: ")
        
        if opc == '1':
            self.consume_item("agua")
        elif opc == '2':
            self.consume_item("comida")
        elif opc == '3':
            self.consume_item("botiquin")

    def consume_item(self, item_name: str) -> bool:
        if item_name == "agua":
            if self.inventory.consume_resource("agua", 1.0):
                self.thirst += 30
                print("Glup, glup... Te sientes más hidratado.")
                self.clamp_stats()
                return True
        elif item_name == "comida":
            if self.inventory.consume_resource("comida", 1.0):
                self.hunger += 30
                print("Ñam, ñam... Has saciado tu hambre.")
                self.clamp_stats()
                return True
        elif item_name == "botiquin":
            if self.inventory.consume_resource("botiquin", 1.0):
                self.health += 40
                print("Has curado tus heridas.")
                self.clamp_stats()
                return True
        elif item_name == "carne_cruda":
            if self.inventory.consume_resource("carne_cruda", 1.0):
                self.hunger += 15
                self.health -= 15
                print("Te comiste la carne cruda. Sabe horrible y te duele el estómago.")
                self.clamp_stats()
                return True
        elif item_name == "carne_asada":
            if self.inventory.consume_resource("carne_asada", 1.0):
                self.hunger += 50
                print("¡Deliciosa carne asada! Recuperas mucha energía.")
                self.clamp_stats()
                return True
        return False

    def explore(self):
        print("\nHas salido a explorar los alrededores...")
        # time.sleep(1) # Removed for GUI compatibility
        
        # Explorar cuesta energía
        self.hunger -= 10
        self.thirst -= 15
        
        evento = random.randint(1, 100)
        
        if evento <= 45: # 45% chance of finding resources
            loot = random.choice([
                ("agua", random.randint(1, 3), "litros", "vital"),
                ("comida", random.randint(1, 3), "raciones", "vital"),
                ("madera", random.randint(2, 6), "unidades", "material"),
                ("botiquin", 1, "unidades", "medicina")
            ])
            print(f"¡Tuviste suerte! Encontraste: {loot[1]} de {loot[0]}.")
            self.inventory.add_resource(loot[0], float(loot[1]), loot[2], loot[3])
        elif evento <= 65: # 20% chance bad event
            damage = random.randint(10, 25)
            self.health -= damage
            print(f"¡Cuidado! Un animal salvaje te atacó. Pierdes {damage} de salud.")
        elif evento <= 85: # 20% chance minor bad event
            print("El sol está muy fuerte y el terreno es duro. Te cansaste demasiado.")
            self.thirst -= 15
            self.hunger -= 10
        else: # 15% chance nothing
            print("No encontraste nada útil. Mejor regresa.")
            
        self.clamp_stats()

    def sleep(self):
        print("\nDecides irte a dormir. Pasando al siguiente día...")
        # time.sleep(1.5) # Removed for GUI compatibility
        self.day += 1
        
        # Penalizaciones diarias
        self.hunger -= 30
        self.thirst -= 40
        
        if self.hunger <= 0:
            print("¡Te estás muriendo de hambre!")
            self.health -= 20
        if self.thirst <= 0:
            print("¡Estás deshidratado!")
            self.health -= 30
            
        self.clamp_stats()
        
        if not self.is_dead:
            print("Amanece. Tienes que sobrevivir otro día.")
            self.save_game()

    def save_game(self):
        data = {
            "name": self.name,
            "health": self.health,
            "hunger": self.hunger,
            "thirst": self.thirst,
            "day": self.day,
            "inventory": self.inventory.to_dict()
        }
        try:
            with open(self.save_file, 'w') as f:
                json.dump(data, f, indent=4)
            print("Partida guardada correctamente.")
        except Exception as e:
            print(f"Error al guardar la partida: {e}")

    def load_game(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                
                self.health = data.get("health", 100)
                self.hunger = data.get("hunger", 100)
                self.thirst = data.get("thirst", 100)
                self.day = data.get("day", 1)
                
                if "inventory" in data:
                    self.inventory = Inventory.from_dict(data["inventory"])
                print(f"Partida cargada para el jugador {self.name}.")
            except Exception as e:
                print(f"Error al cargar la partida: {e}")
        else:
            print(f"Nuevo jugador {self.name} creado. Repartiendo recursos iniciales...")
            self._setup_initial_resources()


def main():
    print("\n" * 5)
    print("======================================")
    print("  SUPERVIVENCIA EXTREMA: EL JUEGO")
    print("======================================")
    
    player_name = input("Introduce tu nombre de sobreviviente: ")
    player = Player(player_name)

    while not player.is_dead:
        player.print_hud()
        
        print("¿Qué deseas hacer?")
        print("1. Ver Inventario")
        print("2. Explorar (Busca recursos, consume energía)")
        print("3. Consumir (Curarte, Comer, Beber)")
        print("4. Dormir (Pasar al siguiente día)")
        print("5. Ver Historial")
        print("6. Guardar y Salir")
        
        opcion = input("Elige una acción (1-6): ")
        
        if opcion == '1':
            player.inventory.display_inventory()
        elif opcion == '2':
            player.explore()
        elif opcion == '3':
            player.consume()
        elif opcion == '4':
            player.sleep()
        elif opcion == '5':
            player.inventory.show_history()
        elif opcion == '6':
            player.save_game()
            print("Saliendo del juego. ¡Vuelve pronto!")
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")
            
    if player.is_dead:
        print("\n======================================")
        print(f" 💀 HAS MUERTO EN EL DÍA {player.day} 💀")
        print("  La supervivencia no es para todos...")
        print("======================================")
        
        # Eliminar el archivo de guardado al morir
        if os.path.exists(player.save_file):
            try:
                os.remove(player.save_file)
                print("(Tu partida ha sido borrada permanentemente)")
            except:
                pass

if __name__ == "__main__":
    main()
