/**
 * Utilidades para el manejo de nombres de empleados
 */

/**
 * Capitaliza la primera letra de cada palabra en un nombre
 * @param {string} name - El nombre a capitalizar
 * @returns {string} - El nombre con la primera letra de cada palabra en mayúscula
 */
export function capitalizeName(name) {
  if (!name || typeof name !== 'string') return name;
  
  return name
    .toLowerCase()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Capitaliza el nombre completo de un empleado (first_name + last_name)
 * @param {string} firstName - Primer nombre
 * @param {string} lastName - Apellido
 * @returns {string} - Nombre completo capitalizado
 */
export function capitalizeFullName(firstName, lastName) {
  const first = capitalizeName(firstName || '');
  const last = capitalizeName(lastName || '');
  
  if (first && last) {
    return `${first} ${last}`;
  } else if (first) {
    return first;
  } else if (last) {
    return last;
  }
  
  return '';
}

/**
 * Capitaliza un nombre completo que ya viene como string
 * @param {string} fullName - Nombre completo como string
 * @returns {string} - Nombre completo capitalizado
 */
export function capitalizeFullNameString(fullName) {
  if (!fullName || typeof fullName !== 'string') return fullName;
  
  return capitalizeName(fullName);
}
