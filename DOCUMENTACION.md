# Wild Survival 3D: Proyecto de Software de Supervivencia

## 1. Resumen
**Wild Survival 3D** es una aplicación de software funcional diseñada como un simulador de supervivencia en tercera persona. El proyecto integra una lógica de negocio sólida (gestión de recursos y estados vitales) con un motor gráfico 3D dinámico. El jugador debe gestionar su salud, hambre y sed mientras explora un entorno hostil, caza osos para obtener alimento y sobrevive a ciclos de día y noche.

---

## 2. Desarrollo del Proyecto

### A. Documento de Requerimientos (Perspectiva del Cliente)
El sistema debe permitir al usuario:
1.  **Control Total 3D**: Moverse en un entorno tridimensional con cámara en tercera persona.
2.  **Gestión Vital**: Visualizar y mantener niveles de Salud, Hambre y Sed.
3.  **Ciclo de Tiempo**: Experimentar un ciclo día/noche que afecte la jugabilidad (aparición de enemigos nocturnos).
4.  **Sistema de Combate**: Atacar depredadores (osos), recibir daño y visualizar la vida de los enemigos.
5.  **Cacería y Cocina**: Obtener carne cruda de los osos y procesarla en una fogata para mejorar sus propiedades nutricionales.
6.  **Inventario Interactivo**: Abrir una interfaz para consumir agua, comida o suministros médicos.
7.  **Persistencia**: Guardado automático del progreso del jugador (Día, recursos y estadísticas).

### B. Simulación de Etapas: Análisis y Diseño

#### Diagrama de Clases (UML Completo)
Este diagrama representa la arquitectura integral del software, detallando las relaciones de dependencia, composición y asociación entre los módulos de lógica y las entidades del motor 3D.

```mermaid
classDiagram
    class Player {
        -String name
        -float health
        -float hunger
        -float thirst
        -int day
        -boolean is_dead
        +Inventory inventory
        +save_game() void
        +load_game() void
        +consume_item(name) bool
        +explore() void
        +sleep() void
        +reset() void
        +clamp_stats() void
    }

    class Inventory {
        +Dict resources
        +History history
        +add_resource(name, qty, unit, cat) void
        +consume_resource(name, qty) bool
        +display_inventory() void
    }

    class Resource {
        +String name
        +float quantity
        +String unit
        +String category
        +to_dict() Dict
    }

    class History {
        +List logs
        +add_log(action, res, amt, total) void
    }

    class Oso {
        +float health
        +float attack_cooldown
        +Entity health_label
        +update() void
        +attack(Player p) void
    }

    class Zombie {
        +Entity model
        +update() void
        +attack(Player p) void
    }

    class Item3D {
        +String r_type
        +Entity model
        +on_pickup() void
    }

    class Fogata {
        +Vector3 position
        +boolean is_active
        +interact(Player p) void

      Player *-- Inventory : posee
    Inventory *-- History : registra
    Inventory o-- Resource : contiene
    Player ..> Oso : Interactua
    Player ..> Zombie : Recibe_dano
    Player ..> Fogata : Usa
    Item3D --> Resource : Representa


#### Diagrama Entidad-Relación (ERD)
Este diagrama representa el modelo de datos persistente que se almacena en los archivos JSON del sistema.

```mermaid
erDiagram
    PLAYER ||--|| INVENTORY : posee
    INVENTORY ||--o{ RESOURCE : almacena
    INVENTORY ||--o{ HISTORY_LOG : registra
    
    PLAYER {
        string name PK
        float health
        float hunger
        float thirst
        int day
    }
    
    RESOURCE {
        string name PK
        float quantity
        string unit
        string category
    }
    
    HISTORY_LOG {
        datetime timestamp
        string action
        float amount
        float total_after
    }
```

### C. Detalle de la Fase de Ejecución (Paso a Paso)
1.  **Fase 1: Motor de Lógica**: Creación de las clases base en Python para manejar el inventario y las estadísticas vitales sin gráficos.
2.  **Fase 2: Entorno 3D**: Implementación de Ursina Engine para generar el terreno, la fogata y el cielo dinámico.
3.  **Fase 3: IA de Enemigos**: Desarrollo de la entidad `Oso` con IA de persecución, animaciones de patas y sistema de salud con etiquetas visuales.
4.  **Fase 4: Interfaz de Usuario (UI)**: Creación del HUD (Heads-Up Display) para HP/Hambre/Sed y el panel de inventario interactivo.
5.  **Fase 5: Mecánicas Avanzadas**: Implementación de la zona segura (campo de fuerza en la fogata) y el sistema de cocción de carne.
6.  **Fase 6: Pulido y Debugging**: Corrección de errores de variables locales, optimización de sonidos y ajuste de la escala del tiempo (Día 3x más largo que la noche).

---

## 3. Conclusión
El proyecto demuestra que es posible integrar sistemas de gestión complejos con entornos gráficos interactivos utilizando Python. Se logró un equilibrio entre la dificultad del juego y la experiencia de usuario, cumpliendo con los principios de diseño de software modular y persistencia de datos.

---

## 4. Despliegue (Instrucciones)

### Requisitos Previos
*   Python 3.10 o superior.
*   Librería Ursina Engine.

### Instalación de Dependencias
```bash
pip install ursina
```

### Ejecución del Sistema
Para iniciar el juego, ejecute el archivo principal:
```bash
python game3d.py
```

### Repositorio
El código fuente completo se encuentra organizado en:
*   `game3d.py`: Motor visual y bucle principal.
*   `supervivencia.py`: Lógica de negocio y persistencia.
*   `/saves/`: Directorio donde se almacenan los archivos JSON de progreso.
