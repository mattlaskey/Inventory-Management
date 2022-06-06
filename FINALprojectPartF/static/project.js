
var app = new Vue({
  el: "#app",

  //------- data --------
  data: {
    serviceURL: "https://cs3103.cs.unb.ca:37426",
    authenticated: false,
    loggedIn: null,
    userData: null,
    presentData: null,
    input: {
      username: "",
      password: ""
    },
    user:{
      userName: "",
      userid:   ""
    },
    present:{
      presentName: "",
      presentId: "",
      presentUserId: "",
      presentPrice: "",
      presentDesc: ""
    },
    presentAdd:{
      presentName: "",
      presentDesc: "",
      presentPrice: "",
      presentId: ""
    },
    presentUpdate:{
      presentNameUp: "",
      presentDescUp: "",
      presentPriceUp: "",
      presentIdUp: ""
    },
    presentDelete:{
      presentId: ""
    },
    userDelete:{
      userId: ""
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
      axios
      .delete(this.serviceURL+"/signin")
      .then(response => {
          location.reload();
      })
      .catch(e => {
        console.log(e);
      });
    },

    getUsers(){
      axios
      .get(this.serviceURL+"/users")
      .then(response => {
          this.userData = response.data.users
      });
    },
    getPresents(){
    axios
      .get(this.serviceURL+"/presents")
      .then(response => {
          this.presentData = response.data.presents
      });
    },
    getPresentById(){
    axios
      .get(this.serviceURL+"/presents/"+this.present.presentId)
      .then(response => {
          this.presentData = response.data.presents
      });
    },
    getPresentByName(){
    axios
      .get(this.serviceURL+"/presents/"+this.present.presentName)
      .then(response => {
          this.presentData = response.data.presents
      });
    },
    getPresentByPrice(){
    axios
      .get(this.serviceURL+"/present/"+this.present.presentPrice)
      .then(response => {
          this.presentData = response.data.presents
      });
    },
    getPresentsByUser(){
    axios
      .get(this.serviceURL+"/present/"+this.present.presentUserId)
      .then(response => {
          this.presentData = response.data.presents
      });
    },
    addPresent(){
    axios
      .post(this.serviceURL+"/present/"+this.loggedIn, {
            "presentName": this.presentAdd.presentName,
	    "presentDesc": this.presentAdd.presentDesc,
	    "presentPrice": this.presentAdd.presentPrice
	})
      .then(response => {
          this.presentData = response.data.presents
      });
    },
    updatePresent(){
    axios
      .post(this.serviceURL+"/presents/"+this.presentUpdate.presentIdUp, {
            "presentName": this.presentUpdate.presentNameUp,
	    "presentDesc": this.presentUpdate.presentDescUp,
	    "presentPrice": this.presentUpdate.presentPriceUp
	})
      .then(response => {
          this.presentData = response.data.presents
      });
    },
    removePresent(){
    axios
      .delete(this.serviceURL+"/presents/"+this.presentDelete.presentId)
      .then(response => {
          this.presentData = response.data.presents
      });
    },
    removeUser(){
    axios
      .delete(this.serviceURL+"/users/"+this.userDelete.userId)
      .then(response => {
          this.presentData = response.data.presents
      });
    },

    getUserById() {
    axios
      .get(this.serviceURL+"/users/"+this.user.userid)
      .then(response => {
          this.userData = response.data.user
      })
      .catch(e => {
        alert("Unable to load the users data");
        console.log(e);
      });
    },
    getUserByName() {
    axios
      .get(this.serviceURL+"/users/"+this.user.userName)
      .then(response => {
          this.userData = response.data.user
      })
      .catch(e => {
        alert("Unable to load the users data");
        console.log(e);
      });
    }

  }
  //------- END methods --------

});
