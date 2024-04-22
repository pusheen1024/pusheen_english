"use strict"

function mouseButtonDown(event){
    mouse.x = event.pageX - this.offsetLeft;
    mouse.y = event.pageY - this.offsetTop;
    draw = true;
    context.beginPath();
    context.moveTo(mouse.x, mouse.y);
}

function mouseMove(event) {
     if (draw) {
        mouse.x = event.pageX - this.offsetLeft;
        mouse.y = event.pageY - this.offsetTop;
        context.lineTo(mouse.x, mouse.y);
        context.stroke();
    }
}

function mouseButtonUp(event) {
    mouse.x = event.pageX - this.offsetLeft;
    mouse.y = event.pageY - this.offsetTop;
    context.lineTo(mouse.x, mouse.y);
    context.stroke();
    context.closePath();
    draw = false;
}

function drawImage() {
    context.drawImage(image, 0, 0);
}

const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");
var image = new Image();
image.src = "static/img/crossword.png";
image.onload = drawImage
const mouse = {x: 0, y: 0};
let draw = false;
canvas.addEventListener("mousedown", mouseButtonDown)
canvas.addEventListener("mousemove", mouseMove)
canvas.addEventListener("mouseup", mouseButtonUp)