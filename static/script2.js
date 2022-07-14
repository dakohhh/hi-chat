const section = document.querySelector("section"),
      hireBtn = document.querySelector(".profile .button");
      cancelBtn = document.querySelectorAll("#close");
      

hireBtn.addEventListener("click", ()=>{
    section.classList.add("active");
})
cancelBtn.forEach(cBtn => {
    cBtn.addEventListener("click", () =>{
        section.classList.remove("active");
    })
});
console.log(cancelBtn);