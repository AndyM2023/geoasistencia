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

            const response = await api.post(`/employees/${employeeId}/register_face/`, requestData, {
                headers: {
                    'Content-Type': 'application/json'
                },
                timeout: 180000 // 3 minutos para procesar 50 fotos con Facenet-512
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
    }
};
