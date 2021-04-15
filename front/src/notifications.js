export default {
  error_handler: function (error) {
    if (error.response && error.response.data.message) {
      this.error(error.response.data.message);
    } else {
      console.log(error);
    }
  },
  error: function (message) {
    alert(message);
  },
  success_handler: function (message) {
    return function() {
      alert(message);
    };
  },
  success: function (message) {
    alert(message);
  },
}
