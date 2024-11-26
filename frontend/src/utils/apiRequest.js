const apiRequest = async (endpoint, method = 'GET', body = null, headers = {}) => {
  try {
    const options = {
      method,
      credentials: "include",
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
    };

    if (body && method !== 'GET') {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}${endpoint}`, options);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        `Error: ${response.status} - ${response.statusText}. ${errorData.message || 'Something went wrong.'}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error('API Request Failed:', error.message);
    throw error;
  }
};

export default apiRequest;
