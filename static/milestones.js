milestoneBtns = document.querySelectorAll('.milestone-btn')
milestones = document.querySelectorAll('.milestones')

milestoneBtns[0].addEventListener('click', function(){
    milestones[0].classList.toggle('toggleMilestone')
})
milestoneBtns[1].addEventListener('click', function(){
    milestones[1].classList.toggle('toggleMilestone')
})
milestoneBtns[2].addEventListener('click', function(){
    milestones[2].classList.toggle('toggleMilestone')
})
milestoneBtns[3].addEventListener('click', function(){
    milestones[3].classList.toggle('toggleMilestone')
})