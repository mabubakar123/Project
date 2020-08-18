
const inputs = document.querySelectorAll('.sliders input');
let myform=document.getElementById('myform');
let targetimage=document.getElementById('targetimage'); 
let inputrange=document.querySelectorAll('input,select');
let cropinput=document.querySelectorAll('#x,#y,#c-width,#c-height');
let imgarea=document.querySelectorAll('.img-area'); 
let imgid=document.getElementById('imageid').value;
let rbs = document.querySelectorAll('input[name="flip"]');


setTimeout(() => {

    editimage();
    
 }, 1000);





inputrange.forEach(input => input.addEventListener('click', editimage));
inputrange.forEach(input => input.addEventListener('input', editimage));

function editimage(){
      
    let gs= document.getElementById('gs');
    let blur= document.getElementById('blur');
    let brightness=document.getElementById('brightness');
    let contrast=document.getElementById('contrast');
 
  
    let huerotate= document.getElementById('hue-rotate');
    let invert= document.getElementById('invert');
    const canvas = document.getElementById('canvas');
  
    
    
    let movex=document.getElementById('text-translate-x').value;
    let movey=document.getElementById('text-translate-y').value;
    let textcontent = document.getElementById('text-content').value;
    let textsize = document.getElementById('text-size').value;
    let fontstyle= document.getElementById('fontstyle').value;
    let textcolor= document.getElementById('text-color').value;
   

   
   
    let width=document.getElementById('width').value;
    let height=document.getElementById('height').value;
   
    let gsval=gs.value;
    let blurval=blur.value;
    let brightnessval=brightness.value;
    let contrastval=contrast.value;
 
    
    let huerotateval=huerotate.value;
    let invertval=invert.value;
  
   


    targetimage.style.filter = 'grayscale('+gsval+'%) blur('+blurval+
    'px) brightness('+brightnessval+'%) contrast('+contrastval+
    '%)   hue-rotate('+huerotateval+'deg)  invert('+invertval+'%)';
   

    if ( width>15 && height>15){
    targetimage.width=width;
    targetimage.height=height;
    }

if (width>15&&height>15){
    canvas.style.width=width+'px';
    canvas.style.height=height+'px';
    
}

else{

   canvas.width=targetimage.width;
   canvas.height=targetimage.height;
}
 
 const ctx = canvas.getContext('2d');

 ctx.font = textsize+'px '+fontstyle;
 ctx.filter = targetimage.style.filter;
 
 canvas.style.webkitTransform=targetimage.style.webkitTransform;
  ctx.drawImage(targetimage, 0, 0);
  ctx.fillStyle=textcolor;
  ctx.fillText(textcontent, movex,movey);
    
}

document.getElementById('text-translate-x').max=targetimage.width-40;
document.getElementById('text-translate-y').max=targetimage.height;


function reset(){
    let slider= document.getElementById('slider-form');
         slider.reset();

         


         setTimeout(() => {
            
            editimage();
            
         }, 1000);
         
}



function togglesubmenu(id) {
        var e = document.getElementById(id);
        if (e.style.display == 'block' || e.style.display=='') {
        e.style.display = 'none';}
        else{
        e.style.display = 'block';}
        
}




 function cancel(){
    
    document.getElementById('c-width').value="";
    document.getElementById('c-height').value="";
    document.getElementById('x').value="";
    document.getElementById('y').value="";
    
 }





function save(){
   
  const canvas = document.getElementById('canvas');


  var dataURL = canvas.toDataURL("image/png");

 
  jQuery.noConflict();


  jQuery('#successAlert').text("Image saving. Wait!").show();
  jQuery('#errorAlert').hide();

jQuery.ajax({
    data : {
    
    imageBase64:dataURL
},
    type : 'POST',
    url : '/post/'+imgid+'/edit'
  
        
}).done(function(data){
   if (data.error){
   jQuery('#errorAlert').text("Something went wrong").show();
        jQuery('#successAlert').hide();
   }
   else{
    jQuery('#successAlert').text(data.success).show();
    jQuery('#errorAlert').hide();
    setTimeout(() => {
        window.location.href="/home"
    }, 1000);
    
    //window.location.href="/post/"+imgid+"/edit/crop";
  
}
})
event.preventDefault();
}



cropinput.forEach(input => input.addEventListener('input', croprectangle));
function croprectangle(){

    width = jQuery('#c-width').val();
    height = jQuery('#c-height').val();
    x= jQuery('#x').val();
    y= jQuery('#y').val();
    color=jQuery('#crop-color').val();

        var c = document.getElementById("canvas");
        var ctx = c.getContext("2d");
        ctx.lineWidth = "2";
        ctx.strokeStyle = color;
        ctx.beginPath();
        ctx.rect(x, y, width, height);
        ctx.stroke();
    }








jQuery.noConflict();
jQuery(document).ready(function() {
 
	jQuery('#cropbtn').on('click', function(event) {
        
       
        const canvas = document.getElementById('canvas');
        var context = canvas.getContext('2d');
        
        var dataURL = canvas.toDataURL("image/png");

    jQuery.ajax({
        data : {
        width : jQuery('#c-width').val(),
        height : jQuery('#c-height').val(),
        x: jQuery('#x').val(),
        y: jQuery('#y').val(),
        imagee:dataURL
    


        },
        type : 'POST',
        dataType: "json",
        url : '/post/'+imgid+'/edit/crop'
      
            
   }).done(function(data){
       if (data.error){
       jQuery('#errorAlert').text(data.error).show();
            jQuery('#successAlert').hide();
       }
       else{
        jQuery('#successAlert').text(data.success).show();
        jQuery('#errorAlert').hide();
        
        window.location.href="/post/"+imgid+"/edit/crop";
      
    }
    })
    event.preventDefault();
    });
      
   
    })

   
 

   
  





jQuery('#resizebtn').on('click', function(event) {
      
    
 
    const canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');
    
    var dataURL = canvas.toDataURL("image/png");

    jQuery.ajax({
        data : {
            width : jQuery('#width').val(),
            height : jQuery('#height').val(),
           
            imageBase64:dataURL
           
           
            

        },
        type : 'POST',
        url : '/post/'+imgid+'/edit/resize'
    })
    .done(function(data) {
    if (data.error){
    jQuery('#errorAlert').text(data.error).show();
         jQuery('#successAlert').hide();
    }
    else{
        window.location.href="/post/"+imgid+"/edit/resize";
    }

    });

    event.preventDefault();
  
});



rbs.forEach(input => input.addEventListener('input', flip));


      
   
function flip(){
 
    const canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');
    
    var dataURL = canvas.toDataURL("image/png");

    jQuery.ajax({
        data : {
            option : jQuery("input[name='flip']:checked").val(),
            rotate:  jQuery("#rotate").val(),
          
           
            imageBase64:dataURL
           
           
            

        },
        type : 'POST',
        url : '/post/'+imgid+'/edit/transform'
    })
    .done(function(data) {
    if (data.error){
    jQuery('#errorAlert').text(data.error).show();
         jQuery('#successAlert').hide();
    }
    else{
        window.location.href="/post/"+imgid+"/edit/transform";
    }
  event.preventDefault();
    });
}


document.getElementById('rotate').addEventListener('click',rotate);
function rotate(){
    const canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');
    
    var dataURL = canvas.toDataURL("image/png");

    jQuery.ajax({
        data : {
            
           
          
           
            imageBase64:dataURL
           
           
            

        },
        type : 'POST',
        url : '/post/'+imgid+'/edit/rotate',
        success:function(data){
            jQuery(targetimage).attr( "src","data:image/png;base64," + data )
        }
    })
    .done(function(data) {
    if (data.error){
    jQuery('#errorAlert').text(data.error).show();
         jQuery('#successAlert').hide();
    }
    else{
       
    }
  event.preventDefault();
    });
}






  
    