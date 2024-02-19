import axios from 'axios';

const instance = axios.create({
  baseURL: "http://jellyfin.home:5000",
});

// You can add interceptors for requests or responses here
// instance.interceptors.request.use(request => { ... });

export default instance;

