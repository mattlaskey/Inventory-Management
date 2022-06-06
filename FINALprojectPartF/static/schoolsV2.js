// register modal component
 Vue.component("modal", {
   template: "#modal-template"
 });

var app = new Vue({
  el: "#app",

  //------- data --------
  data: {
    serviceURL: "https://cs3103.cs.unb.ca:35662",
    authenticated: false,
    schoolsData: null,
    loggedIn: null,
    input: {
      username: "",
      password: ""
    },
    selectedSchool: {
      language: "",
      level: "",
      name: "",
      province: "",
      schoolId: ""
    },
    language: {
      english:"En",
      french:"Fr"
    }

  },
  //------- lifecyle hooks --------
  /*mounted: function() {
    axios
    .get(this.serviceURL+"/signin")
    .then(response => {
      if (response.data.status == "success") {
        this.authenticated = true;
        this.loggedIn = response.data.user_id;
      }
    })
    .catch(error => {
        this.authenticated = false;
        console.log(error);
    });
  },*/
  //------- methods --------
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
      axios
      .get(this.serviceURL+"/schools")
      .then(response => {
          this.schoolsData = response.data.schools;
      });
    },


    deleteSchool(schoolId) {
      alert("This feature not available until YOUR version of schools.")
    },


    selectSchool(schoolId) {
      alert("This feature not available until schoolsV3.")
    },


    updateSchool(updatedSchool) {
      alert("This feature not available until YOUR version of schools.")
      // TODO: use axios.update to send the updated record to the service
    }

  }
  //------- END methods --------

});
