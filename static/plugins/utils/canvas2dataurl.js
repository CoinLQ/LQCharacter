var tnCanvas = document.createElement('canvas');
var tnCanvasContext = tnCanvas.getContext('2d');
var bufferCanvas = document.createElement('canvas');
var bufferContext = bufferCanvas.getContext('2d');
function getImagePortion(imgObj, newWidth, newHeight, startX, startY, ratio){
 /* the parameters: - the image element - the new width - the new height - the x point we start taking pixels - the y point we start taking pixels - the ratio */
 //set up canvas for thumbnail

 tnCanvas.width = newWidth; tnCanvas.height = newHeight;
 
 /* use the sourceCanvas to duplicate the entire image. This step was crucial for iOS4 and under devices. Follow the link at the end of this post to see what happens when you don’t do this */

 bufferCanvas.width = imgObj.width;
 bufferCanvas.height = imgObj.height;
 bufferContext.drawImage(imgObj, 0, 0);
 
 /* now we use the drawImage method to take the pixels from our bufferCanvas and draw them into our thumbnail canvas */
 tnCanvasContext.drawImage(bufferCanvas, startX, startY, newWidth * ratio, newHeight * ratio,0,0, newWidth, newHeight);
 return tnCanvas.toDataURL("image/png");
}