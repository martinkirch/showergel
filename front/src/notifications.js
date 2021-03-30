export default {
  error_handler: function (error) {
    console.log(error);
    if (error.response && error.response.data.message) {
      console.log(error.response.data.message)
    }
  }
}
