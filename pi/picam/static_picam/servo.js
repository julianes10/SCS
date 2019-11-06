//-------------------------------------------------------------------------
function ajax_set_position(operation,servo,data){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
             //alert(this.responseText);
             document.getElementById("position").innerHTML = this.responseText;
         }
    };

    json='{"' + servo + '":{' + '"' + operation +'":' + data + '}}' 
    
    xhttp.open("POST", "/api/v1.0/picam/position", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send(json);
}

function ajax_delta_position(servo,data){
  ajax_set_position("delta",servo,data)
}
function ajax_abs_position(servo,data){
  ajax_set_position("abs",servo,data)
}

function ajax_set_full_position(p,t){
  ajax_abs_position("pan",p)
  ajax_abs_position("tilt",t)
}

