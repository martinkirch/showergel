import axios from 'axios'

if (process.env.NODE_ENV === 'development') {
  console.log("VUE_APP_BACKEND_URL: "+process.env.VUE_APP_BACKEND_URL)
  if (process.env.VUE_APP_BACKEND_URL) {
    axios.defaults.baseURL = process.env.VUE_APP_BACKEND_URL
  } else {
    axios.defaults.baseURL = 'http://localhost:2345'
  }
}

export default axios.create({
  headers: {
    'Content-type': 'application/json'
  }
})
