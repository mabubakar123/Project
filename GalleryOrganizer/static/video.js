
jQuery.noConflict();
  
 
var list=new Array();
var textlist=new Array();
var colorarray=new Array();
var fontsize=new Array();
var fontfamily=new Array();
var position=new Array();
var transition=new Array();


function check(id,img,color,fsize,ffamily,fpos,tran){
  
var checkid=document.getElementById(id);
var textid=document.getElementById(img);
let cid=document.getElementById(color);
let fontsizeid=document.getElementById(fsize);
let fontfamilyid=document.getElementById(ffamily);
let posk=document.getElementById(fpos);
let trans=document.getElementById(tran);

        if (checkid.checked){
           
        list.push(checkid.value); 
        fontsizeid.disabled=false;
        textid.disabled=false;
        cid.disabled=false;
        posk.disabled=false;
        fontfamilyid.disabled=false;
        trans.disabled=false;
        for(var i=0;i<list.length;i++){
            if(list[i]==img){
       colorarray[i]=cid.value;
       textlist[i]=textid.value+" ";
       fontsize[i]=fontsizeid.value;
       fontfamily[i]=fontfamilyid.value;
       position[i]=posk.value;
       transition[i]=trans.value;
       
    }

}   
      
}
    else{
        cid.disabled=true;
        fontsizeid.disabled=true;
        textid.disabled=true;trans.disabled=true;
        fontfamilyid.disabled=true;
        posk.disabled=true;
        textid.value="";
        for (var i = 0; i < list.length; i++) {
            if (list[i] == checkid.value) {
                
                textlist.splice(i,1);
                colorarray.splice(i,1);
                list.splice(i, 1);
                fontsize.splice(i,1);
                fontfamily.splice(i,1);
                position.splice(i,1);
                transition.splice(i,1);
              
            }
    }

}
}

function imagetext(id,color){
  
    var checkid=document.getElementById(id);


    for(var i=0;i<list.length;i++){
        if(list[i]==id){
  
   textlist[i]=checkid.value;
   
}
else{
   
}
}



    }
function colortext(id,color){
  
        
        var colorid=document.getElementById(color);
    
        for(var i=0;i<list.length;i++){
            if(list[i]==id){
colorarray[i]=colorid.value;
}

    
    }
        }
function fosize(id,fontsizea){
  
        
var fontid=document.getElementById(fontsizea);
        
            for(var i=0;i<list.length;i++){
                if(list[i]==id){
           fontsize[i]=fontid.value;
           
    }
    }
}
function fofamily(id,family){
  
        
    var fam=document.getElementById(family);
            
                for(var i=0;i<list.length;i++){
                    if(list[i]==id){
               fontfamily[i]=fam.value;
               
        }
        }
    }

function pos(id,pos){
  
        
        var fam=document.getElementById(pos);
                
                    for(var i=0;i<list.length;i++){
                        if(list[i]==id){
                   position[i]=fam.value;
                   
            }
            }
        }
function animation(id,trans){
  
        
            var transi=document.getElementById(trans);
                    
            for(var i=0;i<list.length;i++){
                if(list[i]==id){
                    transition[i]=transi.value;
                       }
                }
            }
    


var a=document.getElementById('intro1');
a.addEventListener("click", function(){
    document.getElementById('hide-i').style.display="block";
    document.getElementById('intro').style.display="block";
});
var a=document.getElementById('finish1');
a.addEventListener("click", function(){
    document.getElementById('hide-f').style.display="block";
    document.getElementById('finish').style.display="block";
});
var a=document.getElementById('hide-i');
a.addEventListener("click", function(){
    document.getElementById('intro').value="";
    document.getElementById('intro').style.display="none";
    document.getElementById('hide-i').style.display="none";

});
var a=document.getElementById('hide-f');
a.addEventListener("click", function(){
    document.getElementById('finish').value="";
    document.getElementById('finish').style.display="none";
    document.getElementById('hide-f').style.display="none";
});


jQuery.noConflict()
jQuery('#done').on('click', function(event) {
    
   var intro=document.getElementById('intro').value;
   var finish=document.getElementById('finish').value;
   
    //  }
    // textlist[i]=textlist[i]+" ";
    
var ali=JSON.stringify(textlist);
    

    var audio=document.getElementById('file');
    var fps=document.getElementById('fps').value;
    var counter=0;

    if(audio.files.length==0){
        jQuery('#errorAlert').text("Audio file missing").show();
        console.log(textlist);
    }
    else{
        counter=counter+1;
    }
    if (list.length<2){
        jQuery('#errorAlert').text("Mark 2 or more images").show();
    }
    else{
        counter=counter+1;
    }
    if ((list.length<2) && (audio.files.length==0)){
        jQuery('#errorAlert').text("Mark images and upload audio file").show();
    
    } 



  



if (counter==2){

var formData = new FormData();
formData.append('audio',audio.files[0]);

formData.append('array',list);
formData.append('fps',fps);
formData.append('transition',jQuery("#sel1").val());
formData.append('textarray',ali);
formData.append('colorarray',colorarray);
formData.append('fontsize',fontsize);
formData.append('fontfamily',fontfamily);
formData.append('fontposition',position);
formData.append('transition1',transition);
formData.append('intro',intro);
formData.append('finish',finish);

jQuery('#successAlert').text("Creating Your Video. Wait!").show();
jQuery('#errorAlert').hide();
jQuery.ajax({
    data : formData,
    cache: false,
    contentType: false,
    processData: false,
    dataType: 'json',
    type : 'POST',
    url : '/videoclip'
})
.done(function(data) {
if (data.error){

}
else{
 jQuery('#successAlert').text("Video created").show();
    // setTimeout(() => {
    //     window.location.href="/home"
    // }, 3000); 
    
    window.open("video",'_blank');
}

});

event.preventDefault();
}
});
