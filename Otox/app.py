from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import database

app = Flask(__name__)
app.secret_key = "otox_cyberpunk_secret_key_2026"

# Asegurarnos de que las tablas existan antes de atender peticiones
database.inicializar_bd()

# ==========================================
# 1. HELPERS
# ==========================================
def obtener_tiempo_relativo(fecha_creacion):
    if isinstance(fecha_creacion, str):
        try:
            fecha_creacion = datetime.strptime(fecha_creacion, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return fecha_creacion
            
    ahora = datetime.now()
    diferencia = me_ahora = ahora - fecha_creacion
    segundos = diferencia.total_seconds()
    
    if segundos < 60:
        return "Justo ahora"
    minutos = int(segundos // 60)
    if minutos < 60:
        return f"Hace {minutos} min"
    horas = int(minutos // 60)
    if horas < 24:
        return f"Hace {horas} hr" if horas == 1 else f"Hace {horas} hrs"
    dias = int(horas // 24)
    return f"Hace {dias} días"

def procesar_url_media(url_original):
    if not url_original:
        return None
    url_limpia = url_original.strip()
    if "youtube.com/watch?v=" in url_limpia:
        video_id = url_limpia.split("v=")[1].split("&")[0]
        return f"https://www.youtube.com/embed/{video_id}"
    elif "youtu.be/" in url_limpia:
        video_id = url_limpia.split("youtu.be/")[1].split("?")[0]
        return f"https://www.youtube.com/embed/{video_id}"
    elif "open.spotify.com/track/" in url_limpia:
        track_id = url_limpia.split("track/")[1].split("?")[0]
        return f"https://open.spotify.com/embed/track/{track_id}"
    return url_limpia

def ordenar_comentarios(comentarios):
    return sorted(comentarios, key=lambda x: x['likes'], reverse=True)

# ==========================================
# 2. FUNCIONES DE BASE DE DATOS (SQLITE)
# ==========================================

def cargar_perfil_actual():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return None

    conn = database.obtener_conexion()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    u = cursor.fetchone()
    
    if not u:
        conn.close()
        return None
        
    # Seguidores y Siguiendo counts
    cursor.execute("SELECT COUNT(*) FROM seguidores WHERE seguido_id = ?", (usuario_id,))
    seguidores_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM seguidores WHERE seguidor_id = ?", (usuario_id,))
    siguiendo_count = cursor.fetchone()[0]
    
    # Listas de handles
    cursor.execute("""
        SELECT u.handle FROM usuarios u 
        JOIN seguidores s ON u.id = s.seguido_id 
        WHERE s.seguidor_id = ?
    """, (usuario_id,))
    lista_siguiendo = [row['handle'] for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT u.handle FROM usuarios u 
        JOIN seguidores s ON u.id = s.seguido_id 
        WHERE s.seguido_id = ?
    """, (usuario_id,))
    lista_seguidores = [row['handle'] for row in cursor.fetchall()]
    
    perfil = {
        "id": u['id'],
        "nombre": u['nombre'],
        "handle": u['handle'],
        "email": u['email'],
        "password": u['password'],
        "bio": u['bio'] or "",
        "foto_avatar": u['foto_avatar'] or "",
        "banner_url": u['banner_url'] or "",
        "siguiendo_count": siguiendo_count,
        "seguidores_count": seguidores_count,
        "tema": u['tema'] or "oscuro",
        "lista_siguiendo": lista_siguiendo,
        "lista_seguidores": lista_seguidores
    }
    conn.close()
    return perfil

def cargar_usuarios_db(mi_id):
    conn = database.obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id != ?", (mi_id,))
    usuarios_raw = cursor.fetchall()
    
    usuarios_db = {}
    for u in usuarios_raw:
        uid = u['id']
        handle = u['handle']
        
        cursor.execute("SELECT COUNT(*) FROM seguidores WHERE seguido_id = ?", (uid,))
        seguidores_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM seguidores WHERE seguidor_id = ?", (uid,))
        siguiendo_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM seguidores WHERE seguidor_id = ? AND seguido_id = ?", (mi_id, uid))
        siguiendo_por_mi = cursor.fetchone()[0] > 0
        
        usuarios_db[handle] = {
            "id": uid,
            "nombre": u['nombre'],
            "handle": handle,
            "bio": u['bio'] or "",
            "foto_avatar": u['foto_avatar'] or "",
            "banner_url": u['banner_url'] or "",
            "siguiendo_count": seguidores_count,
            "seguidores_count": siguiendo_count,
            "siguiendo_por_mi": siguiendo_por_mi
        }
    conn.close()
    return usuarios_db

def cargar_comentarios_post(post_id, mi_id):
    conn = database.obtener_conexion()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.*, u.nombre as autor, u.handle 
        FROM comentarios c
        JOIN usuarios u ON c.usuario_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.fecha_creacion DESC
    """, (post_id,))
    comentarios_raw = cursor.fetchall()
    
    comentarios = []
    for c in comentarios_raw:
        cid = c['id']
        cursor.execute("SELECT COUNT(*) FROM likes WHERE comentario_id = ?", (cid,))
        likes_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM likes WHERE comentario_id = ? AND usuario_id = ?", (cid, mi_id))
        liked_by_me = cursor.fetchone()[0] > 0
        
        cursor.execute("""
            SELECT r.*, u.nombre as autor, u.handle 
            FROM respuestas r
            JOIN usuarios u ON r.usuario_id = u.id
            WHERE r.comentario_id = ?
            ORDER BY r.fecha_creacion ASC
        """, (cid,))
        respuestas_raw = cursor.fetchall()
        respuestas = [{
            "autor": r['autor'],
            "handle": r['handle'],
            "texto": r['texto'],
            "fecha": obtener_tiempo_relativo(r['fecha_creacion'])
        } for r in respuestas_raw]
        
        comentarios.append({
            "id": cid,
            "autor": c['autor'],
            "handle": c['handle'],
            "texto": c['texto'],
            "fecha": obtener_tiempo_relativo(c['fecha_creacion']),
            "likes": likes_count,
            "liked_by_me": liked_by_me,
            "respuestas": respuestas
        })
        
    conn.close()
    return comentarios

def cargar_posts_db(mi_id):
    conn = database.obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, u.nombre as autor, u.handle 
        FROM posts p
        JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.fecha_creacion DESC
    """)
    posts_raw = cursor.fetchall()
    conn.close()
    
    posts = []
    for p in posts_raw:
        pid = p['id']
        conn_sub = database.obtener_conexion()
        c_sub = conn_sub.cursor()
        
        c_sub.execute("SELECT COUNT(*) FROM likes WHERE post_id = ?", (pid,))
        likes_count = c_sub.fetchone()[0]
        
        c_sub.execute("SELECT COUNT(*) FROM likes WHERE post_id = ? AND usuario_id = ?", (pid, mi_id))
        liked_by_me = c_sub.fetchone()[0] > 0
        conn_sub.close()
        
        comentarios = cargar_comentarios_post(pid, mi_id)
        
        posts.append({
            "id": pid,
            "autor": p['autor'],
            "handle": p['handle'],
            "fecha_creacion": p['fecha_creacion'],
            "tiempo": obtener_tiempo_relativo(p['fecha_creacion']),
            "titulo": p['titulo'],
            "descripcion": p['descripcion'],
            "media_url": p['media_url'],
            "likes": likes_count,
            "liked_by_me": liked_by_me,
            "comentarios": ordenar_comentarios(comentarios)
        })
    return posts

def cargar_comentarios_estudio(estudio_id, mi_id):
    conn = database.obtener_conexion()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.*, u.nombre as autor, u.handle 
        FROM comentarios c
        JOIN usuarios u ON c.usuario_id = u.id
        WHERE c.estudio_id = ?
        ORDER BY c.fecha_creacion DESC
    """, (estudio_id,))
    comentarios_raw = cursor.fetchall()
    
    comentarios = []
    for c in comentarios_raw:
        cid = c['id']
        cursor.execute("SELECT COUNT(*) FROM likes WHERE comentario_id = ?", (cid,))
        likes_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM likes WHERE comentario_id = ? AND usuario_id = ?", (cid, mi_id))
        liked_by_me = cursor.fetchone()[0] > 0
        
        cursor.execute("""
            SELECT r.*, u.nombre as autor, u.handle 
            FROM respuestas r
            JOIN usuarios u ON r.usuario_id = u.id
            WHERE r.comentario_id = ?
            ORDER BY r.fecha_creacion ASC
        """, (cid,))
        respuestas_raw = cursor.fetchall()
        respuestas = [{
            "autor": r['autor'],
            "handle": r['handle'],
            "texto": r['texto'],
            "fecha": obtener_tiempo_relativo(r['fecha_creacion'])
        } for r in respuestas_raw]
        
        comentarios.append({
            "id": cid,
            "autor": c['autor'],
            "handle": c['handle'],
            "texto": c['texto'],
            "fecha": obtener_tiempo_relativo(c['fecha_creacion']),
            "likes": likes_count,
            "liked_by_me": liked_by_me,
            "respuestas": respuestas
        })
        
    conn.close()
    return comentarios

def cargar_estudios_db(mi_id):
    conn = database.obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.*, u.nombre as autor, u.handle 
        FROM estudios e
        JOIN usuarios u ON e.usuario_id = u.id
        ORDER BY e.fecha_creacion DESC
    """)
    estudios_raw = cursor.fetchall()
    conn.close()
    
    estudios = []
    for e in estudios_raw:
        eid = e['id']
        conn_sub = database.obtener_conexion()
        c_sub = conn_sub.cursor()
        
        c_sub.execute("SELECT COUNT(*) FROM likes WHERE estudio_id = ?", (eid,))
        likes_count = c_sub.fetchone()[0]
        
        c_sub.execute("SELECT COUNT(*) FROM likes WHERE estudio_id = ? AND usuario_id = ?", (eid, mi_id))
        liked_by_me = c_sub.fetchone()[0] > 0
        
        c_sub.execute("SELECT COUNT(*) FROM estudios_favoritos WHERE estudio_id = ? AND usuario_id = ?", (eid, mi_id))
        es_favorito = c_sub.fetchone()[0] > 0
        
        c_sub.execute("SELECT * FROM capitulos WHERE estudio_id = ? ORDER BY numero ASC", (eid,))
        capitulos_raw = c_sub.fetchall()
        capitulos = [{
            "numero": cap['numero'],
            "titulo": cap['titulo'],
            "explicacion": cap['explicacion'],
            "media_url": cap['media_url']
        } for cap in capitulos_raw]
        
        conn_sub.close()
        
        comentarios = cargar_comentarios_estudio(eid, mi_id)
        
        estudios.append({
            "id": eid,
            "titulo": e['titulo'],
            "autor": e['autor'],
            "handle": e['handle'],
            "categoria": e['categoria'],
            "descripcion": e['descripcion'],
            "es_favorito": es_favorito,
            "es_mio": (e['usuario_id'] == mi_id),
            "likes": likes_count,
            "liked_by_me": liked_by_me,
            "comentarios": ordenar_comentarios(comentarios),
            "capitulos": capitulos
        })
    return estudios

# ==========================================
# 3. RUTAS
# ==========================================

@app.route('/auth', methods=['POST'])
def auth():
    accion = request.form.get('accion')
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()

    conn = database.obtener_conexion()
    cursor = conn.cursor()

    if accion == 'login':
        cursor.execute("SELECT * FROM usuarios WHERE email = ? AND password = ?", (email, password))
        u = cursor.fetchone()
        conn.close()

        if u:
            session['usuario_id'] = u['id']
            return redirect(url_for('home'))
        else:
            flash("Correo o contraseña incorrectos.")
            return redirect(url_for('home'))

    elif accion == 'register':
        nombre = request.form.get('nombre', '').strip()
        handle = request.form.get('handle', '').strip().replace('@', '').lower()

        if not nombre or not handle or not email or not password:
            flash("Por favor completa todos los campos.")
            conn.close()
            return redirect(url_for('home'))

        cursor.execute("SELECT * FROM usuarios WHERE email = ? OR handle = ?", (email, handle))
        existente = cursor.fetchone()

        if existente:
            flash("El correo o el handle (@usuario) ya están registrados.")
            conn.close()
            return redirect(url_for('home'))

        cursor.execute("""
            INSERT INTO usuarios (nombre, handle, email, password, bio, tema)
            VALUES (?, ?, ?, ?, ?, 'oscuro')
        """, (nombre, handle, email, password, 'Melómano y creador en Otox.'))
        conn.commit()

        # Obtener el id del nuevo usuario creado
        nuevo_id = cursor.lastrowid
        conn.close()

        session['usuario_id'] = nuevo_id
        return redirect(url_for('home'))

    conn.close()
    return redirect(url_for('home'))

@app.route('/')
def home():
    perfil_usuario = cargar_perfil_actual()

    # Si no hay sesión iniciada, verificar si se están pidiendo políticas o términos directamente
    tab_activa = request.args.get('tab', 'feed')
    if not perfil_usuario:
        if tab_activa in ['politicas', 'terminos']:
            return render_template('index.html', perfil=None, tab_activa=tab_activa, posts=[], all_posts=[], estudios=[], all_estudios=[], usuarios_filtrados={})
        return render_template('index.html', perfil=None)

    mi_id = perfil_usuario['id']
    
    posts_db = cargar_posts_db(mi_id)
    estudios_db = cargar_estudios_db(mi_id)
    usuarios_db = cargar_usuarios_db(mi_id)
    
    subtab_estudios = request.args.get('subtab', 'comunidad')
    subtab_boveda = request.args.get('subtab_boveda', 'posts')
    subtab_perfil_visitado = request.args.get('subtab_visitado', 'posts')
    
    q_feed = request.args.get('q_feed', '').strip()
    q_estudios = request.args.get('q_estudios', '').strip()
    q_usuarios = request.args.get('q_usuarios', '').strip()

    posts_filtrados = posts_db
    if q_feed:
        subtab_estudios = 'busqueda_posts'
        posts_filtrados = [p for p in posts_db if q_feed.lower() in p['titulo'].lower() or q_feed.lower() in p['descripcion'].lower()]

    estudios_filtrados = estudios_db
    if q_estudios:
        subtab_estudios = 'busqueda_estudios'
        estudios_filtrados = [e for e in estudios_db if q_estudios.lower() in e['titulo'].lower() or q_estudios.lower() in e['descripcion'].lower() or q_estudios.lower() in e['categoria'].lower()]

    usuarios_filtrados = {}
    if q_usuarios:
        subtab_boveda = 'busqueda_usuarios'
        for handle, u in usuarios_db.items():
            if q_usuarios.lower() in u['nombre'].lower() or q_usuarios.lower() in handle.lower():
                usuarios_filtrados[handle] = u
        if q_usuarios.lower() in perfil_usuario['nombre'].lower() or q_usuarios.lower() in perfil_usuario['handle'].lower():
            usuarios_filtrados[perfil_usuario['handle']] = perfil_usuario

    return render_template(
        'index.html',
        posts=posts_filtrados,
        all_posts=posts_db,
        perfil=perfil_usuario,
        estudios=estudios_filtrados,
        all_estudios=estudios_db,
        usuarios_filtrados=usuarios_filtrados,
        tab_activa=tab_activa,
        subtab_estudios=subtab_estudios,
        subtab_boveda=subtab_boveda,
        subtab_perfil_visitado=subtab_perfil_visitado,
        q_feed=q_feed,
        q_estudios=q_estudios,
        q_usuarios=q_usuarios,
        post_detalle=None,
        estudio_detalle=None,
        perfil_visitado=None
    )

@app.route('/post/<int:post_id>')
def ver_post(post_id):
    perfil_usuario = cargar_perfil_actual()
    if not perfil_usuario:
        return redirect(url_for('home'))
        
    mi_id = perfil_usuario['id']
    
    posts_db = cargar_posts_db(mi_id)
    estudios_db = cargar_estudios_db(mi_id)
    
    post = next((p for p in posts_db if p['id'] == post_id), None)
    return render_template(
        'index.html',
        posts=posts_db,
        all_posts=posts_db,
        perfil=perfil_usuario,
        estudios=estudios_db,
        all_estudios=estudios_db,
        usuarios_filtrados={},
        tab_activa='detalle_post',
        subtab_estudios='comunidad',
        subtab_boveda='posts',
        subtab_perfil_visitado='posts',
        post_detalle=post,
        estudio_detalle=None,
        perfil_visitado=None
    )

@app.route('/estudio/<int:estudio_id>')
def ver_estudio(estudio_id):
    perfil_usuario = cargar_perfil_actual()
    if not perfil_usuario:
        return redirect(url_for('home'))

    mi_id = perfil_usuario['id']
    
    posts_db = cargar_posts_db(mi_id)
    estudios_db = cargar_estudios_db(mi_id)
    
    estudio = next((e for e in estudios_db if e['id'] == estudio_id), None)
    return render_template(
        'index.html',
        posts=posts_db,
        all_posts=posts_db,
        perfil=perfil_usuario,
        estudios=estudios_db,
        all_estudios=estudios_db,
        usuarios_filtrados={},
        tab_activa='detalle_estudio',
        subtab_estudios='comunidad',
        subtab_boveda='posts',
        subtab_perfil_visitado='posts',
        post_detalle=None,
        estudio_detalle=estudio,
        perfil_visitado=None
    )

@app.route('/usuario/<handle>')
def ver_perfil_usuario(handle):
    perfil_usuario = cargar_perfil_actual()
    if not perfil_usuario:
        return redirect(url_for('home'))

    mi_id = perfil_usuario['id']
    
    if handle == perfil_usuario['handle']:
        return redirect(url_for('home', tab='boveda'))
    
    subtab_visitado = request.args.get('subtab_visitado', 'posts')
    q_usuarios = request.args.get('q_usuarios', '').strip()

    posts_db = cargar_posts_db(mi_id)
    estudios_db = cargar_estudios_db(mi_id)
    usuarios_db = cargar_usuarios_db(mi_id)

    usuario = usuarios_db.get(handle)
    if not usuario:
        usuario = {
            "nombre": handle,
            "handle": handle,
            "bio": "Melómano y creador en Otox.",
            "foto_avatar": "",
            "banner_url": "",
            "siguiendo_count": 0,
            "seguidores_count": 0,
            "siguiendo_por_mi": False
        }

    user_posts = [p for p in posts_db if p['handle'] == handle]
    user_estudios = [e for e in estudios_db if e['handle'] == handle]
    
    user_liked_posts = [p for p in posts_db if p.get('liked_by_me')]
    user_liked_estudios = [e for e in estudios_db if e.get('liked_by_me')]

    usuarios_filtrados = {}
    if q_usuarios:
        subtab_visitado = 'busqueda_usuarios'
        for h, u in usuarios_db.items():
            if q_usuarios.lower() in u['nombre'].lower() or q_usuarios.lower() in h.lower():
                usuarios_filtrados[h] = u
        if q_usuarios.lower() in perfil_usuario['nombre'].lower() or q_usuarios.lower() in perfil_usuario['handle'].lower():
            usuarios_filtrados[perfil_usuario['handle']] = perfil_usuario

    return render_template(
        'index.html',
        posts=posts_db,
        all_posts=posts_db,
        perfil=perfil_usuario,
        estudios=estudios_db,
        all_estudios=estudios_db,
        usuarios_filtrados=usuarios_filtrados,
        tab_activa='perfil_visitado',
        subtab_estudios='comunidad',
        subtab_boveda='posts',
        subtab_perfil_visitado=subtab_visitado,
        q_usuarios=q_usuarios,
        post_detalle=None,
        estudio_detalle=None,
        perfil_visitado=usuario,
        user_posts=user_posts,
        user_estudios=user_estudios,
        user_liked_posts=user_liked_posts,
        user_liked_estudios=user_liked_estudios
    )

@app.route('/toggle-seguir/<handle>', methods=['POST'])
def toggle_seguir(handle):
    perfil_usuario = cargar_perfil_actual()
    if not perfil_usuario:
        return redirect(url_for('home'))

    mi_id = perfil_usuario['id']
    
    conn = database.obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE handle = ?", (handle,))
    row = cursor.fetchone()
    
    if row:
        target_id = row['id']
        cursor.execute("SELECT COUNT(*) FROM seguidores WHERE seguidor_id = ? AND seguido_id = ?", (mi_id, target_id))
        ya_sigue = cursor.fetchone()[0] > 0
        
        if ya_sigue:
            cursor.execute("DELETE FROM seguidores WHERE seguidor_id = ? AND seguido_id = ?", (mi_id, target_id))
        else:
            cursor.execute("INSERT INTO seguidores (seguidor_id, seguido_id) VALUES (?, ?)", (mi_id, target_id))
        conn.commit()
        
    conn.close()
    return redirect(url_for('ver_perfil_usuario', handle=handle))

@app.route('/politicas')
def politicas():
    perfil_usuario = cargar_perfil_actual()
    mi_id = perfil_usuario['id'] if perfil_usuario else 1
    posts_db = cargar_posts_db(mi_id) if perfil_usuario else []
    estudios_db = cargar_estudios_db(mi_id) if perfil_usuario else []
    return render_template('index.html', posts=posts_db, all_posts=posts_db, perfil=perfil_usuario, estudios=estudios_db, all_estudios=estudios_db, tab_activa='politicas')

@app.route('/terminos')
def terminos():
    perfil_usuario = cargar_perfil_actual()
    mi_id = perfil_usuario['id'] if perfil_usuario else 1
    posts_db = cargar_posts_db(mi_id) if perfil_usuario else []
    estudios_db = cargar_estudios_db(mi_id) if perfil_usuario else []
    return render_template('index.html', posts=posts_db, all_posts=posts_db, perfil=perfil_usuario, estudios=estudios_db, all_estudios=estudios_db, tab_activa='terminos')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# --- ACCIONES DE POSTS Y ESTUDIOS ---

@app.route('/crear-post', methods=['POST'])
def crear_post():
    perfil_usuario = cargar_perfil_actual()
    if not perfil_usuario:
        return redirect(url_for('home'))

    mi_id = perfil_usuario['id']
    
    titulo = request.form.get('post-title')
    url_raw = request.form.get('post-url')
    descripcion = request.form.get('post-desc')
    media_url = procesar_url_media(url_raw)
    
    conn = database.obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO posts (usuario_id, titulo, descripcion, media_url)
        VALUES (?, ?, ?, ?)
    """, (mi_id, titulo, descripcion, media_url))
    conn.commit()
    conn.close()
    
    return redirect(url_for('home', tab='feed'))

@app.route('/like-post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    perfil_usuario = cargar_perfil_actual()
    if not perfil_usuario:
        return redirect(url_for('home'))

    mi_id = perfil_usuario['id']
    redirect_to = request.args.get('redirect_to', 'feed')
    
    conn = database.obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM likes WHERE post_id = ? AND usuario_id = ?", (post_id, mi_id))
    ya_like = cursor.fetchone()[0] > 0
    
    if ya_like:
        cursor.execute("DELETE FROM likes WHERE post_id = ? AND usuario_id = ?", (post_id, mi_id))
    else:
        cursor.execute("INSERT INTO likes (post_id, usuario_id) VALUES (?, ?)", (post_id, mi_id))
        
    conn.commit()
    conn.close()
    
    if redirect_to == 'detalle':
        return redirect(url_for('ver_post', post_id=post_id))
    return redirect(url_for('home', tab=redirect_to))

@app.route('/comentar-post/<int:post_id>', methods=['POST'])
def comentar_post(post_id):
    perfil_usuario = cargar_perfil_actual()
    if not perfil_usuario:
        return redirect(url_for('home'))

    mi_id = perfil_usuario['id']
    redirect_to = request.args.get('redirect_to', 'feed')
    texto = request.form.get('comentario')
    
    if texto:
        conn = database.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO comentarios (usuario_id, post_id, texto)
            VALUES (?, ?, ?)
        """, (mi_id, post_id, texto))
        conn.commit()
        conn.close()
        
    if redirect_to == 'detalle':
        return redirect(url_for('ver_post', post_id=post_id))
    return redirect(url_for('home', tab=redirect_to))

@app.route('/like-comentario-post/<int:post_id>/<int:comentario_id>', methods=['POST'])
def like_comentario_post(post_id, comentario_id):
    perfil_usuario = cargar_perfil_actual()
    if not perfil_usuario:
        return redirect(url_for('home'))

    mi_id = perfil_usuario['id']
    redirect_to = request.args.get('redirect_to', 'feed')
    
    conn = database.obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM likes WHERE comentario_id = ? AND usuario_id = ?", (comentario_id, mi_id))
    ya_like = cursor.fetchone()[0] > 0
    
    if ya_like:
        cursor.execute("DELETE FROM likes WHERE comentario_id = ? AND usuario_id = ?", (comentario_id, mi_id))
    else:
        cursor.execute("INSERT INTO likes (comentario_id, usuario_id) VALUES (?, ?)", (comentario_id, mi_id))
        
    conn.commit()
    conn.close()
    
    if redirect_to == 'detalle':
        return redirect(url_for('ver_post', post_id=post_id))
    return redirect(url_for('home', tab=redirect_to))

@app.route('/responder-comentario-post/<int:post_id>/<int:comentario_id>', methods=['POST'])
def responder_comentario_post(post_id, comentario_id):
    perfil_usuario = cargar_perfil_actual()
    if not perfil_usuario:
        return redirect(url_for('home'))

    mi_id = perfil_usuario['id']
    redirect_to = request.args.get('redirect_to', 'feed')
    texto = request.form.get('respuesta')
    
    if texto:
        conn = database.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO respuestas (comentario_id, usuario_id, texto)
            VALUES (?, ?, ?)
        """, (comentario_id, mi_id, texto))
        conn.commit()
        conn.close()
        
    if redirect_to == 'detalle':
        return redirect(url_for('ver_post', post_id=post_id))
    return redirect(url_for('home', tab=redirect_to))

@app.route('/crear-estudio', methods=['POST'])
def crear_estudio():
    perfil_usuario = cargar_perfil_actual()
    if not perfil_usuario:
        return redirect(url_for('home'))

    mi_id = perfil_usuario['id']
    
    titulo = request.form.get('estudio-titulo')
    categoria = request.form.get('estudio-categoria', 'Teoría')
    descripcion = request.form.get('estudio-desc')
    
    conn = database.obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO estudios (usuario_id, titulo, categoria, descripcion)
        VALUES (?, ?, ?, ?)
    """, (mi_id, titulo, categoria, descripcion))
    conn.commit()
    conn.close()
    
    return redirect(url_for('home', tab='estudios', subtab='mis_estudios'))

@app.route('/estudio/<int:estudio_id>/agregar-capitulo', methods=['POST'])
def agregar_capitulo(estudio_id):
    titulo_cap = request.form.get('capitulo-titulo')
    explicacion = request.form.get('capitulo-explicacion')
    url_raw = request.form.get('capitulo-url')
    media_url = procesar_url_media(url_raw) if url_raw else None
    
    conn = database.obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM capitulos WHERE estudio_id = ?", (estudio_id,))
    num_cap = cursor.fetchone()[0] + 1
    
    cursor.execute("""
        INSERT INTO capitulos (estudio_id, numero, titulo, explicacion, media_url)
        VALUES (?, ?, ?, ?, ?)
    """, (estudio_id, num_cap, titulo_cap, explicacion, media_url))
    conn.commit()
    conn.close()
    
    return redirect(url_for('ver_estudio', estudio_id=estudio_id))

@app.route('/like-estudio/<int:estudio_id>', methods=['POST'])
def like_estudio(estudio_id):
    perfil_usuario = cargar_perfil_actual()
    if not perfil_usuario:
        return redirect(url_for('home'))

    mi_id = perfil_usuario['id']
    redirect_to = request.args.get('redirect_to', 'estudios')
    
    conn = database.obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM likes WHERE estudio_id = ? AND usuario_id = ?", (estudio_id, mi_id))
    ya_like = cursor.fetchone()[0] > 0
    
    if ya_like:
        cursor.execute("DELETE FROM likes WHERE estudio_id = ? AND usuario_id = ?", (estudio_id, mi_id))
    else:
        cursor.execute("INSERT INTO likes (estudio_id, usuario_id) VALUES (?, ?)", (estudio_id, mi_id))
        
    conn.commit()
    conn.close()
    
    if redirect_to == 'detalle':
        return redirect(url_for('ver_estudio', estudio_id=estudio_id))
    return redirect(url_for('home', tab='estudios', subtab=redirect_to))

@app.route('/toggle-favorito-estudio/<int:estudio_id>', methods=['POST'])
def toggle_favorito_estudio(estudio_id):
    perfil_usuario = cargar_perfil_actual()
    if not perfil_usuario:
        return redirect(url_for('home'))

    mi_id = perfil_usuario['id']
    subtab = request.args.get('subtab', 'comunidad')
    
    conn = database.obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM estudios_favoritos WHERE estudio_id = ? AND usuario_id = ?", (estudio_id, mi_id))
    es_fav = cursor.fetchone()[0] > 0
    
    if es_fav:
        cursor.execute("DELETE FROM estudios_favoritos WHERE estudio_id = ? AND usuario_id = ?", (estudio_id, mi_id))
    else:
        cursor.execute("INSERT INTO estudios_favoritos (estudio_id, usuario_id) VALUES (?, ?)", (estudio_id, mi_id))
        
    conn.commit()
    conn.close()
    
    return redirect(url_for('home', tab='estudios', subtab=subtab))

@app.route('/comentar-estudio/<int:estudio_id>', methods=['POST'])
def comentar_estudio(estudio_id):
    perfil_usuario = cargar_perfil_actual()
    if not perfil_usuario:
        return redirect(url_for('home'))

    mi_id = perfil_usuario['id']
    redirect_to = request.args.get('redirect_to', 'estudios')
    texto = request.form.get('comentario')
    
    if texto:
        conn = database.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO comentarios (usuario_id, estudio_id, texto)
            VALUES (?, ?, ?)
        """, (mi_id, estudio_id, texto))
        conn.commit()
        conn.close()
        
    if redirect_to == 'detalle':
        return redirect(url_for('ver_estudio', estudio_id=estudio_id))
    return redirect(url_for('home', tab='estudios'))

@app.route('/like-comentario-estudio/<int:estudio_id>/<int:comentario_id>', methods=['POST'])
def like_comentario_estudio(estudio_id, comentario_id):
    perfil_usuario = cargar_perfil_actual()
    if not perfil_usuario:
        return redirect(url_for('home'))

    mi_id = perfil_usuario['id']
    redirect_to = request.args.get('redirect_to', 'estudios')
    
    conn = database.obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM likes WHERE comentario_id = ? AND usuario_id = ?", (comentario_id, mi_id))
    ya_like = cursor.fetchone()[0] > 0
    
    if ya_like:
        cursor.execute("DELETE FROM likes WHERE comentario_id = ? AND usuario_id = ?", (comentario_id, mi_id))
    else:
        cursor.execute("INSERT INTO likes (comentario_id, usuario_id) VALUES (?, ?)", (comentario_id, mi_id))
        
    conn.commit()
    conn.close()
    
    if redirect_to == 'detalle':
        return redirect(url_for('ver_estudio', estudio_id=estudio_id))
    return redirect(url_for('home', tab='estudios'))

@app.route('/responder-comentario-estudio/<int:estudio_id>/<int:comentario_id>', methods=['POST'])
def responder_comentario_estudio(estudio_id, comentario_id):
    perfil_usuario = cargar_perfil_actual()
    if not perfil_usuario:
        return redirect(url_for('home'))

    mi_id = perfil_usuario['id']
    redirect_to = request.args.get('redirect_to', 'estudios')
    texto = request.form.get('respuesta')
    
    if texto:
        conn = database.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO respuestas (comentario_id, usuario_id, texto)
            VALUES (?, ?, ?)
        """, (comentario_id, mi_id, texto))
        conn.commit()
        conn.close()
        
    if redirect_to == 'detalle':
        return redirect(url_for('ver_estudio', estudio_id=estudio_id))
    return redirect(url_for('home', tab='estudios'))

@app.route('/actualizar-ajustes', methods=['POST'])
def actualizar_ajustes():
    perfil_usuario = cargar_perfil_actual()
    if not perfil_usuario:
        return redirect(url_for('home'))

    mi_id = perfil_usuario['id']
    
    nombre = request.form.get('alias', perfil_usuario['nombre'])
    handle = request.form.get('handle', perfil_usuario['handle'])
    email = request.form.get('email', perfil_usuario['email'])
    nueva_pass = request.form.get('password') or perfil_usuario['password']
    bio = request.form.get('bio', perfil_usuario['bio'])
    foto_avatar = request.form.get('foto_url', perfil_usuario['foto_avatar'])
    banner_url = request.form.get('banner_url', perfil_usuario['banner_url'])
    tema = request.form.get('tema', perfil_usuario['tema'])
    
    conn = database.obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE usuarios 
        SET nombre = ?, handle = ?, email = ?, password = ?, bio = ?, foto_avatar = ?, banner_url = ?, tema = ?
        WHERE id = ?
    """, (nombre, handle, email, nueva_pass, bio, foto_avatar, banner_url, tema, mi_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('home', tab='ajustes'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)