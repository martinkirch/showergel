import axios from 'axios'

if (import.meta.env.DEV) {
  console.log("VITE_BACKEND_URL: "+import.meta.env.VITE_BACKEND_URL)
  if (import.meta.env.VITE_BACKEND_URL) {
    axios.defaults.baseURL = import.meta.env.VITE_BACKEND_URL
  } else {
    axios.defaults.baseURL = 'http://localhost:2345'
  }
}

export default axios.create({
  headers: {
    'Content-type': 'application/json'
  }
})
