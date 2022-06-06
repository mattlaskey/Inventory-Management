
var app = new Vue({
  el: "#app",

  //------- data --------
  data: {
    serviceURL: "https://cs3103.cs.unb.ca:35662",
    authenticated: false,
    loggedIn: null,
    input: {
      username: "",
      password: ""
    }
  },
  methods: {
    login() {
      if (this.input.username != "" && this.input.password != "") {
        axios
        .post(this.serviceURL+"/signin", {
            "username": this.input.username,
            "password": this.input.password
        })
        .then(response => {
            if (response.data.status == "success") {
              this.authenticated = true;
              this.loggedIn = response.data.user_id;
            }
        })
        .catch(e => {
            alert("The username or password was incorrect, try again");
            this.input.password = "";
            console.log(e);
        });
      } else {
        alert("A username and password must be present");
      }
    },


    logout() {
      alert("No magic on the server yet. You'll have to write the logout code there.");
      axios
      .delete(this.serviceURL+"/signin")
      .then(response => {
          location.reload();
      })
      .catch(e => {
        console.log(e);
      });
    },

    fetchSchools() {
      alert("This feature not available until schoolsV2.")
    }


  }
  //------- END methods --------

});
