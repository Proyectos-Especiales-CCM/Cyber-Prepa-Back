document.addEventListener("DOMContentLoaded", function () {
     const container = document.querySelector(".collapsed__students");
     const scrollButtonLeft = document.querySelector(".scroll-button.left");
     const scrollButtonRight = document.querySelector(".scroll-button.right");
 
     scrollButtonLeft.addEventListener("click", function () {
         container.scrollBy({
             left: -100,
             behavior: "smooth",
         });
     });
 
     scrollButtonRight.addEventListener("click", function () {
         container.scrollBy({
             left: 100,
             behavior: "smooth",
         });
     });
 });
