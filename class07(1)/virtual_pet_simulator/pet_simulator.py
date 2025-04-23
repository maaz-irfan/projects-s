import tkinter as tk
from tkinter import messagebox
import random
import time
import threading
import math



# Base class for all pets
class Pet:
    def __init__(self, name, species):
        self.name = name
        self.species = species
        self.hunger = 50  # 0 (full) to 100 (starving)
        self.happiness = 50  # 0 (sad) to 100 (joyful)
        self.energy = 50  # 0 (exhausted) to 100 (energetic)
        self.is_alive = True

    def eat(self):
        if self.is_alive:
            self.hunger = max(0, self.hunger - 20)
            self.energy = min(100, self.energy + 10)
            return f"{self.name} eats happily! Hunger: {self.hunger}, Energy: {self.energy}"
        return f"{self.name} is no longer with us..."

    def play(self):
        if self.is_alive:
            if self.energy > 20:
                self.happiness = min(100, self.happiness + 15)
                self.energy = max(0, self.energy - 15)
                self.hunger = min(100, self.hunger + 10)
                return f"{self.name} has fun! Happiness: {self.happiness}, Energy: {self.energy}"
            return f"{self.name} is too tired to play!"
        return f"{self.name} is no longer with us..."

    def sleep(self):
        if self.is_alive:
            self.energy = min(100, self.energy + 30)
            self.hunger = min(100, self.hunger + 5)
            return f"{self.name} rests. Energy: {self.energy}"
        return f"{self.name} is no longer with us..."

    def update_status(self):
        if self.is_alive:
            self.hunger = min(100, self.hunger + random.randint(5, 10))
            self.happiness = max(0, self.happiness - random.randint(5, 10))
            self.energy = max(0, self.energy - random.randint(5, 10))
            if self.hunger >= 100 or self.happiness <= 0 or self.energy <= 0:
                self.is_alive = False
                return f"Oh no! {self.name} has passed away..."
            return f"{self.name}'s status - Hunger: {self.hunger}, Happiness: {self.happiness}, Energy: {self.energy}"
        return f"{self.name} is no longer with us..."

    def __str__(self):
        return f"{self.name}, a {self.species}"

# Derived class for Dragon
class Dragon(Pet):
    def __init__(self, name):
        super().__init__(name, "Dragon")
        self.fire_power = 50  # Unique attribute

    def breathe_fire(self):
        if self.is_alive and self.energy > 30 and self.fire_power > 20:
            self.fire_power = max(0, self.fire_power - 10)
            self.energy = max(0, self.energy - 20)
            return f"{self.name} breathes fire! Fire Power: {self.fire_power}, Energy: {self.energy}"
        elif not self.is_alive:
            return f"{self.name} is no longer with us..."
        return f"{self.name} is too weak to breathe fire!"

# Pet factory for creating pets
class PetFactory:
    @staticmethod
    def create_pet(pet_type, name, custom_attributes=None):
        if pet_type.lower() == "dragon":
            return Dragon(name)
        elif pet_type.lower() == "custom":
            class CustomPet(Pet):
                def __init__(self, name, custom_attributes):
                    super().__init__(name, "Custom")
                    for attr, value in custom_attributes.items():
                        setattr(self, attr, value)
                def custom_action(self):
                    return f"{self.name} performs a unique action!"
            return CustomPet(name, custom_attributes)
        else:
            raise ValueError("Unknown pet type")

# GUI class with animations
class PetSimulatorGUI:
    def __init__(self, root, pet):
        self.root = root
        self.pet = pet
        self.root.title(f"Virtual Pet Simulator - {self.pet}")
        self.is_running = True
        self.animation_counter = 0  # For animation timing
        self.action_animation = None  # Track action-specific animations

        # Main frame
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack()

        # Pet canvas
        self.canvas = tk.Canvas(self.main_frame, width=150, height=150, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=2)
        self.pet_item = None  # Canvas item for pet
        self.effect_item = None  # Canvas item for action effects (e.g., fire)
        self.update_pet_image()

        # Pet info
        self.info_label = tk.Label(self.main_frame, text=str(self.pet), font=("Arial", 14))
        self.info_label.grid(row=1, column=0, columnspan=2)

        # Status labels
        self.hunger_label = tk.Label(self.main_frame, text=f"Hunger: {self.pet.hunger}")
        self.hunger_label.grid(row=2, column=0, sticky="w")
        self.happiness_label = tk.Label(self.main_frame, text=f"Happiness: {self.pet.happiness}")
        self.happiness_label.grid(row=3, column=0, sticky="w")
        self.energy_label = tk.Label(self.main_frame, text=f"Energy: {self.pet.energy}")
        self.energy_label.grid(row=4, column=0, sticky="w")
        if isinstance(self.pet, Dragon):
            self.fire_power_label = tk.Label(self.main_frame, text=f"Fire Power: {self.pet.fire_power}")
            self.fire_power_label.grid(row=5, column=0, sticky="w")

        # Action buttons
        tk.Button(self.main_frame, text="Feed", command=self.feed).grid(row=2, column=1)
        tk.Button(self.main_frame, text="Play", command=self.play).grid(row=3, column=1)
        tk.Button(self.main_frame, text="Sleep", command=self.sleep).grid(row=4, column=1)
        if isinstance(self.pet, Dragon):
            tk.Button(self.main_frame, text="Breathe Fire", command=self.breathe_fire).grid(row=5, column=1)

        # Exit button
        tk.Button(self.main_frame, text="Exit", command=self.exit).grid(row=6, column=0, columnspan=2)

        # Start animation and status update
        self.animate_pet()
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()

    def update_pet_image(self):
        self.canvas.delete("all")
        self.effect_item = None
        if self.pet.is_alive:
            # Use an oval shape to represent the pet, colored by happiness
            color = "green" if self.pet.happiness > 50 else "blue"
            self.pet_item = self.canvas.create_oval(50, 50, 100, 100, fill=color)
            # Add eyes or face
            self.canvas.create_oval(65, 65, 70, 70, fill="black")  # Left eye
            self.canvas.create_oval(80, 65, 85, 70, fill="black")  # Right eye
            if self.pet.happiness > 50:
                self.canvas.create_arc(65, 80, 85, 90, start=0, extent=180, style="arc")  # Smile
            else:
                self.canvas.create_arc(65, 90, 85, 80, start=180, extent=180, style="arc")  # Frown
        else:
            self.pet_item = self.canvas.create_text(75, 75, text="💀", font=("Arial", 40))
            self.canvas.create_text(75, 110, text="R.I.P.", font=("Arial", 10))

    def animate_pet(self):
        if not self.is_running or not self.pet.is_alive:
            return

        self.animation_counter += 1
        if self.pet_item and not self.action_animation:
            # Idle animation: wiggle side-to-side based on happiness
            amplitude = 10 * (self.pet.happiness / 100)  # Scale with happiness
            speed = 0.1  # Animation speed
            x_offset = amplitude * math.sin(self.animation_counter * speed)
            self.canvas.move(self.pet_item, x_offset - self.canvas.coords(self.pet_item)[0] + 75, 0)

        # Handle action-specific animations
        if self.action_animation:
            anim_type, frames_left = self.action_animation
            if frames_left > 0:
                if anim_type == "feed":
                    # Move up and down
                    y_offset = 10 * math.sin(self.animation_counter * 0.5)
                    self.canvas.move(self.pet_item, 0, y_offset - (self.canvas.coords(self.pet_item)[1] - 75))
                elif anim_type == "play":
                    # Bounce energetically
                    y_offset = 15 * abs(math.sin(self.animation_counter * 0.7))
                    self.canvas.move(self.pet_item, 0, y_offset - (self.canvas.coords(self.pet_item)[1] - 75))
                elif anim_type == "sleep":
                    # Show "Zzz" effect
                    if self.effect_item is None:
                        self.effect_item = self.canvas.create_text(100, 50, text="Zzz", font=("Arial", 12))
                    self.canvas.move(self.effect_item, 0, -1)  # Float upward
                elif anim_type == "breathe_fire":
                    # Flash a red rectangle
                    if self.effect_item is None:
                        self.effect_item = self.canvas.create_rectangle(100, 60, 120, 80, fill="red")
                    else:
                        self.canvas.itemconfig(self.effect_item, fill="orange" if frames_left % 2 else "red")
                self.action_animation = (anim_type, frames_left - 1)
            else:
                self.action_animation = None
                self.canvas.delete(self.effect_item)
                self.effect_item = None

        # Schedule next frame
        self.root.after(50, self.animate_pet)  # 50ms = ~20 FPS

    def update_status_display(self):
        self.hunger_label.config(text=f"Hunger: {self.pet.hunger}")
        self.happiness_label.config(text=f"Happiness: {self.pet.happiness}")
        self.energy_label.config(text=f"Energy: {self.pet.energy}")
        if isinstance(self.pet, Dragon):
            self.fire_power_label.config(text=f"Fire Power: {self.pet.fire_power}")
        self.update_pet_image()
        if not self.pet.is_alive:
            messagebox.showinfo("Game Over", f"{self.pet.name} has passed away...")
            self.exit()

    def feed(self):
        message = self.pet.eat()
        self.action_animation = ("feed", 20)  # 20 frames (~1 second)
        messagebox.showinfo("Action", message)
        self.update_status_display()

    def play(self):
        message = self.pet.play()
        self.action_animation = ("play", 30)  # 30 frames (~1.5 seconds)
        messagebox.showinfo("Action", message)
        self.update_status_display()

    def sleep(self):
        message = self.pet.sleep()
        self.action_animation = ("sleep", 40)  # 40 frames (~2 seconds)
        messagebox.showinfo("Action", message)
        self.update_status_display()

    def breathe_fire(self):
        if isinstance(self.pet, Dragon):
            message = self.pet.breathe_fire()
            self.action_animation = ("breathe_fire", 20)  # 20 frames (~1 second)
            messagebox.showinfo("Action", message)
            self.update_status_display()

    def update_loop(self):
        while self.is_running and self.pet.is_alive:
            message = self.pet.update_status()
            self.root.after(0, self.update_status_display)
            time.sleep(5)

    def exit(self):
        self.is_running = False
        self.root.quit()
        self.root.destroy()

# Main function
def main():
    print("Welcome to the Virtual Pet Simulator!")
    pet_type = input("Enter pet type (dragon/custom): ")
    if pet_type.lower() == "custom":
        name = input("Enter custom pet name: ")
        attributes = {}
        while True:
            attr = input("Enter attribute name (or 'done' to finish): ")
            if attr.lower() == "done":
                break
            value = int(input(f"Enter value for {attr} (0-100): "))
            attributes[attr] = value
        pet = PetFactory.create_pet("custom", name, attributes)
    else:
        pet_name = input("Enter your pet's name: ")
        pet = PetFactory.create_pet(pet_type, pet_name)

    root = tk.Tk()
    app = PetSimulatorGUI(root, pet)
    root.mainloop()

if __name__ == "__main__":
    main()
