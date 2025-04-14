import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'https://soldega-prod.rj.r.appspot.com/api/',
  timeout: 20000, // 20 segundos de timeout
  headers: {
    'Content-Type': 'application/json',
    accept: 'application/json',
  }
});

axiosInstance.interceptors.request.use(
  config => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token;
    }
    return config;
  },
  error => Promise.reject(error)
);

export default axiosInstance;
