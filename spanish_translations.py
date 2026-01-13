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
    "inactive": "Inactivo",
    
    # Order-related translations
    "order": "Orden",
    "order_label": "Orden",
    "song_order": "Orden de la canción",
    "next_song": "Siguiente canción",
    "previous_song": "Canción anterior",
    "no_next_song": "Última canción del repertorio",
    "no_previous_song": "Primera canción del repertorio",
    "order_number": "Número de orden",
    "performance_order": "Orden de presentación",
    "songs_by_order": "Canciones por orden",
    "upcoming_songs": "Próximas canciones",
    "your_songs": "Tus canciones",
    "order_sequence": "Secuencia de orden",
    "invalid_order": "Orden inválido",
    "missing_order": "Orden faltante",
    "duplicate_order": "Orden duplicado",
    "order_conflict": "Conflicto de orden",
    "order_resolved": "Orden resuelto",
    
    # Enhanced order and navigation translations
    "by_artist": "por",
    "unknown_artist": "Artista desconocido",
    "song_order_aria": "Orden de la canción",
    "select_next_song": "Seleccionar",
    "select_next_song_aria": "Seleccionar siguiente canción",
    "navigated_to_next_song": "Navegando a la siguiente canción",
    "navigated_to_previous_song": "Navegando a la canción anterior",
    "no_song_selected": "No hay canción seleccionada",
    "no_order_info": "La canción actual no tiene información de orden",
    "keyboard_shortcuts": "Atajos de Teclado",
    "next_song_shortcut": "Siguiente canción",
    "previous_song_shortcut": "Canción anterior",
    "next_song_updated": "Siguiente canción actualizada",
    "duration_label": "Duración",
    "instruments_label": "Instrumentos",
    "no_instruments": "Ninguno",
    "view_in_song_selector": "Ver en Selector de Canciones",
    "view_song_in_selector": "Ver",
    "in_song_selector": "en el selector de canciones",
    "no_songs_assigned": "Este músico no tiene canciones asignadas",
    
    # Global selector interface translations
    "global_selector": "Selector Global",
    "global_selector_title": "Selector Global de Canciones",
    "global_song_selection": "Selección Global de Canciones",
    "current_selection": "Selección actual",
    "global_current_song": "Canción global actual",
    "select_global_song": "Seleccionar canción global",
    "global_song_changed": "Canción global cambiada",
    "global_session": "Sesión global",
    "join_global_session": "Unirse a sesión global",
    "leave_global_session": "Salir de sesión global",
    "global_synchronization": "Sincronización global",
    "synchronized": "Sincronizado",
    "not_synchronized": "No sincronizado",
    "synchronizing": "Sincronizando...",
    "sync_complete": "Sincronización completa",
    "sync_failed": "Error de sincronización",
    "global_update": "Actualización global",
    "broadcast_update": "Difundir actualización",
    "session_count": "Sesiones conectadas",
    "active_sessions": "Sesiones activas",
    "connected_users": "Usuarios conectados",
    
    # Connection status and error message translations
    "connection_status": "Estado de conexión",
    "connection_established": "Conexión establecida",
    "connection_lost": "Conexión perdida",
    "connection_restored": "Conexión restaurada",
    "connection_timeout": "Tiempo de conexión agotado",
    "connection_refused": "Conexión rechazada",
    "connection_unstable": "Conexión inestable",
    "websocket_connected": "WebSocket conectado",
    "websocket_disconnected": "WebSocket desconectado",
    "websocket_error": "Error de WebSocket",
    "websocket_reconnecting": "WebSocket reconectando",
    "fallback_mode_active": "Modo de respaldo activo",
    "polling_mode": "Modo de sondeo",
    "sse_mode": "Modo de eventos del servidor",
    "real_time_disabled": "Tiempo real deshabilitado",
    "real_time_enabled": "Tiempo real habilitado",
    "auto_reconnect": "Reconexión automática",
    "manual_reconnect": "Reconexión manual",
    "reconnect_attempt": "Intento de reconexión",
    "reconnect_success": "Reconexión exitosa",
    "reconnect_failed": "Reconexión fallida",
    "max_reconnect_attempts": "Máximo de intentos de reconexión alcanzado",
    "network_unavailable": "Red no disponible",
    "server_maintenance": "Servidor en mantenimiento",
    "service_interrupted": "Servicio interrumpido",
    "session_conflict": "Conflicto de sesión",
    "session_expired_reconnect": "Sesión expirada, reconectando",
    "concurrent_update": "Actualización concurrente",
    "update_conflict": "Conflicto de actualización",
    "conflict_resolved": "Conflicto resuelto",
    "state_mismatch": "Desajuste de estado",
    "state_synchronized": "Estado sincronizado",
    "broadcast_error": "Error de difusión",
    "message_delivery_failed": "Error en entrega de mensaje",
    "session_cleanup": "Limpieza de sesión",
    "invalid_session": "Sesión inválida",
    "session_restored": "Sesión restaurada",
    
    # Enhanced error messages for order functionality
    "order_processing_error": "Error al procesar orden",
    "order_validation_error": "Error de validación de orden",
    "order_assignment_error": "Error de asignación de orden",
    "order_calculation_error": "Error de cálculo de orden",
    "next_song_calculation_error": "Error al calcular siguiente canción",
    "order_data_corrupted": "Datos de orden corruptos",
    "order_sequence_broken": "Secuencia de orden rota",
    "order_synchronization_error": "Error de sincronización de orden",
    
    # Enhanced error messages for global functionality
    "global_state_error": "Error de estado global",
    "global_update_error": "Error de actualización global",
    "global_sync_error": "Error de sincronización global",
    "global_session_error": "Error de sesión global",
    "global_broadcast_error": "Error de difusión global",
    "global_connection_error": "Error de conexión global",
    
    # Real-time synchronization messages (enhanced)
    "connected": "Conectado",
    "disconnected": "Desconectado",
    "reconnecting": "Reconectando...",
    "global_session_joined": "Sesión global iniciada",
    "song_selected": "Canción seleccionada",
    "song_changed": "Canción cambiada",
    "update_failed": "Error al actualizar",
    "service_unavailable": "Servicio no disponible",
    "connection_error": "Error de conexión",
    
    # Enhanced real-time error handling messages
    "websocket_connection_failed": "Error de conexión WebSocket",
    "websocket_upgrade_failed": "Error al actualizar a WebSocket",
    "websocket_handshake_failed": "Error en el protocolo de conexión WebSocket",
    "websocket_protocol_error": "Error de protocolo WebSocket",
    "websocket_security_error": "Error de seguridad WebSocket",
    "websocket_network_error": "Error de red WebSocket",
    "websocket_server_error": "Error del servidor WebSocket",
    "websocket_client_error": "Error del cliente WebSocket",
    "websocket_transport_error": "Error de transporte WebSocket",
    "websocket_authentication_failed": "Error de autenticación WebSocket",
    "websocket_authorization_failed": "Error de autorización WebSocket",
    "websocket_rate_limit_exceeded": "Límite de velocidad WebSocket excedido",
    "websocket_quota_exceeded": "Cuota WebSocket excedida",
    "websocket_service_overloaded": "Servicio WebSocket sobrecargado",
    "websocket_maintenance_mode": "WebSocket en modo de mantenimiento",
    
    # Session synchronization error messages
    "session_sync_failed": "Error de sincronización de sesión",
    "session_conflict_detected": "Conflicto de sesión detectado",
    "session_state_mismatch": "Desajuste de estado de sesión",
    "session_data_corrupted": "Datos de sesión corruptos",
    "session_timeout_exceeded": "Tiempo de sesión excedido",
    "session_invalid_state": "Estado de sesión inválido",
    "session_recovery_failed": "Error en recuperación de sesión",
    "session_cleanup_failed": "Error en limpieza de sesión",
    "session_broadcast_failed": "Error en difusión de sesión",
    "session_update_rejected": "Actualización de sesión rechazada",
    "session_version_mismatch": "Desajuste de versión de sesión",
    "session_lock_timeout": "Tiempo de bloqueo de sesión agotado",
    "session_concurrent_modification": "Modificación concurrente de sesión",
    "session_rollback_failed": "Error en reversión de sesión",
    "session_persistence_failed": "Error en persistencia de sesión",
    
    # Network timeout and retry messages
    "network_timeout_short": "Tiempo de red agotado (corto)",
    "network_timeout_medium": "Tiempo de red agotado (medio)",
    "network_timeout_long": "Tiempo de red agotado (largo)",
    "network_retry_exhausted": "Reintentos de red agotados",
    "network_retry_in_progress": "Reintentando conexión de red",
    "network_retry_scheduled": "Reintento de red programado",
    "network_retry_cancelled": "Reintento de red cancelado",
    "network_backoff_active": "Retroceso de red activo",
    "network_circuit_breaker_open": "Cortacircuitos de red abierto",
    "network_circuit_breaker_half_open": "Cortacircuitos de red semi-abierto",
    "network_circuit_breaker_closed": "Cortacircuitos de red cerrado",
    "network_quality_degraded": "Calidad de red degradada",
    "network_quality_poor": "Calidad de red pobre",
    "network_quality_unstable": "Calidad de red inestable",
    "network_latency_high": "Latencia de red alta",
    "network_bandwidth_limited": "Ancho de banda limitado",
    
    # Conflict resolution messages
    "conflict_resolution_started": "Resolución de conflicto iniciada",
    "conflict_resolution_completed": "Resolución de conflicto completada",
    "conflict_resolution_failed": "Error en resolución de conflicto",
    "conflict_last_write_wins": "Última escritura gana",
    "conflict_first_write_wins": "Primera escritura gana",
    "conflict_merge_attempted": "Intento de fusión de conflicto",
    "conflict_merge_successful": "Fusión de conflicto exitosa",
    "conflict_merge_failed": "Error en fusión de conflicto",
    "conflict_manual_resolution_required": "Resolución manual de conflicto requerida",
    "conflict_auto_resolution_disabled": "Resolución automática de conflicto deshabilitada",
    "conflict_priority_override": "Anulación de prioridad de conflicto",
    "conflict_timestamp_comparison": "Comparación de marca de tiempo de conflicto",
    
    # Recovery and resilience messages
    "recovery_mode_activated": "Modo de recuperación activado",
    "recovery_mode_deactivated": "Modo de recuperación desactivado",
    "recovery_attempt_started": "Intento de recuperación iniciado",
    "recovery_attempt_successful": "Intento de recuperación exitoso",
    "recovery_attempt_failed": "Intento de recuperación fallido",
    "recovery_partial_success": "Recuperación parcialmente exitosa",
    "recovery_full_success": "Recuperación completamente exitosa",
    "recovery_rollback_initiated": "Reversión de recuperación iniciada",
    "recovery_rollback_completed": "Reversión de recuperación completada",
    "recovery_checkpoint_created": "Punto de control de recuperación creado",
    "recovery_checkpoint_restored": "Punto de control de recuperación restaurado",
    "recovery_state_validated": "Estado de recuperación validado",
    "recovery_state_invalid": "Estado de recuperación inválido",
    
    # Graceful degradation messages
    "degraded_mode_active": "Modo degradado activo",
    "degraded_mode_inactive": "Modo degradado inactivo",
    "degraded_functionality_limited": "Funcionalidad limitada en modo degradado",
    "degraded_real_time_disabled": "Tiempo real deshabilitado en modo degradado",
    "degraded_polling_enabled": "Sondeo habilitado en modo degradado",
    "degraded_cache_only": "Solo caché en modo degradado",
    "degraded_offline_mode": "Modo sin conexión degradado",
    "degraded_read_only": "Solo lectura en modo degradado",
    "degraded_essential_only": "Solo funciones esenciales en modo degradado",
    "degraded_performance_reduced": "Rendimiento reducido en modo degradado",
    
    # User notification messages for real-time issues
    "realtime_connection_lost_notification": "Se perdió la conexión en tiempo real. Intentando reconectar...",
    "realtime_connection_restored_notification": "Conexión en tiempo real restaurada",
    "realtime_sync_conflict_notification": "Conflicto de sincronización detectado. Resolviendo automáticamente...",
    "realtime_sync_conflict_resolved_notification": "Conflicto de sincronización resuelto",
    "realtime_service_degraded_notification": "Servicio en tiempo real funcionando con limitaciones",
    "realtime_service_restored_notification": "Servicio en tiempo real completamente restaurado",
    "realtime_update_failed_notification": "Error al actualizar en tiempo real. Reintentando...",
    "realtime_update_successful_notification": "Actualización en tiempo real exitosa",
    "realtime_fallback_mode_notification": "Usando modo de respaldo para sincronización",
    "realtime_normal_mode_notification": "Sincronización en tiempo real normal restaurada"
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
    
    # Check for specific instrument mappings
    instrument_mappings = {
        "lead guitar": "Guitarra Principal",
        "rhythm guitar": "Guitarra Rítmica", 
        "bass": "Bajo",
        "battery": "Batería",
        "drums": "Batería",
        "singer": "Voz",
        "lead singer": "Voz",
        "vocals": "Voz",
        "keyboards": "Teclados",
        "keyboard": "Teclado",
        "piano": "Piano"
    }
    
    # Check for exact matches first
    if key in instrument_mappings:
        return instrument_mappings[key]
    
    # Check for partial matches (e.g., "Electric Guitar" -> "Guitarra Eléctrica")
    if "guitar" in key:
        if "electric" in key:
            return "Guitarra Eléctrica"
        elif "acoustic" in key:
            return "Guitarra Acústica"
        elif "bass" in key:
            return "Guitarra Bajo"
        elif "lead" in key:
            return "Guitarra Principal"
        elif "rhythm" in key or "rythm" in key:  # Handle typo in CSV
            return "Guitarra Rítmica"
        else:
            return "Guitarra"
    elif "bass" in key and "guitar" not in key:
        return "Bajo"
    elif "drum" in key or "battery" in key:
        return "Batería"
    elif "vocal" in key or "voice" in key or "singing" in key or "singer" in key:
        return "Voz"
    elif "keyboard" in key or "keys" in key:
        return "Teclados"
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
        "duplicate_data": get_translation("duplicate_data"),
        
        # WebSocket error types
        "websocket_connection_failed": get_translation("websocket_connection_failed"),
        "websocket_upgrade_failed": get_translation("websocket_upgrade_failed"),
        "websocket_handshake_failed": get_translation("websocket_handshake_failed"),
        "websocket_protocol_error": get_translation("websocket_protocol_error"),
        "websocket_security_error": get_translation("websocket_security_error"),
        "websocket_network_error": get_translation("websocket_network_error"),
        "websocket_server_error": get_translation("websocket_server_error"),
        "websocket_client_error": get_translation("websocket_client_error"),
        "websocket_transport_error": get_translation("websocket_transport_error"),
        "websocket_authentication_failed": get_translation("websocket_authentication_failed"),
        "websocket_authorization_failed": get_translation("websocket_authorization_failed"),
        "websocket_rate_limit_exceeded": get_translation("websocket_rate_limit_exceeded"),
        "websocket_quota_exceeded": get_translation("websocket_quota_exceeded"),
        "websocket_service_overloaded": get_translation("websocket_service_overloaded"),
        "websocket_maintenance_mode": get_translation("websocket_maintenance_mode"),
        
        # Session synchronization error types
        "session_sync_failed": get_translation("session_sync_failed"),
        "session_conflict_detected": get_translation("session_conflict_detected"),
        "session_state_mismatch": get_translation("session_state_mismatch"),
        "session_data_corrupted": get_translation("session_data_corrupted"),
        "session_timeout_exceeded": get_translation("session_timeout_exceeded"),
        "session_invalid_state": get_translation("session_invalid_state"),
        "session_recovery_failed": get_translation("session_recovery_failed"),
        "session_cleanup_failed": get_translation("session_cleanup_failed"),
        "session_broadcast_failed": get_translation("session_broadcast_failed"),
        "session_update_rejected": get_translation("session_update_rejected"),
        "session_version_mismatch": get_translation("session_version_mismatch"),
        "session_lock_timeout": get_translation("session_lock_timeout"),
        "session_concurrent_modification": get_translation("session_concurrent_modification"),
        "session_rollback_failed": get_translation("session_rollback_failed"),
        "session_persistence_failed": get_translation("session_persistence_failed"),
        
        # Network timeout and retry error types
        "network_timeout_short": get_translation("network_timeout_short"),
        "network_timeout_medium": get_translation("network_timeout_medium"),
        "network_timeout_long": get_translation("network_timeout_long"),
        "network_retry_exhausted": get_translation("network_retry_exhausted"),
        "network_circuit_breaker_open": get_translation("network_circuit_breaker_open"),
        "network_quality_degraded": get_translation("network_quality_degraded"),
        "network_quality_poor": get_translation("network_quality_poor"),
        "network_quality_unstable": get_translation("network_quality_unstable"),
        "network_latency_high": get_translation("network_latency_high"),
        "network_bandwidth_limited": get_translation("network_bandwidth_limited")
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

def format_order_display(order_number):
    """
    Format order number for display in Spanish.
    
    Args:
        order_number (int): Order number
        
    Returns:
        str: Formatted order display in Spanish
    """
    if order_number is None or order_number < 0:
        return get_translation("invalid_order")
    
    return f"{get_translation('order_label')}: {order_number}"

def get_next_song_message(has_next_song=True):
    """
    Get appropriate next song message in Spanish.
    
    Args:
        has_next_song (bool): Whether there is a next song
        
    Returns:
        str: Next song message in Spanish
    """
    if has_next_song:
        return get_translation("next_song")
    else:
        return get_translation("no_next_song")

def get_connection_status_message(status):
    """
    Get localized connection status message.
    
    Args:
        status (str): Connection status type
        
    Returns:
        str: Localized connection status message
    """
    status_messages = {
        "connected": get_translation("connected"),
        "disconnected": get_translation("disconnected"),
        "reconnecting": get_translation("reconnecting"),
        "websocket_connected": get_translation("websocket_connected"),
        "websocket_disconnected": get_translation("websocket_disconnected"),
        "websocket_error": get_translation("websocket_error"),
        "websocket_reconnecting": get_translation("websocket_reconnecting"),
        "connection_established": get_translation("connection_established"),
        "connection_lost": get_translation("connection_lost"),
        "connection_restored": get_translation("connection_restored"),
        "connection_timeout": get_translation("connection_timeout"),
        "connection_refused": get_translation("connection_refused"),
        "connection_unstable": get_translation("connection_unstable"),
        "fallback_mode": get_translation("fallback_mode_active"),
        "polling_mode": get_translation("polling_mode"),
        "sse_mode": get_translation("sse_mode"),
        "real_time_disabled": get_translation("real_time_disabled"),
        "real_time_enabled": get_translation("real_time_enabled")
    }
    
    return status_messages.get(status, get_translation("connection_status"))

def get_global_selector_message(message_type, context=None):
    """
    Get localized global selector message.
    
    Args:
        message_type (str): Type of global selector message
        context (str, optional): Additional context
        
    Returns:
        str: Localized global selector message
    """
    global_messages = {
        "title": get_translation("global_selector_title"),
        "current_selection": get_translation("current_selection"),
        "select_song": get_translation("select_global_song"),
        "song_changed": get_translation("global_song_changed"),
        "join_session": get_translation("join_global_session"),
        "leave_session": get_translation("leave_global_session"),
        "synchronized": get_translation("synchronized"),
        "not_synchronized": get_translation("not_synchronized"),
        "synchronizing": get_translation("synchronizing"),
        "sync_complete": get_translation("sync_complete"),
        "sync_failed": get_translation("sync_failed"),
        "session_count": get_translation("session_count"),
        "active_sessions": get_translation("active_sessions"),
        "connected_users": get_translation("connected_users")
    }
    
    message = global_messages.get(message_type, get_translation("global_selector"))
    
    if context:
        message += f": {context}"
    
    return message

def get_order_error_message(error_type, context=None):
    """
    Get localized order-related error message.
    
    Args:
        error_type (str): Type of order error
        context (str, optional): Additional context
        
    Returns:
        str: Localized order error message
    """
    order_error_messages = {
        "processing": get_translation("order_processing_error"),
        "validation": get_translation("order_validation_error"),
        "assignment": get_translation("order_assignment_error"),
        "calculation": get_translation("order_calculation_error"),
        "next_song": get_translation("next_song_calculation_error"),
        "corrupted": get_translation("order_data_corrupted"),
        "sequence_broken": get_translation("order_sequence_broken"),
        "synchronization": get_translation("order_synchronization_error"),
        "invalid": get_translation("invalid_order"),
        "missing": get_translation("missing_order"),
        "duplicate": get_translation("duplicate_order"),
        "conflict": get_translation("order_conflict")
    }
    
    message = order_error_messages.get(error_type, get_translation("order_processing_error"))
    
    if context:
        message += f": {context}"
    
    return message

def get_global_error_message(error_type, context=None):
    """
    Get localized global functionality error message.
    
    Args:
        error_type (str): Type of global error
        context (str, optional): Additional context
        
    Returns:
        str: Localized global error message
    """
    global_error_messages = {
        "state": get_translation("global_state_error"),
        "update": get_translation("global_update_error"),
        "sync": get_translation("global_sync_error"),
        "session": get_translation("global_session_error"),
        "broadcast": get_translation("global_broadcast_error"),
        "connection": get_translation("global_connection_error"),
        "conflict": get_translation("update_conflict"),
        "session_conflict": get_translation("session_conflict"),
        "state_mismatch": get_translation("state_mismatch"),
        "message_delivery": get_translation("message_delivery_failed"),
        "invalid_session": get_translation("invalid_session")
    }
    
    message = global_error_messages.get(error_type, get_translation("global_state_error"))
    
    if context:
        message += f": {context}"
    
    return message

# Export the main translation function for easy import
translate = get_translation

def get_websocket_error_message(error_type, context=None):
    """
    Get localized WebSocket error message.
    
    Args:
        error_type (str): Type of WebSocket error
        context (str, optional): Additional context
        
    Returns:
        str: Localized WebSocket error message
    """
    websocket_error_messages = {
        "connection_failed": get_translation("websocket_connection_failed"),
        "upgrade_failed": get_translation("websocket_upgrade_failed"),
        "handshake_failed": get_translation("websocket_handshake_failed"),
        "protocol_error": get_translation("websocket_protocol_error"),
        "security_error": get_translation("websocket_security_error"),
        "network_error": get_translation("websocket_network_error"),
        "server_error": get_translation("websocket_server_error"),
        "client_error": get_translation("websocket_client_error"),
        "transport_error": get_translation("websocket_transport_error"),
        "authentication_failed": get_translation("websocket_authentication_failed"),
        "authorization_failed": get_translation("websocket_authorization_failed"),
        "rate_limit_exceeded": get_translation("websocket_rate_limit_exceeded"),
        "quota_exceeded": get_translation("websocket_quota_exceeded"),
        "service_overloaded": get_translation("websocket_service_overloaded"),
        "maintenance_mode": get_translation("websocket_maintenance_mode")
    }
    
    message = websocket_error_messages.get(error_type, get_translation("websocket_error"))
    
    if context:
        message += f": {context}"
    
    return message

def get_session_sync_error_message(error_type, context=None):
    """
    Get localized session synchronization error message.
    
    Args:
        error_type (str): Type of session sync error
        context (str, optional): Additional context
        
    Returns:
        str: Localized session sync error message
    """
    session_sync_error_messages = {
        "sync_failed": get_translation("session_sync_failed"),
        "conflict_detected": get_translation("session_conflict_detected"),
        "state_mismatch": get_translation("session_state_mismatch"),
        "data_corrupted": get_translation("session_data_corrupted"),
        "timeout_exceeded": get_translation("session_timeout_exceeded"),
        "invalid_state": get_translation("session_invalid_state"),
        "recovery_failed": get_translation("session_recovery_failed"),
        "cleanup_failed": get_translation("session_cleanup_failed"),
        "broadcast_failed": get_translation("session_broadcast_failed"),
        "update_rejected": get_translation("session_update_rejected"),
        "version_mismatch": get_translation("session_version_mismatch"),
        "lock_timeout": get_translation("session_lock_timeout"),
        "concurrent_modification": get_translation("session_concurrent_modification"),
        "rollback_failed": get_translation("session_rollback_failed"),
        "persistence_failed": get_translation("session_persistence_failed")
    }
    
    message = session_sync_error_messages.get(error_type, get_translation("session_sync_failed"))
    
    if context:
        message += f": {context}"
    
    return message

def get_network_retry_message(retry_type, context=None):
    """
    Get localized network retry message.
    
    Args:
        retry_type (str): Type of network retry
        context (str, optional): Additional context
        
    Returns:
        str: Localized network retry message
    """
    network_retry_messages = {
        "timeout_short": get_translation("network_timeout_short"),
        "timeout_medium": get_translation("network_timeout_medium"),
        "timeout_long": get_translation("network_timeout_long"),
        "retry_exhausted": get_translation("network_retry_exhausted"),
        "retry_in_progress": get_translation("network_retry_in_progress"),
        "retry_scheduled": get_translation("network_retry_scheduled"),
        "retry_cancelled": get_translation("network_retry_cancelled"),
        "backoff_active": get_translation("network_backoff_active"),
        "circuit_breaker_open": get_translation("network_circuit_breaker_open"),
        "circuit_breaker_half_open": get_translation("network_circuit_breaker_half_open"),
        "circuit_breaker_closed": get_translation("network_circuit_breaker_closed"),
        "quality_degraded": get_translation("network_quality_degraded"),
        "quality_poor": get_translation("network_quality_poor"),
        "quality_unstable": get_translation("network_quality_unstable"),
        "latency_high": get_translation("network_latency_high"),
        "bandwidth_limited": get_translation("network_bandwidth_limited")
    }
    
    message = network_retry_messages.get(retry_type, get_translation("network_error"))
    
    if context:
        message += f": {context}"
    
    return message

def get_conflict_resolution_message(resolution_type, context=None):
    """
    Get localized conflict resolution message.
    
    Args:
        resolution_type (str): Type of conflict resolution
        context (str, optional): Additional context
        
    Returns:
        str: Localized conflict resolution message
    """
    conflict_resolution_messages = {
        "started": get_translation("conflict_resolution_started"),
        "completed": get_translation("conflict_resolution_completed"),
        "failed": get_translation("conflict_resolution_failed"),
        "last_write_wins": get_translation("conflict_last_write_wins"),
        "first_write_wins": get_translation("conflict_first_write_wins"),
        "merge_attempted": get_translation("conflict_merge_attempted"),
        "merge_successful": get_translation("conflict_merge_successful"),
        "merge_failed": get_translation("conflict_merge_failed"),
        "manual_resolution_required": get_translation("conflict_manual_resolution_required"),
        "auto_resolution_disabled": get_translation("conflict_auto_resolution_disabled"),
        "priority_override": get_translation("conflict_priority_override"),
        "timestamp_comparison": get_translation("conflict_timestamp_comparison")
    }
    
    message = conflict_resolution_messages.get(resolution_type, get_translation("conflict_resolved"))
    
    if context:
        message += f": {context}"
    
    return message

def get_recovery_status_message(recovery_type, context=None):
    """
    Get localized recovery status message.
    
    Args:
        recovery_type (str): Type of recovery
        context (str, optional): Additional context
        
    Returns:
        str: Localized recovery status message
    """
    recovery_status_messages = {
        "mode_activated": get_translation("recovery_mode_activated"),
        "mode_deactivated": get_translation("recovery_mode_deactivated"),
        "attempt_started": get_translation("recovery_attempt_started"),
        "attempt_successful": get_translation("recovery_attempt_successful"),
        "attempt_failed": get_translation("recovery_attempt_failed"),
        "partial_success": get_translation("recovery_partial_success"),
        "full_success": get_translation("recovery_full_success"),
        "rollback_initiated": get_translation("recovery_rollback_initiated"),
        "rollback_completed": get_translation("recovery_rollback_completed"),
        "checkpoint_created": get_translation("recovery_checkpoint_created"),
        "checkpoint_restored": get_translation("recovery_checkpoint_restored"),
        "state_validated": get_translation("recovery_state_validated"),
        "state_invalid": get_translation("recovery_state_invalid")
    }
    
    message = recovery_status_messages.get(recovery_type, get_translation("recovering"))
    
    if context:
        message += f": {context}"
    
    return message

def get_degraded_mode_message(degraded_type, context=None):
    """
    Get localized degraded mode message.
    
    Args:
        degraded_type (str): Type of degraded mode
        context (str, optional): Additional context
        
    Returns:
        str: Localized degraded mode message
    """
    degraded_mode_messages = {
        "active": get_translation("degraded_mode_active"),
        "inactive": get_translation("degraded_mode_inactive"),
        "functionality_limited": get_translation("degraded_functionality_limited"),
        "real_time_disabled": get_translation("degraded_real_time_disabled"),
        "polling_enabled": get_translation("degraded_polling_enabled"),
        "cache_only": get_translation("degraded_cache_only"),
        "offline_mode": get_translation("degraded_offline_mode"),
        "read_only": get_translation("degraded_read_only"),
        "essential_only": get_translation("degraded_essential_only"),
        "performance_reduced": get_translation("degraded_performance_reduced")
    }
    
    message = degraded_mode_messages.get(degraded_type, get_translation("service_degraded"))
    
    if context:
        message += f": {context}"
    
    return message

def get_realtime_notification_message(notification_type, context=None):
    """
    Get localized real-time notification message for user display.
    
    Args:
        notification_type (str): Type of real-time notification
        context (str, optional): Additional context
        
    Returns:
        str: Localized real-time notification message
    """
    realtime_notification_messages = {
        "connection_lost": get_translation("realtime_connection_lost_notification"),
        "connection_restored": get_translation("realtime_connection_restored_notification"),
        "sync_conflict": get_translation("realtime_sync_conflict_notification"),
        "sync_conflict_resolved": get_translation("realtime_sync_conflict_resolved_notification"),
        "service_degraded": get_translation("realtime_service_degraded_notification"),
        "service_restored": get_translation("realtime_service_restored_notification"),
        "update_failed": get_translation("realtime_update_failed_notification"),
        "update_successful": get_translation("realtime_update_successful_notification"),
        "fallback_mode": get_translation("realtime_fallback_mode_notification"),
        "normal_mode": get_translation("realtime_normal_mode_notification")
    }
    
    message = realtime_notification_messages.get(notification_type, get_translation("connection_status"))
    
    if context:
        message += f": {context}"
    
    return message