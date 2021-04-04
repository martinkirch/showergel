export default {
  error_handler: function (error) {
    if (error.response && error.response.data.message) {
      console.log(error.response.data.message);
    } else {
      console.log(error);
    }
  }
}
