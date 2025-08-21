import api from './api';

// ✅ CONFIGURACIÓN: Umbral de confianza para verificación facial
const CONFIDENCE_THRESHOLD = 0.90; // 90% - Solo entradas con 90% o superior de confianza

export const attendanceService = {
    // Variable para almacenar el token de autenticación
    authToken: null,

    // Método para establecer el token
    setAuthToken(token) {
        this.authToken = token;
        console.log('🔑 Token de autenticación establecido');
    },

    // Método para obtener headers con autenticación
    getAuthHeaders() {
        if (this.authToken) {
            return {
                'Authorization': `Bearer ${this.authToken}`,
                'Content-Type': 'application/json'
            };
        }
        return {
            'Content-Type': 'application/json'
        };
    },

    async verifyFaceAndMarkAttendance(employeeId, photoBase64, areaId, latitude, longitude) {
        try {
            console.log('🔍 Verificando rostro para asistencia...');
            
            // Primero verificar el rostro
            const faceVerification = await this.verifyFace(employeeId, photoBase64);
            
            if (!faceVerification.verified) {
                throw new Error(`Rostro no reconocido: ${faceVerification.message}`);
            }
            
            // ✅ VALIDACIÓN DE UMBRAL DE CONFIANZA: Solo permitir 90% o superior
            if (faceVerification.confidence < CONFIDENCE_THRESHOLD) {
                throw new Error(`Confianza insuficiente: ${(faceVerification.confidence * 100).toFixed(1)}%. Se requiere mínimo ${(CONFIDENCE_THRESHOLD * 100)}% para registrar asistencia.`);
            }
            
            console.log(`✅ Rostro verificado con confianza ${(faceVerification.confidence * 100).toFixed(1)}%, marcando asistencia...`);
            
            // Si el rostro es verificado y cumple el umbral, marcar asistencia
            const attendance = await this.markAttendance(employeeId, areaId, latitude, longitude, true);
            
            return {
                success: true,
                faceVerified: true,
                confidence: faceVerification.confidence,
                attendance: attendance,
                message: 'Asistencia marcada exitosamente con verificación facial'
            };
            
        } catch (error) {
            console.error('❌ Error en verificación facial y asistencia:', error);
            throw error;
        }
    },

    async verifyFace(employeeId, photoBase64) {
        try {
            const response = await api.post(`/employees/${employeeId}/verify_face/`, {
                photo: photoBase64
            }, {
                headers: this.getAuthHeaders()
            });
            
            // ✅ LOGGING MEJORADO: Mostrar información de confianza y umbral
            const result = response.data;
            if (result.verified && result.confidence !== undefined) {
                const confidencePercent = (result.confidence * 100).toFixed(1);
                const thresholdPercent = (CONFIDENCE_THRESHOLD * 100).toFixed(0);
                console.log(`🎯 Verificación facial: ${confidencePercent}% de confianza (Umbral requerido: ${thresholdPercent}%)`);
                
                if (result.confidence < CONFIDENCE_THRESHOLD) {
                    console.warn(`⚠️ ADVERTENCIA: Confianza ${confidencePercent}% está por debajo del umbral requerido de ${thresholdPercent}%`);
                }
            }
            
            return result;
        } catch (error) {
            console.error('Error verificando rostro:', error);
            throw error;
        }
    },

    async markAttendance(employeeId, areaId, latitude, longitude, faceVerified = false) {
        try {
            console.log('📝 MARK_ATTENDANCE - Enviando datos:');
            console.log(`   - Employee ID: ${employeeId}`);
            console.log(`   - Area ID: ${areaId}`);
            console.log(`   - Latitude: ${latitude}`);
            console.log(`   - Longitude: ${longitude}`);
            console.log(`   - Face verified: ${faceVerified}`);
            
            const requestData = {
                employee_id: employeeId,
                area_id: areaId,
                latitude: latitude,
                longitude: longitude,
                face_verified: faceVerified
            };
            
            console.log('📤 Request data completo:', requestData);
            
            const url = `/attendance/mark_attendance/`;
            console.log('🌐 URL completa:', url);
            console.log('🔑 Headers de autenticación:', this.getAuthHeaders());
            
            const response = await api.post(url, requestData, {
                headers: this.getAuthHeaders()
            });
            
            console.log('✅ Respuesta del backend:', response.data);
            return response.data;
        } catch (error) {
            console.error('❌ Error marcando asistencia:', error);
            if (error.response) {
                console.error('📡 Respuesta del servidor:', error.response.data);
                console.error('📊 Estado HTTP:', error.response.status);
                console.error('🌐 URL que falló:', error.config?.url);
            }
            throw error;
        }
    },

    async getEmployeeByCredentials(username, password) {
        try {
            // Hacer login para obtener el usuario usando el endpoint de empleados
            const loginResponse = await api.post(`/auth/employee_login/`, {
                username: username,
                password: password
            });
            
            const user = loginResponse.data.user;
            const token = loginResponse.data.token;
            
            console.log('🔍 Respuesta del login de empleado:', loginResponse.data);
            console.log('👤 Usuario obtenido:', user);
            console.log('🔑 Token obtenido:', token ? 'SÍ' : 'NO');
            
            // Establecer el token de autenticación para futuras peticiones
            if (token) {
                this.setAuthToken(token);
                // También guardar en localStorage para que el interceptor de api.js lo use
                localStorage.setItem('token', token);
                localStorage.setItem('refreshToken', loginResponse.data.refresh);
            }
            
            // Obtener la información del empleado usando el token
            const employeeResponse = await api.get(`/employees/`);
            const responseData = employeeResponse.data;
            
            console.log('🔍 Respuesta del endpoint /employees/:', employeeResponse);
            console.log('📊 responseData:', responseData);
            
            // Manejar respuesta paginada del backend
            let employees;
            if (responseData.results && Array.isArray(responseData.results)) {
                // Respuesta paginada: usar el campo 'results'
                employees = responseData.results;
                console.log('✅ Usando respuesta paginada, empleados encontrados:', employees.length);
            } else if (Array.isArray(responseData)) {
                // Respuesta directa como array
                employees = responseData;
                console.log('✅ Respuesta directa como array, empleados encontrados:', employees.length);
            } else {
                console.error('❌ Formato de respuesta no reconocido:', responseData);
                throw new Error('Formato de respuesta inválido del servidor');
            }
            
            // Buscar el empleado que corresponda al usuario
            const employee = employees.find(emp => emp.user.id === user.id);
            
            if (!employee) {
                throw new Error('Usuario no es un empleado registrado');
            }
            
            console.log('✅ Empleado encontrado:', employee);
            
            return {
                user: user,
                employee_id: employee.id,
                area_id: employee.area
            };
        } catch (error) {
            console.error('Error en login:', error);
            throw error;
        }
    },

    // Método para obtener todas las asistencias
    async getAll(filters = {}) {
        try {
            console.log('📊 Obteniendo todas las asistencias con filtros:', filters);
            console.log('🔑 Token disponible:', this.authToken ? 'SÍ' : 'NO');
            console.log('🔑 Token en localStorage:', localStorage.getItem('token') ? 'SÍ' : 'NO');
            
            let url = '/attendance/';
            const params = new URLSearchParams();
            
            // Aplicar filtros si están presentes
            if (filters.employee) {
                params.append('employee_id', filters.employee);
            }
            if (filters.area) {
                params.append('area_id', filters.area);
            }
            if (filters.status && filters.status !== 'all') {
                params.append('status', filters.status);
            }
            if (filters.dateFrom) {
                // Asegurar que la fecha esté en formato YYYY-MM-DD usando zona horaria local
                let dateFrom = filters.dateFrom;
                if (dateFrom instanceof Date) {
                    // Usar zona horaria local para evitar problemas de UTC
                    const year = dateFrom.getFullYear();
                    const month = String(dateFrom.getMonth() + 1).padStart(2, '0');
                    const day = String(dateFrom.getDate()).padStart(2, '0');
                    dateFrom = `${year}-${month}-${day}`;
                } else if (typeof dateFrom === 'string' && dateFrom.includes('T')) {
                    dateFrom = dateFrom.split('T')[0];
                }
                params.append('date_from', dateFrom);
                console.log('📅 Fecha desde enviada al backend:', dateFrom);
            }
            if (filters.dateTo) {
                // Asegurar que la fecha esté en formato YYYY-MM-DD usando zona horaria local
                let dateTo = filters.dateTo;
                if (dateTo instanceof Date) {
                    // Usar zona horaria local para evitar problemas de UTC
                    const year = dateTo.getFullYear();
                    const month = String(dateTo.getMonth() + 1).padStart(2, '0');
                    const day = String(dateTo.getDate()).padStart(2, '0');
                    dateTo = `${year}-${month}-${day}`;
                } else if (typeof dateTo === 'string' && dateTo.includes('T')) {
                    dateTo = dateTo.split('T')[0];
                }
                params.append('date_to', dateTo);
                console.log('📅 Fecha hasta enviada al backend:', dateTo);
            }
            
            if (params.toString()) {
                url += '?' + params.toString();
            }
            
            console.log('🌐 URL de consulta:', url);
            console.log('🔑 Headers de autenticación:', this.getAuthHeaders());
            
            // Verificar que el token esté disponible antes de hacer la petición
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('No hay token de autenticación disponible');
            }
            
            console.log('🔑 Token que se enviará:', token.substring(0, 30) + '...');
            
            // Verificar que la URL base esté configurada correctamente
            console.log('🌐 URL base de la API:', api.defaults.baseURL);
            console.log('🌐 URL completa que se enviará:', api.defaults.baseURL + url);
            
            // Comparar con la petición exitosa
            console.log('🔍 COMPARACIÓN CON PETICIÓN EXITOSA:');
            console.log('   - URL del proxy (exitosa): /app/attendance/');
            console.log('   - URL del servicio: ' + api.defaults.baseURL + url);
            console.log('   - ¿Son iguales?', '/app/attendance/' === (api.defaults.baseURL + url));
            
            const response = await api.get(url, {
                headers: this.getAuthHeaders()
            });
            
            console.log('✅ Respuesta del backend:', response.data);
            console.log('📊 Estado HTTP:', response.status);
            console.log('📊 Headers de respuesta:', response.headers);
            
            // Manejar respuesta paginada del backend
            if (response.data.results && Array.isArray(response.data.results)) {
                console.log('✅ Respuesta paginada, usando results');
                return response.data.results;
            } else if (Array.isArray(response.data)) {
                console.log('✅ Respuesta directa como array');
                return response.data;
            } else {
                console.error('❌ Formato de respuesta no reconocido:', response.data);
                return [];
            }
        } catch (error) {
            console.error('❌ Error obteniendo asistencias:', error);
            console.error('📡 Detalles del error:', {
                message: error.message,
                status: error.response?.status,
                statusText: error.response?.statusText,
                data: error.response?.data,
                config: error.config,
                url: error.config?.url,
                method: error.config?.method
            });
            throw error;
        }
    },

    // Método para obtener asistencias por rango de fechas
    async getByDateRange(startDate, endDate, additionalFilters = {}) {
        try {
            console.log('📅 Obteniendo asistencias por rango de fechas:', { startDate, endDate, additionalFilters });
            
            const filters = {
                dateFrom: startDate,
                dateTo: endDate,
                ...additionalFilters
            };
            
            return await this.getAll(filters);
        } catch (error) {
            console.error('❌ Error obteniendo asistencias por rango de fechas:', error);
            throw error;
        }
    },

    // ===== MÉTODOS PARA EMPLEADOS =====
    
    // Obtener información del empleado autenticado
    async getEmployeeInfo() {
        try {
            console.log('👤 Obteniendo información del empleado...');
            const response = await api.get('/dashboard/employee_info/');
            console.log('✅ Información del empleado obtenida:', response.data);
            return response.data;
        } catch (error) {
            console.error('❌ Error obteniendo información del empleado:', error);
            throw error;
        }
    },

    // Obtener estadísticas del empleado autenticado
    async getEmployeeStats() {
        try {
            console.log('📊 Obteniendo estadísticas del empleado...');
            const response = await api.get('/dashboard/employee_stats/');
            console.log('✅ Estadísticas del empleado obtenidas:', response.data);
            return response.data;
        } catch (error) {
            console.error('❌ Error obteniendo estadísticas del empleado:', error);
            throw error;
        }
    },

    // Obtener historial de asistencias del empleado autenticado
    async getEmployeeAttendances() {
        try {
            console.log('📋 Obteniendo historial de asistencias del empleado...');
            const response = await api.get('/dashboard/employee_attendances/');
            console.log('✅ Historial de asistencias obtenido:', response.data);
            return response.data.attendances || [];
        } catch (error) {
            console.error('❌ Error obteniendo historial de asistencias:', error);
            throw error;
        }
    }
};
