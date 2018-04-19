function auth(callback) { 
  let options = { 
    type    : 'GET', 
    url     : window.location.pathname, 
    headers : {"Authorization": "Bearer "+getCookie('access_token')}, 
    success : function(data,status,hxr) { 
      let url = hxr.responseURL; 
      if(url.split('/')[4] == 'login') window.location.replace(url); 
      else callback(JSON.parse(data)); 
    }, 
  }; 
  $.ajax(options); 
} 
 
function getCookie(name) { 
  var value = "; " + document.cookie; 
  var parts = value.split("; " + name + "="); 
  if (parts.length == 2) return parts.pop().split(";").shift(); 
} 
 
function deleteCookie(name) { 
    document.cookie = name + '=; path=/;expires=Thu, 01 Jan 1970 00:00:01 GMT;'; 
}; 
 
function login(e) { 
  e.preventDefault(); 
  let data = { 
    csrfmiddlewaretoken : $('[name=csrfmiddlewaretoken]').val(), 
    username            : $('#id_username').val(), 
    password            : $('#id_password').val(), 
  }; 
  $.post(user, data, function(data){ 
    document.cookie = 'access_token='+JSON.parse(data).access_token+'; path=/'; 
    window.location.replace(getNext()); 
  }); 
} 
 
function getNext(){ 
       var query = window.location.search.substring(1); 
       var vars = query.split("&"); 
       for (var i=0;i<vars.length;i++) { 
               var pair = vars[i].split("="); 
               if(pair[0] == 'next'){return pair[1];} 
       } 
       return(profile); 
} 
 
$(document).on('click', '#submit_login', login); 

//call auth to get data for authenticated user 
//auth();