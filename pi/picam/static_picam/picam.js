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

//-------------------------------------------------------------------------
function ajax_auto_update_position(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
             //alert(this.responseText);
             var data=JSON.parse(this.responseText)
             document.getElementById("panvalue").innerHTML = data.data.pan;
             document.getElementById("tiltvalue").innerHTML = data.data.tilt;
         }
    };
 

      xhttp.open("GET", "/api/v1.0/picam/position", true);
      xhttp.send();
      setTimeout(ajax_auto_update_position,500);

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

function ajax_set_live(on){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
         if (this.readyState == 4)  {// && this.status == 200) {
             //alert(this.responseText);
             //document.getElementById("position").innerHTML = this.responseText;
             reload();
         }
    };

    json=JSON.stringify({ live : new Boolean(on)}) 

    
    xhttp.open("POST", "/api/v1.0/picam/live", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send(json);
}

function reload(){
  location.reload(true);
}

function reloadStatus(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
             //alert(this.responseText);
             document.getElementById("statusPicam").innerHTML = this.responseText;
         }
    };
    xhttp.open("GET", "/api/v1.0/picam/status", true);
    xhttp.send();
}

//-------------------------------------------
function ajax_request_simple_track(bk,pi,pe,ti,te,d,r,nt){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
             //alert(this.responseText);
             document.getElementById("position").innerHTML = this.responseText;
         }
    };

    json=JSON.stringify({ backPosition : new Boolean(bk), data : [{backPosition : new Boolean(bk), pan: { ini: new Number(pi), end: new Number(pe)}, tilt: { ini: new Number(ti), end: new Number(te)},duration : new Number(d) , "reverse": new Boolean(r), ntimes : new Number(nt) }]}) 

   
    xhttp.open("POST", "/api/v1.0/picam/track", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send(json);
}

//-------------------------------------------
function ajax_request_track_square(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
             //alert(this.responseText);
             document.getElementById("position").innerHTML = this.responseText;
         }
    };
    json=JSON.stringify({ backPosition : true, data : [
      {backPosition : false, pan: { ini: 10, end: 170 }, tilt: { ini: 10, end: 10},duration : 4 , "reverse": false, ntimes : 1},
      {backPosition : false, pan: { ini: 170, end: 170 }, tilt: { ini: 10, end: 80},duration : 4 , "reverse": false, ntimes : 1},
      {backPosition : false, pan: { ini: 170, end: 10 }, tilt: { ini: 90, end: 90},duration : 4 , "reverse": false, ntimes : 1},
      {backPosition : false, pan: { ini: 10, end: 10 }, tilt: { ini: 80, end: 10},duration : 4 , "reverse": false, ntimes : 1 }
    ]}) 
    
     
    xhttp.open("POST", "/api/v1.0/picam/track", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send(json);
}
//-------------------------------------------
function ajax_request_stop_track(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
             //alert(this.responseText);
             document.getElementById("position").innerHTML = this.responseText;
         }
    };

    json=JSON.stringify({ data : []})
   
    xhttp.open("POST", "/api/v1.0/picam/track", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send(json);
}

//-------------------------------------------
function ajax_request_track_saw(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
             //alert(this.responseText);
             document.getElementById("position").innerHTML = this.responseText;
         }
    };
    json=JSON.stringify({ backPosition : true, data : [
      {backPosition : false, pan: { ini: 15, end: 40 }, tilt: { ini: 10, end: 80},duration : 1 , "reverse": false, ntimes : 1},
      {backPosition : false, pan: { ini: 40, end: 60 }, tilt: { ini: 80, end: 10},duration : 1 , "reverse": false, ntimes : 1},
      {backPosition : false, pan: { ini: 60, end: 80 }, tilt: { ini: 10, end: 80},duration : 1 , "reverse": false, ntimes : 1},
      {backPosition : false, pan: { ini: 80, end: 100 }, tilt: { ini: 80, end: 10},duration : 1 , "reverse": false, ntimes : 1 },
      {backPosition : false, pan: { ini: 100, end: 120 }, tilt: { ini: 10, end: 80},duration : 1 , "reverse": false, ntimes : 1},
      {backPosition : false, pan: { ini: 120, end: 140 }, tilt: { ini: 80, end: 10},duration : 1 , "reverse": false, ntimes : 1},
      {backPosition : false, pan: { ini: 140, end: 165 }, tilt: { ini: 10, end: 80},duration : 1 , "reverse": false, ntimes : 1}

    ]}) 
    
     
    xhttp.open("POST", "/api/v1.0/picam/track", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send(json);
}



