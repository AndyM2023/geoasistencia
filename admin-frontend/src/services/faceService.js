import api from './api';

export const faceService = {
    async registerFace(employeeId, photosBase64) {
        try {
            console.log('Enviando fotos al backend Django:', {
                employeeId,
                photosCount: photosBase64.length
            });

            const response = await api.post(`/employees/${employeeId}/register_face/`, {
                photos_base64: photosBase64
            }, {
                headers: {
                    'Content-Type': 'application/json'
                },
                timeout: 30000 // 30 segundos para procesar múltiples fotos
            });

            console.log('Respuesta del backend Django:', response.data);

            if (!response.data.success) {
                throw new Error(response.data.message || 'Error desconocido en el servidor');
            }

            return response.data;
        } catch (error) {
            console.error('Error detallado en el registro facial:', {
                message: error.message,
                response: error.response?.data,
                status: error.response?.status
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
