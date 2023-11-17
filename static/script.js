$(document).ready(function () {
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
  if (radioValue == undefined) {
    alert("Please select a value");
    event.preventDefault();
  } else if (radioValue == "query" && queryValue == "") {
    alert("Please type a query to execute on the database");
    event.preventDefault();
  }
  document.getElementById("helper").innerHTML =
    "Note: Some commands may take a while to execute";
}
