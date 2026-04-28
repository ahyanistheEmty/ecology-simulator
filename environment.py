import random
# Assuming organism classes will be defined in organisms.py and imported here
# Or, this Environment class might dynamically load them.
# For simplicity, we'll assume direct import or a mechanism to get class by name.

class Environment:
    def __init__(self, settings):
        self.grid_size = settings.get("grid_size", [10, 10])
        self.terrain_type = settings.get("terrain_type", "plains")
        self.resources = settings.get("resources", {"food": 1000})
        self.resource_regeneration_rate = settings.get("resource_regeneration_rate", {"food": 0.01})
        self.max_resources = settings.get("max_resources", {"food": 2000})
        
        self.organisms_in_environment = [] # List of organism objects
        self.grid = self._create_grid() # Optional: for spatial simulation
        
        # Attempt to dynamically import organism classes
        self.organism_classes = {}
        try:
            import organisms
            for name, obj in vars(organisms).items():
                if isinstance(obj, type) and obj.__module__ == 'organisms':
                    self.organism_classes[name] = obj
            print(f"Loaded organism classes: {list(self.organism_classes.keys())}")
        except ImportError:
            print("Warning: Could not import organism classes from organisms.py. Organism instantiation may fail.")
        except Exception as e:
            print(f"An error occurred during organism class loading: {e}")


    def _create_grid(self):
        # Placeholder for grid creation if spatial simulation is needed
        # For now, we can simulate a non-spatial or loosely spatial environment
        return None 

    def add_organism(self, species_name, initial_params):
        """Adds an organism to the environment. Returns the created organism object."""
        if species_name in self.organism_classes:
            OrganismClass = self.organism_classes[species_name]
            
            # Determine initial position if grid-based
            position = (random.randint(0, self.grid_size[0]-1), random.randint(0, self.grid_size[1]-1)) if self.grid else None
            
            try:
                # Pass position and any other specific parameters
                organism = OrganismClass(environment=self, position=position, **initial_params)
                self.organisms_in_environment.append(organism)
                return organism
            except Exception as e:
                print(f"Error creating instance of {species_name}: {e}")
                return None
        else:
            print(f"Error: Organism species '{species_name}' not found or could not be loaded.")
            return None

    def remove_organism(self, organism):
        """Removes an organism from the environment."""
        if organism in self.organisms_in_environment:
            self.organisms_in_environment.remove(organism)
            # Potentially decrement resources or add to decay
        else:
            print(f"Warning: Attempted to remove organism not in environment: {organism}")

    def update_environment(self):
        """Updates environmental factors like resource regeneration."""
        for resource, rate in self.resource_regeneration_rate.items():
            if resource in self.resources:
                regen_amount = rate * (self.max_resources.get(resource, 1000) - self.resources[resource]) # Regenerate up to max
                self.resources[resource] = min(self.resources[resource] + regen_amount, self.max_resources.get(resource, 1000))
        # Add other environmental updates like weather, etc.

    def get_nearby_organisms(self, position, radius, organism_type=None):
        """Finds organisms within a certain radius of a position."""
        # This is a simplified search. A spatial grid would be more efficient.
        nearby = []
        for org in self.organisms_in_environment:
            if org.position: # Check if organism has a position attribute
                distance = ((org.position[0] - position[0])**2 + (org.position[1] - position[1])**2)**0.5
                if distance <= radius:
                    if organism_type is None or isinstance(org, organism_type):
                        nearby.append(org)
        return nearby

    def consume_resource(self, resource_name, amount):
        """Consumes a resource, returning the amount actually consumed."""
        if resource_name in self.resources:
            available = self.resources[resource_name]
            consumed = min(amount, available)
            self.resources[resource_name] -= consumed
            return consumed
        return 0
    
    def get_resource(self, resource_name):
        """Gets the current amount of a resource."""
        return self.resources.get(resource_name, 0)

    def get_all_organisms(self):
        return self.organisms_in_environment
