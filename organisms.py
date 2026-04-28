import random
import math

# Base class for all organisms
class Organism:
    def __init__(self, environment, position=None, species="Unknown", **kwargs):
        self.environment = environment
        self.position = position # (x, y) tuple or None if not spatial
        self.species = species
        self.is_dead = False
        
        # General attributes
        self.energy = kwargs.get("energy", 50)
        self.max_energy = kwargs.get("max_energy", 100)
        self.age = kwargs.get("age", 0)
        self.max_age = kwargs.get("max_age", 30)
        self.reproduction_threshold = kwargs.get("reproduction_threshold", 80)
        self.energy_cost_per_step = kwargs.get("energy_cost_per_step", 1)
        self.growth_rate = kwargs.get("growth_rate", 0) # For plants or similar
        self.speed = kwargs.get("speed", 0) # For mobile organisms

    def is_alive(self):
        return not self.is_dead and self.age < self.max_age and self.energy > 0

    def age_and_consume_energy(self):
        self.age += 1
        self.energy -= self.energy_cost_per_step
        if self.age >= self.max_age or self.energy <= 0:
            self.is_dead = True

    def reproduce(self):
        """Returns a new organism instance if conditions are met, otherwise None."""
        if self.energy >= self.reproduction_threshold and random.random() < 0.3: # 30% chance to reproduce if energy is sufficient
            self.energy *= 0.5 # Parent uses half energy to reproduce
            
            new_position = None
            if self.position:
                # Try to place offspring near parent
                angle = random.uniform(0, 2 * math.pi)
                offset_x = int(self.speed * random.uniform(0.5, 1.5) * math.cos(angle))
                offset_y = int(self.speed * random.uniform(0.5, 1.5) * math.sin(angle))
                new_x = max(0, min(self.environment.grid_size[0] - 1, self.position[0] + offset_x))
                new_y = max(0, min(self.environment.grid_size[1] - 1, self.position[1] + offset_y))
                new_position = (new_x, new_y)

            # Create a new instance of the same species with halved energy
            try:
                offspring_energy = self.energy / 2 
                return self.__class__(environment=self.environment, position=new_position, energy=offspring_energy)
            except Exception as e:
                print(f"Error creating offspring for {self.species}: {e}")
                return None
        return None

    def act(self, environment):
        """Defines the organism's actions in a time step. To be overridden by subclasses."""
        self.age_and_consume_energy()
        # Default action: just age and consume energy. Subclasses will add more.
        pass

# --- Specific Organism Classes ---

class Plant(Organism):
    def __init__(self, environment, position=None, **kwargs):
        super().__init__(environment, position, species="Plant", **kwargs)
        self.energy = kwargs.get("energy", 50) # Plants generate energy
        self.max_energy = kwargs.get("max_energy", 100)
        self.growth_rate = kwargs.get("growth_rate", 0.1)
        self.energy_value = kwargs.get("energy_value", 10) # Energy a consumer gets from eating this plant
        self.max_size = kwargs.get("max_size", 1) # For potential size-based growth/resource

    def grow(self):
        """Plants grow and regenerate energy."""
        if self.is_alive() and self.energy < self.max_energy:
            # Grow based on environment resources or fixed rate
            regen_amount = self.growth_rate * (self.environment.get_resource("food") / self.environment.max_resources.get("food", 1)) if self.environment else self.growth_rate
            self.energy = min(self.max_energy, self.energy + regen_amount * 10) # Scale regen for visible effect
            
            # Plants don't age or consume energy in the same way, they 'grow'
            # We'll override age_and_consume_energy if plants don't age/die like animals
            pass # Plants don't age like animals, they just grow

    def act(self, environment):
        """Plants grow and reproduce."""
        self.grow()
        
        # Plants might reproduce by spreading seeds, not necessarily based on energy threshold like animals
        # For simplicity, we can have them reproduce if they reach a certain 'size' or 'energy'
        if self.energy > self.reproduction_threshold * 0.8 and random.random() < 0.1: # Lower threshold for plant reproduction
             offspring = self.reproduce()
             if offspring:
                 return [offspring] # Return list of new organisms
        return [] # No new organisms

    def reproduce(self):
        """Plant reproduction can be different - e.g., spreading seeds."""
        if self.energy > self.reproduction_threshold and random.random() < 0.4: # Higher chance for plants to spread
            # Parent might lose some energy/resources to reproduce
            self.energy *= 0.7 
            
            new_position = None
            if self.position:
                # Scatter seeds a bit further
                angle = random.uniform(0, 2 * math.pi)
                offset_x = int(15 * random.uniform(0.5, 1.5) * math.cos(angle)) # Seeds scatter wider
                offset_y = int(15 * random.uniform(0.5, 1.5) * math.sin(angle))
                new_x = max(0, min(self.environment.grid_size[0] - 1, self.position[0] + offset_x))
                new_y = max(0, min(self.environment.grid_size[1] - 1, self.position[1] + offset_y))
                new_position = (new_x, new_y)
            
            try:
                # Create a new Plant instance
                # Plants start with a base energy, not half of parent's
                return self.__class__(environment=self.environment, position=new_position, energy=50) 
            except Exception as e:
                print(f"Error creating offspring for {self.species}: {e}")
                return None
        return None

class Herbivore(Organism):
    def __init__(self, environment, position=None, **kwargs):
        super().__init__(environment, position, species="Herbivore", **kwargs)
        self.detection_radius = kwargs.get("detection_radius", 5)
        self.food_source_species = ["Plant"] # What this herbivore eats

    def eat(self, environment):
        """Herbivores search for and eat plants."""
        nearby_plants = environment.get_nearby_organisms(self.position, self.detection_radius, organism_type=self.environment.organism_classes.get("Plant"))
        
        if nearby_plants:
            target_plant = random.choice(nearby_plants)
            plant_energy_value = target_plant.energy_value if hasattr(target_plant, 'energy_value') else 10
            
            self.energy = min(self.max_energy, self.energy + plant_energy_value)
            target_plant.is_dead = True # The plant is consumed
            # print(f"{self.species} at {self.position} ate a Plant. Energy: {self.energy}")
            return True
        return False

    def move(self, environment):
        """Herbivores move randomly or towards food."""
        if self.speed > 0 and self.position:
            # Simple random movement
            angle = random.uniform(0, 2 * math.pi)
            step_distance = self.speed * random.uniform(0.5, 1.5)
            
            # Attempt to move towards food if available nearby
            nearby_plants = environment.get_nearby_organisms(self.position, self.detection_radius, organism_type=self.environment.organism_classes.get("Plant"))
            if nearby_plants:
                target_plant = random.choice(nearby_plants)
                dx = target_plant.position[0] - self.position[0]
                dy = target_plant.position[1] - self.position[1]
                dist = math.hypot(dx, dy)
                if dist > 0:
                    angle = math.atan2(dy, dx)
                else: # Already at the plant's location
                    angle = random.uniform(0, 2 * math.pi) # Move away after eating
            
            offset_x = int(step_distance * math.cos(angle))
            offset_y = int(step_distance * math.sin(angle))
            
            new_x = max(0, min(environment.grid_size[0] - 1, self.position[0] + offset_x))
            new_y = max(0, min(environment.grid_size[1] - 1, self.position[1] + offset_y))
            self.position = (new_x, new_y)
            # print(f"{self.species} moved to {self.position}")

    def act(self, environment):
        if not self.is_alive():
            return

        self.move(environment)
        self.eat(environment)
        self.age_and_consume_energy()
        
        offspring = self.reproduce()
        if offspring:
            return [offspring] # Return new organism
        return []

class Carnivore(Organism):
    def __init__(self, environment, position=None, **kwargs):
        super().__init__(environment, position, species="Carnivore", **kwargs)
        self.detection_radius = kwargs.get("detection_radius", 10)
        self.hunt_chance = kwargs.get("hunt_chance", 0.5)
        self.food_source_species = ["Herbivore"] # What this carnivore eats

    def hunt(self, environment):
        """Carnivores hunt herbivores."""
        # Find nearby herbivores
        nearby_herbivores = environment.get_nearby_organisms(self.position, self.detection_radius, organism_type=self.environment.organism_classes.get("Herbivore"))
        
        if nearby_herbivores and random.random() < self.hunt_chance:
            target_herbivore = random.choice(nearby_herbivores)
            
            # Carnivore gets a significant energy boost from eating a herbivore
            # Assuming herbivore has an 'energy_value' or similar attribute to represent its biomass/energy
            herbivore_energy_value = target_herbivore.energy if hasattr(target_herbivore, 'energy') else 100
            self.energy = min(self.max_energy, self.energy + herbivore_energy_value * 0.8) # Get most of the energy
            target_herbivore.is_dead = True # The herbivore is killed
            # print(f"{self.species} at {self.position} hunted and ate a Herbivore. Energy: {self.energy}")
            return True
        return False

    def move(self, environment):
        """Carnivores move randomly or towards prey."""
        if self.speed > 0 and self.position:
            angle = random.uniform(0, 2 * math.pi)
            step_distance = self.speed * random.uniform(0.5, 1.5)

            # Attempt to move towards prey if available nearby
            nearby_prey = environment.get_nearby_organisms(self.position, self.detection_radius, organism_type=self.environment.organism_classes.get("Herbivore"))
            if nearby_prey:
                target_prey = random.choice(nearby_prey)
                dx = target_prey.position[0] - self.position[0]
                dy = target_prey.position[1] - self.position[1]
                dist = math.hypot(dx, dy)
                if dist > 0:
                    angle = math.atan2(dy, dx)
                else: # Already at the prey's location
                    angle = random.uniform(0, 2 * math.pi) # Move away after hunt
            
            offset_x = int(step_distance * math.cos(angle))
            offset_y = int(step_distance * math.sin(angle))
            
            new_x = max(0, min(environment.grid_size[0] - 1, self.position[0] + offset_x))
            new_y = max(0, min(environment.grid_size[1] - 1, self.position[1] + offset_y))
            self.position = (new_x, new_y)
            # print(f"{self.species} moved to {self.position}")

    def act(self, environment):
        if not self.is_alive():
            return

        self.move(environment)
        self.hunt(environment)
        self.age_and_consume_energy()

        offspring = self.reproduce()
        if offspring:
            return [offspring]
        return []

# Example of how to add new species:
# class Fox(Carnivore):
#     def __init__(self, environment, position=None, **kwargs):
#         super().__init__(environment, position, species="Fox", **kwargs)
#         self.detection_radius = 12
#         self.hunt_chance = 0.6
#         self.food_source_species = ["Rabbit"] # If you had rabbits

# You can add more species like Rabbit, Bear, etc. here
