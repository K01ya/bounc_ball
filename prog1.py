import customtkinter as ctk
import tkinter as tk
import math
import os
import pygame
from PIL import Image, ImageTk


pygame.init()
pygame.mixer.init()
bounce_sound = pygame.mixer.Sound("zvuk_lopte3.wav")

# CustomTkinter podešavanja
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Glavni prozor
root = ctk.CTk()
root.title("Simulacija")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")

upper_height = int(screen_height * 3 / 5)
lower_height = screen_height - upper_height

# Gornji deo za simulaciju (Canvas) sa scrollbarom
upper_frame = ctk.CTkFrame(root, fg_color="lightblue")
upper_frame.pack(fill="both", expand=False, pady=(10, 0))

scroll_frame = tk.Frame(upper_frame)
scroll_frame.pack(fill="both", expand=True)

h_scrollbar = tk.Scrollbar(scroll_frame, orient='horizontal')
h_scrollbar.pack(side='bottom', fill='x')

canvas_width = screen_width * 2
canvas_height = upper_height

canvas = tk.Canvas(scroll_frame, bg="lightblue", width=screen_width, height=canvas_height,
                   xscrollcommand=h_scrollbar.set)
canvas.pack(side='top', fill='both', expand=True)

h_scrollbar.config(command=canvas.xview)
canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))

# Mapa podloga i njihovih slika
# Mapa podloga i njihovih fajlova (relativno u odnosu na ovaj .py fajl)
background_images = {
    "Pesak": "pesak.png",
    "Led": "led.png",
    "Trambolina": "trambolina.png"
}
loaded_images = {}
canvas_background_id = None

# Folder gde se nalazi ovaj .py fajl
base_folder = os.path.dirname(os.path.abspath(__file__))

def update_canvas_background(podloga):
    global canvas_background_id, loaded_images

    if canvas_background_id:
        canvas.delete(canvas_background_id)
        canvas_background_id = None

    if podloga in background_images:
        image_file = background_images[podloga]
        full_path = os.path.join(base_folder, image_file)

        if podloga not in loaded_images:
            try:
                img = Image.open(full_path).resize((canvas_width, canvas_height))
                loaded_images[podloga] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Greška pri učitavanju slike za podlogu '{podloga}': {e}")
                return

        canvas_background_id = canvas.create_image(0, 0, anchor="nw", image=loaded_images[podloga])
        canvas.tag_lower(canvas_background_id)


# Donji deo za kontrole
lower_frame = ctk.CTkFrame(root, fg_color="white", height=lower_height)
lower_frame.pack(fill="both", expand=True, pady=(10, 10))

# 6 kolona u donjem delu
columns = []
for i in range(6):
    col = ctk.CTkFrame(lower_frame, fg_color="white")
    col.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    columns.append(col)

# Globalne promenljive
simulacija_aktivna = False
simulacija_pauzirana = False
ŠIRINA = canvas_width
VISINA = canvas_height
R = 0.1  # m

def skaliraj_m_u_px(m):
    return m * 100

def create_slider_with_label(parent, text, from_, to, steps):
    frame = ctk.CTkFrame(parent, fg_color="white")
    frame.pack(fill="x", pady=(10, 25))

    label = ctk.CTkLabel(frame, text=text, fg_color="white", bg_color="white", font=ctk.CTkFont(size=14, weight="bold"))
    label.pack(anchor="w", pady=(0, 5))

    value_var = ctk.StringVar(value=f"{from_:.1f}")
    value_label = ctk.CTkLabel(frame, textvariable=value_var, width=40, fg_color="white", bg_color="white")
    value_label.pack(side="right", padx=(5, 0))

    slider = ctk.CTkSlider(frame, from_=from_, to=to, number_of_steps=steps)
    slider.set(from_)
    slider.pack(fill="x", expand=True)

    def update_value(val):
        value_var.set(f"{float(val):.1f}")
    slider.configure(command=update_value)

    return slider

# Kolona 1: Težina lopte i otpor vazduha
težina_slider = create_slider_with_label(columns[1], "Težina lopte", 0.1, 10.0, 99)
otpor_slider = create_slider_with_label(columns[1], "Otpor vazduha", 0.0, 2.0, 20)

# Kolona 2: Gravitacija i brzina simulacije
gravitacija_slider = create_slider_with_label(columns[2], "Gravitacija", 0.1, 20.0, 199)
brzina_slider = create_slider_with_label(columns[2], "Brzina simulacije", 0.1, 3.0, 29)

# Kolona 3: Vrsta podloge i dugme pokreni
ctk.CTkLabel(columns[3], text="Vrsta podloge", fg_color="white", bg_color="white", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0, 5))
surface_option = ctk.CTkOptionMenu(columns[3], values=["Ravna povrsina", "Pesak" , "Trambolina", "Led"], fg_color="#6c9ceb", button_color="#0762f5", text_color="black")
surface_option.pack(fill="x", pady=(0, 10))

def pokreni_simulaciju():
    update_canvas_background(surface_option.get())
    global simulacija_aktivna, simulacija_pauzirana
    if simulacija_aktivna:
        return
    simulacija_aktivna = True
    simulacija_pauzirana = False
    if hasattr(run_simulacija, "x"):
        del run_simulacija.x
        del run_simulacija.y
        del run_simulacija.vx
        del run_simulacija.vy
        del run_simulacija.trag
    canvas.delete("lopta")
    run_simulacija()

pokreni_dugme = ctk.CTkButton(columns[3], text="Pokreni simulaciju", fg_color="#5bde62", text_color="black",
    corner_radius=10, height=50, font=ctk.CTkFont(size=14, weight="bold"), command=pokreni_simulaciju)
pokreni_dugme.pack(fill="x", pady=10)

# Kolona 4: Dugmad Restart i Pauza
def restart_simulacije():
    global simulacija_aktivna, simulacija_pauzirana
    simulacija_aktivna = False
    simulacija_pauzirana = False
    canvas.delete("lopta")
    pauza_dugme.configure(text="Pauza")

restart_dugme = ctk.CTkButton(columns[4], text="Restart", fg_color="#e4ed51", text_color="black",
    corner_radius=10, height=50, font=ctk.CTkFont(size=14, weight="bold"), command=restart_simulacije)
restart_dugme.pack(fill="x", pady=(0,10))

def pauziraj_simulaciju():
    global simulacija_pauzirana, simulacija_aktivna
    if simulacija_aktivna:
        simulacija_pauzirana = not simulacija_pauzirana
        if simulacija_pauzirana:
            pauza_dugme.configure(text="Nastavi")
        else:
            pauza_dugme.configure(text="Pauza")
            run_simulacija()

pauza_dugme = ctk.CTkButton(columns[4], text="Pauza", fg_color="#f5a623", text_color="black",
    corner_radius=10, height=50, font=ctk.CTkFont(size=14, weight="bold"), command=pauziraj_simulaciju)
pauza_dugme.pack(fill="x")



# Simulacija
def run_simulacija():
    global simulacija_aktivna
    if not simulacija_aktivna or simulacija_pauzirana:
        return

    # Prvi put inicijalizacija atributa funkcije
    if not hasattr(run_simulacija, "x"):
        run_simulacija.x = 1.0
        run_simulacija.y = 0.5
        run_simulacija.vx = 2.0
        run_simulacija.vy = 0.0
        run_simulacija.trag = []

    masa = težina_slider.get()
    otpor = otpor_slider.get()
    g = gravitacija_slider.get()
    brzina_sim = brzina_slider.get()
    podloga = surface_option.get()

    if podloga == "Ravna povrsina":
        odbijanje = 0.9
    elif podloga == "Pesak":
        odbijanje = 0.3
    elif podloga == "Trambolina":
        odbijanje = 1.05
    elif podloga == "Led":
        odbijanje = 0.95
    else:
        odbijanje = 0.9

    r_px = skaliraj_m_u_px(R)
    dt_osnovni = 0.01
    dt = dt_osnovni * brzina_sim

    x = run_simulacija.x
    y = run_simulacija.y
    vx = run_simulacija.vx
    vy = run_simulacija.vy
    trag = run_simulacija.trag

    Fg = masa * g
    brzina = math.hypot(vx, vy)
    Fd = otpor * brzina ** 2
    ax = -Fd * (vx / brzina) / masa if brzina != 0 else 0
    ay = g - Fd * (vy / brzina) / masa if brzina != 0 else g

    vx += ax * dt
    vy += ay * dt

    x += vx * dt
    y += vy * dt  

    if y + R > VISINA / 100:
        #bounce_sound.play()
        y = VISINA / 100 - R
        vy = -vy * odbijanje
        if abs(vy) < 0.2:
            simulacija_aktivna = False
            return

    run_simulacija.x = x
    run_simulacija.y = y
    run_simulacija.vx = vx
    run_simulacija.vy = vy
    run_simulacija.trag = trag

    canvas.delete("lopta")
    x_px = skaliraj_m_u_px(x)
    y_px = skaliraj_m_u_px(y)
    trag.append((x_px, y_px))

    for i in range(1, len(trag)):
        canvas.create_line(*trag[i - 1], *trag[i], fill="blue", tags="lopta")

    canvas.create_oval(x_px - r_px, y_px - r_px, x_px + r_px, y_px + r_px, fill="red", tags="lopta")

    root.after(int(1000 * dt_osnovni), run_simulacija)

root.mainloop()
