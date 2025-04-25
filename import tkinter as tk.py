import tkinter as tk
import time


ŠIRINA = 1900
VISINA = 520  # prozor
ODBIJANJE = 0.7  # koeficijent odbijanja
R = 0.1  # m poluprečnik lopte

simulacija_aktivna = False  # za prekid simulacije
 
def pokreni_simulaciju():
    global simulacija_aktivna
    if simulacija_aktivna:
        return
    print("Pokrenuta")
    canvas.delete("all")
    simulacija_aktivna = True
    run_simulacija()

def restart_simulacije():
    global simulacija_aktivna
    print("Simulacija prekinuta")
    simulacija_aktivna = False
    canvas.delete("all")

def toggle_simulacija(event=None):
    global simulacija_aktivna
    if simulacija_aktivna:
        restart_simulacije()
    else:
        pokreni_simulaciju()

def run_simulacija():
    print("Pokrećemo...")
    canvas.delete("all")

    # Inicijalne vrednosti
    x = 50
    y = VISINA - 50
    brzina_x = 100  # px/s
    brzina_y = -200  # px/s

    k = 0.1  #koeficijent normalne sile -chatgpt rekao, jer u knjizi pise 1000

    masa = težina_var.get()
    otpor = otpor_var.get()
    gravitacija = gravitacija_var.get()
    brzina_simulacije = brzina_var.get()

    vrsta_podloge = podloga_var.get() #postavljamo koef u zav. od podloge
    if vrsta_podloge == "Normalna":
        odbijanje = 0.7
    elif vrsta_podloge == "Trambolina":
        odbijanje = 1.1
    elif vrsta_podloge == "Pesak":
        odbijanje = 0.2
    elif vrsta_podloge == "Led":
        odbijanje = 0.9
    else:
        odbijanje = 0.7

    dt_osnovni = 0.02   #azuriranje na svakih 0.02 sec
    dt = dt_osnovni * brzina_simulacije 
    r = masa * 3 + 10  # prečnik propor. težini - gpt predlozio formulu

    vreme_poslednjeg = time.time()

    trag = []   # lista za crtanje putanje lopte
    prvi_udarac = True

    def simulacija_petlja():
        nonlocal x, y, brzina_x, brzina_y, vreme_poslednjeg, prvi_udarac
        if not simulacija_aktivna:
            return

        sada = time.time()
        proteklo = sada - vreme_poslednjeg
        if proteklo < dt_osnovni:
            root.after(10, simulacija_petlja)
            return
        vreme_poslednjeg = sada

        brzina_simulacije = brzina_var.get()
        dt = dt_osnovni * brzina_simulacije

        # izracunavanje ubrzanja
        ax = -otpor * brzina_x / masa
        ay = gravitacija - otpor * brzina_y / masa

        # dodavj normalnu silu ako dodiruje pod
        if y + r > VISINA:
            y = VISINA - r
            if prvi_udarac:
                brzina_y = -brzina_y * 0.7
                prvi_udarac = False
            else:
                brzina_y = -brzina_y * odbijanje

            if abs(brzina_y) < 10:
                print("brzina premala, kraj")
                return
        else:
            ay -= k * (R - y) / masa

        # azuriranje brzina
        brzina_x += ax * dt
        brzina_y += ay * dt

        # azuriranje pozicije
        x += brzina_x * dt
        y += brzina_y * dt

       
        trag.append((x, y))   # dodavanje tačke u trag

        # Crtanje
        canvas.delete("lopta")
        for i in range(1, len(trag)):
            x1, y1 = trag[i - 1]
            x2, y2 = trag[i]
            canvas.create_line(x1, y1, x2, y2, fill="blue", tags="lopta", width=1)
        canvas.create_oval(x - r, y - r, x + r, y + r, fill="red", tags="lopta")

        root.after(10, simulacija_petlja)  # sledeći korak simulacije

    simulacija_petlja()

# Glavni prozor
root = tk.Tk()
root.title("Simulacija kretanja lopte")
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

# Platno
canvas = tk.Canvas(root, width=ŠIRINA, height=VISINA, bg="lightblue")
canvas.pack(fill="both", expand=True)

# Kontrole
# Glavni frame
frame = tk.Frame(root)
frame.pack(fill="x", pady=10)

# Unutrašnji frame za kontrole
controls_frame = tk.Frame(frame)
controls_frame.pack(pady=10)

# Prva kolona (kolona 0)
tk.Label(controls_frame, text="Težina lopte").grid(row=0, column=0, padx=10, pady=0)
težina_var = tk.DoubleVar(value=1.0)
tk.Scale(controls_frame, from_=0.1, to=10.0, resolution=0.1, orient='horizontal', variable=težina_var).grid(row=1, column=0, padx=10, pady=0)

tk.Label(controls_frame, text="Otpor vazduha").grid(row=2, column=0, padx=10, pady=0)
otpor_var = tk.DoubleVar(value=0.1)
tk.Scale(controls_frame, from_=0.0, to=2.0, resolution=0.05, orient='horizontal', variable=otpor_var).grid(row=3, column=0, padx=10, pady=0)

# Druga kolona (kolona 2)
tk.Label(controls_frame, text="Gravitacija").grid(row=0, column=2, padx=10, pady=0)
gravitacija_var = tk.DoubleVar(value=9.81)
tk.Scale(controls_frame, from_=0.1, to=20.0, resolution=0.1, orient='horizontal', variable=gravitacija_var).grid(row=1, column=2, padx=10, pady=0)

tk.Label(controls_frame, text="Brzina simulacije").grid(row=2, column=2, padx=10, pady=0)
brzina_var = tk.DoubleVar(value=1.0)
tk.Scale(controls_frame, from_=0.1, to=3.0, resolution=0.1, orient='horizontal', variable=brzina_var).grid(row=3, column=2, padx=10, pady=0)

# Treća kolona (kolona 4)
tk.Label(controls_frame, text="Vrsta podloge").grid(row=0, column=4, padx=10, pady=0)
podloga_var = tk.StringVar(value="Normalna")
tk.OptionMenu(controls_frame, podloga_var, "Normalna", "Trambolina", "Pesak", "Led").grid(row=1, column=4, padx=10, pady=0)

tk.Button(controls_frame, text="Pokreni simulaciju", command=pokreni_simulaciju).grid(row=2, column=4, pady=10)
tk.Button(controls_frame, text="Restart", command=restart_simulacije).grid(row=3, column=4, pady=10)

# Konfigurišemo širinu praznih stubova 1 i 3 da naprave prostor
controls_frame.grid_columnconfigure(1, minsize=100)  # prostor između 1. i 2. kolone
controls_frame.grid_columnconfigure(3, minsize=100)  # prostor između 2. i 3. kolone

root.bind("<space>", toggle_simulacija) #space moze da prekine simul

root.mainloop()
