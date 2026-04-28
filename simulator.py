import json
from environment import Environment
# Assuming Organism class is defined in organisms.py and imported by Environment or used directly here.
# For this basic structure, we'll assume Environment can handle organism instantiation internally or
# organisms.py is imported and used to create specific types.

class EcologySimulator:
    def __init__(self, config_path="config.json"):
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file '{config_path}' not found.")
            # Provide default config or exit
            self.config = {
                "simulation_duration": 100,
                "time_step": 1,
                "environment_settings": {
                    "size": (10, 10), # Example: grid size
                    "resources": {"food": 1000} # Example resources
                },
                "organisms": [
                    {"species": "Herbivore", "initial_population": 10, "initial_params": {"energy": 100}},
                    {"species": "Plant", "initial_population": 50, "initial_params": {"growth_rate": 0.1}}
                ]
            }
            print("Using default configuration.")
            
        self.environment = Environment(self.config.get('environment_settings', {}))
        self.organisms = []
        self.current_time = 0

        # Initialize organisms based on config
        # This part relies heavily on how organisms.py and environment.py are structured.
        # For a robust system, Environment might be responsible for creating organisms.
        # Here, we assume a simplified direct instantiation or environment-assisted creation.
        
        # Dynamically import organism types if possible, or rely on Environment class
        # For this placeholder, we'll assume Environment can create them by name.
        for org_config in self.config.get('organisms', []):
            species = org_config.get('species')
            initial_population = org_config.get('initial_population', 0)
            initial_params = org_config.get('initial_params', {})
            
            for _ in range(initial_population):
                try:
                    # Environment.add_organism should ideally handle instantiation
                    # based on species name and initial_params.
                    organism = self.environment.add_organism(species, initial_params)
                    if organism:
                        self.organisms.append(organism)
                except Exception as e:
                    print(f"Error initializing organism {species}: {e}")


    def run(self):
        max_time = self.config.get('simulation_duration', 100)
        time_step = self.config.get('time_step', 1)

        print(f"Starting simulation for {max_time} time steps.")

        while self.current_time < max_time:
            print(f"--- Time: {self.current_time} ---")
            
            # 1. Update environment (e.g., resource regeneration, weather changes)
            self.environment.update_environment()

            # 2. Update each organism's state and actions
            organisms_to_remove = []
            newly_born_organisms = []
            
            # Iterate over a copy of the list as organisms might be added or removed
            current_organisms_list = list(self.organisms) 
            for org in current_organisms_list:
                if org.is_alive(): # Assume organism has an is_alive method
                    try:
                        # Each organism performs actions like move, eat, reproduce, age
                        # These actions might result in new organisms or removal of the current one
                        org.act(self.environment) # Pass environment for interaction
                        
                        if not org.is_alive():
                            organisms_to_remove.append(org)
                        else:
                            # Handle reproduction - assuming org.act might return new organisms
                            # or a separate reproduction step is needed.
                            # For simplicity, let's assume act() can trigger reproduction.
                            # A more complex model would have separate reproduction logic.
                            pass 
                    except Exception as e:
                        print(f"Error during organism action for {org.__class__.__name__} at time {self.current_time}: {e}")
                        organisms_to_remove.append(org) # Remove if error occurs
                else:
                    organisms_to_remove.append(org) # Remove if already marked dead

            # Remove dead organisms
            for org in organisms_to_remove:
                if org in self.organisms:
                    self.environment.remove_organism(org) # Remove from environment tracking
                    self.organisms.remove(org)

            # Handle new organisms born during this time step (if not handled by org.act directly)
            # Example: self.organisms.extend(newly_born_organisms)
            # self.environment.add_organisms(newly_born_organisms)

            self.current_time += time_step
            
            # Optional: Add logging or statistics gathering here

        print("Simulation finished.")

if __name__ == "__main__":
    # This import structure assumes organisms.py and environment.py are in the same directory
    # and that Environment class can be imported and used.
    try:
        # Attempt to create and run the simulator
        simulator = EcologySimulator("config.json")
        simulator.run()
    except ImportError as e:
        print(f"Critical Error: Could not import necessary modules (Environment, Organism). Ensure 'environment.py' and 'organisms.py' exist and are correctly structured. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during simulation setup or run: {e}")
