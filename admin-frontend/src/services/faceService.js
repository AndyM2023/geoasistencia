import api from './api';

export const faceService = {
    async registerFace(employeeId, photosBase64) {
        try {
            console.log('🔍 Datos enviados al backend:');
            console.log('   - Employee ID:', employeeId);
            console.log('   - Photos count:', photosBase64.length);
            console.log('   - First photo sample:', photosBase64[0] ? photosBase64[0].substring(0, 100) + '...' : 'undefined');
            console.log('   - Photos type:', typeof photosBase64);
            console.log('   - Is array:', Array.isArray(photosBase64));

            const requestData = {
                photos_base64: photosBase64
            };
            
            console.log('📤 Request data completo:', requestData);

            // ✅ OPTIMIZACIÓN: Timeout dinámico basado en número de fotos
            const photoCount = photosBase64.length;
            let timeoutMs;
            
            if (photoCount <= 20) {
                timeoutMs = 15000; // 15 segundos para ≤20 fotos (MODO ULTRA-RÁPIDO)
                console.log(`⚡ MODO ULTRA-RÁPIDO: ${photoCount} fotos - Timeout: 15 segundos`);
            } else if (photoCount <= 50) {
                timeoutMs = 30000; // 30 segundos para 21-50 fotos
                console.log(`🚀 MODO OPTIMIZADO: ${photoCount} fotos - Timeout: 30 segundos`);
            } else {
                timeoutMs = 60000; // 1 minuto para >50 fotos
                console.log(`📦 MODO LOTE: ${photoCount} fotos - Timeout: 1 minuto`);
            }

            const response = await api.post(`/employees/${employeeId}/register_face/`, requestData, {
                headers: {
                    'Content-Type': 'application/json'
                },
                timeout: timeoutMs
            });

            console.log('✅ Respuesta del backend Django:', response.data);

            if (!response.data.success) {
                throw new Error(response.data.message || 'Error desconocido en el servidor');
            }

            return response.data;
        } catch (error) {
            console.error('❌ Error detallado en el registro facial:', {
                message: error.message,
                response: error.response?.data,
                status: error.response?.status,
                statusText: error.response?.statusText
            });

            if (error.response) {
                throw new Error(error.response.data.message || 'Error en el servidor');
            } else if (error.request) {
                throw new Error('No se pudo conectar con el servidor');
            }
            throw new Error('Error de conexión: ' + error.message);
        }
    },

    async getFaceStatus(employeeId) {
        try {
            const response = await api.get(`/employees/${employeeId}/face_status/`);
            console.log('🔍 getFaceStatus - response completa:', response);
            console.log('🔍 getFaceStatus - response.data:', response.data);
            console.log('🔍 getFaceStatus - response.data type:', typeof response.data);
            console.log('🔍 getFaceStatus - response.data keys:', Object.keys(response.data || {}));
            return response.data;
        } catch (error) {
            console.error('Error obteniendo estado facial:', error);
            throw error;
        }
    },

    async verifyFace(employeeId, photoBase64) {
        try {
            const response = await api.post(`/employees/${employeeId}/verify_face/`, {
                photo_base64: photoBase64
            });
            return response.data;
        } catch (error) {
            console.error('Error en la verificación facial:', error);
            throw error;
        }
    },


};
