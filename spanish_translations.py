"""
Spanish Translation System for Rock and Roll Forum Jam en Español
Provides comprehensive Spanish translations for all UI elements.
"""

# Spanish translation dictionary for all UI elements
SPANISH_TRANSLATIONS = {
    # Application branding
    "app_title": "Rock and Roll Forum Jam en Español",
    "app_subtitle": "Selector de Canciones y Músicos para Presentaciones en Vivo",
    "app_description": "Una aplicación web responsiva para que los músicos vean las asignaciones de canciones en presentaciones en vivo",
    "app_tagline": "Gestión profesional de música en vivo",
    "app_copyright": "© 2024 Rock and Roll Forum Jam en Español - Todos los derechos reservados",
    "app_footer_description": "Aplicación web para gestión de presentaciones musicales en vivo",
    
    # Navigation menu
    "menu_toggle": "Abrir menú de navegación",
    "song_selector": "Selector de Canciones",
    "musician_selector": "Selector de Músicos", 
    "live_performance": "Presentación en Vivo",
    "menu_close": "Cerrar menú",
    
    # Song selector section
    "select_song": "Seleccionar una canción...",
    "song_selection": "Selección de Canción",
    "song_details": "Detalles de la Canción",
    "musician_assignments": "Asignaciones de Músicos",
    "instruments": "Instrumentos",
    "duration": "Duración",
    "forward_to_musician": "Ver en Selector de Músicos",
    "navigation_links": "Enlaces de Navegación",
    "no_musicians_assigned": "No hay músicos asignados a esta canción",
    
    # Musician selector section
    "select_musician": "Seleccionar un músico...",
    "musician_selection": "Selección de Músico",
    "musician_details": "Detalles del Músico",
    "musician_songs": "Canciones del Músico",
    "plays_instruments": "Toca",
    "forward_to_song": "Ver en Selector de Canciones",
    "no_musician_selected": "Selecciona un músico para ver sus canciones",
    
    # Live performance section
    "current_song": "Canción Actual",
    "next_song": "Próxima Canción",
    "now_playing": "Reproduciendo Ahora",
    "up_next": "A Continuación",
    "no_performance": "No hay presentación activa",
    "no_current_song": "No hay canción actual seleccionada",
    "no_next_song": "No hay próxima canción seleccionada",
    "performance_status": "Estado de la Presentación",
    
    # Admin control panel
    "admin_control": "Panel de Control Administrativo",
    "set_current": "Establecer Canción Actual",
    "set_next": "Establecer Próxima Canción",
    "update_performance": "Actualizar Presentación",
    "admin_instructions": "Utiliza este panel para controlar qué canciones aparecen en la sección de Presentación en Vivo",
    
    # Common UI elements
    "loading": "Cargando...",
    "error": "Error",
    "success": "Éxito",
    "warning": "Advertencia",
    "info": "Información",
    "close": "Cerrar",
    "save": "Guardar",
    "cancel": "Cancelar",
    "submit": "Enviar",
    "reset": "Restablecer",
    "refresh": "Actualizar",
    "back": "Volver",
    "next": "Siguiente",
    "previous": "Anterior",
    
    # Status messages
    "no_data": "No hay datos disponibles",
    "data_loading": "Cargando datos...",
    "data_error": "Error al cargar los datos",
    "connection_error": "Error de conexión",
    "server_error": "Error del servidor",
    "not_found": "No encontrado",
    "access_denied": "Acceso denegado",
    
    # Instrument names (common translations)
    "guitar": "Guitarra",
    "bass": "Bajo",
    "drums": "Batería",
    "vocals": "Voz",
    "keyboard": "Teclado",
    "piano": "Piano",
    "saxophone": "Saxofón",
    "trumpet": "Trompeta",
    "violin": "Violín",
    "flute": "Flauta",
    "harmonica": "Armónica",
    "accordion": "Acordeón",
    
    # Error messages
    "song_not_found": "Canción no encontrada",
    "musician_not_found": "Músico no encontrado",
    "data_file_not_found": "Archivo de datos no encontrado",
    "invalid_data_format": "Formato de datos inválido",
    "failed_to_load_songs": "Error al cargar las canciones",
    "failed_to_load_musicians": "Error al cargar los músicos",
    "failed_to_load_song_details": "Error al cargar los detalles de la canción",
    "failed_to_load_musician_details": "Error al cargar los detalles del músico",
    "application_not_initialized": "Aplicación no inicializada correctamente",
    
    # Network and API error messages
    "network_error": "Error de conexión de red",
    "timeout_error": "Tiempo de espera agotado",
    "server_unavailable": "Servidor no disponible",
    "api_error": "Error en la API",
    "request_failed": "Solicitud fallida",
    "invalid_response": "Respuesta inválida del servidor",
    "data_corruption": "Datos corruptos detectados",
    "cache_error": "Error en el sistema de caché",
    "session_expired": "Sesión expirada",
    "permission_denied": "Permisos insuficientes",
    
    # Retry and recovery messages
    "retrying": "Reintentando...",
    "retry_failed": "Reintento fallido",
    "max_retries_exceeded": "Máximo número de reintentos excedido",
    "recovering": "Recuperando...",
    "fallback_mode": "Modo de respaldo activado",
    "service_degraded": "Servicio funcionando con limitaciones",
    
    # Data consistency error messages
    "data_inconsistency": "Inconsistencia de datos detectada",
    "sync_error": "Error de sincronización",
    "validation_failed": "Validación de datos fallida",
    "integrity_check_failed": "Verificación de integridad fallida",
    "missing_required_data": "Faltan datos requeridos",
    "duplicate_data": "Datos duplicados detectados",
    
    # Accessibility labels
    "skip_to_content": "Saltar al contenido principal",
    "main_navigation": "Navegación principal",
    "song_information": "Información de la canción",
    "musician_information": "Información del músico",
    "performance_information": "Información de la presentación",
    "admin_controls": "Controles administrativos",
    
    # Form labels and placeholders
    "choose_option": "Elegir una opción",
    "search_placeholder": "Buscar...",
    "filter_placeholder": "Filtrar resultados...",
    
    # Time and date formats
    "minutes": "minutos",
    "seconds": "segundos",
    "hours": "horas",
    
    # Responsive design messages
    "mobile_menu": "Menú móvil",
    "desktop_view": "Vista de escritorio",
    "tablet_view": "Vista de tableta",
    
    # Performance indicators
    "assigned": "Asignado",
    "unassigned": "Sin asignar",
    "available": "Disponible",
    "unavailable": "No disponible",
    "active": "Activo",
    "inactive": "Inactivo"
}

def get_translation(key, default=None):
    """
    Get Spanish translation for a given key.
    
    Args:
        key (str): Translation key
        default (str, optional): Default value if key not found
        
    Returns:
        str: Spanish translation or default value
    """
    return SPANISH_TRANSLATIONS.get(key, default or key)

def translate_instrument_name(instrument_name):
    """
    Translate common instrument names to Spanish.
    
    Args:
        instrument_name (str): English instrument name
        
    Returns:
        str: Spanish instrument name or original if no translation found
    """
    # Convert to lowercase for lookup
    key = instrument_name.lower().strip()
    
    # Check for direct translation
    if key in SPANISH_TRANSLATIONS:
        return SPANISH_TRANSLATIONS[key]
    
    # Check for partial matches (e.g., "Electric Guitar" -> "Guitarra Eléctrica")
    if "guitar" in key:
        if "electric" in key:
            return "Guitarra Eléctrica"
        elif "acoustic" in key:
            return "Guitarra Acústica"
        elif "bass" in key:
            return "Guitarra Bajo"
        else:
            return "Guitarra"
    elif "bass" in key and "guitar" not in key:
        return "Bajo"
    elif "drum" in key:
        return "Batería"
    elif "vocal" in key or "voice" in key or "singing" in key:
        return "Voz"
    elif "keyboard" in key or "keys" in key:
        return "Teclado"
    elif "piano" in key:
        return "Piano"
    
    # Return original if no translation found
    return instrument_name

def get_error_message(error_type, context=None):
    """
    Get localized error message for different error types.
    
    Args:
        error_type (str): Type of error
        context (str, optional): Additional context for the error
        
    Returns:
        str: Localized error message
    """
    error_messages = {
        "404": get_translation("not_found"),
        "500": get_translation("server_error"),
        "connection": get_translation("connection_error"),
        "data": get_translation("data_error"),
        "song_not_found": get_translation("song_not_found"),
        "musician_not_found": get_translation("musician_not_found"),
        "file_not_found": get_translation("data_file_not_found"),
        "invalid_format": get_translation("invalid_data_format"),
        "load_songs": get_translation("failed_to_load_songs"),
        "load_musicians": get_translation("failed_to_load_musicians"),
        "load_song_details": get_translation("failed_to_load_song_details"),
        "load_musician_details": get_translation("failed_to_load_musician_details"),
        "not_initialized": get_translation("application_not_initialized"),
        
        # Enhanced error types
        "network": get_translation("network_error"),
        "timeout": get_translation("timeout_error"),
        "server_unavailable": get_translation("server_unavailable"),
        "api_error": get_translation("api_error"),
        "request_failed": get_translation("request_failed"),
        "invalid_response": get_translation("invalid_response"),
        "data_corruption": get_translation("data_corruption"),
        "cache_error": get_translation("cache_error"),
        "session_expired": get_translation("session_expired"),
        "permission_denied": get_translation("permission_denied"),
        "data_inconsistency": get_translation("data_inconsistency"),
        "sync_error": get_translation("sync_error"),
        "validation_failed": get_translation("validation_failed"),
        "integrity_check_failed": get_translation("integrity_check_failed"),
        "missing_required_data": get_translation("missing_required_data"),
        "duplicate_data": get_translation("duplicate_data")
    }
    
    message = error_messages.get(error_type, get_translation("error"))
    
    if context:
        message += f": {context}"
    
    return message

def get_retry_message(attempt, max_attempts):
    """
    Get localized retry message.
    
    Args:
        attempt (int): Current attempt number
        max_attempts (int): Maximum number of attempts
        
    Returns:
        str: Localized retry message
    """
    if attempt < max_attempts:
        return f"{get_translation('retrying')} ({attempt}/{max_attempts})"
    else:
        return get_translation("max_retries_exceeded")

def get_recovery_message(recovery_type):
    """
    Get localized recovery message.
    
    Args:
        recovery_type (str): Type of recovery being attempted
        
    Returns:
        str: Localized recovery message
    """
    recovery_messages = {
        "fallback": get_translation("fallback_mode"),
        "degraded": get_translation("service_degraded"),
        "recovering": get_translation("recovering")
    }
    
    return recovery_messages.get(recovery_type, get_translation("recovering"))

def format_duration_spanish(duration_str):
    """
    Format duration string in Spanish.
    
    Args:
        duration_str (str): Duration in format "MM:SS" or similar
        
    Returns:
        str: Duration formatted in Spanish
    """
    if not duration_str:
        return ""
    
    # If it's already in MM:SS format, just return it
    if ":" in duration_str:
        return duration_str
    
    # If it's in seconds, convert to MM:SS
    try:
        total_seconds = int(duration_str)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"
    except (ValueError, TypeError):
        return duration_str

# Export the main translation function for easy import
translate = get_translation