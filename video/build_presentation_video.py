import os
import subprocess
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from generate_music import generate_ambient_track

# Configuración de Escenas y Guión de Locución en Castellano Neutro
SCENES = [
    {
        "id": 1,
        "image": "../assets/images/visio_initial_load.png",
        "badge": "01 / INTRODUCCIÓN",
        "title": "HtmlVisio — Suite de Diagramación Vectorial",
        "subtitle": "Entorno profesional de alta fidelidad en un único archivo web autónomo",
        "voice_text": "Bienvenido a HtmlVisio, la suite de diagramación vectorial profesional concebida en un único archivo web autónomo. Cero dependencias, ejecución sin conexión y máxima fidelidad visual."
    },
    {
        "id": 2,
        "image": "../assets/images/insertar_ribbon.png",
        "badge": "02 / INTERFAZ FLUENT",
        "title": "Cinta Ribbon & Herramientas Avanzadas",
        "subtitle": "Diseño moderno con controles de dibujo, tipografía, color y reglas métricas",
        "voice_text": "Su interfaz moderna estilo Fluent UI incorpora una cinta Ribbon interactiva con herramientas de dibujo, formatos tipográficos avanzados, temas de color y reglas métricas dinámicas."
    },
    {
        "id": 3,
        "image": "../assets/images/visio_stencils_expanded.png",
        "badge": "03 / CATÁLOGO DE FORMAS",
        "title": "Más de 35 Formas Vectoriales (Stencils)",
        "subtitle": "5 categorías especializadas con acordeón colapsable y búsqueda en tiempo real",
        "voice_text": "Disfruta de más de treinta y cinco formas clasificadas en categorías: diagramas de flujo, geometría, flechas de bloque, infraestructura de redes y anotaciones, con buscador en tiempo real."
    },
    {
        "id": 4,
        "image": "../assets/images/shape_selection.png",
        "badge": "04 / MANIPULACIÓN Y CONEXIONES",
        "title": "8 Manijas de Transformación & Ruteo Manhattan",
        "subtitle": "Conectores inteligentes ortogonales a 90° con cálculo de trayectoria automático",
        "voice_text": "Controla cada elemento con ocho manijas de precisión y nodo de rotación. Los conectores ortogonales inteligentes calculan rutas automáticas a noventa grados y se adaptan a tus cambios."
    },
    {
        "id": 5,
        "image": "../assets/images/sample_red_ciberseguridad.png",
        "badge": "05 / CASO DE USO TI",
        "title": "Topologías de Red y Ciberseguridad",
        "subtitle": "Servidores rack, cortafuegos perimetrales, routers, PCs y enlaces VPN",
        "voice_text": "Diseña infraestructuras tecnológicas completas: servidores en rack con bahías y leds, cortafuegos perimetrales, enrutadores, estaciones de trabajo y enlaces seguros con monitoreo continuo."
    },
    {
        "id": 6,
        "image": "../assets/images/sample_proceso_industrial.png",
        "badge": "06 / CASO DE USO INDUSTRIAL",
        "title": "Procesos Industriales y Estándares BPMN",
        "subtitle": "Subprocesos certificados, retardos en cola, inspección manual y normas ISO",
        "voice_text": "O modela cadenas de producción con subprocesos certificados, operaciones manuales, retardos térmicos y control de calidad bajo rigurosos estándares internacionales."
    },
    {
        "id": 7,
        "image": "../assets/images/archivo_modal.png",
        "badge": "07 / EXPORTACIÓN Y PERSISTENCIA",
        "title": "Formatos Abiertos y Plantillas a 1 Clic",
        "subtitle": "Guarda en JSON o exporta a vectores SVG e imágenes PNG de alta resolución",
        "voice_text": "Guarda tus diagramas en formato abierto JSON o expórtalos en vectores SVG e imágenes PNG de alta definición. HtmlVisio: potencia, simplicidad y libertad creativa en tu navegador."
    }
]

VOICE = "es-MX-JorgeNeural"
TARGET_W = 1920
TARGET_H = 1080

def get_audio_duration(filepath):
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", filepath
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(res.stdout)
    return float(info["format"]["duration"])

def render_scene_frame(scene, output_path):
    print(f"Creating composite frame for scene {scene['id']}...")
    img_path = scene["image"]
    raw_img = Image.open(img_path).convert("RGBA")
    
    # 1. Base canvas background
    canvas = Image.new("RGBA", (TARGET_W, TARGET_H), (15, 23, 42, 255)) # Dark slate background
    
    # 2. Subtle blurred background from the screenshot to add depth
    bg_blur = raw_img.resize((TARGET_W, TARGET_H), Image.Resampling.BILINEAR)
    bg_blur = bg_blur.filter(ImageFilter.GaussianBlur(radius=40))
    # Darken blurred bg
    dark_overlay = Image.new("RGBA", (TARGET_W, TARGET_H), (10, 15, 30, 200))
    bg_blur.paste(dark_overlay, (0, 0), dark_overlay)
    canvas.paste(bg_blur, (0, 0))
    
    # 3. Compute screenshot placement (leave room for bottom lower-third banner)
    max_w = TARGET_W - 120
    max_h = TARGET_H - 180
    
    ratio = min(max_w / raw_img.width, max_h / raw_img.height)
    new_w = int(raw_img.width * ratio)
    new_h = int(raw_img.height * ratio)
    
    scaled_img = raw_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    pos_x = (TARGET_W - new_w) // 2
    pos_y = 35  # Shift up slightly to balance with bottom bar
    
    # Drop shadow for main screenshot
    shadow_pad = 12
    shadow_box = Image.new("RGBA", (new_w + shadow_pad*2, new_h + shadow_pad*2), (0, 0, 0, 0))
    draw_sh = ImageDraw.Draw(shadow_box)
    draw_sh.rounded_rectangle([shadow_pad, shadow_pad, new_w + shadow_pad, new_h + shadow_pad], radius=8, fill=(0, 0, 0, 140))
    shadow_box = shadow_box.filter(ImageFilter.GaussianBlur(radius=10))
    canvas.paste(shadow_box, (pos_x - shadow_pad, pos_y - shadow_pad), shadow_box)
    
    # Draw screenshot border and paste
    canvas.paste(scaled_img, (pos_x, pos_y))
    draw_c = ImageDraw.Draw(canvas)
    draw_c.rectangle([pos_x, pos_y, pos_x + new_w, pos_y + new_h], outline=(255, 255, 255, 40), width=1)
    
    # 4. Draw Lower-Third Presentation Banner
    banner_w = TARGET_W - 140
    banner_h = 100
    banner_x = 70
    banner_y = TARGET_H - banner_h - 25
    
    # Rounded banner box with glassmorphism dark fill
    banner_box = Image.new("RGBA", (banner_w, banner_h), (0, 0, 0, 0))
    draw_b = ImageDraw.Draw(banner_box)
    draw_b.rounded_rectangle([0, 0, banner_w, banner_h], radius=14, fill=(15, 23, 42, 235), outline=(51, 65, 85, 220), width=1)
    
    # Accent color bar on the left
    draw_b.rounded_rectangle([0, 0, 10, banner_h], radius=5, fill=(15, 108, 189, 255))
    canvas.paste(banner_box, (banner_x, banner_y), banner_box)
    
    # 5. Typography on Lower-Third
    draw_text = ImageDraw.Draw(canvas)
    
    font_bold_path = "C:/Windows/Fonts/segoeuib.ttf"
    font_reg_path = "C:/Windows/Fonts/segoeui.ttf"
    
    font_badge = ImageFont.truetype(font_bold_path, 13)
    font_title = ImageFont.truetype(font_bold_path, 25)
    font_sub = ImageFont.truetype(font_reg_path, 16)
    
    # Badge (Category / Index)
    badge_x = banner_x + 32
    badge_y = banner_y + 14
    draw_text.text((badge_x, badge_y), scene["badge"], font=font_badge, fill=(56, 189, 248, 255)) # Sky blue accent
    
    # Main Title
    title_y = badge_y + 20
    draw_text.text((badge_x, title_y), scene["title"], font=font_title, fill=(255, 255, 255, 255))
    
    # Subtitle
    sub_y = title_y + 34
    draw_text.text((badge_x, sub_y), scene["subtitle"], font=font_sub, fill=(203, 213, 225, 255))
    
    # Watermark / Logo right side of the banner
    font_brand = ImageFont.truetype(font_bold_path, 16)
    draw_text.text((banner_x + banner_w - 140, banner_y + 38), "HtmlVisio Web", font=font_brand, fill=(148, 163, 184, 180))
    
    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    print(f"Saved: {output_path}")

def build_all():
    print("=== Iniciando Producción de Video de Presentación HtmlVisio ===")
    
    clip_files = []
    total_video_duration = 0.0
    
    for scene in SCENES:
        sid = scene["id"]
        print(f"\n--- Procesando Escena {sid}: {scene['title']} ---")
        
        # 1. Generar audio con edge-tts (Castellano Neutro)
        raw_audio = f"voice_raw_{sid}.mp3"
        padded_audio = f"voice_padded_{sid}.wav"
        
        cmd_tts = [
            "python", "-m", "edge_tts",
            "--voice", VOICE,
            "--text", scene["voice_text"],
            "--write-media", raw_audio
        ]
        subprocess.run(cmd_tts, check=True)
        
        # Obtener duración y añadir padding suave (0.5s al inicio, 0.6s al final)
        dur = get_audio_duration(raw_audio)
        print(f"Voz generada: {dur:.2f} segundos")
        
        cmd_pad = [
            "ffmpeg", "-y", "-i", raw_audio,
            "-af", "adelay=500|500,apad=pad_dur=0.6",
            padded_audio
        ]
        subprocess.run(cmd_pad, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        scene_dur = get_audio_duration(padded_audio)
        total_video_duration += scene_dur
        print(f"Duración total de escena {sid}: {scene_dur:.2f}s")
        
        # 2. Renderizar frame compuesto de alta definición
        frame_path = f"frame_{sid}.png"
        render_scene_frame(scene, frame_path)
        
        # 3. Renderizar clip de video MP4
        clip_path = f"clip_{sid}.mp4"
        cmd_clip = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", frame_path,
            "-i", padded_audio,
            "-c:v", "libx264", "-tune", "stillimage", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            clip_path
        ]
        subprocess.run(cmd_clip, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        clip_files.append(clip_path)
        print(f"Clip {clip_path} renderizado con éxito.")
    
    # 4. Concatenar clips
    print("\n--- Concatenando clips de video ---")
    concat_list_file = "concat_list.txt"
    with open(concat_list_file, "w") as f:
        for cf in clip_files:
            f.write(f"file '{cf}'\n")
            
    raw_video = "full_video_no_bgm.mp4"
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list_file,
        "-c", "copy",
        raw_video
    ]
    subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    total_dur = get_audio_duration(raw_video)
    print(f"Video continuo generado: {total_dur:.2f} segundos")
    
    # 5. Generar música de fondo ajustada al tiempo exacto
    print("\n--- Sintetizando música de fondo suave ---")
    music_file = "ambient_music_synced.wav"
    generate_ambient_track(music_file, duration_sec=int(total_dur + 4))
    
    # 6. Mezclar video con locución y música de fondo suave (-22 dB, fade in/out)
    print("\n--- Mezcla final de audio con música muy suave (-22 dB) ---")
    final_output = "HtmlVisio_Presentacion.mp4"
    
    # Filter complex:
    # 1) background music attenuated by volume=0.07 (-23 dB) with 2.5s fade in and 3.5s fade out
    # 2) mix original voice with soft bgm
    fade_out_start = max(1.0, total_dur - 3.5)
    filter_expr = f"[1:a]volume=0.07,afade=t=in:ss=0:d=2.5,afade=t=out:st={fade_out_start:.2f}:d=3.5[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=3[aout]"
    
    cmd_final = [
        "ffmpeg", "-y",
        "-i", raw_video,
        "-i", music_file,
        "-filter_complex", filter_expr,
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        final_output
    ]
    subprocess.run(cmd_final, check=True)
    
    final_dur = get_audio_duration(final_output)
    final_size_mb = os.path.getsize(final_output) / (1024 * 1024)
    print(f"\n========================================================")
    print(f"¡Éxito! Video de presentación final creado:")
    print(f"Archivo: {final_output}")
    print(f"Duración: {final_dur:.2f} segundos (~{final_dur/60:.1f} minutos)")
    print(f"Tamaño: {final_size_mb:.2f} MB")
    print(f"Resolución: 1920x1080 Full HD")
    print(f"Locución: Castellano Neutro ({VOICE})")
    print(f"Música: Ambiente armónico suave a -23 dB")
    print(f"========================================================")

if __name__ == "__main__":
    build_all()
