import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation 
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import is_color_like
from libs.Simulation import Simulation
import json

class Graphical_Interface(ctk.CTk):
    def __init__(self):
        super().__init__()

        margins = 5
        width_left_side = 550
        self.title("Gravity Simulator")
        self.geometry("1400x775")
        global_params = [
            "Lower X limit:","Upper X limit:",
            "Lower Y limit:", "Upper Y limit:",
            "Simulation time (seconds):", "Frames per second:",
            "Gravitational constant (G):"
        ]    
        self.particle_params = ["Colour", "Mass", "Position X", "Position Y", "Speed X", "Speed Y"]

        ctk.set_appearance_mode("Dark")  # Options: "System", "Dark", "Light"
        ctk.set_default_color_theme("dark-blue")  # Options: "blue", "green", "dark-blue"

        self.grid_columnconfigure(0, minsize=10)
        self.grid_columnconfigure(1, minsize=width_left_side)
        self.grid_columnconfigure(2, minsize=20)

        self.global_entries = []
        self.particles = []
        self.errors = []
        

        self.upper_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.upper_frame.grid(row=0, column=1, pady=margins, sticky="ew")
        self.setup_upper_frame()

        self.global_frame = ctk.CTkFrame(self, corner_radius=10, width=width_left_side, height=225)
        self.global_frame.grid(row=1, column=1, pady=margins, sticky="ew")
        self.setup_global_frame(global_params)
        
        add_particle_button = ctk.CTkButton(self, text="Add particle", command=self.add_particle)
        add_particle_button.grid(row=2, column=1, pady=margins)
        
        self.particle_frame = ctk.CTkScrollableFrame(self, corner_radius=10, height=450)
        self.particle_frame.grid(row=3, column=1, pady=margins, sticky="ew")

        self.initialize_graph()


    def setup_upper_frame(self):
        margins_upper_frame = 5

        container = ctk.CTkFrame(self.upper_frame, fg_color="transparent")
        container.pack(fill="x", expand=True, pady=2)

        container.grid_columnconfigure(0, weight=0)
        container.grid_columnconfigure(1, weight=1)
        container.grid_columnconfigure(2, weight=0)
        
        load_button = ctk.CTkButton(container, text="Load configuration", command=self.load_config)
        load_button.grid(row=0, column=0, padx=margins_upper_frame, sticky="w")

        obtain_button = ctk.CTkButton(container, text="Run simulation", command=self.run_button_action)
        obtain_button.grid(row=0, column=1, padx=margins_upper_frame, sticky="ew")

        save_button = ctk.CTkButton(container, text="Save configuration", command=self.save_config)
        save_button.grid(row=0, column=2, padx=margins_upper_frame, sticky="w")

    def save_config(self):
        config = {
            "global_parameters": {},
            "particles": []
        }

        self.get_all_inputs()
        config["global_parameters"] = self.global_inputs
        for particle in self.particles_inputs:
            config["particles"].append(particle)

        file_path = ctk.filedialog.asksaveasfilename(defaultextension=".json",
                                                    filetypes=[("JSON files", "*.json")],
                                                    title="Save Configuration")
        if file_path:
            with open(file_path, "w") as file:
                json.dump(config, file, indent=4)

    def load_config(self):
        file_path = ctk.filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], title="Load Configuration")
        
        if not file_path:
            return

        try:
            with open(file_path, "r") as file:
                config = json.load(file)

            for param, value in config.get("global_parameters", {}).items():
                if param in self.global_entries:
                    self.global_entries[param].delete(0, "end")
                    self.global_entries[param].insert(0, value)

            for particle_container, _ in self.particles:
                particle_container.destroy()
            self.particles.clear()

            for particle_data in config.get("particles", []):
                self.add_particle()
                _, particle_entries = self.particles[-1]

                for param, value in particle_data.items():
                    if param in particle_entries:
                        particle_entries[param].delete(0, "end")
                        particle_entries[param].insert(0, value)

        except Exception as e:
            print(f"Error loading configuration: {e}")

    def initialize_graph(self, limits_x=(-10,10), limits_y=(-10,10)):
        self.figure = plt.figure(figsize=(8,7))
        plt.axes(xlim =limits_x, ylim =limits_y)
        plt.grid()

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=3, rowspan=4)

    def start_animation(self):
        frames_per_second = int(self.global_inputs["Frames per second:"])
        simulated_seconds = int(self.global_inputs["Simulation time (seconds):"])
        gravitational_constant = float(self.global_inputs["Gravitational constant (G):"])
        limits_frame_x = (float(self.global_inputs["Lower X limit:"]),
                          float(self.global_inputs["Upper X limit:"]))
        limits_frame_y = (float(self.global_inputs["Lower Y limit:"]),
                          float(self.global_inputs["Upper Y limit:"]))
            
        current_state = Simulation(self.particles_inputs, limits_frame_x, limits_frame_y,
                                   frames_per_second, gravitational_constant)

        anim = animation.FuncAnimation(fig=self.figure,
                                       func=current_state.iterate,
                                       frames=simulated_seconds*frames_per_second,
                                       interval=round(1000/frames_per_second),
                                       repeat=False)
        self.canvas.draw()


    def fill_frame_entries(self, frame, params, max_rows):
        inner_margins = 5
        entries = {}
        row = 0
        column = 0
        for param in params:
            label = ctk.CTkLabel(frame, text=param)
            label.grid(row=row, column=column, sticky='e', padx=inner_margins/2, pady=inner_margins)
            
            entry = ctk.CTkEntry(frame, width=80)
            entry.grid(row=row, column=column+1, padx=inner_margins, pady=inner_margins)

            entries[param] = entry
        
            row += 1
            if row >= max_rows:
                row = 0
                column += 2

        return entries


    def setup_global_frame(self, parameters):
        title = ctk.CTkLabel(self.global_frame, text="Global parameters", font=("Arial", 16))
        title.pack(pady=5)

        container = ctk.CTkFrame(self.global_frame, fg_color="transparent")
        container.pack(padx=10, pady=2)         

        self.global_entries = self.fill_frame_entries(container, parameters, 4)
    

    def add_particle(self):
        particle_container = ctk.CTkFrame(self.particle_frame, corner_radius=10)
        particle_container.pack(pady=10, padx=10)
        entries = self.fill_frame_entries(particle_container, self.particle_params, 2)
        
        delete_button = ctk.CTkButton(particle_container, text="X", width=45,
                                      fg_color="red", hover_color="darkred",
                                      command=lambda: self.remove_particle(particle_container))
        delete_button.grid(row=0, column=6, rowspan=2, pady=5, padx=5)
        
        self.particles.append((particle_container, entries))


    def remove_particle(self, particle_container):
        for particle, _ in self.particles:
            if particle == particle_container:
                self.particles.remove((particle, _))
                break
        particle_container.destroy()


    def get_text(self, entries):
        text_entries = {}
        for param, entry in entries.items():
            text_entries[param] = entry.get()
        return text_entries


    def check_particle_float(self, name, var_check, index):
        try:
            float(var_check)
        except ValueError:
            self.errors.append(f"- {name} of particle {index+1} requires a number")


    def check_float(self, name, var_check):
        try:
            float(var_check)
        except ValueError:
            self.errors.append(f"- {name} requires a number")


    def check_int(self, name, var_check):
        try:
            var_to_check = int(var_check)
        except ValueError:
            self.errors.append(f"- {name} requires an integer number bigger than 0")
            return

        if var_to_check <= 0:
            self.errors.append(f"- {name} has to be bigger than 0")


    def check_positive(self, name, var_check):
        try:
            var_to_check = float(var_check)
        except ValueError:
            self.errors.append(f"- {name} requires a number bigger than 0")
            return

        if var_to_check <= 0:
            self.errors.append(f"- {name} has to be bigger than 0")


    def check_higher(self, higher, lower, higher_name, lower_name):
        try:
            higher_as_number = float(higher)
            lower_as_number = float(lower)
        except ValueError:
            return
        
        if higher_as_number <= lower_as_number:
            self.errors.append(f"- {higher_name} has to be bigger than {lower_name}")


    def check_global_inputs(self):
        shall_be_floats = ["Lower X limit:","Upper X limit:",
                           "Lower Y limit:","Upper Y limit:", "Gravitational constant (G):"]
        shall_be_ints = ["Frames per second:"]
        shall_be_positive = ["Simulation time (seconds):"]

        for name in shall_be_floats:
            self.check_float(name, self.global_inputs[name])
        for name in shall_be_ints:
            self.check_int(name, self.global_inputs[name])
        for name in shall_be_positive:
            self.check_positive(name, self.global_inputs[name])

        self.check_higher(self.global_inputs["Upper X limit:"],
                          self.global_inputs["Lower X limit:"],
                          "Upper X limit",
                          "Lower X limit")


    def check_colour(self, name, var_check, index):
        if is_color_like(var_check):
            return
        print(var_check, is_color_like(var_check))
        self.errors.append(f"- Colour of particle {index+1} is not recognizable (as name, hexadecimal or RGB code)")

    def report_errors(self):
        space_between_texts = 5

        new_window = ctk.CTkToplevel(self) 
        new_window.geometry("600x525")
        new_window.transient(self)
        
        if len(self.errors) > 1:
            announcement_text = "The simulation cannot start due to the following errors:"
            new_window.title("Errors")
        else:
            announcement_text = "The simulation cannot start due to the following error:"
            new_window.title("Error")

        announcement = ctk.CTkLabel(new_window, text=announcement_text)
        announcement.pack(pady=space_between_texts)

        if len(self.errors) > 10:
            messages_frame = ctk.CTkScrollableFrame(new_window, corner_radius=10,
                                                    height=400, width=500)
            messages_frame.pack(pady=space_between_texts)
            for error in self.errors:
                message = ctk.CTkLabel(messages_frame, text=error)
                message.pack(pady=space_between_texts)
        else:
            for error in self.errors:
                message = ctk.CTkLabel(new_window, text=error)
                message.pack(pady=space_between_texts)
        
        exit_button = ctk.CTkButton(new_window,
                                    text="Close",
                                    command= lambda: new_window.destroy())
        exit_button.pack(pady=space_between_texts)


    def check_particles_inputs(self):
        shall_be_floats = ["Mass", "Position X", "Position Y", "Speed X", "Speed Y"]
        
        for index, particle in enumerate(self.particles_inputs):
            for name in shall_be_floats:
                self.check_particle_float(name, particle[name], index)
            self.check_colour(name, particle["Colour"], index)

    def get_all_inputs(self):
        self.global_inputs = self.get_text(self.global_entries)

        self.particles_inputs = []
        for _, particle in self.particles:
            text_entries = self.get_text(particle)
            self.particles_inputs.append(text_entries)

    def run_button_action(self):

        self.get_all_inputs()
        self.check_global_inputs()
        self.check_particles_inputs()
        
        if self.errors:
            self.report_errors()
            self.errors = []
            return
        
        self.initialize_graph()
        self.start_animation()