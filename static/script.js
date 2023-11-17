$(document).ready(function () {
  // Render text box if user wants to input a specific query
  $("input[name='action']").click(function () {
    var radioValue = $("input[name='action']:checked").val();
    if (radioValue == "query") {
      document.getElementById("query_div").style = "display: block;";
    } else {
      document.getElementById("query_div").style = "display: none;";
    }
  });
});

function formSubmit() {
  var radioValue = $("input[name='action']:checked").val();
  var queryValue = document.getElementById("specific_query").value;
  // Make sure user inputs a query if "query" option is selected
  if (radioValue == "query" && queryValue == "") {
    alert("Please type a query to execute on the database");
    event.preventDefault();
  } else {
    document.getElementById("helper").innerHTML =
      "Note: Some commands may take a while to execute";
  }
}
