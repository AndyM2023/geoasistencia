import axios from 'axios';

const BACKEND_URL = 'http://localhost:8000/api';

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
            
            console.log('✅ Rostro verificado, marcando asistencia...');
            
            // Si el rostro es verificado, marcar asistencia
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
            const response = await axios.post(`${BACKEND_URL}/employees/${employeeId}/verify_face/`, {
                photo: photoBase64
            }, {
                headers: this.getAuthHeaders()
            });
            
            return response.data;
        } catch (error) {
            console.error('Error verificando rostro:', error);
            throw error;
        }
    },

    async markAttendance(employeeId, areaId, latitude, longitude, faceVerified = false) {
        try {
            const response = await axios.post(`${BACKEND_URL}/attendance/mark_attendance/`, {
                employee_id: employeeId,
                area_id: areaId,
                latitude: latitude,
                longitude: longitude,
                face_verified: faceVerified
            }, {
                headers: this.getAuthHeaders()
            });
            
            return response.data;
        } catch (error) {
            console.error('Error marcando asistencia:', error);
            throw error;
        }
    },

    async getEmployeeByCredentials(username, password) {
        try {
            // Hacer login para obtener el usuario
            const loginResponse = await axios.post(`${BACKEND_URL}/auth/login/`, {
                username: username,
                password: password
            });
            
            const user = loginResponse.data.user;
            
            console.log('🔍 Respuesta del login:', loginResponse.data);
            console.log('👤 Usuario obtenido:', user);
            
            // Obtener la información del empleado
            const employeeResponse = await axios.get(`${BACKEND_URL}/employees/`);
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
            
            // Establecer el token de autenticación para futuras peticiones
            if (loginResponse.data.token) {
                this.setAuthToken(loginResponse.data.token);
            }
            
            return {
                user: user,
                employee_id: employee.id,
                area_id: employee.area
            };
        } catch (error) {
            console.error('Error en login:', error);
            throw error;
        }
    }
};
