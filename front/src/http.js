import axios from 'axios'

if (process.env.NODE_ENV === 'development') {
  axios.defaults.baseURL = 'http://localhost:2345'
}

export default axios.create({
  headers: {
    'Content-type': 'application/json'
  }
})
