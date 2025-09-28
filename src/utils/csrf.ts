// Función para obtener el token CSRF de las cookies
export const getCSRFToken = (): string | null => {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

// Función para hacer fetch con CSRF token
export const fetchWithCSRF = async (url: string, options: RequestInit = {}) => {
  const csrfToken = getCSRFToken();
  
  const headers = {
    ...options.headers,
    ...(csrfToken && { 'X-CSRFToken': csrfToken }),
  };

  return fetch(url, {
    ...options,
    headers,
    credentials: 'include',
  });
};