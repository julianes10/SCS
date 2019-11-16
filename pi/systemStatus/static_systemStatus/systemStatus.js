function reload(){
  location.reload(true);
}

function reloadDumpStatus(element){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
             //alert(this.responseText);
             var data=JSON.parse(this.responseText)
             document.getElementById("dumpbox"+element).innerHTML = data.dump;
         }
    };
    xhttp.open("GET", "/api/v1.0/systemStatus/"+element, true);
    xhttp.send();
}

